"""
Terminal front end for the PDF reports: pick an engine, edit the design point (live performance preview), choose
the sweeps, build. The report itself comes from reports/build.py, same as the CLI and the web API.

Run from the repo root:  .venv/Scripts/python -m interface.tui.reports_app
"""
import os
import sys
import time
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, RichLog, Select, SelectionList, Static

from interface.gui.dashboard_view import EngineView, performance_tiles
from interface.gui.engines import ENGINES
from reports.build import DEFAULT_POINTS, DEFAULT_SWEEPS, OUTPUT, build_report
from reports.report import ReportError


def _numeric_inputs(view: EngineView):
    return [i for group in view.inputs.values() for i in group if not i.options]


class InputRow(Horizontal):
    """One design-point input: label and a number field, or a choice."""

    def __init__(self, inp, value):
        super().__init__(classes="row")
        self.inp = inp
        self.value = value

    def compose(self) -> ComposeResult:
        yield Label(self.inp.label, classes="name")
        if self.inp.options:
            yield Select([(v, k) for k, v in self.inp.options.items()], value=self.value, allow_blank=False,
                         id=f"in-{self.inp.key}", compact=True)
        else:
            yield Input(f"{self.value:g}", type="number", id=f"in-{self.inp.key}", compact=True)

    def mark(self, changed: bool) -> None:
        self.set_class(changed, "changed")


