#!/usr/bin/env python3
"""Build downloadable DXF, A3 PDF and native DXF preview from checkpoint geometry."""
import argparse, hashlib, json, math
from pathlib import Path
import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

p=argparse.ArgumentParser()
p.add_argument("--geometry",required=True,type=Path)
p.add_argument("--output",default="dist",type=Path)
args=p.parse_args()
out=args.output
out.mkdir(parents=True,exist_ok=True)
source=json.loads(args.geometry.read_text(encoding="utf8"))
assert source["units"]=="mm" and len(source["entities"])==15
doc=ezdxf.new("R2010")
doc.header["$INSUNITS"]=4
layers={"EXTERIOR_200":8,"PARTITIONS_90":5,"BEARING_MARKED_200":30,"JOINED_T_WALLS":6}
for name,color in layers.items():doc.layers.new(name,dxfattribs={"color":color})
m=doc.modelspace()
for wall in source["entities"]:
    assert wall["layer"] in layers and len(wall["points"])>=2
    assert all(len(pt)==2 and all(math.isfinite(float(v)) for v in pt) for pt in wall["points"])
    m.add_lwpolyline(wall["points"],close=wall["closed"],dxfattribs={"layer":wall["layer"]})
# Apply the proven upper-orange T fix: break the host and remove the branch cap.
branch=next(e for e in m.query("LWPOLYLINE") if e.dxf.layer=="BEARING_MARKED_200" and any(abs(x-4667)<0.02 for x,y in e.get_points("xy")) and len(e)==10)
host=next(e for e in m.query("LWPOLYLINE") if e.dxf.layer=="EXTERIOR_200" and len(e)==2 and any(abs(x-3214.2)<0.02 for x,y in e.get_points("xy")) and any(abs(x-6510)<0.02 for x,y in e.get_points("xy")))
b=[(float(x),float(y)) for x,y in branch.get_points("xy")]
h=[(float(x),float(y)) for x,y in host.get_points("xy")]
assert abs(b[5][0]-4667)<.02 and abs(b[6][0]-4757)<.02
def host_y(x):return h[0][1]+(h[1][1]-h[0][1])*(x-h[0][0])/(h[1][0]-h[0][0])
x0,x1=4667.0,4757.0
y0,y1=host_y(x0),host_y(x1)
branch.set_points(b[:5]+[(x0,y0)],format="xy")
m.add_lwpolyline([(x1,y1)]+b[7:],dxfattribs={"layer":"BEARING_MARKED_200"})
host.set_points([h[0],(x1,y1)],format="xy")
m.add_lwpolyline([(x0,y0),h[1]],dxfattribs={"layer":"EXTERIOR_200"})
def has_segment_between(xa,xb,ya,yb):
    for e in m.query("LWPOLYLINE"):
        pts=list(e.get_points("xy"))
        for a,b in zip(pts,pts[1:]):
            if abs(a[0]-xa)<.02 and abs(b[0]-xb)<.02 and abs(a[1]-ya)<.02 and abs(b[1]-yb)<.02:return True
    return False
assert not has_segment_between(x0,x1,y0,y1)
assert not has_segment_between(x1,x0,y1,y0)
# Seven explicit dimensions; all CAD geometry stays 1:1 in mm.
doc.layers.new("DIMENSIONS",dxfattribs={"color":7})
doc.dimstyles.new("CADCRAFT_50",dxfattribs={"dimtxt":125,"dimasz":100,"dimexo":75,"dimexe":75,"dimgap":40,"dimdec":0,"dimtad":1})
dimensions=[
 ("horizontal",(15.2,547.2),(8582.8,547.2),-340),
 ("vertical",(15.2,547.2),(15.2,5418.8),-340),
 ("horizontal",(1582,2418),(3182,2418),330),
 ("horizontal",(3782,2418),(5482,2418),330),
 ("vertical",(1582,2218),(1582,2418),-300),
 ("vertical",(5482,2218),(5482,2418),320),
 ("horizontal",(4667,5000),(4757,5000),-170)]
for orient,a,b,offset in dimensions:
    if orient=="horizontal":base=((a[0]+b[0])/2,a[1]+offset);angle=0
    else:base=(a[0]+offset,(a[1]+b[1])/2);angle=90
    m.add_linear_dim(base=base,p1=a,p2=b,angle=angle,dimstyle="CADCRAFT_50",dxfattribs={"layer":"DIMENSIONS"}).render()
assert len(list(m.query("DIMENSION")))==7
# Editable A3 paperspace viewport.
sheet=doc.layouts.new("A3_1_50")
sheet.page_setup(size=(420,297),margins=(10,10,10,10),units="mm")
sheet.add_viewport(center=(210,164),size=(200,140),view_center_point=(4500,3000),view_height=7000,status=2)
sheet.add_lwpolyline([(10,10),(410,10),(410,287),(10,287)],close=True)
sheet.add_line((10,43),(410,43))
sheet.add_text("APARTMENT PLAN",dxfattribs={"height":5,"insert":(16,25)})
sheet.add_text("A3 / 1:50 / mm",dxfattribs={"height":4,"insert":(265,25)})
dxf=out/"apartment_A3_1_50.dxf"
doc.saveas(dxf)
assert len(list(ezdxf.readfile(dxf).modelspace().query("DIMENSION")))==7
# Native DXF renderer, no manually reconstructed dimensions.
fig=plt.figure(figsize=(200/25.4,140/25.4),dpi=220,facecolor="#171b23")
ax=fig.add_axes([0,0,1,1],facecolor="#171b23")
Frontend(RenderContext(doc),MatplotlibBackend(ax)).draw_layout(m,finalize=True)
ax.set_xlim(-500,9500);ax.set_ylim(-500,6500);ax.set_aspect("auto");ax.set_axis_off()
png=out/"apartment_preview.png"
fig.savefig(png,dpi=220,facecolor="#171b23",pad_inches=0)
plt.close(fig)
pdf=out/"apartment_A3_1_50.pdf"
c=canvas.Canvas(str(pdf),pagesize=(420*mm,297*mm))
c.setTitle("CADCraft apartment A3 1:50")
c.rect(10*mm,10*mm,400*mm,277*mm)
c.line(10*mm,43*mm,410*mm,43*mm)
c.drawImage(str(png),100*mm,100*mm,width=200*mm,height=140*mm)
c.setFont("Helvetica-Bold",14);c.drawString(17*mm,25*mm,"APARTMENT PLAN")
c.setFont("Helvetica",10);c.drawString(265*mm,25*mm,"A3 | 1:50")
c.setFont("Helvetica",8);c.drawString(265*mm,16*mm,"Experimental / not surveyed")
c.showPage();c.save()
assert pdf.stat().st_size>5000 and png.stat().st_size>5000
manifest={"status":"PASS","source_version":source["version"],"source_geometry_sha256":hashlib.sha256(args.geometry.read_bytes()).hexdigest(),"source_entities":15,"dimensions":7,"upper_orange_tee":"PASS","paper":"A3","scale":"1:50","pdf_plan_is_raster":True,"files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [dxf,pdf,png]}}
(out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf8")
print(json.dumps(manifest))
