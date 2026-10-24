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
    rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"junction-trim-test","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})+"\n")
    process.stdin.flush()
    tool("new_drawing",{"metric":True})
    execute("layer.new",{"name":"OUTER_WALL_INNER_FACE","current":True})
    boundary=handle(execute("line",{"points":[[0,200],[3000,200]]}))
    execute("layer.new",{"name":"PARTITION_90","current":True})
    # Two wall edges extend through the host face. Native TRIM must remove
    # the protruding portions and leave the edge ends exactly at y=200.
    a=handle(execute("line",{"points":[[955,100],[955,1800]]}))
    b=handle(execute("line",{"points":[[1045,100],[1045,1800]]}))
    # End cap is a separate LINE so we can test whether native erase/trim
    # removes it without altering either side face.
    cap=handle(execute("line",{"points":[[955,200],[1045,200]]}))
    tool("save",{"path":str(out/"junction_before.dxf")})
    trims=[]
    for h,pick in [(a,[955,150]),(b,[1045,150])]:
        trims.append(execute("trim",{"handle":h,"pick":pick,"edges":[boundary],"mode":"standard"}))
    execute("erase",{"handles":[cap]})
    tool("save",{"path":str(out/"junction_after.dxf")})
    execute("plot",{"path":str(out/"junction_after.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    doc=ezdxf.readfile(out/"junction_after.dxf")
    lines={e.dxf.handle:e for e in doc.modelspace().query("LINE")}
    assert cap not in lines
    assert a in lines and b in lines and boundary in lines
    for h in (a,b):
        e=lines[h]
        ys=sorted([float(e.dxf.start.y),float(e.dxf.end.y)])
        assert abs(ys[0]-200)<0.01 and abs(ys[1]-1800)<0.01,(h,ys)
    assert (out/"junction_after.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"junction-trim-report.json").write_text(json.dumps({
        "status":"PASS","trim_results":trims,"wall_face_y":200,
        "partition_width_mm":90,"cap_removed":True,
        "note":"Separate edge LINE test; does not yet trim a closed polyline in the apartment."
    },indent=2),encoding="utf-8")
    print("PASS: native TRIM removes protruding wall edges and ERASE removes cap")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
