"""
pgfplots drawing: marks (lines, filled shapes, colour-mapped patches, text) inside axes, axes inside a group.
Coordinates arrive in the data's own units; LaTeX does the painting.
"""
import math
from dataclasses import dataclass, field

from reports.elements.element import Element
from reports.latex import coord


ABOVE = "{at={(0,1.03)}, anchor=south west, legend columns=-1, /tikz/every even column/.append style={column sep=0.6em}}"   # legend over the frame, clear of the data


def _options(options: dict[str, str | None]) -> str:
    """{'width': '5cm', 'grid': None} -> 'width={5cm}, grid'. Values are braced so brackets in labels stay inside."""
    def value(v) -> str:
        v = str(v)
        return v if v.startswith("{") else f"{{{v}}}"
    return ", ".join(k if v is None else f"{k}={value(v)}" for k, v in options.items())


def _points(x, y) -> str:
    return " ".join(f"({coord(a)},{coord(b)})" for a, b in zip(x, y))


#---- Marks: what goes inside an axis ----#
class Mark(Element):
    pass


@dataclass
class Line(Mark):
    """A data series. Non-finite / missing points break the line."""
    x: list
    y: list
    style: str = ""
    legend: str | None = None

    def to_tex(self) -> str:
        y = [b if b is not None and math.isfinite(b) else math.nan for b in self.y]
        tex = rf"\addplot[unbounded coords=jump, {self.style}] coordinates {{{_points(self.x, y)}}};"
        return tex + (rf" \addlegendentry{{{self.legend}}}" if self.legend else "")


@dataclass
class Polygon(Mark):
    """A closed shape in axis coordinates; command \\fill, \\draw or \\filldraw."""
    x: list
    y: list
    style: str = ""
    command: str = r"\fill"

    def to_tex(self) -> str:
        points = " -- ".join(f"({coord(a)},{coord(b)})" for a, b in zip(self.x, self.y))
        return rf"{self.command}[{self.style}] {points} -- cycle;"


@dataclass
class Band(Mark):
    """The area between a lower and an upper curve, coloured by a value along x (shaded smoothly)."""
    x: list
    lo: list
    hi: list
    meta: list                  # colour value at each x

    def to_tex(self) -> str:
        quads = []
        for i in range(len(self.x) - 1):
            x0, x1, c0, c1 = self.x[i], self.x[i + 1], self.meta[i], self.meta[i + 1]
            quads += [(x0, self.lo[i], c0), (x1, self.lo[i + 1], c1), (x1, self.hi[i + 1], c1), (x0, self.hi[i], c0)]
        points = " ".join(f"({coord(a)},{coord(b)}) [{coord(c)}]" for a, b, c in quads)
        return (r"\addplot[patch, patch type=rectangle, shader=interp, point meta=explicit, forget plot] "
                rf"coordinates {{{points}}};")


@dataclass
class Text(Mark):
    x: float
    y: float
    text: str
    style: str = ""

    def to_tex(self) -> str:
        return rf"\node[{self.style}] at ({coord(self.x)},{coord(self.y)}) {{{self.text}}};"
#-----------------------------------------#


#---- Axes ----#
@dataclass
class Axis(Element):
    marks: list[Mark]
    options: dict[str, str | None] = field(default_factory=dict)

    def to_tex(self) -> str:
        body = "\n".join(m.to_tex() for m in self.marks)
        return rf"\begin{{axis}}[{_options(self.options)}]" + f"\n{body}\n" + r"\end{axis}"


@dataclass
class GroupPlot(Element):
    """Axes on a grid sharing one style; options of each Axis apply to it alone."""
    axes: list[Axis]
    columns: int
    options: dict[str, str | None] = field(default_factory=dict)

    def to_tex(self) -> str:
        rows = -(-len(self.axes) // self.columns)
        group = {"group style": f"{{group size={self.columns} by {rows}, horizontal sep=1.8cm, vertical sep=1.6cm}}"}
        body = "\n".join(
            rf"\nextgroupplot[{_options(a.options)}]" + "\n" + "\n".join(m.to_tex() for m in a.marks) for a in self.axes)
        return rf"\begin{{groupplot}}[{_options(group | self.options)}]" + f"\n{body}\n" + r"\end{groupplot}"
#--------------#


@dataclass
class Figure(Element):
    """A numbered float holding one drawing (an Axis or a GroupPlot)."""
    drawing: Axis | GroupPlot
    caption: str
    label: str

    def to_tex(self) -> str:
        return "\n".join([
            r"\begin{figure}[H]", r"\centering", r"\begin{tikzpicture}", self.drawing.to_tex(), r"\end{tikzpicture}",
            rf"\caption{{{self.caption}}}", rf"\label{{fig:{self.label}}}", r"\end{figure}"])
