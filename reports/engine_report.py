"""
The engine performance report: design point, flow state, compressor and off-design sweeps, assembled from sections.
"""
from interface.gui.dashboard_view import KPIS
from reports.latex import escape, in_sentence, num, split_unit
from reports.report import Case, Report
from reports.sections.compressor import Compressor
from reports.sections.design_point import DesignPoint
from reports.sections.engine_model import EngineModel
from reports.sections.nomenclature import Nomenclature
from reports.sections.off_design import OffDesign
from reports.sections.station_results import StationResults
from reports.sweep import run_sweep

AUTHOR = "Systems Modelling Tool"


def _kpi(case: Case, key: str) -> str:
    _, unit, scale = KPIS[key]
    return rf"{num(case.snap.result[key] * scale, 3)}~{escape(unit)}"


def _abstract(case: Case, sweep_keys: list[str]) -> str:
    v = case.values
    text = (rf"This report documents the design-point performance of the {escape(case.view.title.lower())} at "
            rf"a flight Mach number of {num(v['M_0'], 3)}, static temperature {num(v['T_0'], 4)}~K and static pressure "
            rf"{num(v['P_0'], 4)}~kPa. The engine delivers a net thrust of {_kpi(case, 'F_total')}")
    text += rf" at a TSFC of {_kpi(case, 'TSFC')}." if "TSFC" in case.snap.result else "."
    text += (" The flow state at every station, the sizing of the axial compressor"
             + (" and the off-design performance against " + ", ".join(
                 escape(in_sentence(split_unit(i.label)[0])) for g in case.view.inputs.values() for i in g if i.key in sweep_keys)
                if sweep_keys else "")
             + " are reported.")
    return text


def engine_report(case: Case, sweep_keys: list[str], n_points: int = 25) -> Report:
    sweeps = [run_sweep(case, key, n_points) for key in sweep_keys]
    sections = [Nomenclature(case), EngineModel(case), DesignPoint(case), StationResults(case), Compressor(case)]
    if sweeps:
        sections.append(OffDesign(case, sweeps))
    return Report(
        title=escape(case.view.title),
        subtitle="Design-point and off-design performance",
        author=AUTHOR,
        abstract=_abstract(case, sweep_keys),
        sections=sections)
