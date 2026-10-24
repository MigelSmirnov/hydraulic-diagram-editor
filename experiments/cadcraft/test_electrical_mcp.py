#!/usr/bin/env python3
"""End-to-end CADCraft MCP test: geometry -> BLOCK -> INSERT -> DXF/PNG."""
import json
import subprocess
from pathlib import Path

out = Path("cadcraft-test-output")
out.mkdir(exist_ok=True)
process = subprocess.Popen(
    ["_cadcraft/target/release/cadcraft-cli", "mcp"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, bufsize=1,
)
seq = 0
def rpc(method, params=None):
    global seq
    seq += 1
    request = {"jsonrpc": "2.0", "id": seq, "method": method, "params": params or {}}
    process.stdin.write(json.dumps(request) + "\n")
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
    if result.get("isError"):
        raise RuntimeError(f"{name}: {result}")
    texts = [item["text"] for item in result.get("content", []) if item.get("type") == "text"]
    if not texts:
        raise RuntimeError(f"{name}: missing text response")
    return json.loads(texts[0])

def execute(command, params):
    return tool("execute", {"command": command, "params": params})

def handle(result):
    if isinstance(result, dict):
        if isinstance(result.get("handle"), str):
            return result["handle"]
        handles = result.get("handles")
        if isinstance(handles, list) and len(handles) == 1 and isinstance(handles[0], str):
            return handles[0]
    raise RuntimeError(f"Expected exactly one entity handle: {result}")

try:
    rpc("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"electrical-wall-anchor","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("new_drawing", {"metric":True})
    # Two perpendicular walls represented as rectangular closed line segments.
    walls = {
        "WALL_H": {"start":[0,0],"end":[5000,0],"thickness_mm":150},
        "WALL_V": {"start":[5000,0],"end":[5000,3500],"thickness_mm":150}
    }
    execute("layer.new", {"name":"WALLS", "current":True})
    def segment(a,b):
        return handle(execute("line",{"points":[a,b]}))
    for a,b in [
        ([0,0],[5000,0]),([5000,0],[5000,150]),
        ([5000,150],[0,150]),([0,150],[0,0]),
        ([5000,0],[5150,0]),([5150,0],[5150,3500]),
        ([5150,3500],[5000,3500]),([5000,3500],[5000,0])
    ]:
        segment(a,b)
    execute("layer.new", {"name":"ELECTRICAL", "current":True})
    # Symbol graphics: 6 mm on paper at 1:50 => 300 mm in model.
    # Local origin is wall attachment point; symbol extends into room.
    symbol_handles = []
    for cx in (-75,75):
        symbol_handles.append(handle(execute("circle",{"center":[cx,90],"radius":55})))
        for dx in (-18,18):
            symbol_handles.append(handle(execute("circle",{"center":[cx+dx,90],"radius":5})))
    symbol_handles.append(segment([-150,0],[150,0]))
    block = execute("block",{"name":"ELEC_DOUBLE_SOCKET_1_50","base":[0,0],"handles":symbol_handles,"keep":"delete"})
    assert block.get("block")=="ELEC_DOUBLE_SOCKET_1_50"
    # Anchor point on wall inner face. Rotation follows wall tangent.
    anchors = [
        {"id":"SOCKET_1","wall":"WALL_H","point":[2000,150],"rotation_deg":0,"side":"interior"},
        {"id":"SOCKET_2","wall":"WALL_V","point":[5000,1900],"rotation_deg":90,"side":"interior"},
    ]
    for a in anchors:
        result=execute("insert",{"name":"ELEC_DOUBLE_SOCKET_1_50","at":a["point"],"scale":1,"rotation":a["rotation_deg"]})
        a["handle"]=handle(result)
    tool("save",{"path":str(out/"electrical_wall_socket.dxf")})
    tool("save",{"path":str(out/"electrical_wall_socket.png")})
    import ezdxf
    d=ezdxf.readfile(out/"electrical_wall_socket.dxf")
    inserts=list(d.modelspace().query("INSERT"))
    assert len(inserts)==2, len(inserts)
    assert sorted(round(x.dxf.rotation) for x in inserts)==[0,90]
    assert "ELEC_DOUBLE_SOCKET_1_50" in d.blocks
    (out/"electrical_anchors.json").write_text(json.dumps({
        "scale":"1:50","paper_symbol_width_mm":6,
        "model_symbol_width_mm":300,"walls":walls,"anchors":anchors,
        "warning":"Anchors are sidecar metadata; moving walls does not yet auto-update socket INSERTs."
    },ensure_ascii=False,indent=2),encoding="utf-8")
    print("PASS: two sockets inserted with 0 and 90 degree rotation and sidecar wall anchors")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
