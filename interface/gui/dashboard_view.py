"""
What every engine dashboard shares, dynamic or static: the flow figure (engine on top, plots underneath),
the tiles, the page styling and the static HTML page.
"""
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from graphics.compressor_illustration import compressor_figure
from graphics.engine_illustration import FREESTREAM_LENGTH, LABEL_ROOM, EngineLayout, draw_engine
from graphics.theme import BORDER, CRITICAL, FONT, GOOD, INK, INK_2, MUTED, PAGE, SURFACE, style
from plotting.station_profiles import PANELS, add_station_profiles
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing

ALL_PANELS = list(PANELS)

# run_point() scalar -> (label, display unit, SI -> display scale); unknown keys are shown raw
KPIS = {
    "F_total": ("Net thrust", "kN", 1e-3),
    "F_core": ("Core thrust", "kN", 1e-3),
    "F_bypass": ("Bypass thrust", "kN", 1e-3),
    "Power": ("Thrust power", "MW", 1e-6),
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

CSS = f"""
.tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; font-family: {FONT}; }}
.tile {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px; padding: 14px 16px; }}
.tile .label {{ color: {INK_2}; font-size: 12px; letter-spacing: .02em; }}
.tile .value {{ color: {INK}; font-size: 24px; font-weight: 600; margin-top: 6px; line-height: 1.1; }}
.tile .value small {{ color: {MUTED}; font-size: 13px; font-weight: 400; }}
.tile.hero {{ grid-column: span 2; background: linear-gradient(135deg, #1f2a3a, {SURFACE} 70%); }}
.tile.hero .value {{ font-size: 40px; }}
.tile .good {{ color: {GOOD}; }} .tile .critical {{ color: {CRITICAL}; }}
"""

PAGE_CSS = f"""
body {{ margin: 0; padding: 28px 36px 48px; background: {PAGE}; color: {INK}; font: 14px {FONT}; }}
h1 {{ font-size: 24px; margin: 0; }}
h2 {{ font-size: 15px; font-weight: 600; margin: 36px 0 12px; color: {INK_2}; }}
p {{ color: {INK_2}; margin: 6px 0 22px; }}
p.note {{ font-size: 12px; margin: 10px 0 0; max-width: 110ch; }}
.card {{ border-radius: 10px; overflow: hidden; border: 1px solid {BORDER}; }}
"""


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


def _tile(label: str, value: str, hero: bool = False) -> str:
    return f'<div class="tile{" hero" if hero else ""}"><div class="label">{label}</div><div class="value">{value}</div></div>'


def performance_tiles(result: dict) -> str:
    tiles = []
    for key, value in result.items():
        if key == "stations":
            continue
        label, unit, scale = KPIS.get(key, (key, "", 1.0))
        if isinstance(value, (bool, np.bool_)):
            text = '<span class="good">✓ Within</span>' if value else '<span class="critical">✕ Exceeded</span>'
        else:
            text = f"{value * scale:,.4g} <small>{unit}</small>"
        tiles.append(_tile(label, text, hero=key == "F_total"))
    return f'<div class="tiles">{"".join(tiles)}</div>'


def sizing_tiles(sizing: AxialCompressorSizing) -> str:
    tiles = [
        _tile("Stages", f"{sizing.n_stages}"),
        _tile("Compressor length", f"{sizing.L:,.3g} <small>m</small>"),
        _tile("Exit hub radius", f"{sizing.r_hub_stage[-1]:,.3g} <small>m</small>"),
        _tile("Exit tip radius", f"{sizing.r_tip_stage[-1]:,.3g} <small>m</small>")]
    return f'<div class="tiles">{"".join(tiles)}</div>'


def write_static_page(title: str, subtitle: str, result: dict, flow: go.Figure, geometry: AxialCompressorGeometry,
                      sizing: AxialCompressorSizing, save_path: str | Path) -> Path:
    """One operating point as a single HTML file."""
    config = {"displaylogo": False, "responsive": True}
    # plotly.js from the CDN keeps the file small but needs internet; include_plotlyjs=True for offline (+4.6 MB)
    flow_html = flow.to_html(full_html=False, include_plotlyjs="cdn", config=config)
    compressor_html = compressor_figure(geometry, sizing).to_html(full_html=False, include_plotlyjs=False, config=config)

    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title><style>{PAGE_CSS}{CSS}</style></head>
<body>
<h1>{title}</h1><p>{subtitle}</p>
{performance_tiles(result)}
<h2>Flow through the engine</h2><div class="card">{flow_html}</div>
<p class="note">{FLOW_NOTE}</p>
<h2>Compressor sizing</h2>{sizing_tiles(sizing)}<div class="card" style="margin-top: 12px">{compressor_html}</div>
</body></html>"""

    save_path = Path(save_path)
    save_path.write_text(page, encoding="utf-8")
    return save_path
