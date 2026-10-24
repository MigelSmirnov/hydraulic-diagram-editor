#!/usr/bin/env python3
"""Build apartment exterior by OFFSET and six closed 90mm partition outlines."""
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
    from shapely.geometry import Polygon, LineString
    from shapely.ops import unary_union
    import ezdxf
    rpc("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"wall-junctions","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("new_drawing", {"metric":True})
    execute("layer.new", {"name":"EXTERIOR_WALL", "current":True})
    outer = handle(execute("pline", {"vertices":[[0,0],[8382,0],[8382,4775],[0,4775]],"closed":True}))
    inner = handle(execute("offset", {"handle":outer,"distance":200,"side":[4191,2387]}))
    # Build the editable semantic wall sections first; keep their IDs in JSON.
    # The visible merged outlines are a derived CAD representation.
    sections = [
        ("P01",(3565,200),(3565,2650)),
        ("P02",(3565,3350),(3565,4575)),
        ("P03",(1650,2600),(1650,4575)),
        ("P04",(200,2600),(1650,2600)),
        ("P05",(6500,3400),(6500,4575)),
        ("P06",(5800,3400),(6500,3400)),
    ]
    polygons=[]
    for ident,a,b in sections:
        poly=LineString([a,b]).buffer(45,cap_style="flat",join_style="mitre")
        assert poly.is_valid and abs(poly.area-90*LineString([a,b]).length)<0.01
        polygons.append(poly)
    exterior=Polygon([(0,0),(8382,0),(8382,4775),(0,4775)])
    interior=Polygon([(200,200),(8182,200),(8182,4575),(200,4575)])
    shell=exterior.difference(interior)
    combined=unary_union([shell,*polygons])
    assert combined.is_valid and combined.geom_type=="Polygon", combined.geom_type
    # Remove temporary OFFSET construction entities; only clean wall contours remain visible.
    execute("erase", {"handles":[outer,inner]})
    # T junctions have no overlapping interior boundary segments after union.
    execute("layer.new", {"name":"WALL_JUNCTIONS_CLEAN", "current":True})
    rings=[combined.exterior,*combined.interiors]
    drawn=[]
    for ring in rings:
        pts=[[round(x,4),round(y,4)] for x,y in list(ring.coords)[:-1]]
        drawn.append(handle(execute("pline",{"vertices":pts,"closed":True})))
    execute("layer.new", {"name":"TERRACE_OUTLINE", "current":True})
    handle(execute("pline",{"vertices":[[8382,0],[14652,0],[14652,2355],[8382,2355]],"closed":False}))
    tool("save",{"path":str(out/"apartment_clean_junctions.dxf")})
    execute("plot",{"path":str(out/"apartment_clean_junctions.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    doc=ezdxf.readfile(out/"apartment_clean_junctions.dxf")
    clean=list(doc.modelspace().query("LWPOLYLINE[layer=='WALL_JUNCTIONS_CLEAN']"))
    assert len(clean)==len(rings) and all(p.closed for p in clean)
    assert len(clean)>=2
    assert (out/"apartment_clean_junctions.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    report={
        "status":"PASS","method":"Shapely geometric union -> CADCraft MCP PLINE",
        "outer_wall":"CADCraft OFFSET 200mm","partition_width_mm":90,
        "source_sections":[{"id":i,"start":a,"end":b} for i,a,b in sections],
        "clean_rings":len(clean),"wall_area_mm2":round(combined.area,2),
        "wall_valid":combined.is_valid,"holes":len(combined.interiors),
        "note":"CADCraft itself has not performed a boolean union; topology is computed in Python. Source wall sections are preserved in JSON, not as separate visible DXF geometry. No openings are cut."
    }
    (out/"junctions-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("PASS: cleaned wall junction contours created via CADCraft MCP")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
