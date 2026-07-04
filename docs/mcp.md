# MCP server

Local stdio MCP server for agent-driven hydraulic diagram editing.

The server lets an AI agent edit the same JSON diagram format that the React
editor can load with `Load JSON`. The agent does not click the UI directly:
it creates elements, updates elements, connects ports, validates the document
and can render a PNG through the real editor UI.

---

## 1. Install and run

From the project root:

```bash
npm install
npm run mcp
```

The MCP server communicates over stdio, so it is normally started by an MCP
client rather than by a human terminal session.

For PNG rendering, install the Chromium browser once after dependency
installation:

```bash
npx playwright install chromium
```

---

## 2. Diagram file location

By default the tools read and write:

```text
hydraulic-diagram.agent.json
```

You can choose another file in two ways:

1. Set an environment variable for the MCP server:

   ```bash
   HYDRAULIC_DIAGRAM_FILE=examples/mcp/my-agent-diagram.json npm run mcp
   ```

2. Pass `diagramPath` to an individual MCP tool.

For safety, diagram paths must stay inside the project root. Attempts to write
outside the repository are rejected.

---

## 3. MCP client configuration

Use the absolute path to this repository on your machine.

### Claude Desktop-style config

```json
{
  "mcpServers": {
    "hydraulic-diagram-editor": {
      "command": "npm",
      "args": ["run", "mcp"],
      "cwd": "/absolute/path/to/hydraulic-diagram-editor",
      "env": {
        "HYDRAULIC_DIAGRAM_FILE": "hydraulic-diagram.agent.json"
      }
    }
  }
}
```

### Cursor-style config

```json
{
  "mcpServers": {
    "hydraulic-diagram-editor": {
      "command": "npm",
      "args": ["run", "mcp"],
      "cwd": "/absolute/path/to/hydraulic-diagram-editor"
    }
  }
}
```

If the client does not support `cwd`, use a shell command instead:

```json
{
  "mcpServers": {
    "hydraulic-diagram-editor": {
      "command": "bash",
      "args": [
        "-lc",
        "cd /absolute/path/to/hydraulic-diagram-editor && npm run mcp"
      ]
    }
  }
}
```

---

## 4. Available tools

- `hydraulic_list_catalog` — list element types, ports and line types.
- `hydraulic_create_diagram` — create an empty diagram JSON file.
- `hydraulic_read_diagram` — read and validate a diagram JSON file.
- `hydraulic_add_element` — add a catalog element to the diagram.
- `hydraulic_update_element` — update an existing element position, label,
  rotation or line tint.
- `hydraulic_connect_ports` — connect two element ports.
- `hydraulic_validate_diagram` — return validation errors.
- `hydraulic_render_png` — render the JSON through the real React editor UI
  and save a canvas PNG screenshot.

The default PNG output is:

```text
exports/agent-preview.png
```

---

## 5. Update existing elements

Use `hydraulic_update_element` when the agent needs to refine a generated layout
without deleting and recreating nodes.

Input fields:

- `nodeId` — existing node id to update.
- `x` / `y` — new canvas position; each field is optional.
- `label` — new visible label.
- `rotation` — one of `0`, `90`, `180`, `270`.
- `lineType` — line type id used to tint elements that support line tinting.
- `diagramPath` — optional diagram file path.

Omitted fields keep their current values.

Example request to an agent:

```text
Move the boiler 80 px lower, rename it to "БКН 200 л", rotate the pump by 90°,
then validate and render the PNG again.
```

---

## 6. Smoke test prompt

After connecting the MCP server to a client, send this prompt to the agent:

```text
Use the hydraulic-diagram-editor MCP server.

1. List the catalog.
2. Create a new diagram at hydraulic-diagram.agent.json and overwrite it if it exists.
3. Add a water connection, a filter, a pressure reducer, a water meter and an indirect boiler.
4. Update the boiler label to "БКН 200 л" and move it slightly lower for readability.
5. Connect them with cold-water pipes in a left-to-right chain.
6. Validate the diagram.
7. Render a PNG preview to exports/agent-preview.png.
8. Tell me the validation result and where the PNG was written.
```

A successful run should create or update `hydraulic-diagram.agent.json`, return
no validation errors, and write `exports/agent-preview.png`.

---

## 7. Engineering prompt examples

### Solar boiler scheme

```text
Create a domestic hot-water scheme with a solar collector, an indirect boiler,
a circulation pump on the solar supply, an expansion tank and solar supply/return
pipes. Arrange the elements so lines are easy to read, validate it and render a
PNG preview.
```

### Cold-water inlet group

```text
Create a cold-water inlet group: water connection, ball valve, filter, pressure
reducer, water meter and outlet to the boiler cold inlet. Use cold-water pipes,
rename the boiler to "БКН 200 л", validate the diagram and render a PNG.
```

### Review an existing diagram

```text
Read hydraulic-diagram.agent.json, validate it, summarize the elements and lines,
and tell me what looks incomplete from an engineering point of view.
```

---

## 8. Troubleshooting

### The MCP client does not see the server

Check that the configured `cwd` points to the repository root and that
`npm install` has already been run.

### PNG rendering fails

Install Chromium for Playwright:

```bash
npx playwright install chromium
```

Then retry `hydraulic_render_png`.

### The agent uses a wrong element or port name

Ask it to run `hydraulic_list_catalog` first. Element types, port ids and line
types must come from the catalog, not from guessed human labels.

### The diagram file is written in the wrong place

Set `HYDRAULIC_DIAGRAM_FILE` in the MCP client config or pass `diagramPath` to
the tool call. Paths must stay inside the project root.
