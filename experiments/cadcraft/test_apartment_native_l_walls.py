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
    from math import hypot
    rpc("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"apartment-native-l-walls","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("new_drawing",{"metric":True})
    execute("layer.new",{"name":"EXTERIOR_200","current":True})
    outer=handle(execute("pline",{"vertices":[[0,0],[8382,0],[8382,4775],[0,4775]],"closed":True}))
    inner=handle(execute("offset",{"handle":outer,"distance":200,"side":[4191,2387]}))
    execute("layer.new",{"name":"PARTITIONS_90","current":True})
    l_axes=[
        ("L_LEFT",[[200,2600],[1650,2600],[1650,4575]], [900,2800], [900,2300]),
        ("L_RIGHT",[[5800,3400],[6500,3400],[6500,4575]], [6100,3550], [6100,3200])
    ]
    intermediate=[]
    for name,pts,side_a,side_b in l_axes:
        axis=handle(execute("pline",{"vertices":pts,"closed":False}))
        left=handle(execute("offset",{"handle":axis,"distance":45,"side":side_a}))
        right=handle(execute("offset",{"handle":axis,"distance":45,"side":side_b}))
        execute("erase",{"handles":[axis]})
        intermediate.append((name,pts,left,right))
    tool("save",{"path":str(out/"apartment_l_walls_intermediate.dxf")})
    snapshot=ezdxf.readfile(out/"apartment_l_walls_intermediate.dxf")
    by_handle={p.dxf.handle:p for p in snapshot.modelspace().query("LWPOLYLINE")}
    wall_records=[]
    for name,pts,left,right in intermediate:
        def ends(poly):
            vertices=list(poly.get_points("xy"))
            return ([float(vertices[0][0]),float(vertices[0][1])],
                    [float(vertices[-1][0]),float(vertices[-1][1])])
        l0,l1=ends(by_handle[left]); r0,r1=ends(by_handle[right])
        cap0=handle(execute("line",{"points":[l0,r0]}))
        cap1=handle(execute("line",{"points":[l1,r1]}))
        joined=execute("pedit",{"handle":left,"option":"join","handles2":[right,cap0,cap1],"fuzz":0.01,"convert":True})
        wall_records.append({"id":name,"axis":pts,"joined":joined,"width_mm":90})
    # Remaining independent straight partitions, as closed CAD polylines.
    straight=[
        ("P01",[3565,200],[3565,2650]),
        ("P02",[3565,3350],[3565,4575])
    ]
    for name,a,b in straight:
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=hypot(dx,dy)
        nx,ny=-45*dy/length,45*dx/length
        corners=[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],
                 [b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]]
        handle(execute("pline",{"vertices":corners,"closed":True}))
    execute("layer.new",{"name":"TERRACE_OUTLINE","current":True})
    handle(execute("pline",{"vertices":[[8382,0],[14652,0],[14652,2355],[8382,2355]],"closed":False}))
    tool("save",{"path":str(out/"apartment_native_l_walls.dxf")})
    execute("plot",{"path":str(out/"apartment_native_l_walls.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    final=ezdxf.readfile(out/"apartment_native_l_walls.dxf")
    partitions=list(final.modelspace().query("LWPOLYLINE[layer=='PARTITIONS_90']"))
    assert len(partitions)==4 and all(p.closed for p in partitions),[(p.dxf.handle,p.closed) for p in partitions]
    assert len(final.modelspace().query("LINE"))==0
    assert len(final.modelspace().query("LWPOLYLINE"))==7
    assert (out/"apartment_native_l_walls.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"apartment-native-l-walls-report.json").write_text(json.dumps({
        "status":"PASS","native_commands":"PLINE OFFSET ERASE LINE PEDIT JOIN",
        "l_walls":wall_records,"straight_partitions":2,
        "closed_partition_objects":len(partitions),
        "notes":"No union with exterior, openings or sockets. Approximate wall axes from draft."
    },indent=2),encoding="utf-8")
    print("PASS: two native closed L walls in apartment plan, no construction axes")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
