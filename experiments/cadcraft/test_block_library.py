#!/usr/bin/env python3
"""Static block library: author a window once, WBLOCK it to a file, INSERT it
from that file into the finished apartment with an attribute.

Runs after test_apartment_p01_integrated.py. CADCraft cannot author dynamic
blocks, so the library holds one static block per size.
"""
import json
import subprocess
from pathlib import Path

out = Path("cadcraft-test-output")
src = out / "apartment_p01_integrated.dxf"
assert src.exists(), f"{src} missing: run test_apartment_p01_integrated.py first"
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

try:
    import ezdxf
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "block-library", "version": "0.1"}})
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()

    # Author: block local X runs along the wall, local +Y goes from the
    # outer face (y=0) to the inner face (y=200). Base point = outer-left corner.
    tool("new_drawing", {"metric": True})
    execute("layer.new", {"name": "WINDOWS", "current": True})
    for points in ([[0, 0], [900, 0]], [[0, 200], [900, 200]], [[0, 100], [900, 100]],
                   [[0, 0], [0, 200]], [[900, 0], [900, 200]]):
        execute("line", {"points": points})
    execute("attdef", {"tag": "MARK", "prompt": "Window mark", "default": "OK-1", "at": [450, -150], "height": 100})
    handles = [e["handle"] for e in tool("query_entities", {})["entities"]]
    assert len(handles) == 6, handles
    assert execute("block", {"name": "WIN_900_W200", "base": [0, 0], "handles": handles, "keep": "delete"})["block"] == "WIN_900_W200"
    path = library / "WIN_900_W200.dxf"
    written = execute("wblock", {"path": str(path), "name": "WIN_900_W200"})
    assert written["entities"] == 6, written

    # Use: the apartment never saw this block; INSERT defines it from the file.
    tool("open", {"path": str(src)})
    execute("layer.new", {"name": "WINDOWS", "current": True})
    bottom = execute("insert", {"name": "WIN_900_W200", "file": str(path), "at": [5000, 0], "rotation": 0,
                                "attribs": {"MARK": "OK-2"}})["handle"]
    # Rotation turns local +Y around the base point: +90 maps it to world -X.
    # On the left wall (outer face x=0, inner x=200) local +Y must become +X,
    # so the rotation is -90 and the base is the outer face at the window's top end.
    left = execute("insert", {"name": "WIN_900_W200", "at": [0, 3900], "rotation": -90,
                              "attribs": {"MARK": "OK-3"}})["handle"]
    marks = {t["text"]: t for t in tool("find_text", {"contains": "OK-"})["texts"]}
    assert set(marks) == {"OK-2", "OK-3"}, marks
    assert all(t["tag"] == "MARK" for t in marks.values())
    blocks = {b["name"]: b for b in execute("blocks.list")["blocks"]}
    assert blocks["WIN_900_W200"]["dynamic"] is False
    assert execute("blocks.dynamic", {"name": "WIN_900_W200"}) is None

    tool("save", {"path": str(out / "block_library_apartment.dxf")})
    execute("plot", {"path": str(out / "block_library_apartment.png"), "output": "png", "layout": "Model",
                     "paper": "A3", "landscape": True, "fit": False, "scale": "1:50",
                     "plotArea": "window", "window": [[-1500, -1500], [16000, 6500]]})

    # Geometry check in world coordinates: both windows sit inside the wall band.
    doc = ezdxf.readfile(out / "block_library_apartment.dxf")
    def world_box(handle):
        ref = doc.entitydb[handle]
        xs, ys = [], []
        for e in ref.virtual_entities():
            if e.dxftype() == "LINE":
                for p in (e.dxf.start, e.dxf.end):
                    xs.append(p.x); ys.append(p.y)
        return [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)]
    assert world_box(bottom) == [5000, 0, 5900, 200], world_box(bottom)
    assert world_box(left) == [0, 3000, 200, 3900], world_box(left)

    report = {"status": "PASS", "library_file": str(path), "inserts": {"OK-2": world_box(bottom), "OK-3": world_box(left)},
              "note": "Transparent block: wall faces show through. Openings use the opaque WIPEOUT blocks of test_opaque_openings.py."}
    (out / "block-library-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PASS: window WBLOCK to library file and INSERT from file with attribute")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
