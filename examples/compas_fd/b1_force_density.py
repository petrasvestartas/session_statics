"""A–G application of the compas_fd tutorial; publish with bash/publish.sh session_statics.

https://github.com/BRG-research/mcp-server-brg/blob/main/knowledge/04_form_finding/compas_fd.md
Supports and loads are chosen reconstruction inputs, not measured paper data.
"""

import json
from pathlib import Path

import numpy as np
from session_py import Color, Line, Matrix, Point, Session, Xform

from session_statics.constrained_force_density import (
    Condition,
    constrained_force_density,
)
from session_statics.force_density import force_density

OUTPUT = Path(__file__).resolve().parents[2] / "data" / "output"


def matrix(values):
    return Matrix.array(np.asarray(values, dtype=float).tolist())


def connectivity(branches, n_free, n_fixed):
    cs = np.zeros((len(branches), n_free + n_fixed))
    for j, (a, b) in enumerate(branches):
        cs[j, a - 1], cs[j, b - 1] = 1, -1
    return cs, cs[:, :n_free], cs[:, n_free:]


def radial_network():
    border = [
        62,
        2,
        4,
        6,
        17,
        19,
        63,
        20,
        21,
        22,
        44,
        61,
        64,
        60,
        59,
        57,
        55,
        65,
        54,
        45,
        28,
        13,
        12,
        11,
        66,
        10,
        5,
        3,
        1,
    ]
    inner = [
        31,
        30,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        42,
        41,
        40,
        39,
        38,
        37,
        36,
        35,
        34,
        33,
        32,
    ]
    middle = [27, 29, 46, 56, 58, 43, 23, 24, 25, 26]
    spokes = [31, 33, 35, 37, 39, 41, 53, 51, 49, 47]
    links = [
        (30, 29),
        (32, 27),
        (34, 26),
        (36, 25),
        (38, 24),
        (40, 23),
        (42, 43),
        (52, 58),
        (50, 56),
        (48, 46),
        (27, 14),
        (29, 28),
        (46, 45),
        (56, 57),
        (58, 59),
        (43, 44),
        (23, 22),
        (24, 18),
        (25, 16),
        (26, 15),
        (1, 2),
        (4, 7),
        (6, 7),
        (7, 8),
        (3, 8),
        (8, 9),
        (5, 9),
        (9, 12),
        (9, 14),
        (13, 14),
        (10, 11),
        (8, 15),
        (14, 15),
        (15, 16),
        (7, 16),
        (16, 18),
        (17, 18),
        (18, 21),
        (19, 20),
        (61, 60),
        (59, 58),
        (57, 56),
        (54, 55),
    ]

    def ring(nodes):
        return list(zip(nodes, nodes[1:] + nodes[:1]))

    edges = list(
        dict.fromkeys(
            tuple(sorted(e))
            for e in ring(border)
            + ring(inner)
            + ring(middle)
            + [(k, 67) for k in spokes]
            + links
        )
    )
    border_edges = {tuple(sorted(e)) for e in ring(border)}
    is_border = np.array([e in border_edges for e in edges])
    is_radial = np.array([67 in e for e in edges])
    touches = np.array([any(k in border for k in e) for e in edges])
    # Free plan coordinates are unknown: only the six traced support positions enter.
    pixels = np.array(
        [[97, 494], [362, 981], [999, 763], [954, 270], [340, 68], [685, 571]],
        dtype=float,
    )
    supports = np.column_stack(((pixels - pixels[-1]) * [0.04, -0.04], np.zeros(6)))
    supports[-1, 2] = 16
    q = np.where(is_border, 100.0, np.where(is_radial, 0.5, 1.0))
    loads = np.zeros((61, 3))
    loads[:, 2] = -0.4
    return edges, supports, q, loads, is_border, is_radial, touches


