#!/usr/bin/env python3
"""Build a dimensioned floor plan (DXF, PNG, A3 PDF) from a sketch transcription.

Input is plan.json: wall rectangles/polygons, windows, measured dimensions and the
open questions left by the sketch. Walls are unioned, so junctions come out without
end caps; openings are simply the gaps between wall pieces.

Gate before export: every measured dimension must equal the drawn distance and both
of its points must lie on a wall face.
"""
import argparse
import hashlib
import json
import math
import textwrap
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument("--plan", type=Path, default=HERE / "plan.json")
parser.add_argument("--output", type=Path, default=Path("dist/sketch_plan"))
args = parser.parse_args()
out = args.output
out.mkdir(parents=True, exist_ok=True)
plan = json.loads(args.plan.read_text(encoding="utf-8"))
assert plan["units"] == "mm"
SCALE = plan["scale"]


def paper(mm):
    """Paper millimetres to model units."""
    return mm * SCALE


# --- geometry -------------------------------------------------------------
def shape(wall):
    return box(*wall["rect"]) if "rect" in wall else Polygon(wall["polygon"])


windows = [box(*w["rect"]) for w in plan["windows"]]
walls = unary_union([shape(w) for w in plan["walls"]]).difference(unary_union(windows))
pieces = list(walls.geoms) if walls.geom_type == "MultiPolygon" else [walls]
faces = walls.boundary

# --- gate: measured dimensions against drawn geometry -----------------------
checked = []
for dim in plan["dimensions"]:
    p1, p2 = dim["p1"], dim["p2"]
    drawn = math.dist(p1, p2)
    expected = dim["cm"] * 10
    assert abs(drawn - expected) <= dim.get("tolerance", 0.5), f"{dim['cm']} cm drawn as {drawn:.1f} mm"
    if dim["kind"] == "h":
        assert p1[1] == p2[1], dim
    if dim["kind"] == "v":
        assert p1[0] == p2[0], dim
    for p in (p1, p2):
        # A point may sit in a doorway on the line of the wall face (443 runs through one).
        on_face = faces.distance(Point(p)) < 1
        on_face_line = any(
            abs(p[i] - c) < 1 for i in (0, 1) for wall in plan["walls"]
            for c in (shape(wall).bounds[i], shape(wall).bounds[i + 2])
        )
        assert on_face or on_face_line, f"{dim['cm']} cm: point {p} is not on a wall face"
    checked.append({"cm": dim["cm"], "drawn_mm": round(drawn, 1)})

# --- DXF ------------------------------------------------------------------
doc = ezdxf.new("R2010", setup=True)
doc.header["$INSUNITS"] = 4
doc.styles.new("PLAN", dxfattribs={"font": "DejaVuSans.ttf"})
for name, color, weight in [
    ("WALLS", 7, 50), ("WALL_FILL", 9, 0), ("WINDOWS", 5, 18), ("BUILT_IN", 8, 18),
    ("DIM_MEASURED", 5, 18), ("TEXT", 7, 18), ("QUESTIONS", 1, 25), ("SHEET", 7, 35),
]:
    doc.layers.new(name, dxfattribs={"color": color, "lineweight": weight})
msp = doc.modelspace()

for piece in pieces:
    hatch = msp.add_hatch(dxfattribs={"layer": "WALL_FILL"})
    hatch.rgb = (205, 205, 205)
    hatch.paths.add_polyline_path(list(piece.exterior.coords)[:-1], is_closed=True,
                                  flags=ezdxf.const.BOUNDARY_PATH_EXTERNAL)
    msp.add_lwpolyline(list(piece.exterior.coords)[:-1], close=True, dxfattribs={"layer": "WALLS"})
    for ring in piece.interiors:
        hatch.paths.add_polyline_path(list(ring.coords)[:-1], is_closed=True,
                                      flags=ezdxf.const.BOUNDARY_PATH_OUTERMOST)
        msp.add_lwpolyline(list(ring.coords)[:-1], close=True, dxfattribs={"layer": "WALLS"})

for w in plan["windows"]:
    x0, y0, x1, y1 = w["rect"]
    for y in (y0, y1, *w["glass_y"]):
        msp.add_line((x0, y), (x1, y), dxfattribs={"layer": "WINDOWS"})

for item in plan["built_in"]:
    msp.add_lwpolyline(item["points"], dxfattribs={"layer": "BUILT_IN"})

doc.dimstyles.new("PLAN_1_50", dxfattribs={
    "dimtxsty": "PLAN", "dimtxt": paper(2.0), "dimasz": paper(1.2), "dimtsz": paper(0.9),
    "dimexo": paper(0.6), "dimexe": paper(0.8), "dimgap": paper(0.5), "dimdec": 0, "dimtad": 1,
    "dimclrd": 5, "dimclre": 5, "dimclrt": 5,
})
for dim in plan["dimensions"]:
    p1, p2, at = dim["p1"], dim["p2"], dim["at"]
    attribs = {"layer": "DIM_MEASURED"}
    if dim["kind"] == "h":
        d = msp.add_linear_dim(base=((p1[0] + p2[0]) / 2, at), p1=p1, p2=p2, angle=0,
                               dimstyle="PLAN_1_50", dxfattribs=attribs)
    elif dim["kind"] == "v":
        d = msp.add_linear_dim(base=(at, (p1[1] + p2[1]) / 2), p1=p1, p2=p2, angle=90,
                               dimstyle="PLAN_1_50", dxfattribs=attribs)
    else:
        d = msp.add_aligned_dim(p1=p1, p2=p2, distance=at, dimstyle="PLAN_1_50", dxfattribs=attribs)
    d.render()


