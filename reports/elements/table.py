"""
A numbered table in booktabs style. Cells arrive as LaTeX.
"""
from dataclasses import dataclass, field

from reports.elements.element import Element


@dataclass
class Group:
    """Rows under an optional italic heading spanning the table."""
    rows: list[list[str]]
    title: str | None = None


@dataclass
class Table(Element):
    caption: str
    label: str
    header: list[list[str]]             # one or more header lines
    groups: list[Group]
    align: str                          # tabular column spec, e.g. "lrl"
    small: bool = False
    notes: list[str] = field(default_factory=list)

    def to_tex(self) -> str:
        n = len(self.header[0])
        lines = [r"\begin{table}[H]", r"\centering"]
        if self.small:
            lines.append(r"\small")
        lines += [rf"\caption{{{self.caption}}}", rf"\label{{tab:{self.label}}}",
                  rf"\begin{{tabular}}{{{self.align}}}", r"\toprule"]
        lines += [" & ".join(h) + r" \\" for h in self.header]
        for group in self.groups:
            lines.append(r"\midrule")
            if group.title:
                lines.append(rf"\multicolumn{{{n}}}{{l}}{{\textit{{{group.title}}}}} \\")
            lines += [" & ".join(r) + r" \\" for r in group.rows]
        lines += [r"\bottomrule", r"\end{tabular}"]
        if self.notes:
            lines.append(r"\par\smallskip\footnotesize " + r" \\ ".join(self.notes))
        lines.append(r"\end{table}")
        return "\n".join(lines)
