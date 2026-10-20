from dataclasses import dataclass

import numpy as np

from .force_density import ForceDensityResult, force_density


@dataclass
class Condition:
    """Branch indices are zero-based; node labels remain one-based."""

    kind: str
    branches: list[int]
    targets: list[float]
    stiffness: float = 100.0


@dataclass
class ConstrainedResult:
    equilibrium: ForceDensityResult
    q: np.ndarray
    iterations: int
    errors: np.ndarray
    history: list[float]
    converged: bool


def condition_values(lengths, q, condition):
    rows = condition.branches
    if condition.kind == "length":
        return lengths[rows]
    if condition.kind == "force":
        return (q * lengths)[rows]
    if condition.kind == "unstrained_length":
        return (condition.stiffness * lengths / (condition.stiffness + q * lengths))[
            rows
        ]
    raise ValueError(f"Unknown condition: {condition.kind}")


def condition_system(c, differences, q, conditions):
    """Implicit coordinate derivatives and the chain rule, Schek (28)–(35)."""
    lengths = np.linalg.norm(differences, axis=1)
    if np.any(lengths <= 1e-12):
        raise ValueError("A constrained branch has zero length")
    d = c.T @ (q[:, None] * c)
    derivatives = [np.linalg.solve(d, -c.T * differences[:, axis]) for axis in range(3)]
    dl = (
        sum(differences[:, axis, None] * (c @ derivatives[axis]) for axis in range(3))
        / lengths[:, None]
    )
    direct = np.diag(lengths)
    blocks = []
    values = []
    for condition in conditions:
        rows = condition.branches
        if condition.kind == "length":
            jacobian = dl
        elif condition.kind == "force":
            jacobian = q[:, None] * dl + direct
        elif condition.kind == "unstrained_length":
            h = condition.stiffness
            denominator = h + q * lengths
            jacobian = (h / denominator)[:, None] ** 2 * dl - np.diag(
                h * lengths**2 / denominator**2
            )
        else:
            raise ValueError(f"Unknown condition: {condition.kind}")
        blocks.append(jacobian[rows])
        values.extend(condition_values(lengths, q, condition) - condition.targets)
    return np.asarray(values), np.vstack(blocks)


def constrained_force_density(
    branches, n_free, fixed, q, loads, conditions, *, tolerance=1e-9, max_iterations=200
):
    """Iterate on positive force densities, re-solving equilibrium at every trial.

    A stopped iterate is returned with converged=False; it is never presented as
    satisfying the conditions. Condition errors retain their original m/kN units.
    """
    q = np.asarray(q, dtype=float).copy()
    if q.shape != (len(branches),) or not np.all(np.isfinite(q)) or np.any(q <= 0):
        raise ValueError("Expected one positive finite force density per branch")
    if not conditions or tolerance <= 0 or max_iterations < 0:
        raise ValueError(
            "Provide conditions, a positive tolerance, and a nonnegative iteration limit"
        )
    for condition in conditions:
        if not condition.branches or len(condition.branches) != len(condition.targets):
            raise ValueError("Each condition needs matching branch indices and targets")
        if any(
            not isinstance(j, (int, np.integer)) or j < 0 or j >= len(branches)
            for j in condition.branches
        ):
            raise ValueError("Condition branch indices must be in 0..m-1")
        if not np.all(np.isfinite(condition.targets)) or np.any(
            np.asarray(condition.targets) <= 0
        ):
            raise ValueError("Condition targets must be positive and finite")
        if not np.isfinite(condition.stiffness) or condition.stiffness <= 0:
            raise ValueError("Axial stiffness must be positive and finite")
    connectivity = np.zeros((len(branches), n_free + fixed.rows))
    # Validate topology and all other inputs with the linear solver first.
    equilibrium = force_density(branches, n_free, fixed, q.tolist(), loads)
    for j, (a, b) in enumerate(branches):
        connectivity[j, a - 1], connectivity[j, b - 1] = 1, -1
    c = connectivity[:, :n_free]

    def evaluate(values):
        result = force_density(branches, n_free, fixed, values.tolist(), loads)
        xyz = np.asarray(result.coordinates.data).reshape(-1, 3)
        lengths = np.asarray(result.lengths.data)
        errors = np.concatenate(
            [
                condition_values(lengths, values, item) - item.targets
                for item in conditions
            ]
        )
        return result, connectivity @ xyz, errors

    equilibrium, differences, errors = evaluate(q)
    history = [float(np.max(np.abs(errors)))]
    damping = 1e-6
    for _ in range(max_iterations):
        if history[-1] <= tolerance:
            break
        _, jacobian = condition_system(c, differences, q, conditions)
        gram = jacobian @ jacobian.T
        diagonal = np.maximum(np.diag(gram), 1e-12)
        for _ in range(16):
            step = jacobian.T @ np.linalg.solve(
                gram + np.diag(damping * 0.8**2 * diagonal), -0.8 * errors
            )
            negative = step < 0
            if negative.any():
                step *= min(1.0, float(np.min(-0.5 * q[negative] / step[negative])))
            trial = evaluate(q + step)
            error = float(np.max(np.abs(trial[2])))
            if error < history[-1]:
                q += step
                equilibrium, differences, errors = trial
                history.append(error)
                damping = max(damping / 2, 1e-9)
                break
            damping *= 4
        else:
            break
    return ConstrainedResult(
        equilibrium, q, len(history) - 1, errors, history, history[-1] <= tolerance
    )
