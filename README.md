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

Run one and publish its scene to the viewer (`bash/publish-scene.sh` is in `wood_research`):

```bash
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py
../../bash/publish-scene.sh data/output/a1_vectors_and_matrices.pb
```

View: <https://petrasvestartas.github.io/session/>
