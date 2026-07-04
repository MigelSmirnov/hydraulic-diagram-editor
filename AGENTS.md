# Agent Instructions

## Project

Hydraulic diagram editor built with React, TypeScript, Vite, React Flow and Zustand.
There is no backend. The React editor and MCP server both use the same diagram JSON
format.

## Architecture Rules

- Keep editor business logic inside `src/features/diagram-editor`.
- `src/app/App.tsx` is layout composition only.
- Element definitions live in `src/features/diagram-editor/model/elementCatalog.ts`.
- Line definitions live in `src/features/diagram-editor/model/lineTypes.ts`.
- Shared SVG icons live in `src/shared/icons` and must be pure SVG components using
  `stroke="currentColor"` where possible.
- Diagram mutations should go through testable commands or MCP helpers, not ad hoc UI
  state changes.
- Preserve the existing React Flow JSON shape unless intentionally changing
  `schemaVersion`.

## MCP

Run the local stdio MCP server from the project root:

```bash
npm run mcp
```

The default agent diagram file is `hydraulic-diagram.agent.json`. Tools may also pass
`diagramPath`, which must stay inside the project root.

Available MCP tools include:

- `hydraulic_list_catalog`
- `hydraulic_create_diagram`
- `hydraulic_read_diagram`
- `hydraulic_add_element`
- `hydraulic_update_element`
- `hydraulic_connect_ports`
- `hydraulic_validate_diagram`
- `hydraulic_render_png`

PNG rendering uses Playwright. Install Chromium once per machine:

```bash
npx playwright install chromium
```

Generated PNG output defaults to `exports/agent-preview.png`; `exports/` is ignored by
git.

## Validation

Before finishing code changes, run:

```bash
npm test
npm run build
```

For MCP PNG changes, also smoke-test `hydraulic_render_png` against
`examples/mcp/boiler-agent-diagram.json`.

When generating or refining diagrams, call `hydraulic_list_catalog` before using
element types or port ids. Use `hydraulic_update_element` for layout cleanup,
renaming and rotation rather than deleting and recreating nodes.

## Git

- Keep commits focused.
- Do not commit generated `dist/`, `tmp/`, `exports/`, or local autosave files.
- If adding elements, include icon registration and catalog entry in the same commit.
