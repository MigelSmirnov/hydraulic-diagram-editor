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
    rpc("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"l-wall-no-axis","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("new_drawing", {"metric":True})
    execute("layer.new", {"name":"PARTITION_90", "current":True})
    axis_points=[[0,0],[2000,0],[2000,1400]]
    axis=handle(execute("pline",{"vertices":axis_points,"closed":False}))
    left=handle(execute("offset",{"handle":axis,"distance":45,"side":[1000,300]}))
    right=handle(execute("offset",{"handle":axis,"distance":45,"side":[1000,-300]}))
    # The axis is only construction geometry; remove it before exporting.
    execute("erase",{"handles":[axis]})
    # The offset curves should have mitred corners and matching end stations.
    # Save intermediate DXF so we can inspect actual returned geometry, rather
    # than guessing the endpoint coordinates.
    tool("save",{"path":str(out/"l_wall_offset_intermediate.dxf")})
    d=ezdxf.readfile(out/"l_wall_offset_intermediate.dxf")
    curves=list(d.modelspace().query("LWPOLYLINE"))
    assert len(curves)==2, f"Expected exactly two offset edges, not axis: {len(curves)}"
    by_handle={p.dxf.handle:p for p in curves}
    assert set(by_handle)=={left,right}, (list(by_handle),left,right)
    def endpoints(poly):
        pts=list(poly.get_points("xy"))
        return ([float(pts[0][0]),float(pts[0][1])],
                [float(pts[-1][0]),float(pts[-1][1])])
    l0,l1=endpoints(by_handle[left])
    r0,r1=endpoints(by_handle[right])
    # Connect the actual end points using native CADCraft LINE commands.
    cap1=handle(execute("line",{"points":[l0,r0]}))
    cap2=handle(execute("line",{"points":[l1,r1]}))
    # PEDIT JOIN should combine the two offset polylines and cap lines
    # into one closed CAD polyline. This is what the CI test must establish.
    joined=execute("pedit",{"handle":left,"option":"join","handles2":[right,cap1,cap2],"fuzz":0.01,"convert":True})
    tool("save",{"path":str(out/"l_wall_closed_90.dxf")})
    execute("plot",{"path":str(out/"l_wall_closed_90.png"),"output":"png","layout":"Model","paper":"A3","landscape":True,"fit":True,"plotArea":"extents"})
    final=ezdxf.readfile(out/"l_wall_closed_90.dxf")
    polys=list(final.modelspace().query("LWPOLYLINE"))
    assert len(polys)==1 and polys[0].closed, f"Expected single closed polyline: {[(p.dxf.handle,p.closed) for p in polys]}"
    assert len(final.modelspace().query("LINE"))==0, "Caps must be joined, not remain loose lines"
    assert (out/"l_wall_closed_90.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a"))
    (out/"l-wall-closed-report.json").write_text(json.dumps({
        "status":"PASS","width_mm":90,"construction_axis_deleted":True,
        "closed_polyline_handle":polys[0].dxf.handle,
        "offset_handles":[left,right],"join_result":joined,
        "source_axis_points":axis_points,
    },indent=2),encoding="utf-8")
    print("PASS: single closed 90mm L wall via native OFFSET, ERASE, PEDIT JOIN")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
