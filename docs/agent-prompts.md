# Agent prompts for hydraulic diagrams

Use these prompts with an MCP client connected to the local
`hydraulic-diagram-editor` server.

The best workflow is:

1. Ask the agent to call `hydraulic_list_catalog` first.
2. Ask it to create or overwrite a named JSON diagram file.
3. Ask it to add elements using catalog `type` values.
4. Ask it to update positions, labels or rotations when the layout needs cleanup.
5. Ask it to connect ports using catalog port ids.
6. Ask it to validate the result.
7. Ask it to render a PNG preview.

---

## 1. Basic MCP smoke test

```text
Use the hydraulic-diagram-editor MCP server.

First call hydraulic_list_catalog and use only catalog element types, port ids
and line types.

Create a new diagram at hydraulic-diagram.agent.json and overwrite it if it
already exists.

Build a simple cold-water chain from left to right:
water connection -> ball valve -> filter -> pressure reducer -> water meter.

After adding the elements, use hydraulic_update_element if needed to align the
chain neatly and rename the water meter to "Счётчик ХВС".

Use cold-water pipes. Validate the diagram and render a PNG preview to
exports/agent-preview.png. Then summarize the created nodes, updated nodes,
edges, validation result and PNG path.
```

---

## 2. Solar indirect boiler

```text
Use the hydraulic-diagram-editor MCP server.

Create a new diagram at examples/mcp/solar-boiler-agent.json and overwrite it.
Call hydraulic_list_catalog before choosing element types or ports.

Build a solar domestic hot-water scheme:
- solar collector at the top;
- indirect boiler below it;
- circulation pump on the solar supply line;
- expansion tank connected to the solar return side;
- hot-water outlet from the boiler;
- cold-water inlet to the boiler.

Use hydraulic_update_element to rename the boiler to "БКН 200 л" and improve
positions or rotations after the initial placement.

Use solar supply and solar return line types where appropriate. Use cold-water
and hot-water line types for domestic water. Validate the diagram and render a
PNG preview to exports/solar-boiler-agent.png.

After rendering, explain which elements were updated, which connections were
created and mention any validation errors.
```

---

## 3. Domestic cold-water inlet group

```text
Use the hydraulic-diagram-editor MCP server.

Create a new diagram at examples/mcp/cold-water-inlet-agent.json and overwrite
it. Call hydraulic_list_catalog first.

Build a cold-water inlet group for a small domestic installation:
water connection -> ball valve -> filter -> pressure reducer -> water meter ->
indirect boiler cold inlet.

Use hydraulic_update_element to keep the inlet group in a clean horizontal row
and rename the boiler to "Бойлер ГВС".

Use pipe_cold_water for all connections. Validate the diagram and render a PNG
to exports/cold-water-inlet-agent.png.

Return a compact engineering summary of the result.
```

---

## 4. Review existing agent diagram

```text
Use the hydraulic-diagram-editor MCP server.

Read hydraulic-diagram.agent.json and validate it. Summarize:
- all elements by type and label;
- all connections by line type;
- validation errors, if any;
- engineering gaps that are visible from the diagram structure.

Do not modify the diagram unless I explicitly ask.
```

---

## 5. Iterate after review

```text
Use the hydraulic-diagram-editor MCP server.

Read hydraulic-diagram.agent.json. Improve the diagram by adding the missing
basic service elements that make sense for a domestic hot-water installation,
but do not invent unknown component types. Use hydraulic_list_catalog first if
you need to check available elements.

Use hydraulic_update_element to clean up labels, rotations and positions instead
of deleting and recreating existing nodes.

After editing, validate the diagram, render exports/agent-preview.png and list
exactly what changed.
```

---

## 6. Layout cleanup only

```text
Use the hydraulic-diagram-editor MCP server.

Read hydraulic-diagram.agent.json. Do not add or delete elements. Only improve
the layout by updating existing element positions, rotations and labels with
hydraulic_update_element. Keep the hydraulic meaning unchanged.

After editing, validate the diagram and render exports/agent-preview.png. List
all updated node ids and what changed for each one.
```

---

## Notes for agents

- Always prefer catalog ids over guessed names.
- Use `hydraulic_update_element` for layout cleanup, renaming and rotation.
- Validate before rendering.
- Keep generated files inside the repository.
- Use explicit `diagramPath` and `outputPath` in tool calls when the prompt names
  a target file.
- If a requested engineering component does not exist in the catalog, say so and
  use the closest available component only if the user asked for an approximation.
