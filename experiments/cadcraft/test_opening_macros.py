#!/usr/bin/env python3
"""AutoLISP macros that keep doors and windows on their walls (lisp/hde_openings.lsp).

Runs after test_opaque_openings.py: uses its block library and the layer-states
apartment. Places openings with hde-place and the interactive HDE-OPENING command,
moves and rotates a partition with its door, and checks that HDE-CHECK reports an
opening pushed off its wall.
"""
import json
import math
import subprocess
from pathlib import Path

out = Path("cadcraft-test-output")
src = out / "layers_with_states.dxf"
library = out / "block-library"
macros = Path(__file__).resolve().parent / "lisp" / "hde_openings.lsp"
for required in (src, library / "DOOR_800_W90.dxf", library / "WIN_900_W200_OPAQUE.dxf"):
    assert required.exists(), f"{required} missing: run test_layer_states.py and test_opaque_openings.py first"
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

def lisp(code, inputs=None):
    params = {"code": code}
    if inputs:
        params["inputs"] = inputs
    result = execute("lisp", params)
    assert not result.get("error"), f"{code}: {result}"
    return result

def insert_of(handle):
    """Insertion point and rotation (degrees) of a block reference, through MCP."""
    entity = next(e for e in tool("query_entities", {"type": "INSERT"})["entities"] if e["handle"] == handle)
    g = entity["geometry"]
    return [round(g["insert"]["x"], 2), round(g["insert"]["y"], 2)], round(math.degrees(g["rotation"]) % 360, 3)

try:
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "opening-macros", "version": "0.1"}})
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("open", {"path": str(src)})
    execute("layerstate.restore", {"name": "ALL"})
    loaded = execute("appload", {"path": str(macros)})
    assert set(loaded["commands"]) == {"HDE-OPENING", "HDE-WALLMOVE", "HDE-WALLROTATE", "HDE-CHECK"}, loaded
    # Define the library blocks in this drawing (INSERT from file, then drop the reference).
    for name in ("DOOR_800_W90", "WIN_900_W200_OPAQUE"):
        h = execute("insert", {"name": name, "file": str(library / f"{name}.dxf"), "at": [0, -5000]})["handle"]
        execute("erase", {"handles": [h]})
    execute("layer.new", {"name": "OPENINGS", "current": True})

    def place(block, p, side):
        value = lisp(f'(cdr (assoc 5 (entget (hde-place "{block}" (list {p[0]} {p[1]}) (list {side[0]} {side[1]})))))')["value"]
        return value.strip('"')

    # Approximate picks (a few mm off the face) land exactly on the face; the side point sets local +Y.
    bottom = place("WIN_900_W200_OPAQUE", (5000, 3), (5000, 100))
    left = place("WIN_900_W200_OPAQUE", (2, 3000), (100, 3000))
    door = place("DOOR_800_W90", (3612, 3600), (3560, 3600))
    assert insert_of(bottom) == ([5000, 0], 0), insert_of(bottom)
    assert insert_of(left) == ([0, 3000], 270), insert_of(left)
    assert insert_of(door) == ([3610, 3600], 90), insert_of(door)

    # The interactive command answered as a person would: block name, start point, side point.
    lisp("(c:HDE-OPENING)", ["WIN_900_W200_OPAQUE", [6000, 4774], [6000, 4700]])
    top = lisp('(cdr (assoc 5 (entget (entlast))))')["value"].strip('"')
    assert insert_of(top) == ([6000, 4775], 180), insert_of(top)
    assert lisp("(hde-orphans)")["value"] == "nil"

    # P02 (closed partition polyline, faces x=3520/3610) carries its door when it moves...
    lisp("(setq p02 (car (hde-face-at (list 3612 3600))))")
    assert lisp("(hde-wall-move (list p02) (list 0 0) (list 300 0))")["value"] == "1"
    assert insert_of(door) == ([3910, 3600], 90), insert_of(door)
    # ...and when it rotates 15 degrees about its top end.
    assert lisp("(hde-wall-rotate (list p02) (list 3865 4575) 15)")["value"] == "1"
    a = math.radians(15)
    expected = [round(3865 + 45 * math.cos(a) + 975 * math.sin(a), 2), round(4575 + 45 * math.sin(a) - 975 * math.cos(a), 2)]
    assert insert_of(door) == (expected, 105), (insert_of(door), expected)
    assert lisp("(hde-orphans)")["value"] == "nil"
    # The other openings did not move.
    assert insert_of(bottom) == ([5000, 0], 0) and insert_of(left) == ([0, 3000], 270)

    # A plain MOVE of the door alone breaks the link; HDE-CHECK finds it.
    execute("move", {"handles": [door], "delta": [-500, 0]})
    assert lisp("(hde-orphans)")["value"] == f'("{door}")'
    check = lisp("(c:HDE-CHECK)")
    assert any(door in line for line in check["output"]), check

    tool("save", {"path": str(out / "opening_macros.dxf")})
    execute("plot", {"path": str(out / "opening_macros.png"), "output": "png", "layout": "Model", "paper": "A3",
                     "landscape": True, "fit": False, "scale": "1:50", "plotArea": "window",
                     "window": [[-1500, -1500], [16000, 6500]]})
    report = {"status": "PASS", "openings": {"bottom": insert_of(bottom), "left": insert_of(left),
                                             "top": insert_of(top), "door_after_rotate_and_push": insert_of(door)},
              "orphans": [door]}
    (out / "opening-macros-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PASS: openings placed on wall faces, follow wall move and rotate, orphans reported")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
