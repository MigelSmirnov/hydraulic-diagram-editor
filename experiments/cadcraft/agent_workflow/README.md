# Agent-guided CADCraft workflow (experimental)

This is a **workflow contract**, not an installed MCP server/tool. It defines the next-step protocol for a future orchestrator. The agent executes the native CADCraft commands through the existing `execute` MCP tool and receives a proposed `next_action` only after validation.

## State and step result
```json
{
  "workflow_id": "apartment-walls-cadcraft",
  "run_id": "project-001",
  "step_id": "host_break",
  "status": "passed",
  "evidence": [{"type": "dxf", "check": "junction_overlap", "count": 0}],
  "next_action": {
    "step_id": "partition_cap_break",
    "instruction": "Remove the cap from the corresponding partition polyline, then validate no overlap",
    "required_inputs": ["current_partition_handle", "cap_start", "cap_end"]
  },
  "warnings": []
}
```

## Execution contract
1. Resolve placeholders from current project geometry and fresh CADCraft handles.
2. Execute only the current step's commands.
3. Save and re-read the DXF for geometric assertions, especially after BREAK/TRIM.
4. If validation fails return `blocked` with diagnostic evidence; never advance automatically.
5. If validation passes persist step state and return `next_action`.
6. After export require visual acceptance before marking the project baseline.

The declarative sequence and checks are in [workflow.json](./workflow.json). This design can be implemented as an MCP wrapper exposing `workflow_start`, `workflow_next`, `workflow_validate`, `workflow_resume` and `workflow_status`. These are **proposed** tools, not existing CADCraft commands.

## Evidence
- Native L wall: `test_l_wall_closed.py`.
- Apartment walls and dimensions: `test_apartment_native_l_walls.py`.
- Native LINE TRIM: `test_junction_trim.py`.
- One integrated P01 junction: `test_apartment_p01_integrated.py`.
- Multiple BREAK operations: integration test in progress; do not assume successful until CI and PNG review.

## Known issues
The original survey chain 3565/100/4717 differs from the current experimental geometry 3520/90/4772. Socket anchoring is not dynamic. No door/window openings yet. Architectural and structural correctness require review.
