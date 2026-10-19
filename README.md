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

## Examples

`examples/compas_fd/` follows the force density method of Schek (1974) step by step, as laid out
in the [compas_fd note](https://github.com/BRG-research/mcp-server-brg/blob/main/knowledge/04_form_finding/compas_fd.md):

| File | Step |
| --- | --- |
| `a1_vectors_and_matrices.py` | A.1 How the paper writes vectors and matrices (section 1.4) |

Run one and publish its scene to the viewer under its own name, `session_statics`, apart from the
live scene. The example writes the geometry and a manifest carrying the texts (values and matrix
names); `bash/publish.sh` uploads both with the monorepo's R2 helpers (`../bash/lib/view.sh`):

```bash
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py
bash/publish.sh session_statics
```

View from the top: <https://petrasvestartas.github.io/session/?scene=view_session_statics.yaml&cmd=View%20Top;View%20Orthographic;Fit>
