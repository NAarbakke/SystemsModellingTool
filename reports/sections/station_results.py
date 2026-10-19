"""
The flow state at every station: as a table and as plots along the engine.
"""
from reports.elements.element import Element, Raw
from reports.elements.table import Group, Table
from reports.figures.station_plots import station_plots
from reports.latex import FIELD_SYMBOLS, escape, num
from reports.report import Case, Section


class StationResults(Section):
    title = "Flow state along the engine"
    label = "stations"

    def __init__(self, case: Case):
        self.case = case

    def table(self) -> Table:
        columns = [(s["field"], p["unit"], p["scale"]) for p in self.case.engine["panels"] for s in p["series"]]
        header = [["Station", *(FIELD_SYMBOLS[f] for f, _, _ in columns)],
                  ["", *(f"[{escape(u)}]" if u not in ("", "-") else "[--]" for _, u, _ in columns)]]
        rows = [[escape(s["key"]), *(num(None if s[f] is None else s[f] * k) for f, _, k in columns)]
                for s in self.case.point["stations"]]
        return Table("Flow state at each station.", "flow-state", header, [Group(rows)], "c" + "r" * len(columns),
                     small=True)

    def elements(self) -> list[Element]:
        prose = Raw(r"\autoref{tab:flow-state} gives the flow state at every station and "
                    r"\autoref{fig:station-plots} shows it along the engine.")
        return [prose, self.table(), station_plots(self.case.engine, self.case.point, self.case.view.streams)]
