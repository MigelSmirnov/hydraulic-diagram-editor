# Task brief: DHW with solar boiler and three-branch recirculation

Use this brief with an MCP client connected to `hydraulic-diagram-editor`.

The goal is to generate a functional hydraulic diagram, not a construction-ready
legal design.

---

## 1. Context

Object location: Barcelona, Spain.

System:

- Domestic hot water / ACS.
- Indirect boiler in a basement technical room.
- Solar collector on the roof heats the boiler coil.
- Cold-water inlet includes water treatment before the boiler.
- DHW supply has three consumer branches:
  - first floor kitchen;
  - first floor bathroom;
  - second floor bathroom.
- DHW recirculation returns from the three branches into one common return line.

Important drawing-style decisions:

- Do not draw the kitchen or bathrooms as separate consumer elements.
- Do not add dedicated manifold / гребёнка elements.
- Model distribution and return branching with `junction` points and pipes.
- Use valves on branch takeoffs where the layout remains readable.
- Use `flow-arrow` elements to show directions. Arrows should use the same
  `lineType` as the nearby pipe so they inherit the line colour.
- A text/label block is not available yet; do not invent one.
- The user may add textual annotations manually later.

---

## 2. Required MCP workflow

1. Call `hydraulic_list_catalog` first.
2. Use only actual catalog `type`, port ids and line types.
3. Create or overwrite the target diagram file.
4. Add elements.
5. Use `hydraulic_update_element` to improve positions, labels and rotations.
6. Connect ports with the correct line types.
7. Validate the diagram.
8. Render PNG.
9. Return a concise report with created elements, connections, validation errors
   and output paths.

---

## 3. Output files

Diagram JSON:

```text
examples/mcp/barcelona-dhw-solar-recirculation-v1.json
```

PNG preview:

```text
exports/barcelona-dhw-solar-recirculation-v1.png
```

---

## 4. Elements to use

Use catalog elements where available:

### Cold-water inlet and treatment

- `water-connection`
- `ball-valve`
- `filter`, if useful before the treatment block
- `water-treatment-unit`
- `pressure-reducer`, if the layout remains readable
- no `water-meter`

### Boiler and solar heating

- `indirect-boiler`
- `solar-collector`
- `circulation-pump` for solar circulation
- `expansion-tank` for the solar loop

### DHW supply and recirculation

- `junction` for branch points and convergence points
- `ball-valve` on DHW branch takeoffs where readable
- `balancing-valve` on recirculation returns where readable
- `circulation-pump` for DHW recirculation
- `flow-arrow` for direction markers

Do not create or use:

- water meter;
- dedicated consumer nodes;
- dedicated manifold nodes;
- invented text/label nodes.

---

## 5. Line types

Use catalog line types where available:

- `pipe_cold_water` for cold-water inlet and feed to boiler.
- `pipe_hot_water` for DHW supply.
- `pipe_dhw_recirculation` for DHW recirculation.
- `pipe_solar_supply` for solar supply.
- `pipe_solar_return` for solar return.
- `pipe_drain` for drains / service discharge.

---

## 6. Layout intent

Use a functional level-based layout:

- Top zone: roof / solar collector.
- Lower-left zone: cold-water inlet and water treatment.
- Lower-middle zone: basement technical room / boiler.
- Right zone: DHW supply branches and recirculation returns.

Suggested visual structure:

```text
[Roof]
Solar collector
   | solar supply / return

[Basement technical room]
Cold water -> valve -> filter/treatment -> boiler cold inlet
Solar loop -> boiler coil -> pump/expansion tank -> collector
Boiler hot outlet -> DHW trunk -> three branch junctions -> flow arrows
Three recirculation returns -> balancing valves -> common return -> recirc pump -> boiler return area
```

Keep lines readable. Prefer a clean functional diagram over physical accuracy.

---

## 7. Connection logic

### Cold-water and treatment chain

Connect left to right:

```text
water-connection -> ball-valve -> filter or water-treatment-unit -> pressure-reducer if used -> boiler cold inlet
```

If both `filter` and `water-treatment-unit` are used, place the filter before the
treatment unit.

Do not include `water-meter`.

### Solar loop

Connect the solar collector to the boiler coil with two lines:

```text
solar collector solar_supply -> boiler solar_supply
boiler solar_return -> solar pump / expansion tank area -> solar collector solar_return
```

Use the available ports from the catalog. If the exact preferred series cannot be
represented cleanly, keep the solar supply/return loop clear and validate the
result.

### DHW supply branching

From the boiler `hot_out`, create a hot-water trunk with three takeoffs using
`junction` nodes.

Each branch should end with a `flow-arrow` tinted as `pipe_hot_water`.

Do not create endpoint consumer nodes. The three arrows represent:

1. first floor kitchen;
2. first floor bathroom;
3. second floor bathroom.

Because no text block exists yet, branch names may be reported in the final
summary instead of placed on the diagram.

### DHW recirculation return

Create three recirculation return lines from the branch ends back toward a common
return line using `junction` nodes.

Where readable, place `balancing-valve` elements on the three recirculation
returns.

Then connect:

```text
three recirculation returns -> common return junction -> recirculation pump -> boiler return area
```

If the current boiler catalog does not provide a dedicated DHW recirculation
return port, connect the common return to a clearly placed `junction` near the
boiler cold inlet area and mention this as an engineering/catalog limitation in
the report.

---

## 8. Validation and report

After generation:

1. Run `hydraulic_validate_diagram`.
2. Render PNG.
3. Return:
   - diagram JSON path;
   - PNG path;
   - number of elements;
   - number of connections;
   - validation errors, if any;
   - engineering assumptions, especially the missing dedicated boiler recirculation return port;
   - note that consumer labels are not placed because a text block is not available yet.

---

## 9. Important constraints

- Do not invent catalog types or port ids.
- Do not add new source-code files.
- Do not modify application code.
- Do not draw a water meter.
- Do not draw kitchen/bathroom consumer elements.
- Do not use dedicated manifold elements.
- Use `junction` nodes for branch logic.
- Use `flow-arrow` nodes for branch direction.
- Keep all generated files inside the repository.
