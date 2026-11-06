"""Apply upper-orange tee to a generated v35-based DXF. Never edit input."""
from pathlib import Path
import argparse, hashlib, yaml, ezdxf

p=argparse.ArgumentParser()
p.add_argument("input",type=Path)
p.add_argument("--output",required=True,type=Path)
a=p.parse_args()
spec=yaml.safe_load((Path(__file__).parent/"upper-orange-tee.yaml").read_text())
assert spec["operations"]==["snap_branch_endpoints_to_host","break_host_face","remove_branch_end_cap"]
digest=hashlib.sha256(a.input.read_bytes()).hexdigest()
d=ezdxf.readfile(a.input)
host=d.entitydb[spec["host"]["entity_handle"]]
branch=d.entitydb[spec["branch"]["entity_handle"]]
assert host.dxf.layer==spec["host"]["layer"] and branch.dxf.layer==spec["branch"]["layer"]
h=[tuple(map(float,v)) for v in host.get_points("xy")]
b=[tuple(map(float,v)) for v in branch.get_points("xy")]
assert len(h)==2 and len(b)==10 and not host.closed and not branch.closed
x0,x1=spec["contact"]["x_range_mm"]
assert x0<x1 and abs(b[5][0]-x0)<.02 and abs(b[6][0]-x1)<.02
assert h[0][0]>x1 and h[1][0]<x0
def y_at(x):
    return h[0][1]+(h[1][1]-h[0][1])*(x-h[0][0])/(h[1][0]-h[0][0])
y0,y1=y_at(x0),y_at(x1)
assert abs(b[5][1]-y0)<2 and abs(b[6][1]-y1)<2
branch.set_points(b[:5]+[(x0,y0)],format="xy")
branch.closed=False
d.modelspace().add_lwpolyline([(x1,y1)]+b[7:],close=False,dxfattribs={"layer":branch.dxf.layer})
host.set_points([(x0,y0),h[1]],format="xy")
d.modelspace().add_lwpolyline([h[0],(x1,y1)],close=False,dxfattribs={"layer":host.dxf.layer})
a.output.parent.mkdir(parents=True,exist_ok=True)
d.saveas(a.output)
assert hashlib.sha256(a.input.read_bytes()).hexdigest()==digest
