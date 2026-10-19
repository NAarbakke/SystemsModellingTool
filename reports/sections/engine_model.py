"""
The engine as modelled: its component chain, the stations between components and the cross-section.
"""
from reports.elements.element import Element, Raw
from reports.elements.table import Group, Table
from reports.figures.engine_section import engine_section
from reports.latex import escape, num
from reports.report import Case, Section


class EngineModel(Section):
    title = "Engine model"
    label = "engine-model"

    def __init__(self, case: Case):
        self.case = case

    def elements(self) -> list[Element]:
        point = self.case.point
        components = [label["text"] for label in point["layout"]["labels"]]
        chain = r" $\rightarrow$ ".join(escape(c) for c in components)
        prose = Raw(
            rf"The {escape(self.case.view.title.lower())} is modelled as a chain of components, each taking the flow "
            rf"state at its entry station and returning the state at its exit: {chain}. "
            r"Stations are listed in \autoref{tab:stations} and drawn to scale in \autoref{fig:engine-section}. "
            r"Every component is a one-dimensional model; the flow state at a station is the total and static "
            r"temperature and pressure, Mach number, velocity, density and mass flow.")

        rows = [[escape(s["key"]), escape(s["name"]), num(s["x"], 3)] for s in point["stations"]]
        stations = Table(
            r"Stations. Axial position $x$ from the inlet lip.", "stations",
            [["Station", "Location", r"$x$ [m]"]], [Group(rows)], "clr")
        return [prose, stations, engine_section(point)]
