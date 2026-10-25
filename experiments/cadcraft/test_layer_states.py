#!/usr/bin/env python3
"""Layer visibility and layer states on the finished apartment drawing.

Runs after test_apartment_p01_integrated.py and opens its DXF. Proves the
"draw plumbing, hide it, draw electrical" workflow: named layer states,
on/frozen/plot flags, fixed-scale sheets and persistence through DXF.
"""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageOps

out = Path("cadcraft-test-output")
src = out / "apartment_p01_integrated.dxf"
assert src.exists(), f"{src} missing: run test_apartment_p01_integrated.py first"
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

def tool(name, args=None, ok=True):
    result = rpc("tools/call", {"name": name, "arguments": args or {}})
    text = next(item["text"] for item in result.get("content", []) if item.get("type") == "text")
    if result.get("isError"):
        if ok:
            raise RuntimeError(f"{name}: {text}")
        return {"error": text}
    return json.loads(text)

def execute(command, params=None, ok=True):
    return tool("execute", {"command": command, "params": params or {}}, ok=ok)

# A fixed window and scale give sheets that overlay pixel for pixel;
# fit=true rescales every sheet to its own visible extents.
WINDOW = [[-1500, -1500], [16000, 6500]]
def plot(name):
    path = out / f"layers_{name}.png"
    execute("plot", {"path": str(path), "output": "png", "layout": "Model", "paper": "A3", "landscape": True,
                     "fit": False, "scale": "1:50", "plotArea": "window", "window": WINDOW})
    image = Image.open(path).convert("L")
    return image, ImageOps.invert(image).getbbox()

def layer(name):
    return next(l for l in execute("layer")["layers"] if l["name"] == name)

try:
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "layer-states", "version": "0.1"}})
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("open", {"path": str(src)})

    execute("layer.new", {"name": "PLUMBING", "color": 5, "current": True})
    execute("circle", {"center": [400, 400], "radius": 60})
    execute("pline", {"vertices": [[400, 400], [2800, 400], [2800, 1200]], "closed": False})
    execute("layer.current", {"name": "0"})

    execute("layerstate.save", {"name": "ALL"})
    execute("layer.set", {"name": "ELECTRICAL_SOCKET", "on": False})
    execute("layer.set", {"name": "DIMENSIONS", "on": False})
    execute("layerstate.save", {"name": "PLUMBING_SHEET"})
    execute("layer.set", {"name": "ELECTRICAL_SOCKET", "on": True})
    execute("layer.set", {"name": "PLUMBING", "frozen": True})
    execute("layerstate.save", {"name": "ELECTRICAL_SHEET"})
    states = [s["name"] for s in execute("layerstate.list")["states"]]
    assert states == ["ALL", "PLUMBING_SHEET", "ELECTRICAL_SHEET"], states

    execute("layerstate.restore", {"name": "ALL"})
    all_img, all_box = plot("all")
    execute("layerstate.restore", {"name": "PLUMBING_SHEET"})
    assert not layer("ELECTRICAL_SOCKET")["on"] and layer("PLUMBING")["on"]
    plumbing_img, plumbing_box = plot("plumbing_sheet")
    # Trap: query_entities still returns objects on hidden layers.
    hidden = tool("query_entities", {"layer": "ELECTRICAL_SOCKET"})["count"]
    assert hidden == 3, hidden
    execute("layerstate.restore", {"name": "ELECTRICAL_SHEET"})
    assert layer("PLUMBING")["frozen"]
    electrical_img, electrical_box = plot("electrical_sheet")
    assert tool("query_entities", {"layer": "PLUMBING"})["count"] == 2

    # Hidden layers are not printed: fewer ink pixels than the full sheet.
    def ink(image):
        return sum(image.histogram()[:128])
    assert ink(plumbing_img) < ink(all_img) and ink(electrical_img) < ink(all_img)
    # Same window and scale: the walls start at the same pixel on every sheet.
    assert plumbing_box[:2] == electrical_box[:2], (plumbing_box, electrical_box)

    # Walls only: 8382 mm at 1:50 is 167.64 mm on A3 (420 mm wide).
    execute("layerstate.restore", {"name": "ALL"})
    for name in ["DIMENSIONS", "ELECTRICAL_SOCKET", "PLUMBING", "TERRACE_OUTLINE", "PARTITIONS_90", "P01_JUNCTION_90"]:
        execute("layer.set", {"name": name, "on": False})
    walls_img, walls_box = plot("walls_only")
    paper_mm = (walls_box[2] - walls_box[0]) / (walls_img.size[0] / 420)
    assert abs(paper_mm - 8382 / 50) < 1.0, paper_mm

    # plot=false keeps a layer on screen but out of the sheet.
    execute("layerstate.restore", {"name": "ALL"})
    execute("layer.set", {"name": "DIMENSIONS", "plot": False})
    noplot_img, _ = plot("dimensions_noplot")
    assert ink(noplot_img) < ink(all_img)
    execute("layer.set", {"name": "DIMENSIONS", "plot": True})

    # Guards.
    execute("layer.current", {"name": "PLUMBING"})
    frozen_current = execute("layer.set", {"name": "PLUMBING", "frozen": True}, ok=False)
    assert "cannot freeze the current layer" in str(frozen_current), frozen_current
    execute("layer.current", {"name": "0"})
    execute("layer.set", {"name": "PLUMBING", "locked": True})
    pipe = tool("query_entities", {"layer": "PLUMBING"})["entities"][0]["handle"]
    # Trap: ERASE on a locked layer is not an error, it reports erased: 0.
    locked_erase = execute("erase", {"handles": [pipe]})
    assert locked_erase == {"erased": 0}, locked_erase
    assert tool("query_entities", {"layer": "PLUMBING"})["count"] == 2
    execute("layer.set", {"name": "PLUMBING", "locked": False})

    # Layer states and the active visibility survive save and reopen.
    execute("layerstate.restore", {"name": "PLUMBING_SHEET"})
    tool("save", {"path": str(out / "layers_with_states.dxf")})
    tool("new_drawing", {"metric": True})
    tool("open", {"path": str(out / "layers_with_states.dxf")})
    reopened = [s["name"] for s in execute("layerstate.list")["states"]]
    assert reopened == states, reopened
    assert not layer("DIMENSIONS")["on"]
    execute("layerstate.restore", {"name": "ALL"})
    assert layer("DIMENSIONS")["on"] and layer("ELECTRICAL_SOCKET")["on"]

    report = {"status": "PASS", "states": states, "hidden_layer_query_count": hidden,
              "walls_paper_mm": round(paper_mm, 2), "locked_erase": locked_erase}
    (out / "layer-states-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PASS: layer states switch plumbing/electrical sheets at fixed 1:50 and persist in DXF")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
