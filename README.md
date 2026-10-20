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

Nothing to draw here: an example puts kernel objects in a `session_py.Session` and writes it with
`pb_dump`. A `Matrix` carries its own look (BRG colours, cell size) and the session viewer draws it
with one shader instance per matrix.

## Examples

`examples/compas_fd/` follows the force density method of Schek (1974) step by step, as laid out
in the [compas_fd note](https://github.com/BRG-research/mcp-server-brg/blob/main/knowledge/04_form_finding/compas_fd.md):

| File | Step |
| --- | --- |
| `a1_vectors_and_matrices.py` | A.1–A.3: connectivity and its free/fixed column blocks |
| `linear_force_density.py` | B–D: solve the linear force density method using kernel Matrix operations |

Run one and publish its scene to the viewer under its own name, `session_statics`, apart from the
live scene. `bash/publish.sh` uploads the session as an immutable revision with a manifest that opens
it from the top, without the floor grid, reloading live; an open page reloads at once:

```bash
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py
bash/publish.sh session_statics
```

View: <https://petrasvestartas.github.io/session/?scene=view_session_statics.yaml>

## Linear force density solver

`session_statics.force_density.force_density(branches, n_free, fixed, q, loads)`
uses `session_py.Matrix` throughout: connectivity, column blocks, weighted
products, a three-column coordinate solve, lengths, forces, and reactions.
Node labels start at one; free nodes come first, followed by the rows of `fixed`.
`fixed` and `loads` have three columns; loads apply to free nodes only.
The result contains all-node `coordinates`, branch `lengths` and `forces`,
support `reactions` acting on the net, and all-node equilibrium `residuals`.

```bash
uv run python examples/compas_fd/linear_force_density.py
```

The coordinates and loads in this example are chosen inputs, not values reported
by Schek. Positive force densities use Cholesky; other signs use partial-pivoted
elimination. All three coordinate axes share one factorization. This is a dense
linear solver; it does not implement the tutorial's additional nonlinear conditions.

## Matrix operations

C++, Python, and Rust provide the same operations. `Matrix` is always two-dimensional.
`array` takes rows; `column` turns a flat sequence into an N × 1 vector. The existing
`from_rows`, `from_cols`, `identity`, and multiplication operators still work.

| Operation | Python example |
|---|---|
| Rows | `Matrix.array([[2, 1], [1, 3]])` |
| Column vector | `Matrix.column([5, 10])` |
| Zeros / ones / constant | `Matrix.zeros(2, 3)`, `Matrix.ones(2, 3)`, `Matrix.full(2, 3, -0.5)` |
| Identity / diagonal | `Matrix.eye(3)`, `Matrix.diag([2, 1, 1])` |
| Shape / transpose | `A.shape`, `A.T` or `A.transpose()` |
| Rectangular copy | `A.block(row, col, rows, cols)` |
| Matrix multiplication | `A @ B` or `A.matmul(B)` |
| Entrywise multiplication | `A.hadamard(B)` |
| Diagonal weighting without a diagonal allocation | `A.scale_rows(q)`, `A.scale_cols(q)` |
| Length of each row | `A.row_norms()` |
| General solve | `A.solve(B)` |
| Positive-definite solve | `A.solve_positive_definite(B)` |

In C++, use `Matrix::array(...)` and `A.matmul(B)`; in Rust, use
`Matrix::array(&[vec![...], ...])` and `a.matmul(&b)`. Shape is `shape()` in C++
and Rust. Both solves accept multiple right-hand-side columns. An invalid or
singular system returns `None` in Python/Rust or an empty optional in C++.
Python uses NumPy kernels; C++ and Rust use portable native implementations.
