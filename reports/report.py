"""
A report is a title block and a list of sections; each section is a list of elements (tables, figures, prose).
Report.build() writes the LaTeX and compiles it to PDF with latexmk (xelatex).
"""
import shutil
import subprocess
from dataclasses import dataclass
from datetime import date
from functools import cached_property
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from interface.api.serialise import engine_summary, snapshot
from interface.gui.dashboard_view import EngineView, Snapshot
from reports.elements.element import Element

TEMPLATES = Path(__file__).parent / "templates"

# Jinja delimiters that do not clash with LaTeX braces
_JINJA = Environment(
    loader=FileSystemLoader(TEMPLATES), block_start_string=r"\BLOCK{", block_end_string="}",
    variable_start_string=r"\VAR{", variable_end_string="}", comment_start_string=r"\#{", comment_end_string="}",
    trim_blocks=True, lstrip_blocks=True, autoescape=False)


class ReportError(RuntimeError):
    pass


@dataclass
class Case:
    """The operating point a report is about: the engine, its input values and the evaluated point.
    `point` and `engine` are the dashboard's ready-to-draw data (interface/api/serialise.py), so the report paints
    exactly what the dashboard paints."""
    key: str
    view: EngineView
    values: dict
    snap: Snapshot

    @classmethod
    def evaluate(cls, key: str, view: EngineView, values: dict) -> "Case":
        values = view.defaults | values
        try:
            snap = view.evaluate(values)
        except Exception as e:      # the model raising is a point it cannot run
            raise ReportError(f"The model could not run the design point: {e}") from None
        if snap.error:
            raise ReportError(f"The design point is not physical: {snap.error}")
        return cls(key, view, values, snap)

    @cached_property
    def point(self) -> dict:
        return snapshot(self.view, self.snap)

    @cached_property
    def engine(self) -> dict:
        return engine_summary(self.key, self.key, self.view)


class Section(Element):
    """A section: a title and the elements under it. Subclasses fill elements()."""
    title: str = ""
    label: str = ""
    numbered: bool = True

    def elements(self) -> list[Element]:
        raise NotImplementedError

    def to_tex(self) -> str:
        star = "" if self.numbered else "*"
        head = rf"\section{star}{{{self.title}}}\label{{sec:{self.label}}}"
        return "\n\n".join([head, *(e.to_tex() for e in self.elements())])


@dataclass
class Report:
    title: str
    subtitle: str
    author: str
    abstract: str
    sections: list[Section]

    def to_tex(self) -> str:
        return _JINJA.get_template("report.tex.j2").render(
            title=self.title, subtitle=self.subtitle, author=self.author, date=date.today().strftime("%d %B %Y"),
            abstract=self.abstract, sections=[s.to_tex() for s in self.sections])

    def build(self, pdf: Path) -> Path:
        """Write <name>.tex next to a build folder and compile; returns the PDF path."""
        if not shutil.which("latexmk"):
            raise ReportError("latexmk not found - install TeX Live and put it on PATH")
        pdf = Path(pdf).resolve()
        work = pdf.parent / f"{pdf.stem}_build"
        work.mkdir(parents=True, exist_ok=True)
        tex = work / f"{pdf.stem}.tex"
        tex.write_text(self.to_tex(), encoding="utf-8")

        run = subprocess.run(
            ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", tex.name],
            cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace")
        built = work / f"{pdf.stem}.pdf"
        if run.returncode != 0 or not built.exists():
            log = (work / f"{pdf.stem}.log")
            tail = log.read_text(encoding="utf-8", errors="replace")[-3000:] if log.exists() else run.stdout[-3000:]
            raise ReportError(f"LaTeX failed, see {log}\n...\n{tail}")
        shutil.copyfile(built, pdf)
        return pdf
