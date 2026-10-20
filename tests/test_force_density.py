import math

import pytest
from session_py import Matrix

from session_statics.force_density import force_density


def test_four_cable_equilibrium():
    branches = [(1, 2), (1, 3), (1, 4), (1, 5)]
    fixed = Matrix.array([[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]])
    result = force_density(branches, 1, fixed, [1.0] * 4, Matrix.array([[0, 0, -1]]))
    assert result.coordinates.data[:3] == pytest.approx([0, 0, -0.25])
    assert result.coordinates.data[3:] == fixed.data
    assert result.lengths.data == pytest.approx([math.sqrt(2.0625)] * 4)
    assert result.forces.data == pytest.approx(result.lengths.data)
    assert result.residuals.data[:3] == pytest.approx([0, 0, 0], abs=1e-12)
    assert sum(result.reactions[i, 2] for i in range(4)) == pytest.approx(1)


def test_tutorial_network():
    branches = [(1, 6), (2, 7), (3, 8), (4, 9), (1, 4), (1, 2),
                (2, 3), (3, 4), (4, 5), (1, 5), (2, 5), (3, 5)]
    fixed = Matrix.array([[-2, 0, 0], [0, -2, 1], [2, 0, 0], [0, 2, 1]])
    result = force_density(branches, 5, fixed, [2.0] * 4 + [1.0] * 8, Matrix.array([[0, 0, -0.5] for _ in range(5)]))
    assert result.coordinates.block(0, 0, 5, 1).data == pytest.approx([-0.8, 0, 0.8, 0, 0], abs=1e-12)
    assert result.coordinates.block(0, 2, 5, 1).data == pytest.approx([5/112, 37/112, 5/112, 37/112, 1/16])
    assert result.residuals.block(0, 0, 5, 3).norm_inf() < 1e-12
    assert sum(result.reactions[i, 2] for i in range(4)) == pytest.approx(2.5)


def test_compression_uses_general_solve():
    result = force_density([(1, 2)], 1, Matrix.array([[0, 0, 0]]), [-1], Matrix.array([[0, 0, -1]]))
    assert result.coordinates.data[:3] == pytest.approx([0, 0, 1])
    assert result.forces.data == pytest.approx([-1])


@pytest.mark.parametrize("branches,q,fixed,loads", [
    ([(1, 2)], [], [[0, 0, 0]], [[0, 0, -1]]),
    ([(1, 3)], [1], [[0, 0, 0]], [[0, 0, -1]]),
    ([(1, 1)], [1], [[0, 0, 0]], [[0, 0, -1]]),
    ([(1, 2)], [float("nan")], [[0, 0, 0]], [[0, 0, -1]]),
    ([(1, 2)], [0], [[0, 0, 0]], [[0, 0, -1]]),
    ([], [], [[0, 0, 0]], [[0, 0, -1]]),
    ([(1, 2)], [1], [[0, 0]], [[0, 0, -1]]),
    ([(1, 2)], [1], [[0, 0, 0]], [[0, -1]]),
])
def test_invalid_inputs(branches, q, fixed, loads):
    with pytest.raises(ValueError):
        force_density(branches, 1, Matrix.array(fixed), q, Matrix.array(loads))
