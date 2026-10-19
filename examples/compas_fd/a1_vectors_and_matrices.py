"""Force density method, step A.1: how the paper writes vectors and matrices (Schek 1974, section 1.4).

A vector is a lower-case letter, the diagonal matrix built from it the same capital letter
(U = diag(u)), a general matrix a capital letter, C^t its transpose. In NumPy: a 1-D array,
np.diag(u), C.T and @. Every matrix is printed the way the paper prints figures 2 and 4, a dot
for a zero, and drawn as a grid on the floor: a point at every entry, a bar of the entry's
height on every non-zero one, blue up for positive and red down for negative.
"""

from pathlib import Path

import numpy as np
from session_py import Color, Line, Point, Polyline, Session

np.set_printoptions(precision=3, suppress=True, linewidth=120)


def show(name, M, fmt="{:>7.2f}", zero="      ."):
    """Print a matrix the way the paper prints figures 2 and 4: a dot for a zero."""
    M = np.atleast_2d(M)
    print(f"{name}  shape {M.shape}")
    for row in M:
        print("     " + "".join(zero if abs(v) < 1e-12 else fmt.format(v) for v in row))


def draw(session, name, M, x0):
    """Draw a matrix as a grid in its own group, row r at y = -r, column c at x = x0 + c; returns the x after it."""
    M = np.atleast_2d(M)
    group = session.add_group(name)
    rows, cols = M.shape

    # frame: the outline of the matrix on the floor
    frame = Polyline([
        Point(x0 - 0.5, 0.5, 0.0),
        Point(x0 + cols - 0.5, 0.5, 0.0),
        Point(x0 + cols - 0.5, -rows + 0.5, 0.0),
        Point(x0 - 0.5, -rows + 0.5, 0.0),
        Point(x0 - 0.5, 0.5, 0.0),
    ])
    frame.name = f"{name}_frame"
    frame.linecolor = Color.grey()
    session.add_polyline(frame, group)

    # entries: a point at every entry, a bar on every non-zero one
    for r in range(rows):
        for c in range(cols):
            base = Point(x0 + c, -r, 0.0)
            base.name = f"{name}_{r + 1}_{c + 1}"
            base.pointcolor = Color.grey()
            session.add_point(base, group)
            if abs(M[r, c]) < 1e-12:
                continue
            bar = Line.from_points(base, Point(x0 + c, -r, float(M[r, c])))
            bar.name = f"{name}_{r + 1}_{c + 1}_value"
            bar.width = 4.0
            bar.linecolor = Color.blue() if M[r, c] > 0 else Color.red()
            session.add_line(bar, group)

    return x0 + cols + 1.0


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

# scene: the six objects side by side, each in its group
session = Session("fd_a1_vectors_and_matrices")
x = 0.0
x = draw(session, "u", u, x)
x = draw(session, "U = diag(u)", U, x)
x = draw(session, "C", C, x)
x = draw(session, "C^t", Ct, x)
x = draw(session, "U @ u", Uu, x)
x = draw(session, "C @ u", Cu, x)

output = Path(__file__).resolve().parents[2] / "data" / "output" / "a1_vectors_and_matrices.pb"
output.parent.mkdir(parents=True, exist_ok=True)
session.pb_dump(output)
print(f"wrote {output}")

"""
|||||||| DESCRIPTION ||||||||
Step A.1 of the force density method (Schek 1974, section 1.4; compas_fd note, Part A): the
notation alone. A vector u, its diagonal matrix U = diag(u), a branch-node style matrix C and its
transpose C^t, and the products U @ u and C @ u, printed with a dot for every zero and drawn side
by side as bar grids, each in its own group.

|||||||| DIRECTORY ||||||||
cd wood_research/session/session_statics

|||||||| SETUP ||||||||
uv venv && uv pip install -e .

|||||||| RUN && CLOUDFLARE ||||||||
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py && ../../bash/publish-scene.sh data/output/a1_vectors_and_matrices.pb

|||||||| VIEW ||||||||
https://petrasvestartas.github.io/session/
"""
