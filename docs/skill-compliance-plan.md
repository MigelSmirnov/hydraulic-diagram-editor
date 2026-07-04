# Skill Compliance Work Plan

This plan tracks the work needed to align the editor with the
`svg-engineering-editors-skills` requirements.

## Current Baseline

- Element catalog is the source of truth for palette items, SVG symbols and ports.
- Connections reference React Flow node ids and handle ids, not stored endpoint coordinates.
- Port geometry and orthogonal edge routing are implemented as pure helpers.
- JSON save/load has a schema version, basic structure checks and domain reference validation.
- Architecture and invariants are documented; the first executable document validation layer is in place.

## Target Architecture

1. Add `architecture/app-architecture.yaml` in the skill-required module format.
2. Keep UI components thin; move validation, persistence and command behavior out of UI.
3. Introduce executable invariant files for document and connection rules.
4. Separate editable diagram persistence from image/document export.
5. Add command-level state changes as the basis for undo/redo.
6. Keep React Flow as a canvas adapter; gradually move durable project data toward a clean diagram model.

## Work Phases

### Phase 1: Test and Validation Foundation

- Add a test runner and `tests/` folder.
- Add unit tests for port rotation and orthogonal routing.
- Add document validation for node/edge references, element types, handles, line types and rotation.
- Run validation before replacing editor state from imported JSON.

Status: done.

### Phase 2: Architecture Contract

- Add `architecture/app-architecture.yaml`.
- Move persistence code into a dedicated module.
- Split invariant docs into executable validators and keep Markdown as human guidance.

Status: in progress. Architecture YAML and the first persistence module boundary are done; persistence schema/types still need to move behind the module boundary.

### Phase 3: Commands and Undo/Redo

- Add command functions for add, move, rotate, connect, delete and update line type.
- Route store mutations through commands.
- Add undo/redo history and command tests.

Status: in progress. Core add/connect/rotate/delete/update/load/replace commands are implemented and tested. Undo/redo history is implemented for command-driven actions. Move history for React Flow drag changes remains.

### Phase 4: Domain Model Cleanup

- Define durable `DiagramElementInstance` and `DiagramConnection` types.
- Add adapters between domain model and React Flow nodes/edges.
- Save the durable model instead of raw React Flow structures.

### Phase 5: Broader Coverage

- Add tests for JSON import/export and invalid connection cases.
- Add tests for delete-node-removes-edges behavior.
- Add validation coverage for custom connection rules and required elements.
