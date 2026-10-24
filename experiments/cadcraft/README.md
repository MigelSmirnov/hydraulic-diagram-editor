# CADCraft hydraulic smoke experiment

This experiment does **not** replace React Flow or change the production editor.

Workflow: `.github/workflows/cadcraft-smoke.yml` (manual dispatch or changes to experiment files).
1. Python/ezdxf creates a pump block with two INSERTs and a pipe.
2. CADCraft CLI imports the DXF and renders PNG.
3. Upstream CADCraft MCP crate tests run.

Outputs: `pump_demo.dxf`, `pump_demo.png`, `ports.json`, `cadcraft-info.txt`.
Semantic ports are stored in a sidecar JSON, not yet integrated into CADCraft.
The first test is a compatibility smoke test, **not** an agent creating geometry over MCP.
Next milestone: execute CADCraft commands via MCP and assert handles/block contents.

Security: upstream repository is currently checked out by branch for an experiment; pin its reviewed commit before production.
No Cabinet Kernel, no VPS and no changes to the existing hydraulic editor.
