"""A session that also writes its viewer manifest: texts, the opening view, the floor grid and live reload."""

import json
from pathlib import Path

from session_py import Point, Session

from .matrix_plot import MatrixPlot


class StaticsSession(Session):
    """A session named after its viewer scene, view_<name>; matrices added left to right with a cell of space between."""

    def __init__(
        self,
        name: str = "session_statics",
        title: str = "",
        view: str = "top",
        live: bool = True,
        grid: bool = False,
        gap: float = 1.0,
    ):
        super().__init__(name)
        self.title = title or name
        self.view = view
        self.live = live
        self.grid = grid
        self.gap = gap
        self.texts: list[dict] = []
        self.next_x = 0.0

    def add_matrix(self, values, title: str = "", **options) -> MatrixPlot:
        """Draw a matrix or vector as a heatmap after the last one, or at options['origin']; MatrixPlot takes the other options."""
        options.setdefault("origin", Point(self.next_x, 0.0, 0.0))
        plot = MatrixPlot(values, title, **options)
        self.add_mesh(plot.mesh)
        self.texts.extend(plot.texts)
        self.next_x = max(self.next_x, plot.origin[0] + (plot.cols + self.gap) * plot.cell)
        return plot

    def pb_dump(self, filename: str | Path) -> None:
        """Write the session to filename and its viewer manifest beside it, the same name with .yaml."""
        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        super().pb_dump(filename)
        manifest = {
            "name": self.title,
            "live": self.live,
            "view": self.view,
            "grid": self.grid,
            "items": [{"file": f"pb/{filename.name}", "name": self.title, "at": [0, 0, 0]}],
            "texts": self.texts,
        }
        filename.with_suffix(".yaml").write_text(json.dumps(manifest, indent=2))
