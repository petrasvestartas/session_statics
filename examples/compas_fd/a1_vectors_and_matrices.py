# A1

from pathlib import Path
from typing import TypeAlias

import numpy as np
from session_py import Matrix, Session, Xform

# Both are NumPy arrays: a matrix has two dimensions; a vector has one.
FloatMatrix: TypeAlias = np.ndarray[tuple[int, int], np.dtype[np.float64]]
FloatVector: TypeAlias = np.ndarray[tuple[int], np.dtype[np.float64]]

# A2 - Topology: a Python list of node-label pairs

branches: list[tuple[int, int]] = [
    (1,6), (2,7), (3,8), (4,9), # 1-4 one branch from each free corner to its anchor
    (1,4), (1,2), (2,3), (3,4), # the rotated square ring
    (4,5), (1,5), (2,5), (3,5), # 9-12 connection to the center
]

n: int = 5 # number of free nodes: labels 1..5
n_f: int = 4 # number of fixed nodes: labels 6..9
m: int = len(branches) # number of branches: 12

# A3
C_s: FloatMatrix = np.zeros((m, n + n_f), dtype=np.float64) # shape (12, 9): rows are branches, columns are nodes
for j, (i, k) in enumerate(branches):
    C_s[j, i - 1] = 1.0 # edge starting node
    C_s[j, k - 1] = -1.0 # edge ending node

C: FloatMatrix = C_s[:, :n] # shape (12, 5): free-node columns
C_f: FloatMatrix = C_s[:, n:] # shape (12, 4): fixed-node columns

# print(C_s)
# print(C)
# print(C_f)

# B1 - Chosen support coordinates (metres) and free-node loads (kN).
# Each coordinate/load variable below is a 1-D array, not one number.
# Fixed arrays: [node 6, node 7, node 8, node 9], shape (4,).
# Load arrays: [node 1, node 2, node 3, node 4, node 5], shape (5,).

x_f: FloatVector = np.array([-2.0, 0.0, 2.0, 0.0], dtype=np.float64) # anchors 6, 7, 8, 9
y_f: FloatVector = np.array([0.0, 2.0, 0.0, -2.0], dtype=np.float64)
z_f: FloatVector = np.array([0.0, 1.0, 0.0, 1.0], dtype=np.float64) # two anchors lifted by 1 m

x = np.array([-1.0, 0.0, 1.0, 0.0, 0.0])    # a flat guess for the free nodes
y = np.array([0.0, -1.0, 0.0, 1.0, 0.0])
z = np.zeros(n)
p_x: FloatVector = np.zeros(n, dtype=np.float64)
p_y: FloatVector = np.zeros(n, dtype=np.float64)
p_z: FloatVector = np.full(n, -0.5, dtype=np.float64) # 0.5 kN downward at every free node
s = np.ones(m)                              # 1 kN in every branch

# B2 Coordinate differences and lengths

def coordinate_differences(
    C: FloatMatrix,
    x: FloatVector,
    y: FloatVector,
    z: FloatVector,
    C_f: FloatMatrix,
    x_f: FloatVector,
    y_f: FloatVector,
    z_f: FloatVector,
) -> tuple[FloatVector, FloatVector, FloatVector, FloatVector]:
    """Given node positions, measure branches; this does not solve for the positions.

    C, C_f: FloatMatrix, two-dimensional arrays of shape (m, n), (m, n_f).
    x, y, z: (n,) arrays, one coordinate per free node; the solve computes them later.
    x_f, y_f, z_f: (n_f,) arrays, one coordinate per fixed node, already given.
    u, v, w, l: (m,) arrays, one value per branch.
    x[0] is one scalar coordinate of node 1; x_f[0] is one of node 6.
    """
    # (12, 5) @ (5,) -> (12,); (12, 4) @ (4,) -> (12,).
    # Each matrix row gives one number; all 12 rows give a 12-entry vector.
    # Add the two vectors entry by entry, branch by branch.
    u: FloatVector = C @ x + C_f @ x_f
    v: FloatVector = C @ y + C_f @ y_f
    w: FloatVector = C @ z + C_f @ z_f
    l: FloatVector = np.sqrt(u**2 + v**2 + w**2)
    return u, v, w, l

# B3 Equilibrium with the unknown forces, equation.
def equilibrium_error(
        C: FloatMatrix,
        x: FloatVector,
        y: FloatVector,
        z: FloatVector,
        s: FloatVector, # Force per every cable in kN
        C_f: FloatMatrix,
        x_f: FloatVector,
        y_f: FloatVector,
        z_f: FloatVector) -> tuple[FloatVector, FloatVector, FloatVector]:
    """Eq. (2): C^t U L^-1 s - p for the three axes.  All zeros means the net is in equilibrium."""

    # Get Cable lengths
    u, v, w, l = coordinate_differences(C, x, y, z, C_f, x_f, y_f, z_f)

    L_inv = np.diag(1.0 / l) # (12, 12) diagonal matrix holding 1/L, following notation q = F/L

    # Step 1: L_inv @ s - force densities per cable
    # Step 2: np.diag(u) @ L_inv @ s - projection of the force density into the x-axis
    # Step 3: C.T @ np.diag(u) @ L_inv - the connectivity matrix of free nodes, allows to sum the forces per node
    # Step 4: -p_x - the original loading of free nodes must sum to zero as internal forces deform the cable net
    return (C.T @ np.diag(u) @ L_inv @ s-p_x,
            C.T @ np.diag(v) @ L_inv @ s-p_y,
            C.T @ np.diag(w) @ L_inv @ s-p_z)

ex, ey, ez = equilibrium_error(C, x, y, z, s, C_f, x_f, y_f, z_f)

print(ex)


# https://github.com/BRG-research/mcp-server-brg/blob/main/knowledge/04_form_finding/compas_fd.md

# Scene positions are scalars; they are unrelated to the coordinate arrays.
session = Session("session_statics")
scene_x: float = 0.0
for name, values in [("C_s", C_s), ("C", C), ("C_f", C_f)]:
    matrix = Matrix.from_rows(np.atleast_2d(values).tolist())
    matrix.name = name
    session.add_matrix(matrix)
    session.set_xform(matrix.guid, Xform.translation(scene_x, 0.0, 0.0))
    scene_x += matrix.cols + 1.0
output = Path(__file__).resolve().parents[2] / "data" / "output"
output.mkdir(parents=True, exist_ok=True)
session.pb_dump(output / "view_session_statics.pb")

"""
|||||||| DESCRIPTION ||||||||
Steps A.1–B.2 of the force density method (Schek 1974).
branches is a list of node-label pairs; C_s, C and C_f are two-dimensional NumPy arrays.
Fixed coordinate arrays have four entries; load arrays have five entries.
coordinate_differences takes the five-entry free-coordinate arrays x, y, z and returns
four twelve-entry branch arrays. It is defined here but is not called until free
coordinates are available. The scene contains the three connectivity matrices.

|||||||| DIRECTORY ||||||||
cd session/session_statics

|||||||| SETUP ||||||||
uv venv && uv pip install -e .

|||||||| RUN && CLOUDFLARE ||||||||
.venv/bin/python examples/compas_fd/a1_vectors_and_matrices.py && bash/publish.sh session_statics

|||||||| VIEW ||||||||
https://petrasvestartas.github.io/session/?scene=view_session_statics.yaml&cmd=View%20Top;View%20Orthographic;Fit
"""
