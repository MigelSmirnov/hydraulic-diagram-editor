#!/usr/bin/env python3
"""Convert plan.json into the cadcraft_bridge YAML: wall-face polylines and junctions.

Output follows projects/panelforge_sandbox/cadcraft_bridge in code-factory:
project.yaml carries walls {id, layer, closed, points_mm}; junctions.yaml carries
the contacts gate.py checks. Wall faces are split by layer and left open where a
wall of one layer meets a wall of another, so no end cap and no host face remains.
"""
import argparse
import json
from pathlib import Path

import yaml
from shapely.geometry import LineString, Polygon, box
from shapely.ops import linemerge, unary_union

HERE = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument("--plan", type=Path, default=HERE / "plan.json")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
plan = json.loads(args.plan.read_text(encoding="utf-8"))
t = plan["thickness"]

# Host first: a later layer is the branch where it meets an earlier one.
LAYERS = {
    "WALLS_EXTERIOR": f"EXTERIOR_{t['exterior']}",
    "WALLS_BEARING": f"BEARING_{t['bearing']}",
    "WALLS_PARTITION": f"PARTITIONS_{t['partition']}",
}


def shape(wall):
    return box(*wall["rect"]) if "rect" in wall else Polygon(wall["polygon"])


def r(v):
    return round(float(v), 4) + 0.0


def straight_parts(geometry):
    """Maximal straight segments of a linear geometry."""
    if geometry.is_empty:
        return []
    merged = linemerge(geometry) if geometry.geom_type != "LineString" else geometry
    lines = [merged] if merged.geom_type == "LineString" else list(merged.geoms)
    parts = []
    for line in lines:
        pts = list(line.simplify(0).coords)
        parts += [(a, b) for a, b in zip(pts, pts[1:])]
    return parts


windows = unary_union([box(*w["rect"]) for w in plan["windows"]])
solids, taken = {}, None
for source, layer in LAYERS.items():
    solid = unary_union([shape(w) for w in plan["walls"] if w["layer"] == source])
    if source == "WALLS_EXTERIOR":
        solid = solid.difference(windows)
    if taken is not None:
        solid = solid.difference(taken)
    solids[layer] = solid
    taken = solid if taken is None else taken.union(solid)

names = list(solids)
junctions, shared = [], {name: [] for name in names}
for i, host in enumerate(names):
    for branch in names[i + 1:]:
        contact = solids[host].boundary.intersection(solids[branch].boundary)
        lines = [g for g in getattr(contact, "geoms", [contact]) if g.geom_type in ("LineString", "MultiLineString")]
        for a, b in straight_parts(unary_union(lines)) if lines else []:
            junctions.append({"host_layer": host, "branch_layer": branch,
                              "contact": [[r(a[0]), r(a[1])], [r(b[0]), r(b[1])]]})
            shared[host].append(LineString([a, b]))
            shared[branch].append(LineString([a, b]))

walls = []
for layer in names:
    faces = solids[layer].boundary
    if shared[layer]:
        faces = faces.difference(unary_union(shared[layer]).buffer(1e-6))
    merged = linemerge(faces) if faces.geom_type != "LineString" else faces
    for line in ([merged] if merged.geom_type == "LineString" else merged.geoms):
        pts = [[r(x), r(y)] for x, y in line.simplify(0).coords]
        # The buffer trims ~1e-6 off each open end; rounding puts the ends back on the contact.
        closed = pts[0] == pts[-1] and len(pts) > 2
        walls.append({"layer": layer, "closed": closed, "points_mm": pts[:-1] if closed else pts})
for w in plan["windows"]:
    x0, y0, x1, y1 = w["rect"]
    for y in (y0, y1, *w["glass_y"]):
        walls.append({"layer": "WINDOWS", "closed": False, "points_mm": [[r(x0), r(y)], [r(x1), r(y)]]})
for item in plan["built_in"]:
    walls.append({"layer": "BUILT_IN", "closed": False, "points_mm": [[r(x), r(y)] for x, y in item["points"]]})
walls.sort(key=lambda w: (list(LAYERS.values()) + ["WINDOWS", "BUILT_IN"]).index(w["layer"]))
walls = [{"id": f"CAD-{n:02d}", **w} for n, w in enumerate(walls, 1)]
junctions.sort(key=lambda j: (j["host_layer"], j["branch_layer"], j["contact"]))
junctions = [{"id": f"J-{n:02d}", **j} for n, j in enumerate(junctions, 1)]

dimensions = []
for d in plan["dimensions"]:
    orient = {"h": "horizontal", "v": "vertical", "aligned": "aligned"}[d["kind"]]
    p1, p2, at = d["p1"], d["p2"], d["at"]
    offset = at - p1[1] if orient == "horizontal" else at - p1[0] if orient == "vertical" else at
    dimensions.append({"orient": orient, "p1": p1, "p2": p2, "offset": offset, "expect_mm": d["cm"] * 10})

minx, miny, maxx, maxy = taken.bounds
project = {
    "schema_version": "0.1",
    "project_id": plan["id"],
    "units": "mm",
    "source_checkpoint": "hydraulic-diagram-editor experiments/cadcraft/sketch_plan/plan.json",
    "note": "Draft from a photographed hand-dimensioned sketch; open questions are listed in questions. Not a survey.",
    "junctions_file": "junctions.yaml",
    "recipes": [],
    "layers": {**{name: color for name, color in zip(names, (8, 30, 5))}, "WINDOWS": 4, "BUILT_IN": 9},
    "sheet": {"title": "APARTMENT PLAN FROM SKETCH", "viewport_mm": [150, 226],
              "viewport_center_mm": [100, 162], "pdf_origin_mm": [25, 49],
              "view_center_mm": [r((minx + maxx) / 2), r((miny + maxy) / 2)]},
    "walls": walls,
    "dimensions": dimensions,
    "questions": [{"n": q["n"], "at_mm": q["at"], "text": q["text"]} for q in plan["questions"]],
}
args.output.mkdir(parents=True, exist_ok=True)


class Dumper(yaml.SafeDumper):
    pass


def represent_list(dumper, data):
    flat = all(isinstance(v, (int, float)) for v in data)
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flat)


Dumper.add_representer(list, represent_list)
for name, data in (("project.yaml", project),
                   ("junctions.yaml", {"schema_version": "0.2", "tolerance_mm": 0.05, "junctions": junctions})):
    (args.output / name).write_text(yaml.dump(data, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=120),
                                    encoding="utf-8")
print(f"walls: {len(walls)}, junctions: {len(junctions)}, dimensions: {len(dimensions)}")
