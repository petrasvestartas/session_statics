from pathlib import Path

import numpy as np
from session_py import Matrix, Session, Xform

# a vector u and the diagonal matrix U = diag(u) built from it
u = np.array([0.5, 1.0, 1.5, 2.0])
U = np.diag(u)

# a general matrix C (three branches over four nodes, +1 at the start node, -1 at the end) and its transpose
C = np.array([[1.0, -1.0, 0.0, 0.0],
              [0.0, 1.0, -1.0, 0.0],
              [0.0, 0.0, 1.0, -1.0]])
Ct = C.T

# products with @: U u squares u entry by entry, C u takes the difference along every branch
Uu = U @ u
Cu = C @ u

# scene: the six side by side, one cell apart; the viewer draws every Matrix itself
session = Session("session_statics")
x = 0.0
for name, values in [("u", u), ("U = diag(u)", U), ("C", C), ("C^t", Ct), ("U @ u", Uu), ("C @ u", Cu)]:
    matrix = Matrix.from_rows(np.atleast_2d(values).tolist())
    matrix.name = name
    session.add_matrix(matrix)
    session.set_xform(matrix.guid, Xform.translation(x, 0.0, 0.0))
    x += matrix.cols + 1.0
output = Path(__file__).resolve().parents[2] / "data" / "output"
output.mkdir(parents=True, exist_ok=True)
session.pb_dump(output / "view_session_statics.pb")

"""
|||||||| DESCRIPTION ||||||||
Step A.1 of the force density method (Schek 1974, section 1.4; compas_fd note, Part A): the
notation alone. A vector u, its diagonal matrix U = diag(u), a branch-node style matrix C and its
transpose C^t, and the products U @ u and C @ u, added to a kernel
Session as Matrix objects, one cell apart. The viewer draws each with one shader instance from the
Matrix's own defaults: cells from BRG navy at the smallest entry to BRG pink at the largest, grey for
zero, black edges, every value in white at the centre of its cell, the name above as the title.

|||||||| DIRECTORY ||||||||
cd session/session_statics

|||||||| SETUP ||||||||
uv venv && uv pip install -e .

|||||||| RUN && CLOUDFLARE ||||||||
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py && bash/publish.sh session_statics

|||||||| VIEW ||||||||
https://petrasvestartas.github.io/session/?scene=view_session_statics.yaml&cmd=View%20Top;View%20Orthographic;Fit
"""
