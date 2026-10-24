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
    rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"native-break-junction","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})+"\n")
    process.stdin.flush()
    tool("new_drawing",{"metric":True})
    execute("layer.new",{"name":"EXTERIOR_200","current":True})
    outer=handle(execute("pline",{"vertices":[[0,0],[8382,0],[8382,4775],[0,4775]],"closed":True}))
    inner=handle(execute("offset",{"handle":outer,"distance":200,"side":[4191,2387]}))
    tool("save",{"path":str(out/"break_before.dxf")})
    before=ezdxf.readfile(out/"break_before.dxf")
    original=list(before.modelspace().query("LWPOLYLINE"))
    assert len(original)==2 and all(p.closed for p in original)
    result=execute("break",{"handle":inner,"p1":[3520,200],"p2":[3610,200]})
    print("BREAK_RESULT="+json.dumps(result),flush=True)
    tool("save",{"path":str(out/"break_after.dxf")})
    execute("plot",{"path":str(out/"break_after.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    doc=ezdxf.readfile(out/"break_after.dxf")
    polys=list(doc.modelspace().query("LWPOLYLINE"))
    def segments(p):
        pts=[(float(x),float(y)) for x,y in p.get_points("xy")]
        pairs=list(zip(pts,pts[1:]))
        if p.closed: pairs.append((pts[-1],pts[0]))
        return pairs
    all_segments=[(p.dxf.handle,a,b) for p in polys for a,b in segments(p)]
    crossing=[]
    for h,a,b in all_segments:
        if abs(a[1]-200)<.01 and abs(b[1]-200)<.01:
            low,high=sorted((a[0],b[0]))
            overlap=max(0,min(high,3610)-max(low,3520))
            if overlap>.01: crossing.append({"handle":h,"start":a,"end":b,"overlap":overlap})
    report={
        "break_result":result,"original_inner_handle":inner,
        "polylines":[{"handle":p.dxf.handle,"closed":p.closed,"vertices":len(p)} for p in polys],
        "segments_overlapping_junction":crossing,
        "outer_preserved":any(p.dxf.handle==outer and p.closed for p in polys),
        "criterion_pass":not crossing,
        "note":"Only native BREAK of closed inner OFFSET; partition edges not yet merged."
    }
    (out/"break-junction-report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("BREAK_JUNCTION_REPORT="+json.dumps(report),flush=True)
    assert report["outer_preserved"],"Exterior boundary damaged"
    assert not crossing,"Inner wall still crosses junction gap"
    assert (out/"break_after.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    print("PASS: native BREAK opens inner wall at P01 junction")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