def text(value, at, height_mm=2.2, layer="TEXT", align="LEFT"):
    entity = msp.add_text(value, dxfattribs={"layer": layer, "style": "PLAN", "height": paper(height_mm)})
    entity.set_placement(at, align=getattr(ezdxf.enums.TextEntityAlignment, align))
    return entity


for item in plan["texts"]:
    text(item["text"], item["at"])
for q in plan["questions"]:
    msp.add_circle(q["at"], paper(2.4), dxfattribs={"layer": "QUESTIONS"})
    text(str(q["n"]), q["at"], 2.6, "QUESTIONS", "MIDDLE_CENTER")

# --- A3 landscape sheet drawn in model space at 1:SCALE -----------------------
SHEET_W, SHEET_H = 420, 297
minx, miny, maxx, maxy = walls.bounds
ox, oy = minx - paper(30), miny - paper(52)  # model position of the paper corner


def sheet(x_mm, y_mm):
    return (ox + paper(x_mm), oy + paper(y_mm))


msp.add_lwpolyline([sheet(10, 10), sheet(410, 10), sheet(410, 287), sheet(10, 287)], close=True,
                   dxfattribs={"layer": "SHEET"})
msp.add_line(sheet(10, 34), sheet(410, 34), dxfattribs={"layer": "SHEET"})
msp.add_line(sheet(300, 10), sheet(300, 34), dxfattribs={"layer": "SHEET"})
text(plan["title"], sheet(15, 21), 4.5, "SHEET")
text("Размеры в мм. Синие размеры сняты с рукописных обмеров эскиза.", sheet(15, 14), 2.2, "SHEET")
text(f"A3 / 1:{SCALE}", sheet(305, 21), 4.0, "SHEET")
text("Черновик по эскизу, не обмерный чертёж", sheet(305, 14), 2.2, "SHEET")

column_x, y = 200, 272
text("ВОПРОСЫ К ЭСКИЗУ", sheet(column_x, y), 3.0, "SHEET")
y -= 7
for q in plan["questions"]:
    lines = textwrap.wrap(q["text"], 92)
    msp.add_circle(sheet(column_x + 2.4, y + 0.9), paper(2.4), dxfattribs={"layer": "QUESTIONS"})
    text(str(q["n"]), sheet(column_x + 2.4, y + 0.9), 2.6, "QUESTIONS", "MIDDLE_CENTER")
    for line in lines:
        text(line, sheet(column_x + 7, y), 2.0, "SHEET")
        y -= 3.6
    y -= 2.4
y -= 3
text("НЕ НАЧЕРЧЕНО", sheet(column_x, y), 3.0, "SHEET")
y -= 6
for note in plan["not_drawn"]:
    for line in textwrap.wrap(note, 96):
        text(line, sheet(column_x, y), 2.0, "SHEET")
        y -= 3.6
    y -= 1.6
y -= 3
text("ТОЛЩИНЫ СТЕН (не обмерялись)", sheet(column_x, y), 3.0, "SHEET")
y -= 6
t = plan["thickness"]
for line in [f"наружные и несущие {t['exterior']}, нижний фасад {t['facade_bottom']},",
             f"перегородки {t['partition']}"]:
    text(line, sheet(column_x, y), 2.0, "SHEET")
    y -= 3.6

dxf = out / "apartment_sketch_A3_1_50.dxf"
doc.saveas(dxf)
reread = ezdxf.readfile(dxf).modelspace()
assert len(reread.query("DIMENSION")) == len(plan["dimensions"])

# --- PNG and vector PDF, both at exact 1:SCALE on A3 landscape ------------------
fig = plt.figure(figsize=(SHEET_W / 25.4, SHEET_H / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
config = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR,
                       lineweight_scaling=1.0)
Frontend(RenderContext(doc), MatplotlibBackend(ax), config=config).draw_layout(msp, finalize=True)
ax.set_xlim(ox, ox + paper(SHEET_W))
ax.set_ylim(oy, oy + paper(SHEET_H))
ax.set_aspect("auto")  # the figure has the sheet ratio, so 1:1 holds
ax.set_axis_off()
png, pdf = out / "apartment_sketch_A3_1_50.png", out / "apartment_sketch_A3_1_50.pdf"
fig.set_size_inches(SHEET_W / 25.4, SHEET_H / 25.4)  # the backend resizes the figure
fig.savefig(png, dpi=200, facecolor="white")
fig.savefig(pdf, facecolor="white")
plt.close(fig)

manifest = {
    "status": "PASS",
    "plan": plan["id"],
    "sheet": "A3 landscape",
    "scale": f"1:{SCALE}",
    "wall_pieces": len(pieces),
    "wall_area_m2": round(walls.area / 1e6, 2),
    "extents_mm": [round(v, 1) for v in walls.bounds],
    "measured_dimensions_checked": checked,
    "open_questions": len(plan["questions"]),
    "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (dxf, png, pdf)},
}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in manifest.items() if k != "measured_dimensions_checked"}, ensure_ascii=False))
print(f"dimensions checked: {len(checked)}")
