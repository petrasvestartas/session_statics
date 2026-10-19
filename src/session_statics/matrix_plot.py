"""A matrix drawn as a heatmap: a mesh of cells coloured from the minimum to the maximum entry, its values and title as texts."""

import numpy as np
from session_py import Color, Mesh, Point

# BRG Equilibrium palette, the vivid pair: navy for the minimum, pink for the maximum, the darker grey for zero
BRG_BLUE = Color(0x0B / 255, 0x19 / 255, 0x57 / 255)
BRG_PINK = Color(0xCE / 255, 0x40 / 255, 0x95 / 255)
BRG_ZERO = Color(0xB9 / 255, 0xB9 / 255, 0xBD / 255)

# Noto Sans, the viewer's font: advance widths in em, and the digits' middle below the line box top
ADVANCE = {".": 0.268, "-": 0.322, "e": 0.561, "+": 0.572}
DIGIT_ADVANCE = 0.572
DIGIT_MIDDLE = 0.753


class MatrixPlot:
    """A matrix or vector as a heatmap: row r at y = -r * cell and column c at x = c * cell from the origin, the first cell centred on it."""

    def __init__(
        self,
        values,
        title: str = "",
        origin: Point | None = None,
        cell: float = 100.0,
        min_color: Color = BRG_BLUE,
        max_color: Color = BRG_PINK,
        zero_color: Color = BRG_ZERO,
        text_color: Color = Color.white(),
        title_color: Color = Color.black(),
        text_height: float = 0.3,
        title_height: float = 0.35,
    ):
        self.values = np.atleast_2d(np.asarray(values, dtype=float))
        self.title = title
        self.origin = origin if origin is not None else Point(0.0, 0.0, 0.0)
        self.cell = cell
        self.min_color = min_color
        self.max_color = max_color
        self.zero_color = zero_color
        self.text_color = text_color
        self.title_color = title_color
        self.text_height = text_height
        self.title_height = title_height

        # cells: a quad per entry, coloured from the smallest to the largest non-zero entry, zero in its own colour
        self.mesh = self._compute_mesh()

        # texts: every non-zero value centred on its cell, the title above the matrix
        self.texts = self._compute_texts()

    @property
    def rows(self) -> int:
        """Number of rows."""
        return self.values.shape[0]

    @property
    def cols(self) -> int:
        """Number of columns."""
        return self.values.shape[1]

    def _compute_mesh(self) -> Mesh:
        """One quad per entry, its face colour from the value."""
        nonzero = self.values[np.abs(self.values) >= 1e-12]
        low = float(nonzero.min()) if nonzero.size else 0.0
        high = float(nonzero.max()) if nonzero.size else 0.0
        half = 0.5 * self.cell
        mesh = Mesh()
        colors = []

        for r in range(self.rows):
            for c in range(self.cols):
                x = self.origin[0] + c * self.cell
                y = self.origin[1] - r * self.cell
                z = self.origin[2]
                mesh.add_face([
                    mesh.add_vertex(Point(x - half, y + half, z)),
                    mesh.add_vertex(Point(x - half, y - half, z)),
                    mesh.add_vertex(Point(x + half, y - half, z)),
                    mesh.add_vertex(Point(x + half, y + half, z)),
                ])
                value = float(self.values[r, c])

                if abs(value) < 1e-12:
                    colors.append(self.zero_color)
                    continue

                t = (value - low) / (high - low) if high > low else 1.0
                colors.append(Color(
                    self.min_color.r + (self.max_color.r - self.min_color.r) * t,
                    self.min_color.g + (self.max_color.g - self.min_color.g) * t,
                    self.min_color.b + (self.max_color.b - self.min_color.b) * t,
                ))

        mesh.set_facecolors(colors)
        mesh.name = self.title or "matrix"
        return mesh

    def _compute_texts(self) -> list[dict]:
        """The viewer manifest texts: values centred on their cells, the title above."""
        ink = [round(self.text_color.r * 255), round(self.text_color.g * 255), round(self.text_color.b * 255), 255]
        title_ink = [round(self.title_color.r * 255), round(self.title_color.g * 255), round(self.title_color.b * 255), 255]
        height = self.text_height * self.cell
        texts = []

        if self.title:
            texts.append({
                "text": self.title,
                "at": [self.origin[0] - 0.5 * self.cell, self.origin[1] + 1.2 * self.cell, self.origin[2]],
                "height": self.title_height * self.cell,
                "plate": False,
                "color": title_ink,
            })

        for r in range(self.rows):
            for c in range(self.cols):
                value = float(self.values[r, c])

                if abs(value) < 1e-12:
                    continue

                label = f"{value:g}"
                width = sum(ADVANCE.get(character, DIGIT_ADVANCE) for character in label) * height
                texts.append({
                    "text": label,
                    "at": [
                        self.origin[0] + c * self.cell - width / 2,
                        self.origin[1] - r * self.cell + DIGIT_MIDDLE * height,
                        self.origin[2] + 0.01 * self.cell,
                    ],
                    "height": height,
                    "plate": False,
                    "color": ink,
                })

        return texts
