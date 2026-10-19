"""
Symbols, subscripts and abbreviations used in the report.
"""
from interface.gui.dashboard_view import PANELS
from reports.elements.element import Element
from reports.elements.table import Group, Table
from reports.latex import FIELD_SYMBOLS, escape
from reports.report import Case, Section

PERFORMANCE_SYMBOLS = [
    (r"$A_e$", "Nozzle exit area", r"m$^2$"),
    (r"$F$", "Net thrust", "kN"),
    (r"$\dot{m}_f$", "Fuel mass flow", "kg/s"),
    ("TSFC", "Thrust-specific fuel consumption", r"g/(kN$\cdot$s)")]

SUBSCRIPTS = [
    ("$t$", "Total (stagnation) quantity"),
    ("$e$", "Nozzle exit"),
    ("0, 1, \\ldots", "Station, see \\autoref{tab:stations}")]


class Nomenclature(Section):
    title = "Nomenclature"
    label = "nomenclature"
    numbered = False

    def __init__(self, case: Case):
        self.case = case

    def elements(self) -> list[Element]:
        flow = []
        for name, (unit, _, series) in PANELS.items():
            for field, _, kind in series:
                what = f"{kind} {name.lower()}" if kind else name
                flow.append([FIELD_SYMBOLS[field], escape(what), escape(unit) if unit != "-" else "--"])
        return [Table(
            "Symbols. Units are those used in the tables and figures.", "nomenclature",
            [["Symbol", "Description", "Unit"]],
            [Group(flow, "Flow state"), Group([list(r) for r in PERFORMANCE_SYMBOLS], "Performance"),
             Group([[s, d, ""] for s, d in SUBSCRIPTS], "Subscripts")],
            "llr")]
