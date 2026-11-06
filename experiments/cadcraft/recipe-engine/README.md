# CADCraft: upper-orange tee regression and gated publication

Approved baseline: apartment v35, unchanged. Target: v37 geometry.

The YAML recipe above drives the upper orange wall T-junction:
snap both branch endpoints to the sloped host, break the host face,
and **remove the branch end cap**. This last operation is the regression
that was missing in v36.

Verified locally 2026-11-06:
- The P4/P9 YAML build reconstructed 15/15 v35 objects.
- Applying the upper-orange recipe produced a new DXF.
- The six-junction topology gate returned PASS (6/6).
- Atomic publication succeeded.
- An uncorrected v35 build was rejected by the gate.
- No modifications to the approved v35 source.

The full runnable integration package, including the gate, fixtures,
builder and release scripts, was delivered separately as a ZIP artifact.
This repository checkpoint contains the recipe and executable transformation,
not the complete integration package or a binary DXF.
