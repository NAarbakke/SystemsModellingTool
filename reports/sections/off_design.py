"""
Off-design performance: one figure per swept input.
"""
from interface.gui.dashboard_view import KPIS
from reports.elements.element import Element, Raw
from reports.figures.sweep_plot import sweep_plot
from reports.latex import escape, in_sentence, num, split_unit
from reports.report import Case, Section
from reports.sweep import Sweep

OUTPUTS = ["Thrust", "TSFC"]       # run_point() scalars plotted against each swept input


class OffDesign(Section):
    title = "Off-design performance"
    label = "off-design"

    def __init__(self, case: Case, sweeps: list[Sweep]):
        self.case = case
        self.sweeps = sweeps

    def _range(self, sweep: Sweep, key: str) -> str:
        label, unit, scale = KPIS[key]
        values = [v for v in sweep.series(key, scale) if v is not None]
        return rf"{escape(in_sentence(label))} from {num(min(values), 3)} to {num(max(values), 3)} {escape(unit)}"

    def elements(self) -> list[Element]:
        out: list[Element] = []
        design = self.case.snap.result
        for sweep in self.sweeps:
            outputs = [k for k in OUTPUTS if k in design]
            name, _ = split_unit(sweep.input.label)
            fig = sweep_plot(sweep, outputs, design, self.case.values[sweep.input.key])
            if sweep.n_failed == len(sweep.x):
                out.append(Raw(rf"No point of the {escape(in_sentence(name))} sweep is physical."))
                continue
            ranges = " and ".join(self._range(sweep, k) for k in outputs)
            out.append(Raw(
                rf"Varying {escape(in_sentence(name))} from {num(sweep.input.lo, 3)} to {num(sweep.input.hi, 3)} "
                rf"with every other input held at the design point moves {ranges} (\autoref{{fig:{fig.label}}})."))
            out.append(fig)
        return out
