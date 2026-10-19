# session_statics

Structural calculations over the [session](https://github.com/petrasvestartas/session) geometry
kernel, in Python. Geometry comes from `session_py`; every example writes a session `.pb` scene
for the session viewer.

## Development setup

Inside the `session` monorepo, beside `session_py` (picked up as an editable path by `uv`):

```bash
uv venv
uv pip install -e .
```

Standalone, `session-py` comes from PyPI: `pip install -e ".[dev]"`.

## Drawing

`StaticsSession` is a session that also writes its viewer manifest: it opens from the top and
reloads live whenever it is published again. `add_matrix` draws a matrix or vector as a heatmap
next to the last one, with defaults out of the box:

```python
from session_statics import StaticsSession

session = StaticsSession("session_statics", "my scene")
session.add_matrix(U, "U = diag(u)")                 # BRG navy at the minimum, BRG pink at the maximum, white values
session.add_matrix(C, "C", cell=50.0, max_color=my_color)  # any MatrixPlot option: origin, cell, colours, text
session.pb_dump("data/output/view_session_statics.pb")  # and view_session_statics.yaml beside it
```

## Examples

`examples/compas_fd/` follows the force density method of Schek (1974) step by step, as laid out
in the [compas_fd note](https://github.com/BRG-research/mcp-server-brg/blob/main/knowledge/04_form_finding/compas_fd.md):

| File | Step |
| --- | --- |
| `a1_vectors_and_matrices.py` | A.1 How the paper writes vectors and matrices (section 1.4) |

Run one and publish its scene to the viewer under its own name, `session_statics`, apart from the
live scene. `bash/publish.sh` uploads the geometry as an immutable revision and the manifest that
names it, with the monorepo's R2 helpers (`../bash/lib/view.sh`); an open page reloads at once:

```bash
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py
bash/publish.sh session_statics
```

View: <https://petrasvestartas.github.io/session/?scene=view_session_statics.yaml>
