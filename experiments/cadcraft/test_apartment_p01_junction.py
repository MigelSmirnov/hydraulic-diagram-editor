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
    rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"apartment-bottom-junction","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})+"\n")
    process.stdin.flush()
    tool("new_drawing",{"metric":True})
    execute("layer.new",{"name":"EXTERIOR_200","current":True})
    outer=handle(execute("pline",{"vertices":[[0,0],[8382,0],[8382,4775],[0,4775]],"closed":True}))
    inner=handle(execute("offset",{"handle":outer,"distance":200,"side":[4191,2387]}))
    # Use a separate, exact inner-face cutting LINE for the native TRIM test.
    # The exterior OFFSET remains intact and editable in the resulting DXF.
    execute("layer.new",{"name":"JUNCTION_CUTTER","current":True})
    cutter=handle(execute("line",{"points":[[200,200],[8182,200]]}))
    execute("layer.new",{"name":"PARTITION_P01_90","current":True})
    axis=handle(execute("line",{"points":[[3565,100],[3565,2650]]}))
    # Real partition faces at x=3520 and x=3610, not at the axis x=3565.
    left=handle(execute("line",{"points":[[3520,100],[3520,2650]]}))
    right=handle(execute("line",{"points":[[3610,100],[3610,2650]]}))
    execute("erase",{"handles":[axis]})
    tool("save",{"path":str(out/"apartment_p01_before_trim.dxf")})
    trims=[
        execute("trim",{"handle":left,"pick":[3520,150],"edges":[cutter],"mode":"standard"}),
        execute("trim",{"handle":right,"pick":[3610,150],"edges":[cutter],"mode":"standard"}),
    ]
    # Do not add a cap at y=200: the partition joins the exterior face.
    # Keep an exposed top cap, since this is a single open-ended wall section.
    handle(execute("line",{"points":[[3520,2650],[3610,2650]]}))
    execute("erase",{"handles":[cutter]})
    # A face-based dimension, NOT the unresolved 3565mm source dimension.
    for key,value in {"DIMSCALE":50,"DIMTXT":2.5,"DIMASZ":2.5,"DIMGAP":1.0}.items():
        execute("setvar",{"name":key,"value":value})
    execute("layer.new",{"name":"DIMENSIONS","current":True})
    execute("dimlinear",{"p1":[0,0],"p2":[3520,0],"at":[1760,-550]})
    tool("save",{"path":str(out/"apartment_p01_junction.dxf")})
    execute("plot",{"path":str(out/"apartment_p01_junction.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    d=ezdxf.readfile(out/"apartment_p01_junction.dxf")
    lines=list(d.modelspace().query("LINE"))
    def segment(e,a,b,tol=.01):
        p=(float(e.dxf.start.x),float(e.dxf.start.y))
        q=(float(e.dxf.end.x),float(e.dxf.end.y))
        close=lambda u,v: all(abs(x-y)<tol for x,y in zip(u,v))
        return (close(p,a) and close(q,b)) or (close(p,b) and close(q,a))
    for x in (3520,3610):
        assert any(segment(e,(x,200),(x,2650)) for e in lines),f"Missing trimmed face at x={x}"
    assert not any(segment(e,(3520,200),(3610,200)) for e in lines),"Unwanted junction cap"
    assert not any(e.dxf.layer=="JUNCTION_CUTTER" for e in lines)
    dims=list(d.modelspace().query("DIMENSION"))
    assert len(dims)==1
    dim=dims[0]
    assert abs(dim.dxf.defpoint2.x-0)<.01 and abs(dim.dxf.defpoint3.x-3520)<.01
    assert abs(dim.dxf.defpoint3.x-dim.dxf.defpoint2.x-3520)<.01
    assert (out/"apartment_p01_junction.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"apartment-p01-junction-report.json").write_text(json.dumps({
        "status":"PASS","wall_id":"P01","partition_width_mm":90,
        "axis_x_mm":3565,"left_face_x_mm":3520,"right_face_x_mm":3610,
        "outer_wall_inner_face_y_mm":200,"junction_cap_present":False,
        "dimension_to_left_face_mm":3520,"original_chain_mm":3565,
        "dimension_difference_mm":45,"trim_results":trims,
        "scope":"one junction, native LINE/TRIM; closed wall polyline not modified",
        "limitations":"source dimension chain unresolved; no doors/windows; separate test only"
    },indent=2),encoding="utf-8")
    print("PASS: apartment P01 native TRIM junction and dimension to real left face")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
