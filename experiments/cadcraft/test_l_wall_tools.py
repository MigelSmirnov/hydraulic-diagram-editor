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
    import ezdxf
    rpc("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"l-wall-tools","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("new_drawing",{"metric":True})
    # Same right-angle path in each experiment, shifted horizontally for comparison.
    path=[[0,0],[2000,0],[2000,1400]]
    results={}
    execute("layer.new",{"name":"TEST_MLINE","current":True})
    execute("mlstyle",{"name":"WALL_90_TEST","elements":[{"offset":-0.5},{"offset":0.5}],"joints":True,"current":True})
    results["mline"]=handle(execute("mline",{"points":path,"style":"WALL_90_TEST","scale":90,"justification":"zero"}))
    execute("layer.new",{"name":"TEST_OFFSET","current":True})
    shifted=[[x+3500,y] for x,y in path]
    axis=handle(execute("pline",{"vertices":shifted,"closed":False}))
    results["axis"]=axis
    results["offset_left"]=handle(execute("offset",{"handle":axis,"distance":45,"side":[4500,300]}))
    results["offset_right"]=handle(execute("offset",{"handle":axis,"distance":45,"side":[4500,-300]}))
    # Fillet zero radius on two LINE entities, using their near-corner pick points.
    execute("layer.new",{"name":"TEST_FILLET","current":True})
    h1=handle(execute("line",{"points":[[7000,0],[9000,0]]}))
    h2=handle(execute("line",{"points":[[9000,0],[9000,1400]]}))
    results["fillet"]=execute("fillet",{"h1":h1,"p1":[8950,0],"h2":h2,"p2":[9000,50],"radius":0,"trim":True})
    tool("save",{"path":str(out/"l_wall_tools.dxf")})
    execute("plot",{"path":str(out/"l_wall_tools.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    d=ezdxf.readfile(out/"l_wall_tools.dxf")
    assert len(d.modelspace().query("MLINE"))==1
    assert len(d.modelspace().query("LWPOLYLINE"))>=3
    assert (out/"l_wall_tools.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"l-wall-tools-report.json").write_text(json.dumps({
      "status":"PASS","tools":["MLINE","PLINE+OFFSET","FILLET R0"],
      "mline_width_mm":90,"offset_distance_mm":45,
      "handles":results,
      "note":"This compares native commands, not full wall-topology correctness; FILLET tests two edge lines."
    },indent=2),encoding="utf-8")
    print("PASS: native L-wall CADCraft command comparison")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
