from dataclasses import dataclass
from math import isfinite

from session_py import Matrix


@dataclass
class ForceDensityResult:
    """Equilibrium results in the input node and branch order."""

    coordinates: Matrix
    lengths: Matrix
    forces: Matrix
    reactions: Matrix
    residuals: Matrix


def force_density(
    branches: list[tuple[int, int]],
    n_free: int,
    fixed: Matrix,
    q: list[float],
    loads: Matrix,
) -> ForceDensityResult:
    """Solve linear force density equilibrium, using one-based node labels.

    Free nodes are 1..n_free; fixed nodes follow in the order of fixed's rows.
    fixed and loads have three columns (x, y, z). Loads apply to free nodes only.
    q has one force/length value per branch; positive values denote tension.
    Coordinates include all nodes. Reactions act on the net at fixed nodes;
    residuals are applied loads minus C_s.T Q C_s coordinates.
    """
    if n_free < 0 or fixed.cols != 3 or loads.shape != (n_free, 3):
        raise ValueError("Expected fixed coordinates (n_fixed, 3) and loads (n_free, 3)")
    if len(q) != len(branches):
        raise ValueError("Expected one force density per branch")
    if not all(isfinite(v) for values in (fixed.data, loads.data, q) for v in values):
        raise ValueError("Coordinates, loads, and force densities must be finite")
    n_nodes = n_free + fixed.rows
    connectivity = Matrix.zeros(len(branches), n_nodes)
    for j, (i, k) in enumerate(branches):
        if not (1 <= i <= n_nodes and 1 <= k <= n_nodes) or i == k:
            raise ValueError("Branches need two distinct node labels in 1..n_nodes")
        connectivity[j, i - 1] = 1.0
        connectivity[j, k - 1] = -1.0
    c = connectivity.block(0, 0, len(branches), n_free)
    cf = connectivity.block(0, n_free, len(branches), fixed.rows)
    ct = c.transpose()
    d = ct @ c.scale_rows(q)
    df = ct @ cf.scale_rows(q)
    rhs = loads - df @ fixed
    free = d.solve_positive_definite(rhs) if all(v > 0 for v in q) else d.solve(rhs)
    if free is None:
        raise ValueError("No unique equilibrium: check supports, connectivity, and force densities")
    coordinates = Matrix.from_vec(n_nodes, 3, free.data + fixed.data)
    differences = connectivity @ coordinates
    lengths = differences.row_norms()
    forces = lengths.scale_rows(q)
    nodal = connectivity.transpose() @ differences.scale_rows(q)
    applied = Matrix.from_vec(n_nodes, 3, loads.data + [0.0] * (fixed.rows * 3))
    return ForceDensityResult(
        coordinates,
        lengths,
        forces,
        nodal.block(n_free, 0, fixed.rows, 3),
        applied - nodal,
    )
