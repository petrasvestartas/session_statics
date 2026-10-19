from pathlib import Path

import numpy as np
from session_statics import StaticsSession

np.set_printoptions(precision=3, suppress=True, linewidth=120)


def show(name, M, fmt="{:>7.2f}", zero="      ."):
    """Print a matrix the way the paper prints figures 2 and 4: a dot for a zero."""
    M = np.atleast_2d(M)
    print(f"{name}  shape {M.shape}")
    for row in M:
        print("     " + "".join(zero if abs(v) < 1e-12 else fmt.format(v) for v in row))


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

show("u", u)
show("U = diag(u)", U)
show("C", C)
show("C^t", Ct)
show("U @ u", Uu)
show("C @ u", Cu)

# scene: the six side by side as heatmaps, opened from the top and reloaded live
session = StaticsSession("session_statics", "compas_fd A.1: vectors and matrices")
session.add_matrix(u, "u")
session.add_matrix(U, "U = diag(u)")
session.add_matrix(C, "C")
session.add_matrix(Ct, "C^t")
session.add_matrix(Uu, "U @ u")
session.add_matrix(Cu, "C @ u")
print(f"wrote {session.dump(Path(__file__).resolve().parents[2] / 'data' / 'output')}")

"""
|||||||| DESCRIPTION ||||||||
Step A.1 of the force density method (Schek 1974, section 1.4; compas_fd note, Part A): the
notation alone. A vector u, its diagonal matrix U = diag(u), a branch-node style matrix C and its
transpose C^t, and the products U @ u and C @ u, printed with a dot for every zero and drawn side
by side by StaticsSession.add_matrix with its defaults: a heatmap per matrix, cells from vivid BRG navy at
the smallest entry to vivid BRG pink at the largest, grey where nothing is set, black edges, every value
in white at the centre of its cell and the title above in black, opened from the top and reloaded live.

|||||||| DIRECTORY ||||||||
cd session/session_statics

|||||||| SETUP ||||||||
uv venv && uv pip install -e .

|||||||| RUN && CLOUDFLARE ||||||||
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py && bash/publish.sh session_statics

|||||||| VIEW ||||||||
https://petrasvestartas.github.io/session/?scene=view_session_statics.yaml
"""