def grid_network():
    corners = [0, 7, 63, 56]
    order = [j for j in range(64) if j not in corners] + corners
    labels = {old: new + 1 for new, old in enumerate(order)}
    original = [(8 * y + x, 8 * y + x + 1) for y in range(8) for x in range(7)]
    original += [(8 * y + x, 8 * (y + 1) + x) for y in range(7) for x in range(8)]
    branches = [(labels[a], labels[b]) for a, b in original]
    flat = np.array([[j % 8, j // 8, 0] for j in order], dtype=float)

    def boundary(j):
        return j % 8 in (0, 7) or j // 8 in (0, 7)

    border = np.array(
        [
            (a // 8 == b // 8 and a // 8 in (0, 7))
            or (a % 8 == b % 8 and a % 8 in (0, 7))
            for a, b in original
        ]
    )
    touches = np.array([boundary(a) or boundary(b) for a, b in original])
    supports = flat[-4:].copy()
    supports[:, :2] = (supports[:, :2] - 3.5) * 0.8 + 3.5
    loads = np.zeros((60, 3))
    loads[:, 2] = -0.075 * np.bincount(np.array(branches).ravel(), minlength=65)[1:61]
    return branches, supports, loads, border, touches


def main():
    np.set_printoptions(precision=6, suppress=True)
    scene, report = Session("session_statics"), []

    def keep(name, edges, n, fixed, q, loads, conditions=(), required=True):
        if conditions:
            solution = constrained_force_density(
                edges, n, matrix(fixed), q, matrix(loads), conditions
            )
            result, q = solution.equilibrium, solution.q
            iterations, error, converged = (
                solution.iterations,
                solution.history[-1],
                solution.converged,
            )
            if required and not converged:
                raise RuntimeError(f"{name}: conditions did not converge: {error}")
        else:
            result = force_density(edges, n, matrix(fixed), list(q), matrix(loads))
            iterations, error, converged = 0, 0.0, True
        xyz = np.asarray(result.coordinates.data).reshape(-1, 3)
        lengths, forces = (
            np.asarray(result.lengths.data),
            np.asarray(result.forces.data),
        )
        # Check the original nonlinear equilibrium independently by summing member forces.
        balance = np.vstack([loads, np.zeros_like(fixed)])
        for j, (a, b) in enumerate(edges):
            force = forces[j] * (xyz[b - 1] - xyz[a - 1]) / lengths[j]
            balance[a - 1] += force
            balance[b - 1] -= force
        residual = float(np.max(np.abs(balance[:n])))
        reactions = np.asarray(result.reactions.data).reshape(-1, 3)
        np.testing.assert_allclose(xyz[n:], fixed, atol=1e-12)
        np.testing.assert_allclose(balance[:n], 0, atol=1e-8)
        np.testing.assert_allclose(
            reactions.sum(axis=0) + loads.sum(axis=0), 0, atol=1e-8
        )
        status = "converged" if converged else "STOPPED: targets not met"
        print(
            f"{name}: {status}; iterations={iterations}; condition error={error:.3e}; equilibrium error={residual:.3e}",
            flush=True,
        )
        report.append(
            {
                "name": name,
                "converged": converged,
                "iterations": iterations,
                "condition_error": error,
                "equilibrium_error": residual,
                "q": list(q),
                "lengths": lengths.tolist(),
                "forces": forces.tolist(),
                "coordinates": xyz.tolist(),
                "reactions": reactions.tolist(),
                "conditions": [
                    {
                        "kind": c.kind,
                        "branches": list(c.branches),
                        "targets": list(c.targets),
                        "stiffness": c.stiffness,
                    }
                    for c in conditions
                ],
            }
        )
        group = scene.add_group(f"{name} | {status}")
        # Uniform scaling affects the gallery only; the report retains metres and kN.
        i = len(report) - 1
        origin = np.array([(i % 5) * 12.0, -(i // 5) * 13.0, 0.0])
        extent = max(float(np.ptp(xyz[:, :2], axis=0).max()), 1.0)
        display = (xyz - (xyz.min(axis=0) + xyz.max(axis=0)) / 2) * (
            8 / extent
        ) + origin
        for j, (a, b) in enumerate(edges):
            line = Line(*display[a - 1], *display[b - 1])
            line.name = f"branch {j + 1}: q={q[j]:.4g} kN/m, l={lengths[j]:.4g} m, s={forces[j]:.4g} kN"
            line.linecolor = (
                Color(0.12, 0.35, 0.65) if converged else Color(0.9, 0.45, 0.08)
            )
            line.width = 2
            scene.add_line(line, group)
        for j, position in enumerate(display):
            point = Point(*position)
            point.name = f"{'support' if j >= n else 'free node'} {j + 1}"
            point.width = 9 if j >= n else 4
            point.pointcolor = (
                Color(0.85, 0.15, 0.2) if j >= n else Color(0.12, 0.35, 0.65)
            )
            scene.add_point(point, group)
        table = Matrix.array([[iterations, error, residual]])
        table.name = f"{name}: iterations | condition error | equilibrium error"
        scene.add_matrix(table, group)
        scene.set_xform(table.guid, Xform.translation(origin[0] - 4, origin[1] - 5, 0))
        return xyz, lengths, forces, np.asarray(q)

    # A–D: build the network, evaluate a trial, solve, then change design inputs.
    edges = [
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
    supports = np.array([[-2, 0, 0], [0, 2, 1], [2, 0, 0], [0, -2, 1]], dtype=float)
    loads = np.tile([0.0, 0.0, -0.5], (5, 1))
    q = np.array([2.0] * 4 + [1.0] * 8)
    cs, c, cf = connectivity(edges, 5, 4)
    trial = np.array(
        [[-1, 0, 0], [0, 1, 0], [1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=float
    )
    delta = cs @ np.vstack([trial, supports])
    print(
        "B3 trial vertical imbalance:",
        (c.T @ (delta / np.linalg.norm(delta, axis=1)[:, None]) - loads)[:, 2],
    )
    d, df = c.T @ (q[:, None] * c), c.T @ (q[:, None] * cf)
    rhs = loads - df @ supports
    print("C2 D:\n", d, "\nD_f:\n", df, "\nright-hand side:\n", rhs)
    xyz, _lengths, _, _ = keep("C linear equilibrium", edges, 5, supports, q, loads)
    np.testing.assert_allclose(xyz[:5], np.linalg.solve(d, rhs), atol=1e-12)
    raised, *_ = keep("D lifted supports", edges, 5, supports + [0, 0, 1], q, loads)
    np.testing.assert_allclose(raised, xyz + [0, 0, 1], atol=1e-12)
    keep("D anchor q=10", edges, 5, supports, np.array([10.0] * 4 + [1.0] * 8), loads)
    # E: the unloaded weighted squared-length minimum and equal-force identity.
    unloaded, l0, _, _ = keep(
        "E unloaded minimum", edges, 5, supports, q, np.zeros_like(loads)
    )
    np.testing.assert_allclose(2 * c.T @ (q[:, None] * (cs @ unloaded)), 0, atol=1e-12)
    np.testing.assert_allclose(l0 * (1 / l0), 1)
    # F: distance, force, mixed and finite-stiffness unstrained-length conditions.
    keep(
        "F anchor lengths 1.2 m",
        edges,
        5,
        supports,
        q,
        loads,
        [Condition("length", list(range(4)), [1.2] * 4)],
    )
    keep(
        "F mixed lengths and forces",
        edges,
        5,
        supports,
        q,
        loads,
        [
            Condition("length", list(range(8, 12)), [0.9] * 4),
            Condition("force", list(range(4)), [2.0] * 4),
        ],
    )
    keep(
        "F unstrained lengths",
        edges,
        5,
        supports,
        q,
        loads,
        [Condition("unstrained_length", list(range(4)), [1.15] * 4, 100.0)],
    )
    # G1–G4: the 67-node/110-branch radial net and its parameter studies.
    radial, anchors, qr, pr, border, spokes, touches = radial_network()
    assert len(radial) == 110
    for i, offset in enumerate(([0, 0, 0], [6, 2, 0], [12, 4, 0]), 1):
        fixed = anchors.copy()
        fixed[-1] += offset
        keep(f"G fig6.{i} moved apex", radial, 61, fixed, qr, pr)
    for i, value in enumerate([1.0, 0.7, 0.3], 1):
        keep(
            f"G fig7.{i} radial q={value}",
            radial,
            61,
            anchors,
            np.where(spokes, value, qr),
            pr,
        )
    for i, value in enumerate([10.0, 5.0, 1.0], 1):
        keep(
            f"G fig8.{i} border q={value:g}",
            radial,
            61,
            anchors,
            np.where(border, value, qr),
            pr,
        )
    baseline = force_density(radial, 61, matrix(anchors), qr.tolist(), matrix(pr))
    base_lengths = np.asarray(baseline.lengths.data)
    rows = np.flatnonzero(~touches).tolist()
    for i, (radial_length, factor) in enumerate(
        [(6.0, 1.25), (6.0, 0.85), (4.5, 0.7)], 1
    ):
        targets = [
            radial_length if spokes[j] else base_lengths[j] * factor for j in rows
        ]
        keep(
            f"G fig9.{i} prescribed lengths",
            radial,
            61,
            anchors,
            qr,
            pr,
            [Condition("length", rows, targets)],
            required=i == 2,
        )
    # G5: 112 bars: equal-length hanging grid, prestress, then mixed conditions.
    grid, anchors, weights, border, touches = grid_network()
    keep(
        "G fig10.1 equal 1 m bars",
        grid,
        60,
        anchors,
        np.ones(112),
        weights,
        [Condition("length", list(range(112)), [1.0] * 112)],
    )
    anchors[[0, 2], 2] = 3
    qg = np.where(border, 10.0, 1.0)
    _, lg, sg, _ = keep(
        "G fig10.2 prestressed grid", grid, 60, anchors, qg, np.zeros_like(weights)
    )
    inner = np.flatnonzero(~border & ~touches).tolist()
    links = np.flatnonzero(~border & touches).tolist()
    keep(
        "G fig10.3 mixed grid",
        grid,
        60,
        anchors,
        qg,
        np.zeros_like(weights),
        [
            Condition("length", inner, [float(lg[inner].mean())] * len(inner)),
            Condition("force", links, [float(sg[links].mean())] * len(links)),
        ],
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    scene.pb_dump(OUTPUT / "view_session_statics.pb")
    (OUTPUT / "force_density_results.json").write_text(json.dumps(report, indent=2))
    print(f"Saved {len(report)} cases to {OUTPUT}")


if __name__ == "__main__":
    main()
