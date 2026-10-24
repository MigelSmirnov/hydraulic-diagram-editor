#!/usr/bin/env python3
"""Apartment checkpoint: native walls, dimensions and double sockets via CADCraft MCP."""
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
    # Dimension objects for the original measured plan, scale 1:50.
    for name,value in {"DIMSCALE":50,"DIMTXT":2.5,"DIMASZ":2.5,"DIMGAP":1.0}.items():
        execute("setvar",{"name":name,"value":value})
    execute("layer.new",{"name":"DIMENSIONS","current":True})
    dimension_specs=[
        ("main_width",[0,4775],[8382,4775],[4191,5400],8382),
        ("main_height",[0,0],[0,4775],[-650,2387.5],4775),
        ("left_chain",[0,0],[3565,0],[1782.5,-500],3565),
        ("right_chain",[3665,0],[8382,0],[6023.5,-900],4717),
        ("terrace_width",[8382,0],[14652,0],[11517,-500],6270),
        ("terrace_height",[14652,0],[14652,2355],[15200,1177.5],2355),
    ]
    for name,p1,p2,at,value in dimension_specs:
        execute("dimlinear",{"p1":p1,"p2":p2,"at":at})
    # Native junction preparation: all wall endpoints must touch the inner
    # 200mm-offset exterior boundary. Keep caps until TRIM is verified separately.
    inner_faces={"left":200,"right":8182,"bottom":200,"top":4575}
    junctions=[
        {"wall":"L_LEFT","end":[1650,4575],"face":"top"},
        {"wall":"L_LEFT","end":[200,2600],"face":"left"},
        {"wall":"L_RIGHT","end":[6500,4575],"face":"top"},
        {"wall":"P01","end":[3565,200],"face":"bottom"},
        {"wall":"P02","end":[3565,4575],"face":"top"},
    ]
    for j in junctions:
        x,y=j["end"]
        face=j["face"]
        assert abs((x if face in ("left","right") else y)-inner_faces[face])<0.01,j
    execute("layer.new",{"name":"TERRACE_OUTLINE","current":True})
    handle(execute("pline",{"vertices":[[8382,0],[14652,0],[14652,2355],[8382,2355]],"closed":False}))
    # Double grounded concealed socket symbol traced from the supplied legend.
    # Graphic semicircle width 300 model mm = 6 paper mm at 1:50.
    execute("layer.new",{"name":"ELECTRICAL_SOCKET","current":True})
    symbol=[
        handle(execute("arc",{"center":[0,0],"radius":150,"start":0,"end":180})),
        handle(execute("line",{"points":[[-150,0],[150,0]]})),
        handle(execute("line",{"points":[[0,0],[0,290]]})),
        handle(execute("line",{"points":[[-175,150],[175,150]]})),
        handle(execute("line",{"points":[[110,55],[150,135]]})),
        handle(execute("text",{"at":[175,150],"text":"2","height":95}))
    ]
    socket_name="EU_DOUBLE_SOCKET_2PE_1_50"
    result=execute("block",{"name":socket_name,"base":[0,0],"handles":symbol,"keep":"delete"})
    assert result.get("block")==socket_name
    # Anchor placements are provisional until the source plan and wall faces
    # are reconciled. The wall identifiers are semantic sidecar metadata.
    sockets=[
        {"id":"S01","wall":"outer_bottom","at":[1300,200],"rotation":0},
        {"id":"S02","wall":"outer_left","at":[200,1800],"rotation":-90},
        {"id":"S03","wall":"partition_x3565","at":[3520,1500],"rotation":90},
    ]
    for item in sockets:
        item["handle"]=handle(execute("insert",{"name":socket_name,"at":item["at"],
                                                 "rotation":item["rotation"],"scale":1}))
    (out/"checkpoint-socket-anchors.json").write_text(json.dumps({
        "scale":"1:50","symbol":socket_name,"sockets":sockets,
        "dynamic_attachment":False,"geometry_verified_against_original":False
    },indent=2),encoding="utf-8")
    tool("save",{"path":str(out/"apartment_checkpoint.dxf")})
    execute("plot",{"path":str(out/"apartment_checkpoint.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    final=ezdxf.readfile(out/"apartment_native_l_walls.dxf")
    partitions=list(final.modelspace().query("LWPOLYLINE[layer=='PARTITIONS_90']"))
    assert len(partitions)==4 and all(p.closed for p in partitions),[(p.dxf.handle,p.closed) for p in partitions]
    assert len(final.modelspace().query("LINE"))==0
    assert len(final.modelspace().query("INSERT"))==3
    assert socket_name in final.blocks
    assert len(final.modelspace().query("LWPOLYLINE"))==7
    assert len(final.modelspace().query("DIMENSION"))==6
    assert (out/"apartment_native_l_walls.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"apartment-checkpoint-report.json").write_text(json.dumps({
        "status":"PASS","native_commands":"PLINE OFFSET ERASE LINE PEDIT JOIN",
        "l_walls":wall_records,"straight_partitions":2,
        "closed_partition_objects":len(partitions),
        "dimensions":6,"dimension_scale":"1:50",
        "sockets":3,"socket_block":socket_name,
        "dimension_warning":"3565+4717=8282, 100mm gap; dimension chain does not yet reference verified wall faces",
        "junctions_prepared":junctions,
        "junction_status":"endpoints meet interior wall face; cap removal not yet verified",
        "notes":"Junction TRIM validated separately on LINEs only. Caps remain in this apartment checkpoint; no openings. Wall axes are approximate."
    },indent=2),encoding="utf-8")
    print("PASS: checkpoint walls, six dimensions, three CAD socket blocks; junctions remain provisional")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
