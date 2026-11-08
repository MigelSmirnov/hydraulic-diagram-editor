"""Convert generated CAD drawing to B/W A3 with only left exterior dimension."""
from pathlib import Path
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext,Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import json,hashlib
out=Path("dist")
dxf=out/"apartment_A3_1_50.dxf"
doc=ezdxf.readfile(dxf)
m=doc.modelspace()
for e in list(m.query("DIMENSION")):m.delete_entity(e)
for layer in doc.layers:
    if layer.dxf.name not in ("0","Defpoints"):
        layer.dxf.color=7
        layer.dxf.lineweight=35 if layer.dxf.name=="EXTERIOR_200" else 25
if "DIMENSIONS" not in doc.layers:doc.layers.new("DIMENSIONS",dxfattribs={"color":7})
if "BW_A3" not in doc.dimstyles:doc.dimstyles.new("BW_A3",dxfattribs={"dimtxt":125,"dimasz":90,"dimdec":0,"dimtad":1})
m.add_linear_dim(base=(-350,2983),p1=(15.2,547.2),p2=(15.2,5418.8),angle=90,dimstyle="BW_A3",dxfattribs={"layer":"DIMENSIONS"}).render()
assert len(list(m.query("DIMENSION")))==1
doc.saveas(out/"apartment_BW_one_left_dimension.dxf")
# Vector PDF: real geometry in mm, plotted 1:50 on A3.
pdf=out/"apartment_BW_one_left_dimension_A3.pdf"
c=canvas.Canvas(str(pdf),pagesize=(420*mm,297*mm))
c.setTitle("CADCraft A3 B/W 1:50")
c.setLineWidth(.4);c.rect(10*mm,10*mm,400*mm,277*mm)
c.line(10*mm,43*mm,410*mm,43*mm);c.line(255*mm,10*mm,255*mm,43*mm)
def pos(x,y):return ((122+x/50)*mm,(100+y/50)*mm)
for e in m.query("LWPOLYLINE"):
    pts=[(float(x),float(y)) for x,y in e.get_points("xy")]
    if not pts:continue
    c.setLineWidth((.35 if e.dxf.layer=="EXTERIOR_200" else .25)*mm)
    path=c.beginPath();path.moveTo(*pos(*pts[0]))
    for pt in pts[1:]:path.lineTo(*pos(*pt))
    if e.closed:path.close()
    c.drawPath(path,stroke=1,fill=0)
c.setLineWidth(.18*mm)
x=-350;lo=547.2;hi=5418.8
c.line(*pos(x,lo),*pos(x,hi))
for y in (lo,hi):
    c.line(*pos(15.2,y),*pos(x-70,y))
    xx,yy=pos(x,y);c.line(xx-1.4*mm,yy-1.4*mm,xx+1.4*mm,yy+1.4*mm)
c.saveState();xx,yy=pos(x-120,(lo+hi)/2);c.translate(xx,yy);c.rotate(90)
c.setFont("Helvetica",9);c.drawCentredString(0,0,"4872");c.restoreState()
c.setFont("Helvetica-Bold",14);c.drawString(17*mm,25*mm,"APARTMENT PLAN | B/W")
c.setFont("Helvetica",10);c.drawString(266*mm,25*mm,"A3 | 1:50")
c.showPage();c.save()
# Generate black-on-white PNG from actual model lines and the single dimension.
fig=plt.figure(figsize=(12,8),facecolor="white")
ax=fig.add_subplot(111);ax.set_facecolor("white")
for e in m.query("LWPOLYLINE"):
    pts=[tuple(map(float,v)) for v in e.get_points("xy")]
    if e.closed:pts.append(pts[0])
    ax.plot([p[0] for p in pts],[p[1] for p in pts],color="black",lw=.9)
ax.plot([x,x],[lo,hi],color="black",lw=.6)
for y in (lo,hi):ax.plot([15.2,x-70],[y,y],color="black",lw=.6)
ax.text(x-120,(lo+hi)/2,"4872",rotation=90,ha="center",va="center",fontsize=10)
ax.set_aspect("equal");ax.set_xlim(-700,9100);ax.set_ylim(-300,5900);ax.axis("off")
fig.savefig(out/"apartment_BW_preview.png",dpi=170,bbox_inches="tight",facecolor="white")
plt.close(fig)
manifest={"status":"PASS","mode":"black-and-white","dimensions":1,"left_dimension_mm":4871.6,"sheet":"A3","scale":"1:50"}
(out/"bw_manifest.json").write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest))
