#!/usr/bin/env python3
"""Draw plan.json with native CADCraft commands over MCP, then verify the saved DXF.

Walls are unioned first (shapely), so each wall piece is one closed PLINE without
junction caps. Everything else is a native command: layer.new, pline, hatch, line,
dimlinear, dimaligned, text, circle, save, plot.

Gate: the DXF saved by CADCraft is re-read with ezdxf; wall outlines must match the
plan by count and area, and every dimension must measure what the sketch says.
"""
import argparse
import hashlib
import json
import math
import subprocess
import textwrap
from pathlib import Path

import ezdxf
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument("--plan", type=Path, default=HERE / "plan.json")
parser.add_argument("--cli", default="_cadcraft/target/release/cadcraft-cli")
parser.add_argument("--output", type=Path, default=Path("dist/sketch_plan_cadcraft"))
args = parser.parse_args()
out = args.output
out.mkdir(parents=True, exist_ok=True)
plan = json.loads(args.plan.read_text(encoding="utf-8"))
SCALE = plan["scale"]


def paper(mm):
    return mm * SCALE


def shape(wall):
    return box(*wall["rect"]) if "rect" in wall else Polygon(wall["polygon"])


walls = unary_union([shape(w) for w in plan["walls"]]).difference(
    unary_union([box(*w["rect"]) for w in plan["windows"]]))
pieces = list(walls.geoms) if walls.geom_type == "MultiPolygon" else [walls]

process = subprocess.Popen([args.cli, "mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, bufsize=1)
seq = 0
commands = {}
warnings = []


def rpc(method, params=None):
    global seq
    seq += 1
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": seq, "method": method, "params": params or {}}) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError("MCP server ended without a response: " + process.stderr.read()[-2000:])
    response = json.loads(line)
    if "error" in response:
        raise RuntimeError(str(response["error"]))
    return response["result"]


def tool(name, arguments=None):
    result = rpc("tools/call", {"name": name, "arguments": arguments or {}})
    text = next((item["text"] for item in result.get("content", []) if item.get("type") == "text"), "")
    if result.get("isError"):
        raise RuntimeError(f"{name} {json.dumps(arguments, ensure_ascii=False)[:300]}: {text}")
    return json.loads(text) if text else {}


def execute(command, params=None):
    commands[command] = commands.get(command, 0) + 1
    return tool("execute", {"command": command, "params": params or {}})


def handle(result):
    if isinstance(result.get("handle"), str):
        return result["handle"]
    handles = result.get("handles")
    if isinstance(handles, list) and len(handles) == 1:
        return handles[0]
    raise RuntimeError(f"expected one entity handle: {result}")


def layer(name, color):
    execute("layer.new", {"name": name, "color": color, "current": True})


def text(value, at, height_mm=2.2, justify="L"):
    execute("text", {"at": list(at), "text": value, "height": paper(height_mm), "justify": justify})


def ring(coords):
    return [[round(x, 4), round(y, 4)] for x, y in list(coords)[:-1]]


try:
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "sketch-plan", "version": "0.1"}})
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("new_drawing", {"metric": True})

    # Walls: one closed PLINE per ring of the unioned wall shape.
    layer("WALLS", 7)
    outlines = []
    for piece in pieces:
        loops = [handle(execute("pline", {"vertices": ring(r.coords), "closed": True}))
                 for r in (piece.exterior, *piece.interiors)]
        outlines.append(loops)
    layer("WALL_FILL", 9)
    for loops in outlines:
        try:
            execute("hatch", {"handles": loops, "pattern": "SOLID", "associative": False})
        except RuntimeError as error:  # the fill is decoration; outlines are the geometry
            warnings.append(f"hatch: {error}")

    layer("WINDOWS", 5)
    for w in plan["windows"]:
        x0, y0, x1, y1 = w["rect"]
        for y in (y0, y1, *w["glass_y"]):
            execute("line", {"points": [[x0, y], [x1, y]]})
    layer("BUILT_IN", 8)
    for item in plan["built_in"]:
        execute("pline", {"vertices": item["points"], "closed": False})

    # Dimensions at 1:SCALE, placed as on the sketch: inside the rooms.
    for name, value in {"DIMSCALE": SCALE, "DIMTXT": 2.0, "DIMASZ": 1.2, "DIMGAP": 0.5}.items():
        execute("setvar", {"name": name, "value": value})
    layer("DIM_MEASURED", 5)
    for dim in plan["dimensions"]:
        p1, p2, at = dim["p1"], dim["p2"], dim["at"]
        if dim["kind"] == "h":
            execute("dimlinear", {"p1": p1, "p2": p2, "at": [(p1[0] + p2[0]) / 2, at], "rotation": 0})
        elif dim["kind"] == "v":
            execute("dimlinear", {"p1": p1, "p2": p2, "at": [at, (p1[1] + p2[1]) / 2], "rotation": 90})
        else:
            length = math.dist(p1, p2)
            nx, ny = -(p2[1] - p1[1]) / length, (p2[0] - p1[0]) / length
            mid = [(p1[0] + p2[0]) / 2 + nx * at, (p1[1] + p2[1]) / 2 + ny * at]
            execute("dimaligned", {"p1": p1, "p2": p2, "at": mid})

    layer("TEXT", 7)
    for item in plan["texts"]:
        text(item["text"], item["at"])
    layer("QUESTIONS", 1)
    for q in plan["questions"]:
        execute("circle", {"center": q["at"], "radius": paper(2.4)})
        text(str(q["n"]), q["at"], 2.6, "MC")

    # A3 landscape sheet in model space; the plot window is the sheet itself.
    SHEET_W, SHEET_H = 420, 297
    minx, miny, _, _ = walls.bounds
    ox, oy = minx - paper(30), miny - paper(52)

    def sheet(x_mm, y_mm):
        return [ox + paper(x_mm), oy + paper(y_mm)]

    layer("SHEET", 7)
    execute("pline", {"vertices": [sheet(10, 10), sheet(410, 10), sheet(410, 287), sheet(10, 287)], "closed": True})
    execute("line", {"points": [sheet(10, 34), sheet(410, 34)]})
    execute("line", {"points": [sheet(300, 10), sheet(300, 34)]})
    text(plan["title"], sheet(15, 21), 4.5)
    text("Размеры в мм. Начерчено командами CADCraft по рукописным обмерам эскиза.", sheet(15, 14), 2.2)
    text(f"A3 / 1:{SCALE}", sheet(305, 21), 4.0)
    text("Черновик по эскизу, не обмерный чертёж", sheet(305, 14), 2.2)
    column_x, y = 200, 272
    text("ВОПРОСЫ К ЭСКИЗУ", sheet(column_x, y), 3.0)
    y -= 7
    for q in plan["questions"]:
        text(f"{q['n']}.", sheet(column_x, y), 2.0)
        for line in textwrap.wrap(q["text"], 92):
            text(line, sheet(column_x + 7, y), 2.0)
            y -= 3.6
        y -= 2.4

    dxf = out / "apartment_sketch_cadcraft.dxf"
    png = out / "apartment_sketch_cadcraft_A3_1_50.png"
    tool("save", {"path": str(dxf)})
    execute("plot", {"path": str(png), "output": "png", "layout": "Model", "paper": "A3", "landscape": True,
                     "fit": False, "scale": f"1:{SCALE}", "plotArea": "window",
                     "window": [sheet(0, 0), sheet(SHEET_W, SHEET_H)]})
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

