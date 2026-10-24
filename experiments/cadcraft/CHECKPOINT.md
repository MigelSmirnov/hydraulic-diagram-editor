# CADCraft apartment experiment — checkpoint candidate

Status: **candidate, pending GitHub Actions and visual review**. Not a production release.

## Reproducible output
Run `python experiments/cadcraft/test_apartment_checkpoint.py` after building CADCraft CLI.
CI workflow: `.github/workflows/cadcraft-smoke.yml`.
Expected artifacts: `apartment_checkpoint.dxf`, `apartment_checkpoint.png`,
`apartment-checkpoint-report.json`, `checkpoint-socket-anchors.json`.

## CADCraft tools demonstrated
| Purpose | MCP / native command | Evidence |
| --- | --- | --- |
| Exterior 200mm wall | `pline` closed, `offset` inward 200 | `test_exterior_offset.py` |
| 90mm L-wall | `pline` axis, `offset` ±45, `erase` axis, `line` caps, `pedit join` | `test_l_wall_closed.py` |
| Apartment L-walls | Same sequence twice | `test_apartment_native_l_walls.py` |
| 90mm straight partitions | `pline` closed rectangle | `test_apartment_native_l_walls.py` |
| Dimension annotations | `setvar` DIMSCALE=50, DIMTXT=2.5, DIMASZ=2.5, DIMGAP=1; `dimlinear` | `test_apartment_native_l_walls.py` |
| Socket block | `arc`, `line`, `text`, `block`, `insert` with rotation | `test_apartment_checkpoint.py` |
| CAD drawing and white paper | `save` DXF, `plot` with output=png | checkpoint |
| Native wall-edge trim | `trim` with cutting edge and pick point, `erase` cap | `test_junction_trim.py` (separate straight LINE test) |

## Explicit limitations / pending checks
- The apartment checkpoint **does not yet apply TRIM to closed L-wall polylines**. End caps at exterior wall junctions remain visible. The separate TRIM experiment proved only straight LINE behaviour; handles can change.
- The original lower dimension chain 3565 + 4717 differs from 8382 by 100mm. The 90mm partition and reference-face mapping are not reconciled. Do not claim that dimensions are tied to wall faces.
- Interior wall positions are approximate; door and window openings have not been modeled.
- Socket symbol is traced from a user-provided legend, not certified as an exact IEC 60617 glyph. The socket anchors are sidecar JSON, not dynamic CAD constraints.
- `fit: true` on A3 means a printed sheet is **not guaranteed to be exactly 1:50**; 1:50 currently configures symbol and dimension graphic sizes in model space.
- GitHub Actions verifies entity counts and PNG signature, **not architectural correctness**.

## Promotion criteria
1. CI success for checkpoint.
2. Review PNG against the source image.
3. Verify wall faces, junction cap removal, and dimension endpoints.
4. Reconcile 100mm dimension discrepancy.
5. Pin CADCraft upstream commit and record license/version.
6. Only then tag a baseline checkpoint.
