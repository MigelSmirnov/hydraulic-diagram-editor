#!/usr/bin/env python3
"""Opaque door and window blocks placed on top of uncut walls.

Runs after test_layer_states.py and opens its DXF. The wall is never broken:
each opening block carries a WIPEOUT that masks the wall under it, so the
block can be moved along the wall and the wall reappears behind it.
Also proves typed object snaps (INS, END, NEA, MID) at a point prompt.
"""
import json
import subprocess
from pathlib import Path

from PIL import Image

out = Path("cadcraft-test-output")
src = out / "layers_with_states.dxf"
assert src.exists(), f"{src} missing: run test_layer_states.py first"
library = out / "block-library"
library.mkdir(exist_ok=True)
process = subprocess.Popen(
    ["_cadcraft/target/release/cadcraft-cli", "mcp"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, bufsize=1,
)
seq = 0
def rpc(method, params=None):
    global seq
    seq += 1
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": seq, "method": method, "params": params or {}}) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError("MCP server ended without a response")
    response = json.loads(line)
    if "error" in response:
        raise RuntimeError(str(response["error"]))
    return response["result"]

def tool(name, args=None):
    result = rpc("tools/call", {"name": name, "arguments": args or {}})
    text = next(item["text"] for item in result.get("content", []) if item.get("type") == "text")
    if result.get("isError"):
        raise RuntimeError(f"{name}: {text}")
    return json.loads(text)

def execute(command, params=None):
    return tool("execute", {"command": command, "params": params or {}})

# The mask must overshoot the wall faces by about half a printed line width
# (0.2 mm on paper = 10 mm at 1:50), otherwise a face lying exactly on the
# mask edge stays half visible.
MARGIN = 10
WINDOW = [[-1500, -1500], [16000, 6500]]
CENTER = (7250, 2500)
PX_PER_MM = 4961 / 420 / 50  # A3 landscape PNG, 1:50

def plot(name):
    path = out / f"opaque_{name}.png"
    execute("plot", {"path": str(path), "output": "png", "layout": "Model", "paper": "A3", "landscape": True,
                     "fit": False, "scale": "1:50", "plotArea": "window", "window": WINDOW})
    return Image.open(path).convert("L")

def ink(image, x0, x1, y):
    """Dark pixels on one row between model x0 and x1 at model y."""
    row = int(1754 - (y - CENTER[1]) * PX_PER_MM)
    cols = range(int(2480 + (x0 - CENTER[0]) * PX_PER_MM), int(2480 + (x1 - CENTER[0]) * PX_PER_MM) + 1)
    return sum(1 for c in cols if image.getpixel((c, row)) < 200)

def ink_column(image, x, y0, y1):
    col = int(2480 + (x - CENTER[0]) * PX_PER_MM)
    rows = range(int(1754 - (y1 - CENTER[1]) * PX_PER_MM), int(1754 - (y0 - CENTER[1]) * PX_PER_MM) + 1)
    return sum(1 for r in rows if image.getpixel((col, r)) < 200)

def make_block(name, layer, wall, lines, arcs=()):
    """Opening block: local X along the wall, local +Y across it (0..wall), base at the corner."""
    tool("new_drawing", {"metric": True})
    execute("layer.new", {"name": layer, "current": True})
    width = max(max(p[0] for p in pts) for pts in lines)
    execute("wipeout", {"points": [[0, -MARGIN], [width, -MARGIN], [width, wall + MARGIN], [0, wall + MARGIN]]})
    for pts in lines:
        execute("line", {"points": pts})
    for arc in arcs:
        execute("arc", arc)
    handles = [e["handle"] for e in tool("query_entities", {})["entities"]]
    execute("block", {"name": name, "base": [0, 0], "handles": handles, "keep": "delete"})
    path = library / f"{name}.dxf"
    execute("wblock", {"path": str(path), "name": name})
    return path

try:
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "opaque-openings", "version": "0.1"}})
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()

    door_file = make_block("DOOR_800_W90", "DOORS", 90,
                           [[[0, 0], [0, 90]], [[800, 0], [800, 90]], [[0, 90], [0, 890]]],
                           [{"center": [0, 90], "radius": 800, "start": 0, "end": 90}])
    window_file = make_block("WIN_900_W200_OPAQUE", "WINDOWS", 200,
                             [[[0, 0], [900, 0]], [[0, 200], [900, 200]], [[0, 90], [900, 90]],
                              [[0, 110], [900, 110]], [[0, 0], [0, 200]], [[900, 0], [900, 200]]])

    tool("open", {"path": str(src)})
    execute("layerstate.restore", {"name": "ALL"})
    execute("wipeout", {"frames": "off"})
    before = plot("before")
    # P02 faces x=3520/3610, y=3350..4575. Rotation 90: local X -> +Y, local +Y -> -X,
    # so the base sits on the x=3610 face.
    execute("layer.new", {"name": "OPENINGS", "current": True})
    door = execute("insert", {"name": "DOOR_800_W90", "file": str(door_file), "at": [3610, 3600], "rotation": 90})["handle"]
    window = execute("insert", {"name": "WIN_900_W200_OPAQUE", "file": str(window_file), "at": [5000, 0], "rotation": 0})["handle"]
    placed = plot("placed")

    # Both partition faces are visible at the door's height before and masked after.
    for x in (3520, 3610):
        assert ink_column(before, x, 3700, 4300) > 0, f"face x={x} missing before door"
        assert ink_column(placed, x, 3700, 4300) == 0, f"face x={x} shows through the door"
    # The window's own centre lines replace the wall: no ink between 10 and 80 mm inside the wall.
    assert ink(placed, 5100, 5800, 40) == 0, "wall interior shows through the window"
    assert ink(placed, 5100, 5800, 0) > 0 and ink(placed, 5100, 5800, 200) > 0, "window frame lines missing"

    # Draw order: a line drawn after the block lies on top until the block is brought to front.
    execute("layer.new", {"name": "LATE", "current": True})
    execute("line", {"points": [[4800, 40], [6100, 40]]})
    late = plot("late_line")
    assert ink(late, 5100, 5800, 40) > 0, "late line expected on top of the window"
    assert execute("draworder", {"handles": [door, window], "order": "front"})["moved"] == 2
    fronted = plot("after_front")
    assert ink(fronted, 5100, 5800, 40) == 0, "window does not mask the late line after draworder front"
    execute("erase", {"handles": [e["handle"] for e in tool("query_entities", {"layer": "LATE"})["entities"]]})

    # Move along the wall: the wall is whole behind the old position.
    assert execute("move", {"handles": [window], "delta": [1500, 0]})["moved"] == 1
    moved = plot("moved")
    assert ink(moved, 5100, 5800, 0) > 0 and ink(moved, 5100, 5800, 200) > 0, "wall faces missing at old position"
    assert ink(moved, 6600, 7300, 40) == 0, "window not masking at new position"

    # Typed object snaps at a point prompt: an approximate point plus a mode.
    execute("layer.new", {"name": "SNAPS", "current": True})
    for text in ["point ins 6510,10", "point end 3615,3345", "point nea 3600,1000", "point mid 6950,5"]:
        tool("command_line", {"text": text})
    snapped = [[round(e["geometry"]["p"]["x"], 3), round(e["geometry"]["p"]["y"], 3)]
               for e in tool("query_entities", {"layer": "SNAPS"})["entities"]]
    expected = [[6500, 0], [3610, 3350], [3610, 1000], [6950, 0]]
    assert snapped == expected, snapped

    tool("save", {"path": str(out / "opaque_openings.dxf")})
    report = {"status": "PASS", "wipeout_margin_mm": MARGIN, "door": door, "window": window,
              "snaps": dict(zip(["ins", "end", "nea", "mid"], snapped))}
    (out / "opaque-openings-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PASS: opaque door/window blocks mask uncut walls, follow draw order, move, and snap")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
