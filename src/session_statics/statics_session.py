"""A session that also writes its viewer manifest: texts, the opening view and live reload."""

import json
from pathlib import Path

from session_py import Point, Session

from .matrix_plot import MatrixPlot


class StaticsSession(Session):
    """A session named after its viewer scene, view_<name>; matrices added left to right with a cell of space between."""

    def __init__(self, name: str = "session_statics", title: str = "", view: str = "top", live: bool = True, gap: float = 1.0):
        super().__init__(name)
        self.title = title or name
        self.view = view
        self.live = live
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

    def dump(self, directory: str | Path) -> Path:
        """Write view_<name>.pb and its manifest view_<name>.yaml into directory; returns the .pb."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        geometry = directory / f"view_{self.name}.pb"
        self.pb_dump(geometry)
        manifest = {
            "name": self.title,
            "live": self.live,
            "view": self.view,
            "items": [{"file": f"pb/view_{self.name}.pb", "name": self.title, "at": [0, 0, 0]}],
            "texts": self.texts,
        }
        (directory / f"view_{self.name}.yaml").write_text(json.dumps(manifest, indent=2))
        return geometry
