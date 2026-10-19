"""
The design point: every input (flagging those changed from the vehicle specification) and the performance.
"""
from reports.elements.element import Element, Raw
from reports.elements.table import Group, Table
from reports.latex import escape, num, split_unit
from reports.report import Case, Section


class DesignPoint(Section):
    title = "Design point"
    label = "design-point"

    def __init__(self, case: Case):
        self.case = case

    def _value(self, item: dict) -> str:
        value = self.case.values[item["key"]]
        if "options" in item:
            return escape(next(o["label"] for o in item["options"] if o["value"] == value))
        return num(value)

    def inputs_table(self) -> Table:
        defaults = self.case.view.defaults
        groups, changed = [], False
        for group in self.case.engine["inputs"]:
            rows = []
            for item in group["items"]:
                name, unit = split_unit(item["label"])
                mark = self.case.values[item["key"]] != defaults[item["key"]]
                changed |= mark
                rows.append([escape(name) + ("$^{*}$" if mark else ""), self._value(item), escape(unit)])
            groups.append(Group(rows, escape(group["group"])))
        notes = ["$^{*}$ Changed from the vehicle specification."] if changed else []
        return Table("Design-point inputs.", "inputs", [["Parameter", "Value", "Unit"]], groups, "lrl", notes=notes)

    def performance_table(self) -> Table:
        rows = [[escape(t["label"]), escape(t["value"]), escape(t["unit"])] for t in self.case.point["kpis"]]
        return Table("Design-point performance.", "performance", [["Quantity", "Value", "Unit"]], [Group(rows)], "lrl")

    def elements(self) -> list[Element]:
        fuel = "TSFC" in self.case.snap.result
        prose = Raw(
            r"The inputs of \autoref{tab:inputs} fix the flight condition and the components. "
            r"Net thrust follows from a momentum balance over the engine, air entering at the flight velocity and "
            + ("air and fuel" if fuel else "air") + r" leaving the nozzle, with a pressure term when the nozzle is choked:"
            "\n" r"\begin{equation}" "\n"
            r"  F = \dot{m}_e V_e - \dot{m}_0 V_0 + \left(P_e - P_0\right) A_e"
            + (r", \qquad \mathrm{TSFC} = \frac{\dot{m}_f}{F}." if fuel else ".") + "\n"
            r"\end{equation}" "\n"
            r"\autoref{tab:performance} lists the resulting performance.")
        return [prose, self.inputs_table(), self.performance_table()]
