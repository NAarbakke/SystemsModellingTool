"""
The axial compressor as sized at the design point: stages and annulus.
"""
from reports.elements.element import Element, Raw
from reports.elements.table import Group, Table
from reports.figures.compressor_annulus import compressor_annulus
from reports.latex import num
from reports.report import Case, Section


class Compressor(Section):
    title = "Axial compressor"
    label = "compressor"

    def __init__(self, case: Case):
        self.case = case

    def elements(self) -> list[Element]:
        comp = self.case.point["compressor"]
        stages = comp["stages"]
        prose = Raw(
            rf"The compressor is sized from the design-point flow at stations 1 and 3 to {len(stages)} "
            rf"stage{'s' if len(stages) != 1 else ''} with an overall length of \SI{{{comp['length']:.3g}}}{{\metre}} "
            r"(\autoref{tab:compressor-stages}, \autoref{fig:compressor-annulus}).")
        rows = [[str(s["n"]), num(s["length"], 3), num(s["r_hub"], 3), num(s["r_tip"], 3), num(s["r_hub"] / s["r_tip"], 3)]
                for s in stages]
        table = Table(
            "Compressor stages: axial length and annulus radii at stage entry.", "compressor-stages",
            [["Stage", "Length [m]", r"$r_\mathrm{hub}$ [m]", r"$r_\mathrm{tip}$ [m]", "Hub-to-tip [--]"]],
            [Group(rows)], "crrrr")
        return [prose, table, compressor_annulus(self.case.point)]
