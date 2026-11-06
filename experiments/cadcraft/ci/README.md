# Download CADCraft drawings from GitHub Actions

Open **Actions** in the repository, choose **CADCraft - build A3 drawing**, then **Run workflow** (default branch). After the job succeeds, download **CADCraft-A3-DXF-PDF-PNG** under Artifacts.

The workflow reads the committed v35 geometry JSON from the `checkpoint/apartment-v20` branch, reconstructs an experimental v37-style upper orange T-junction, adds seven dimensions, and exports an editable A3 DXF, PDF, PNG, and SHA-256 manifest.

**Limitations:** The JSON checkpoint was rounded and is not byte-identical to the approved v35 DXF. This is a reproducible A3 export from the repository geometry, not a certified reconstruction of every approved CAD contour. The PDF contains a raster plan at a declared 1:50 placement. The pipeline does not yet run the full six-junction topology gate or the full 24-dimension engine. It is intended as a working downloadable-artifacts workflow.

The workflow does not commit generated binary files. It publishes them as downloadable GitHub Actions artifacts with a 30-day retention.
