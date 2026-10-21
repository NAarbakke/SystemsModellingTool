"""
What every engine dashboard shares, whatever draws the page (the web dashboard via interface/api/): how an engine
describes itself (EngineView), its inputs, the station plot panels and the tiles, all as data.
"""
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from graphics.engine_illustration import EngineLayout
from specifications.SKYF.flight_state.cruise import h_cruise, V_cruise
from specifications.SKYF.initial_conditions.atmosphere import isa
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.helpers.gas_model import GasModel

# Station plots: FlowState quantities against station, one panel per quantity. Total and static values of the
# same quantity share a panel.
# panel -> (display unit, SI -> display scale, [(FlowState field, symbol, "Total" / "Static" / None)])
PANELS = {
    "Temperature": ("K", 1.0, [("Tt", "Tt", "Total"), ("T", "T", "Static")]),
    "Pressure": ("kPa", 1e-3, [("Pt", "Pt", "Total"), ("P", "P", "Static")]),
    "Density": ("kg/m³", 1.0, [("rho_t", "ρt", "Total"), ("rho", "ρ", "Static")]),
    "Velocity": ("m/s", 1.0, [("V", "V", None)]),
    "Mach number": ("-", 1.0, [("M", "M", None)]),
    "Mass flow": ("kg/s", 1.0, [("m_dot", "ṁ", None)])}

# run_point() scalar -> (label, display unit, SI -> display scale); unknown keys are shown raw
KPIS = {
    "F_total": ("Net thrust", "kN", 1e-3),
    "F_core": ("Core thrust", "kN", 1e-3),
    "F_bypass": ("Bypass thrust", "kN", 1e-3),
    "Power": ("Thrust power", "MW", 1e-6),
    "TSFC": ("TSFC", "g/(kN·s)", 1e6),
    "m_dot_fuel": ("Fuel flow", "kg/s", 1.0),
    "Q_reactor": ("Reactor thermal power", "MW", 1e-6),
    "power_density": ("Core power density", "GW/m³", 1e-9),
    "heat_flux": ("Rod heat flux", "MW/m²", 1e-6),
    "within_limits": ("Reactor limits", "", 1.0)}

#---- How an engine describes itself to a dashboard ----#
@dataclass(frozen=True)
class Input:
    """One sidebar control. A slider unless options is given, then a choice (options: value -> label)."""
    key: str
    label: str
    default: Any
    lo: float = 0.0
    hi: float = 1.0
    step: float = 0.01
    options: dict[Any, str] | None = None


@dataclass
class Snapshot:
    """One evaluated operating point: everything a page shows."""
    result: dict
    layout: EngineLayout
    subtitle: str
    geometry: AxialCompressorGeometry | None = None     # axial compressors only: sized at the operating point
    sizing: AxialCompressorSizing | None = None
    error: str | None = None        # set when the point is not physical; the page shows it instead of the plots


NO_EXPANSION = ("No valid operating point: the nozzle total pressure is below ambient, so the flow cannot expand. "
                "Lower the pressure ratio or raise the turbine entry temperature.")


@dataclass(frozen=True)
class EngineView:
    title: str
    stations: dict[str, str]                        # station -> name, in run_point() numbering
    streams: dict[str, list[str]]                   # stream -> its stations, upstream to downstream
    inputs: dict[str, list[Input]]                  # sidebar group -> its inputs
    evaluate: Callable[[dict[str, Any]], Snapshot]  # input values (by key) -> operating point

    @property
    def defaults(self) -> dict[str, Any]:
        return {i.key: i.default for group in self.inputs.values() for i in group}

    def check(self, values: dict) -> dict:
        """Input values by key (e.g. typed on a command line), checked against the inputs; numbers as float.
        Raises ValueError."""
        inputs = {i.key: i for group in self.inputs.values() for i in group}
        out = {}
        for key, value in values.items():
            if key not in inputs:
                raise ValueError(f"Unknown input '{key}'. Inputs: {', '.join(inputs)}")
            inp = inputs[key]
            if inp.options:
                if value not in inp.options:
                    raise ValueError(f"{key} must be one of: {', '.join(inp.options)}")
                out[key] = value
            else:
                try:
                    out[key] = float(value)
                except (TypeError, ValueError):
                    raise ValueError(f"{key} must be a number, got '{value}'") from None
        return out


def freestream(gas: GasModel) -> dict[str, float]:
    """Fixed SKYF cruise flight state (altitude, airspeed) -> run_point() freestream (T_0, P_0, M_0), through the ISA."""
    atmosphere = isa.conditions(h_cruise)
    return {"T_0": atmosphere.T_0, "P_0": atmosphere.P_0, "M_0": V_cruise / atmosphere.a_0(gas)}


def flight_subtitle(flow: dict[str, float]) -> str:
    return (f"h₀ {h_cruise:g} m · V₀ {V_cruise:g} m/s · "
            f"T₀ {flow['T_0']:.4g} K · P₀ {flow['P_0'] * 1e-3:.4g} kPa · M₀ {flow['M_0']:.3g}")
#-------------------------------------------------------#


#---- Tiles as data: each frontend renders them its own way ----#
@dataclass(frozen=True)
class Tile:
    label: str
    value: str
    unit: str = ""
    status: str | None = None       # "good" / "critical" colours the value
    hero: bool = False              # double width, large


def performance_tiles(result: dict) -> list[Tile]:
    tiles = []
    for key, value in result.items():
        if not isinstance(value, (int, float, np.number, np.bool_)):     # stations, component results (e.g. hx_result)
            continue
        label, unit, scale = KPIS.get(key, (key, "", 1.0))
        if isinstance(value, (bool, np.bool_)):
            tiles.append(Tile(label, "Within" if value else "Exceeded", status="good" if value else "critical"))
        else:
            tiles.append(Tile(label, f"{value * scale:,.4g}", unit, hero=key == "F_total"))
    return tiles


def sizing_tiles(sizing: AxialCompressorSizing) -> list[Tile]:
    return [
        Tile("Stages", f"{sizing.n_stages}"),
        Tile("Compressor length", f"{sizing.L:,.3g}", "m"),
        Tile("Exit hub radius", f"{sizing.r_hub_stage[-1]:,.3g}", "m"),
        Tile("Exit tip radius", f"{sizing.r_tip_stage[-1]:,.3g}", "m")]
#---------------------------------------------------------------------#