class ReportsApp(App):
    TITLE = "Systems Modelling Tool"
    SUB_TITLE = "Engine reports"
    CSS_PATH = "reports_app.tcss"
    BINDINGS = [("ctrl+b", "build", "Build report"), ("ctrl+o", "open_pdf", "Open PDF"),
                ("ctrl+r", "reset", "Reset inputs"), ("ctrl+q", "quit", "Quit")]

    def __init__(self, engine: str = "conventional"):
        super().__init__()
        self.engine = engine
        self.values = {key: view.defaults for key, (_, view) in ENGINES.items()}     # per engine, kept when switching
        self.pdf: Path | None = None

    @property
    def view(self) -> EngineView:
        return ENGINES[self.engine][1]

    #---- Layout ----#
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="side"):
                yield Label("ENGINE", classes="eyebrow")
                yield Select([(label, key) for key, (label, _) in ENGINES.items()], value=self.engine,
                             allow_blank=False, id="engine")
                yield VerticalScroll(id="inputs")
                yield Static(id="changed")
            with Vertical(id="main"):
                yield Static(id="title")
                yield Label("DESIGN POINT", classes="eyebrow")
                yield DataTable(id="kpis", show_cursor=False, zebra_stripes=False)
                yield Label("OFF-DESIGN SWEEPS", classes="eyebrow")
                yield SelectionList[str](id="sweeps")
                with Horizontal(id="options"):
                    yield Label("Points per sweep", classes="name")
                    yield Input(str(DEFAULT_POINTS), type="integer", id="points", compact=True)
                with Horizontal(id="actions"):
                    yield Button("Build report", id="build", variant="primary")
                    yield Button("Open PDF", id="open", disabled=True)
                yield RichLog(id="log", markup=True, wrap=True)
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#kpis", DataTable).add_columns("Quantity", "Value", "Unit")
        await self.load_engine()
        self.log_line(f"[dim]PDFs go to {OUTPUT}[/]")

    async def load_engine(self) -> None:
        """Rebuild the input rows and sweep choices for the current engine."""
        pane = self.query_one("#inputs", VerticalScroll)
        await pane.remove_children()
        values = self.values[self.engine]
        for group, items in self.view.inputs.items():
            await pane.mount(Label(group, classes="group"))
            await pane.mount_all(InputRow(i, values[i.key]) for i in items)
        sweeps = self.query_one("#sweeps", SelectionList)
        sweeps.clear_options()
        sweeps.add_options([(i.label, i.key, i.key in DEFAULT_SWEEPS) for i in _numeric_inputs(self.view)])
        self.query_one("#title", Static).update(f"[b]{self.view.title}[/]")
        self.refresh_point()
    #----------------#

    #---- Live design point ----#
    def refresh_point(self) -> None:
        values = self.values[self.engine]
        defaults = self.view.defaults
        for row in self.query(InputRow):
            row.mark(values[row.inp.key] != defaults[row.inp.key])
        n = sum(values[k] != defaults[k] for k in values)
        self.query_one("#changed", Static).update("SKYF specification" if n == 0 else f"[#ff8a3d]{n} changed[/] from SKYF spec")

        table = self.query_one("#kpis", DataTable)
        table.clear()
        try:
            snap = self.view.evaluate(values)
            error = snap.error
        except Exception as e:
            snap, error = None, f"The model could not run this point: {e}"
        if error:
            table.add_row("[#e5484d]Not physical[/]", "", "")
            self.query_one("#build", Button).disabled = True
            self.log_line(f"[#e5484d]{error}[/]")
            return
        self.query_one("#build", Button).disabled = False
        for t in performance_tiles(snap.result):
            table.add_row(t.label, f"[b]{t.value}[/]", t.unit)

    def on_input_changed(self, event: Input.Changed) -> None:
        key = (event.input.id or "").removeprefix("in-")
        if key not in self.values[self.engine]:
            return
        try:
            self.values[self.engine][key] = float(event.value)
        except ValueError:
            return                                  # mid-edit ("", "-", "1e")
        self.refresh_point()

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "engine":
            if event.value != self.engine:
                self.engine = str(event.value)
                await self.load_engine()
            return
        key = (event.select.id or "").removeprefix("in-")
        if key in self.values[self.engine]:
            self.values[self.engine][key] = event.value
            self.refresh_point()
    #---------------------------#

    #---- Build ----#
    def log_line(self, text: str) -> None:
        self.query_one("#log", RichLog).write(f"[dim]{time.strftime('%H:%M:%S')}[/]  {text}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        {"build": self.action_build, "open": self.action_open_pdf}[event.button.id]()

    def action_build(self) -> None:
        button = self.query_one("#build", Button)
        if button.disabled:
            return
        sweeps = list(self.query_one("#sweeps", SelectionList).selected)
        try:
            points = max(3, int(self.query_one("#points", Input).value))
        except ValueError:
            points = DEFAULT_POINTS
        button.disabled, button.label = True, "Building…"
        self.log_line(f"Building {self.engine} report, sweeps: {', '.join(sweeps) or 'none'} ({points} points)…")
        self.build(self.engine, dict(self.values[self.engine]), sweeps, points)

    @work(thread=True, exclusive=True)
    def build(self, engine: str, values: dict, sweeps: list[str], points: int) -> None:
        start = time.perf_counter()
        try:
            pdf = build_report(engine, values, sweeps, points)
        except ReportError as e:
            self.call_from_thread(self.built, None, str(e).splitlines()[0], 0.0)
            return
        self.call_from_thread(self.built, pdf, None, time.perf_counter() - start)

    def built(self, pdf: Path | None, error: str | None, seconds: float) -> None:
        button = self.query_one("#build", Button)
        button.disabled, button.label = False, "Build report"
        if error:
            self.log_line(f"[#e5484d]Failed:[/] {error}")
            return
        self.pdf = pdf
        self.query_one("#open", Button).disabled = False
        self.log_line(f"[#46a758]Written[/] {pdf}  [dim]({seconds:.1f} s)[/]")

    def action_open_pdf(self) -> None:
        if self.pdf and self.pdf.exists():
            if sys.platform == "win32":
                os.startfile(self.pdf)
            else:
                self.log_line(f"Open {self.pdf}")

    async def action_reset(self) -> None:
        self.values[self.engine] = self.view.defaults
        await self.load_engine()
    #---------------#


if __name__ == "__main__":
    ReportsApp().run()
