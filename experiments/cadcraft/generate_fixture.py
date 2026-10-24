#!/usr/bin/env python3
"""Generate a minimal hydraulic CAD block fixture, preserving semantic ports in JSON."""
import json
from pathlib import Path
import ezdxf

out = Path("cadcraft-test-output")
out.mkdir(exist_ok=True)
doc = ezdxf.new("R2000")
doc.header["$INSUNITS"] = 4  # millimetres
for layer, color in [("HYD_SYMBOL", 7), ("HYD_PIPE", 4), ("HYD_PORT", 3)]:
    doc.layers.new(layer, dxfattribs={"color": color})
block = doc.blocks.new("HYD_CIRCULATION_PUMP", base_point=(0, 0))
block.add_circle((37, 37), 23, dxfattribs={"layer": "HYD_SYMBOL"})
for a, b in [((0,37),(14,37)),((60,37),(74,37)),((37,37),(52,27)),((37,37),(37,20)),((37,37),(23,47))]:
    block.add_line(a, b, dxfattribs={"layer": "HYD_SYMBOL"})
space = doc.modelspace()
space.add_blockref("HYD_CIRCULATION_PUMP", (0, 0))
space.add_blockref("HYD_CIRCULATION_PUMP", (200, 0))
space.add_line((74,37),(200,37),dxfattribs={"layer":"HYD_PIPE"})
for x in (0,74,200,274):
    space.add_point((x,37),dxfattribs={"layer":"HYD_PORT"})
path = out / "pump_demo.dxf"
doc.saveas(path)
check = ezdxf.readfile(path)
assert "HYD_CIRCULATION_PUMP" in check.blocks
assert len(check.modelspace().query("INSERT")) == 2
assert len(check.modelspace().query("LINE")) == 1
ports = {"units":"mm","symbol":"HYD_CIRCULATION_PUMP","ports":[{"id":"inlet","x":0,"y":37},{"id":"outlet","x":74,"y":37}],"note":"These are semantic ports in a sidecar, not native CADCraft port objects."}
(out / "ports.json").write_text(json.dumps(ports,indent=2),encoding="utf-8")
print("PASS: DXF fixture and structural assertions")
