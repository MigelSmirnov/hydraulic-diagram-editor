# MCP server

Local stdio MCP server for agent-driven hydraulic diagram editing.

Run from the project root:

```bash
npm run mcp
```

By default the tools read and write `hydraulic-diagram.agent.json` in the
project root. Set `HYDRAULIC_DIAGRAM_FILE` or pass `diagramPath` to a tool to
use another file inside the project.

Tools:

- `hydraulic_list_catalog` — list element types, ports and line types.
- `hydraulic_create_diagram` — create an empty diagram JSON file.
- `hydraulic_read_diagram` — read and validate a diagram JSON file.
- `hydraulic_add_element` — add a catalog element to the diagram.
- `hydraulic_connect_ports` — connect two element ports.
- `hydraulic_validate_diagram` — return validation errors.

The server edits the same JSON format that the React editor can load with
`Load JSON`.
