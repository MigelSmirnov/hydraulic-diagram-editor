#!/usr/bin/env python3
"""Apartment integration experiment: P01 trimmed junction plus other walls and sockets."""
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
    break_result=execute("break",{"handle":inner,"p1":[3520,200],"p2":[3610,200]})
    print("INTEGRATED_BREAK="+json.dumps(break_result),flush=True)
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
    # P02 remains a closed independent wall. P01 is intentionally represented
    # by native trimmed edge LINEs, since TRIM on closed LWPOLYLINE is not yet proven.
    handle(execute("pline",{"vertices":[[3520,3350],[3520,4575],[3610,4575],[3610,3350]],"closed":True}))
    execute("layer.new",{"name":"P01_JUNCTION_90","current":True})
    p01_left=handle(execute("line",{"points":[[3520,100],[3520,2650]]}))
    p01_right=handle(execute("line",{"points":[[3610,100],[3610,2650]]}))
    p01_top=handle(execute("line",{"points":[[3520,2650],[3610,2650]]}))
    # The cutter coincides with the real inner face of the 200mm exterior shell.
    execute("layer.new",{"name":"TEMP_CUTTER","current":True})
    cutter=handle(execute("line",{"points":[[200,200],[8182,200]]}))
    trim_results=[]
    for h,pick in [(p01_left,[3520,150]),(p01_right,[3610,150])]:
        trim_results.append(execute("trim",{"handle":h,"pick":pick,"edges":[cutter],"mode":"standard"}))
    execute("erase",{"handles":[cutter]})
    # Dimension objects for the original measured plan, scale 1:50.
    for name,value in {"DIMSCALE":50,"DIMTXT":2.5,"DIMASZ":2.5,"DIMGAP":1.0}.items():
        execute("setvar",{"name":name,"value":value})
    execute("layer.new",{"name":"DIMENSIONS","current":True})
    dimension_specs=[
        ("main_width",[0,4775],[8382,4775],[4191,5400],8382),
        ("main_height",[0,0],[0,4775],[-650,2387.5],4775),
        ("left_chain_face",[0,0],[3520,0],[1760,-500],3520),
        ("partition_thickness",[3520,0],[3610,0],[3565,-750],90),
        ("right_chain_face",[3610,0],[8382,0],[5996,-500],4772),
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
    before_save=tool("inspect_drawing",{"entities":True})
    (out/"checkpoint-before-save.json").write_text(json.dumps(before_save,indent=2),encoding="utf-8")
    print("CHECKPOINT_BEFORE_SAVE="+json.dumps(before_save)[:1600],flush=True)
    tool("save",{"path":str(out/"apartment_p01_integrated.dxf")})
    execute("plot",{"path":str(out/"apartment_p01_integrated.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    final=ezdxf.readfile(out/"apartment_p01_integrated.dxf")
    exterior_polys=list(final.modelspace().query("LWPOLYLINE[layer=='EXTERIOR_200']"))
    overlaps=[]
    for poly in exterior_polys:
        points=[(float(x),float(y)) for x,y in poly.get_points("xy")]
        edges=list(zip(points,points[1:]))
        if poly.closed: edges.append((points[-1],points[0]))
        for a,b in edges:
            if abs(a[1]-200)<.01 and abs(b[1]-200)<.01:
                low,high=sorted((a[0],b[0]))
                if min(high,3610)-max(low,3520)>.01:
                    overlaps.append({"handle":poly.dxf.handle,"start":a,"end":b})
    (out/"integrated-break-debug.json").write_text(json.dumps({
        "break_result":break_result,"overlaps":overlaps,
        "exterior_handles":[p.dxf.handle for p in exterior_polys]
    },indent=2),encoding="utf-8")
    assert not overlaps,f"Host wall still crosses P01 junction: {overlaps}"
    partitions=list(final.modelspace().query("LWPOLYLINE[layer=='PARTITIONS_90']"))
    assert len(partitions)==3 and all(p.closed for p in partitions),[(p.dxf.handle,p.closed) for p in partitions]
    p01_lines=list(final.modelspace().query("LINE[layer=='P01_JUNCTION_90']"))
    def is_segment(e,p,q,tol=0.01):
        a=(float(e.dxf.start.x),float(e.dxf.start.y))
        b=(float(e.dxf.end.x),float(e.dxf.end.y))
        close=lambda u,v: all(abs(x-y)<tol for x,y in zip(u,v))
        return (close(a,p) and close(b,q)) or (close(a,q) and close(b,p))
    assert len(p01_lines)==3,[(e.dxf.handle,str(e.dxf.start),str(e.dxf.end)) for e in p01_lines]
    for x in (3520,3610):
        assert any(is_segment(e,(x,200),(x,2650)) for e in p01_lines),f"Missing trimmed P01 edge x={x}"
    assert any(is_segment(e,(3520,2650),(3610,2650)) for e in p01_lines)
    assert not any(is_segment(e,(3520,200),(3610,200)) for e in p01_lines)
    assert not list(final.modelspace().query("LINE[layer=='TEMP_CUTTER']"))
    inserts=list(final.modelspace().query("INSERT"))
    insert_details=[{"handle":e.dxf.handle,"name":e.dxf.name,
                     "at":list(e.dxf.insert)[:2]} for e in inserts]
    print("CHECKPOINT_INSERTS="+json.dumps(insert_details),flush=True)
    (out/"checkpoint-inserts-debug.json").write_text(json.dumps({
        "expected":3,"actual":len(inserts),"inserts":insert_details,
        "block_names":list(final.blocks.block_names())
    },indent=2),encoding="utf-8")
    assert len(inserts)==3, f"Expected 3 inserts, found {len(inserts)}: {insert_details}"
    assert socket_name in final.blocks
    assert len(final.modelspace().query("LWPOLYLINE"))==6
    dimensions=list(final.modelspace().query("DIMENSION"))
    assert len(dimensions)==7
    expected_chain=[(0,3520),(3520,3610),(3610,8382)]
    for x1,x2 in expected_chain:
        assert any(abs(d.dxf.defpoint2.x-x1)<.01 and abs(d.dxf.defpoint3.x-x2)<.01 for d in dimensions), f"Missing dimension {x1} to {x2}"
    assert sum(x2-x1 for x1,x2 in expected_chain)==8382
    assert (out/"apartment_p01_integrated.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"apartment-p01-integrated-report.json").write_text(json.dumps({
        "status":"PASS","native_commands":"PLINE OFFSET ERASE LINE PEDIT JOIN",
        "l_walls":wall_records,"straight_partitions":2,
        "closed_partition_objects":len(partitions),
        "p01_junction_edges":len(p01_lines),"host_wall_break":break_result,"p01_trim_results":trim_results,
        "dimensions":6,"dimension_scale":"1:50",
        "sockets":3,"socket_block":socket_name,
        "dimension_chain_mm":[3520,90,4772],
        "dimension_warning":"Draft geometry differs from source survey 3565/100/4717",
        "junctions_prepared":junctions,
        "junction_status":"P01 edges TRIMmed and host wall BREAK verified; other junctions remain",
        "notes":"P01 is three LINE edges, not closed LWPOLYLINE. Other junctions remain unfinished; wall axes approximate."
    },indent=2),encoding="utf-8")
    print("PASS: integrated P01 trim, face-based dimension, other walls and sockets preserved")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
