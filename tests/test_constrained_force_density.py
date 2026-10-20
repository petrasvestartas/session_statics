import numpy as np
import pytest
from session_py import Matrix

from session_statics.constrained_force_density import (
    Condition,
    condition_system,
    condition_values,
    constrained_force_density,
)
from session_statics.force_density import force_density


@pytest.fixture
def network():
    branches = [
        (1, 6),
        (2, 7),
        (3, 8),
        (4, 9),
        (1, 4),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
        (1, 5),
        (2, 5),
        (3, 5),
    ]
    fixed = Matrix.array([[-2, 0, 0], [0, 2, 1], [2, 0, 0], [0, -2, 1]])
    loads = Matrix.array([[0, 0, -0.5]] * 5)
    return branches, fixed, np.array([2.0] * 4 + [1.0] * 8), loads


@pytest.mark.parametrize("kind", ["length", "force", "unstrained_length"])
def test_condition_derivatives_against_central_differences(network, kind):
    branches, fixed, q, loads = network
    condition = Condition(kind, [0, 3, 8], [1.0] * 3, stiffness=50.0)
    cs = np.zeros((12, 9))
    for row, (a, b) in enumerate(branches):
        cs[row, a - 1], cs[row, b - 1] = 1, -1
    result = force_density(branches, 5, fixed, q.tolist(), loads)
    differences = cs @ np.asarray(result.coordinates.data).reshape(-1, 3)
    _, analytic = condition_system(cs[:, :5], differences, q, [condition])
    numeric = np.zeros_like(analytic)
    for j in range(len(q)):

        def measure(delta, index=j):
            trial = q.copy()
            trial[index] += delta
            lengths = np.asarray(
                force_density(branches, 5, fixed, trial.tolist(), loads).lengths.data
            )
            return condition_values(lengths, trial, condition)

        numeric[:, j] = (measure(1e-5) - measure(-1e-5)) / 2e-5
    np.testing.assert_allclose(analytic, numeric, rtol=1e-6, atol=1e-9)


@pytest.mark.parametrize(
    "conditions",
    [
        [Condition("length", list(range(4)), [1.2] * 4)],
        [
            Condition("length", list(range(8, 12)), [0.9] * 4),
            Condition("force", list(range(4)), [2.0] * 4),
        ],
        [Condition("unstrained_length", list(range(4)), [1.15] * 4)],
    ],
)
def test_constraints_and_equilibrium(network, conditions):
    branches, fixed, q, loads = network
    result = constrained_force_density(branches, 5, fixed, q, loads, conditions)
    assert result.converged
    assert np.all(result.q > 0)
    assert np.all(np.diff(result.history) < 0)
    lengths = np.asarray(result.equilibrium.lengths.data)
    for condition in conditions:
        np.testing.assert_allclose(
            condition_values(lengths, result.q, condition), condition.targets, atol=1e-8
        )
    assert result.equilibrium.residuals.block(0, 0, 5, 3).norm_inf() < 1e-10
    np.testing.assert_allclose(
        np.asarray(result.equilibrium.reactions.data).reshape(-1, 3).sum(axis=0),
        [0, 0, 2.5],
        atol=1e-10,
    )


def test_iteration_limit_does_not_claim_convergence(network):
    branches, fixed, q, loads = network
    result = constrained_force_density(
        branches,
        5,
        fixed,
        q,
        loads,
        [Condition("length", [0], [100.0])],
        max_iterations=0,
    )
    assert not result.converged
    assert result.iterations == 0
    assert result.history[-1] > 1
