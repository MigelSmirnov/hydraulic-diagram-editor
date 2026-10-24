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
    # Provisional partition centre lines from the source image.
    # Keep each section a closed polyline; doors/windows are not cut yet.
    execute("layer.new", {"name":"PARTITIONS_90", "current":True})
    sections = [
        ("P01", [3565,200], [3565,2650]),
        ("P02", [3565,3350], [3565,4575]),
        ("P03", [1650,2600], [1650,4575]),
        ("P04", [200,2600], [1650,2600]),
        ("P05", [6500,3400], [6500,4575]),
        ("P06", [5800,3400], [6500,3400]),
    ]
    from math import hypot
    partitions = []
    for name, a, b in sections:
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = hypot(dx,dy)
        nx, ny = -45*dy/length, 45*dx/length
        vertices = [
            [a[0]+nx,a[1]+ny], [b[0]+nx,b[1]+ny],
            [b[0]-nx,b[1]-ny], [a[0]-nx,a[1]-ny],
        ]
        result = execute("pline", {"vertices":vertices, "closed":True})
        partitions.append({"id":name, "handle":handle(result),
                           "axis":[a,b], "vertices":vertices, "thickness_mm":90})
    tool("save", {"path":str(out/"apartment_closed_partitions.dxf")})
    execute("plot", {"path":str(out/"apartment_closed_partitions.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    import ezdxf
    doc=ezdxf.readfile(out/"apartment_closed_partitions.dxf")
    polylines=list(doc.modelspace().query("LWPOLYLINE"))
    assert len(polylines)==9, f"Expected 2 exterior, 1 terrace, 6 partitions: {len(polylines)}"
    closed=[p for p in polylines if p.closed]
    assert len(closed)==8
    bounds=[]
    for p in closed:
        xy=[(float(v[0]),float(v[1])) for v in p.get_points("xy")]
        bounds.append([min(x for x,y in xy),min(y for x,y in xy),max(x for x,y in xy),max(y for x,y in xy)])
    expected=[[0,0,8382,4775],[200,200,8182,4575]]
    for want in expected:
        assert any(all(abs(a-b)<0.01 for a,b in zip(want,got)) for got in bounds), (want,bounds)
    part_entities=[p for p in polylines if p.dxf.layer=="PARTITIONS_90"]
    assert len(part_entities)==6 and all(p.closed for p in part_entities)
    for p in part_entities:
        pts=list(p.get_points("xy"))
        edges=[hypot(pts[(i+1)%4][0]-pts[i][0],pts[(i+1)%4][1]-pts[i][1]) for i in range(4)]
        assert min(edges)==90 or abs(min(edges)-90)<0.01, edges
    png=(out/"apartment_closed_partitions.png").read_bytes()
    assert png.startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"closed-partitions-report.json").write_text(json.dumps({
        "status":"PASS","wall_thickness_mm":200,"outer_bounds_mm":[0,0,8382,4775],
        "inner_bounds_mm":[200,200,8182,4575],"polyline_count":len(polylines),"partition_count":len(partitions),
        "partitions":partitions,
        "outer_handle":outer_handle,"inner_handle":inner_handle,
        "terrace":"separate open outline, no load-bearing classification",
        "limitations":"Provisional partitions; no openings, junction cleanup, or verified wall locations"
    },indent=2),encoding="utf-8")
    print("PASS: exterior OFFSET plus six closed 90mm CADCraft partition polylines")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