# --- gate on what CADCraft actually saved -------------------------------------
saved = ezdxf.readfile(dxf).modelspace()
outline_entities = saved.query("LWPOLYLINE[layer=='WALLS']")
expected_rings = sum(1 + len(p.interiors) for p in pieces)
assert len(outline_entities) == expected_rings, f"wall outlines: {len(outline_entities)} != {expected_rings}"
assert all(e.closed for e in outline_entities), "open wall outline"
ring_area = sum(Polygon([(x, y) for x, y in e.get_points("xy")]).area for e in outline_entities)
expected_ring_area = sum(Polygon(p.exterior).area + sum(Polygon(r).area for r in p.interiors) for p in pieces)
assert abs(ring_area - expected_ring_area) < 100, f"wall outline area {ring_area} != {expected_ring_area}"


def measured(entity):
    a, b = entity.dxf.defpoint2, entity.dxf.defpoint3
    if entity.dimtype & 7 == 1:  # aligned
        return math.hypot(b[0] - a[0], b[1] - a[1])
    angle = math.radians(entity.dxf.get("angle", 0))
    return abs((b[0] - a[0]) * math.cos(angle) + (b[1] - a[1]) * math.sin(angle))


dims = saved.query("DIMENSION")
assert len(dims) == len(plan["dimensions"]), f"dimensions: {len(dims)} != {len(plan['dimensions'])}"
got = sorted(round(measured(e), 1) for e in dims)
want = sorted(d["cm"] * 10 for d in plan["dimensions"])
mismatch = [(g, w) for g, w in zip(got, want) if abs(g - w) > 1]
assert not mismatch, f"dimension measurements differ from the sketch (drawn, sketch): {mismatch}"
assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" and png.stat().st_size > 20000, "plot is not a real PNG"

report = {
    "status": "PASS",
    "plan": plan["id"],
    "engine": "CADCraft MCP execute",
    "commands": commands,
    "wall_outlines": len(outline_entities),
    "wall_fills": len(saved.query("HATCH")),
    "dimensions_checked_mm": got,
    "warnings": warnings,
    "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (dxf, png)},
}
(out / "cadcraft-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
