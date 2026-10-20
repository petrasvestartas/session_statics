# A1

from pathlib import Path

import numpy as np
from session_py import Matrix, Session, Xform

# A2

branches = [
    (1,6), (2,7), (3,8), (4,9), # 1-4 one branch from each free corner to its anchor
    (1,4), (1,2), (2,3), (3,4), # the rotated square rint
    (4,5), (1,5), (2,5), (3,5), # 9-12 connection to the center
]

n = 5 # free nodes 1..5
n_f =  4 # fixed nodes 6..9
m = len(branches) # branches 1..12

# A3
C_s = np.zeros((m, n + n_f)) # Number of columns are branches and rows are nodes
for j, (i, k) in enumerate(branches):
    C_s[j, i - 1] = 1.0 # edge starting node
    C_s[j, k - 1] = -1.0 # edge ending node

C = C_s[:, :n] # (m, n) free column
C_f = C_s[:, n:] # (m, n_f) fixed column

print(C_s)
print(C)
print(C_f)



# scene: the six side by side, one cell apart; the viewer draws every Matrix itself
session = Session("session_statics")
x = 0.0
for name, values in [("C_s", C_s), ("C", C), ("C_f", C_f)]:
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
