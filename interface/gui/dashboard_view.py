"""
What every engine dashboard shares, whatever draws the page (the web frontends via interface/api/): how an engine
describes itself (EngineView), its inputs, the tiles as data, and the Plotly flow figure (engine on top, plots underneath).
"""
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from graphics.engine_illustration import FREESTREAM_LENGTH, LABEL_ROOM, EngineLayout, draw_engine
from graphics.theme import style
from plotting.station_profiles import PANELS, add_station_profiles
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing

ALL_PANELS = list(PANELS)
DEFAULT_PANELS = ["Temperature", "Pressure", "Velocity", "Mass flow"]

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

PLOT_WIDTH = 1300      # [px] typical width of the plot area - sets the engine row height so the drawing fills it
PANEL_HEIGHT = 190      # [px]
NAME_ROOM = 0.25        # [m] station names go on the axis only if neighbouring stations are at least this far apart

FLOW_NOTE = (
    "The engine is drawn to scale where the model has geometry (compressor annulus and blade rows, reactor length, "
    "fan radii, nozzle exit areas); the other lengths are nominal. Bright rows are rotors, dim rows are stators. "
    "Colour is total temperature, interpolated linearly between stations. Gaps in a curve are stations where the "
    "model does not compute that quantity.")


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
    geometry: AxialCompressorGeometry
    sizing: AxialCompressorSizing
    subtitle: str
    error: str | None = None        # set when the point is not physical; the page shows it instead of the plots


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


FLIGHT_INPUTS = [
    Input("M_0", "Mach number M₀", 0.80, 0.10, 0.95, 0.01),
    Input("T_0", "Static temperature T₀ [K]", 250.0, 200.0, 320.0, 1.0),
    Input("P_0", "Static pressure P₀ [kPa]", 100.0, 20.0, 110.0, 1.0)]


def flight_subtitle(values: dict) -> str:
    return f"T₀ {values['T_0']:g} K · P₀ {values['P_0']:g} kPa · M₀ {values['M_0']:g}"
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
        if key == "stations":
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


def flow_figure(layout: EngineLayout, stations: dict, streams: dict[str, list[str]], panels: list[str],
                station_names: dict[str, str] | None = None) -> go.Figure:
    """Engine cross-section on top, one plot per panel underneath, all on the same axial axis."""
    x_range = [-FREESTREAM_LENGTH - 0.12, layout.x_end + FREESTREAM_LENGTH + 0.05]
    engine_height = round(PLOT_WIDTH * 2 * (layout.r_max + LABEL_ROOM) / (x_range[1] - x_range[0]))
    height = engine_height + PANEL_HEIGHT * len(panels) + 150
    fig = make_subplots(
        rows=1 + len(panels), cols=1, shared_xaxes=True, vertical_spacing=24 / height,
        row_heights=[engine_height] + [PANEL_HEIGHT] * len(panels))

    # Under the plots, ticks (and so the vertical gridlines) sit on the stations
    positions = sorted(set(layout.station_x.values()))
    named = station_names is not None and min(np.diff(positions)) >= NAME_ROOM
    ticktext = []
    for x in positions:
        keys = [k for k, x_k in layout.station_x.items() if x_k == x]
        ticktext.append(f"<b>{' / '.join(keys)}</b>" + (f"<br>{station_names[keys[0]]}" if named else ""))
    fig.update_xaxes(tickvals=positions, ticktext=ticktext, range=x_range)

    draw_engine(fig, layout, stations)
    add_station_profiles(fig, stations, layout.station_x, streams, panels, first_row=2)

    style(fig, height)
    fig.update_layout(
        hovermode="x unified", hoversubplots="axis", margin=dict(t=100, b=60, r=90),
        legend=dict(x=1, xanchor="right", y=1 + 55 / (height - 160)))
    return fig

