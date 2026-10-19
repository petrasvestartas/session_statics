import json
from pathlib import Path

import numpy as np

from session_py import Color, Point, Session

np.set_printoptions(precision=3, suppress=True, linewidth=120)


def show(name, M, fmt="{:>7.2f}", zero="      ."):
    """Print a matrix the way the paper prints figures 2 and 4: a dot for a zero."""
    M = np.atleast_2d(M)
    print(f"{name}  shape {M.shape}")
    for row in M:
        print("     " + "".join(zero if abs(v) < 1e-12 else fmt.format(v) for v in row))


def draw(session, texts, name, M, x0):
    """Draw a matrix in its own group, row r at y = -r, column c at x = x0 + c, its texts added to texts; returns the x after it."""
    M = np.atleast_2d(M)
    group = session.add_group(name)
    rows, cols = M.shape

    # name: above the matrix, lying on the floor
    texts.append({"text": name, "at": [x0 - 0.4, 1.1, 0.0], "height": 0.35})

    # entries: a dot at every entry, blue for positive, red for negative, small and grey for zero, its value beside it
    for r in range(rows):
        for c in range(cols):
            value = float(M[r, c])
            dot = Point(x0 + c, -r, 0.0)
            dot.name = f"{name}_{r + 1}_{c + 1}"
            dot.width = 3.0 if abs(value) < 1e-12 else 10.0
            dot.pointcolor = Color.grey() if abs(value) < 1e-12 else Color.blue() if value > 0 else Color.red()
            session.add_point(dot, group)
            if abs(value) >= 1e-12:
                texts.append({"text": f"{value:g}", "at": [x0 + c + 0.12, -r - 0.08, 0.0], "height": 0.22})

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

# scene: the six objects side by side, each in its group; the texts go in the viewer manifest, which names the geometry
scene = "session_statics"
session = Session("fd_a1_vectors_and_matrices")
texts = []
x = 0.0
x = draw(session, texts, "u", u, x)
x = draw(session, texts, "U = diag(u)", U, x)
x = draw(session, texts, "C", C, x)
x = draw(session, texts, "C^t", Ct, x)
x = draw(session, texts, "U @ u", Uu, x)
x = draw(session, texts, "C @ u", Cu, x)
manifest = {
    "name": "compas_fd A.1: vectors and matrices",
    "items": [{"file": f"pb/view_{scene}.pb", "name": "A.1 vectors and matrices", "at": [0, 0, 0]}],
    "texts": texts,
}

output = Path(__file__).resolve().parents[2] / "data" / "output"
output.mkdir(parents=True, exist_ok=True)
session.pb_dump(output / f"view_{scene}.pb")
(output / f"view_{scene}.yaml").write_text(json.dumps(manifest, indent=2))
print(f"wrote {output / f'view_{scene}.pb'} and its manifest")

"""
|||||||| DESCRIPTION ||||||||
Step A.1 of the force density method (Schek 1974, section 1.4; compas_fd note, Part A): the
notation alone. A vector u, its diagonal matrix U = diag(u), a branch-node style matrix C and its
transpose C^t, and the products U @ u and C @ u, printed with a dot for every zero and drawn side
by side, each in its own group: a dot per entry, blue for positive, red for negative, small and
grey for zero, with its value and the matrix name as text from the viewer manifest.

|||||||| DIRECTORY ||||||||
cd session/session_statics

|||||||| SETUP ||||||||
uv venv && uv pip install -e .

|||||||| RUN && CLOUDFLARE ||||||||
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py && bash/publish.sh session_statics

|||||||| VIEW ||||||||
https://petrasvestartas.github.io/session/?scene=view_session_statics.yaml&cmd=View Top;View Orthographic;Fit
"""
