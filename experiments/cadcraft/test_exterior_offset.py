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
    rpc("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"outer-wall-offset-test","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("new_drawing", {"metric":True})
    execute("layer.new", {"name":"EXTERIOR_WALL", "current":True})
    outer = execute("pline", {"vertices":[[0,0],[8382,0],[8382,4775],[0,4775]],"closed":True})
    outer_handle = handle(outer)
    inner = execute("offset", {"handle":outer_handle,"distance":200,"side":[4191,2387]})
    inner_handle = handle(inner)
    execute("layer.new", {"name":"TERRACE_OUTLINE", "current":True})
    terrace = execute("pline", {"vertices":[[8382,0],[14652,0],[14652,2355],[8382,2355]],"closed":False})
    tool("save", {"path":str(out/"exterior_offset_200.dxf")})
    execute("plot", {"path":str(out/"exterior_offset_200.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    import ezdxf
    doc=ezdxf.readfile(out/"exterior_offset_200.dxf")
    polylines=list(doc.modelspace().query("LWPOLYLINE"))
    assert len(polylines)==3, f"Expected exterior, offset and terrace: {len(polylines)}"
    closed=[p for p in polylines if p.closed]
    assert len(closed)==2
    bounds=[]
    for p in closed:
        xy=[(float(v[0]),float(v[1])) for v in p.get_points("xy")]
        bounds.append([min(x for x,y in xy),min(y for x,y in xy),max(x for x,y in xy),max(y for x,y in xy)])
    expected=[[0,0,8382,4775],[200,200,8182,4575]]
    for want in expected:
        assert any(all(abs(a-b)<0.01 for a,b in zip(want,got)) for got in bounds), (want,bounds)
    png=(out/"exterior_offset_200.png").read_bytes()
    assert png.startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"exterior-offset-report.json").write_text(json.dumps({
        "status":"PASS","wall_thickness_mm":200,"outer_bounds_mm":[0,0,8382,4775],
        "inner_bounds_mm":[200,200,8182,4575],"polyline_count":len(polylines),
        "outer_handle":outer_handle,"inner_handle":inner_handle,
        "terrace":"separate open outline, no load-bearing classification",
        "limitations":"no openings; rectangle is a simplified outer shell"
    },indent=2),encoding="utf-8")
    print("PASS: true CADCraft OFFSET 200mm inward with validated exterior dimensions")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
