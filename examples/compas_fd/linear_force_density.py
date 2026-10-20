from pathlib import Path

from session_py import Line, Matrix, Session, Xform
from session_statics.force_density import force_density

branches = [
    (1, 6), (2, 7), (3, 8), (4, 9),
    (1, 4), (1, 2), (2, 3), (3, 4),
    (4, 5), (1, 5), (2, 5), (3, 5),
]
# Chosen example inputs, not coordinates or loads reported by Schek.
fixed = Matrix.array([[-2, 0, 0], [0, -2, 1], [2, 0, 0], [0, 2, 1]])
loads = Matrix.zeros(5, 3)
for i in range(5):
    loads[i, 2] = -0.5
q = [2.0] * 4 + [1.0] * 8
result = force_density(branches, 5, fixed, q, loads)

session = Session("session_statics")
for i, k in branches:
    a = result.coordinates.data[(i - 1) * 3:i * 3]
    b = result.coordinates.data[(k - 1) * 3:k * 3]
    session.add_line(Line(*a, *b))
x = 5.0
for name, matrix in [
    ("coordinates", result.coordinates),
    ("lengths", result.lengths),
    ("forces", result.forces),
    ("reactions", result.reactions),
]:
    matrix.name = name
    session.add_matrix(matrix)
    session.set_xform(matrix.guid, Xform.translation(x, 0, 0))
    x += matrix.cols + 1
output = Path(__file__).resolve().parents[2] / "data" / "output"
output.mkdir(parents=True, exist_ok=True)
session.pb_dump(output / "view_session_statics.pb")
print("free-node coordinates:", result.coordinates.block(0, 0, 5, 3).data)
print("scene:", output / "view_session_statics.pb")
