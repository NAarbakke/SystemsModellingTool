"""
Static engine dashboard: architecture schematic + FlowState at every station, written to one HTML file.

Engine-agnostic: takes any engine's run_point() result ({"stations": {key: FlowState}, <scalars>}) plus the
flow path of each stream as alternating station / component names:
    streams = {"Core": ["0", "Inlet", "1", "Fan", "2", ...], "Bypass": ["2", "Splitter", "25b", ...]}

Run from the repo root:  python -m graphics.engine_dashboard
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
from plotly.subplots import make_subplots

# FlowState field -> (label, display unit, SI -> display scale)
FIELDS = {
    "Tt": ("Tt", "K", 1.0),
    "Pt": ("Pt", "kPa", 1e-3),
    "T": ("T", "K", 1.0),
    "P": ("P", "kPa", 1e-3),
    "M": ("M", "-", 1.0),
    "V": ("V", "m/s", 1.0),
    "rho": ("ρ", "kg/m³", 1.0),
    "m_dot": ("ṁ", "kg/s", 1.0)}

# run_point() scalar -> (label, display unit, SI -> display scale); unknown keys are shown raw
KPIS = {
    "F_total": ("Net thrust", "kN", 1e-3),
    "F_core": ("Core thrust", "kN", 1e-3),
    "F_bypass": ("Bypass thrust", "kN", 1e-3),
    "Power": ("Thrust power", "MW", 1e-6),
    "Q_reactor": ("Reactor power", "MW", 1e-6),
    "power_density": ("Core power density", "GW/m³", 1e-9),
    "heat_flux": ("Rod heat flux", "MW/m²", 1e-6),
    "within_limits": ("Reactor limits", "", 1.0)}

PLOTTED = ["Tt", "Pt", "m_dot", "V"]
STREAM_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a"]      # categorical slots 1-3, validated all-pairs
HEAT = [[i / 10, c] for i, c in enumerate(sample_colorscale("YlOrRd", [0.15 + 0.085 * i for i in range(11)]))]  # skips near-white end
INK, INK_2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

# ponytail: light theme only, plotly figures can't read CSS vars; add a dark template if it's ever needed
CSS = """
body { margin: 0; padding: 24px 32px; background: #f9f9f7; color: #0b0b0b; font: 14px system-ui, -apple-system, "Segoe UI", sans-serif; }
h1 { font-size: 20px; margin: 0; }
h2 { font-size: 15px; margin: 28px 0 8px; color: #52514e; }
.sub { color: #52514e; margin: 4px 0 20px; }
.kpis { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
.kpi, .card { background: #fcfcfb; border: 1px solid rgba(11, 11, 11, .1); border-radius: 8px; }
.kpi { padding: 12px 14px; }
.kpi .label { color: #52514e; font-size: 12px; }
.kpi .value { font-size: 22px; margin-top: 4px; }
.kpi small { font-size: 13px; color: #898781; }
.ok { color: #006300; } .bad { color: #d03b3b; }
.card { padding: 8px; overflow-x: auto; }
table.stations { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
.stations th, .stations td { padding: 6px 10px; text-align: right; border-bottom: 1px solid #e1e0d9; white-space: nowrap; }
.stations th:nth-child(-n+2), .stations td:nth-child(-n+2) { text-align: left; }
"""


def _layout(streams: dict[str, list[str]]) -> dict[str, tuple[int, int]]:
    """Station -> (x, row). x counts along its stream; a branch starts at its parent station's x. First appearance wins."""
    pos = {}
    for row, path in enumerate(streams.values()):
        x_0 = pos[path[0]][0] if path[0] in pos else 0
        for i, key in enumerate(path[::2]):
            pos.setdefault(key, (x_0 + i, row))
    return pos


def _describe(streams: dict[str, list[str]]) -> dict[str, str]:
    """Station -> 'upstream component → downstream component'."""
    desc = {}
    for path in streams.values():
        for i in range(0, len(path), 2):
            upstream = path[i - 1] if i else "Freestream"
            downstream = path[i + 1] if i + 1 < len(path) else "Atmosphere"
            desc.setdefault(path[i], f"{upstream} → {downstream}")
    return desc


def _state_text(key, state) -> str:
    lines = [f"{lab} {v * s:,.4g} {u}" for f, (lab, u, s) in FIELDS.items() if (v := getattr(state, f)) is not None]
    return f"<b>Station {key}</b><br>" + "<br>".join(lines)


def _style(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=60, r=20, t=40, b=30),
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(family=FONT, color=INK, size=12),
        hoverlabel=dict(bgcolor=SURFACE, font=dict(family=FONT, color=INK)))
    return fig


def _schematic(stations: dict, streams: dict[str, list[str]], pos: dict) -> go.Figure:
    fig = go.Figure()
    Tt_lo = min(s.Tt for s in stations.values())
    Tt_hi = max(s.Tt for s in stations.values())
    box_x, box_y, box_Tt, box_text = [], [], [], []

    for row, (colour, path) in enumerate(zip(STREAM_COLOURS, streams.values())):
        for key_in, component, key_out in zip(path[0::2], path[1::2], path[2::2]):
            (x_in, y_in), (x_out, y_out) = pos[key_in], pos[key_out]
            state_in, state_out = stations[key_in], stations[key_out]
            t = (state_out.Tt - Tt_lo) / ((Tt_hi - Tt_lo) or 1.0)

            # Flow path first, so the component box sits on top of it. Elbows (V) route a branch/merge through the station gap.
            fig.add_shape(
                type="path", path=f"M {x_in},{y_in} V {row} H {x_out} V {y_out}", layer="below",
                line=dict(color=colour, width=2))
            fig.add_shape(
                type="rect", x0=x_in + 0.2, x1=x_out - 0.2, y0=row - 0.28, y1=row + 0.28, layer="below",
                fillcolor=sample_colorscale(HEAT, [t])[0], line=dict(color=GRID, width=1))
            fig.add_annotation(
                x=(x_in + x_out) / 2, y=row, text=component, showarrow=False,
                font=dict(color="white" if t > 0.55 else INK))

            box_x.append((x_in + x_out) / 2)
            box_y.append(row)
            box_Tt.append(state_out.Tt)
            box_text.append(
                f"<b>{component}</b><br>"
                f"Tt {state_in.Tt:,.4g} → {state_out.Tt:,.4g} K<br>"
                f"Pt {state_in.Pt * 1e-3:,.4g} → {state_out.Pt * 1e-3:,.4g} kPa")

    # Invisible hit targets over the boxes: component hover + the Tt colour bar
    fig.add_trace(go.Scatter(
        x=box_x, y=box_y, mode="markers", hovertext=box_text, hoverinfo="text", showlegend=False,
        marker=dict(
            size=44, symbol="square", opacity=0, color=box_Tt, colorscale=HEAT, cmin=Tt_lo, cmax=Tt_hi,
            showscale=True, colorbar=dict(title="Tt exit [K]", thickness=10, outlinewidth=0))))

    keys = list(pos)
    fig.add_trace(go.Scatter(
        x=[pos[k][0] for k in keys], y=[pos[k][1] for k in keys], mode="markers+text",
        text=keys, textposition="top center", textfont=dict(color=INK_2, size=11),
        hovertext=[_state_text(k, stations[k]) for k in keys], hoverinfo="text", showlegend=False,
        marker=dict(size=9, color=SURFACE, line=dict(color=INK, width=1.5))))

    fig.update_xaxes(visible=False, range=[-0.5, max(x for x, _ in pos.values()) + 0.5])
    fig.update_yaxes(
        tickvals=list(range(len(streams))), ticktext=list(streams), range=[-0.6, len(streams) - 0.4],
        showgrid=False, zeroline=False, fixedrange=True)
    return _style(fig, height=130 * len(streams) + 70)


def _profiles(stations: dict, streams: dict[str, list[str]], pos: dict) -> go.Figure:
    titles = [f"{FIELDS[f][0]} [{FIELDS[f][1]}]" for f in PLOTTED]
    fig = make_subplots(rows=2, cols=2, subplot_titles=titles, vertical_spacing=0.16, horizontal_spacing=0.08)

    for colour, (name, path) in zip(STREAM_COLOURS, streams.items()):
        keys = path[::2]
        for i, field in enumerate(PLOTTED):
            _, unit, scale = FIELDS[field]
            # None (not computed by the model at that station) -> gap, never an interpolated line
            y = [None if (v := getattr(stations[k], field)) is None else v * scale for k in keys]
            fig.add_trace(go.Scatter(
                x=[pos[k][0] for k in keys], y=y, customdata=keys, name=name,
                mode="lines+markers", legendgroup=name, showlegend=i == 0,
                line=dict(color=colour, width=2), marker=dict(size=8, line=dict(color=SURFACE, width=2)),
                hovertemplate=f"Station %{{customdata}}: %{{y:,.4g}} {unit}<extra>{name}</extra>"),
                row=i // 2 + 1, col=i % 2 + 1)

    ticks = {}
    for key, (x, _) in pos.items():
        ticks.setdefault(x, []).append(key)
    fig.update_xaxes(
        tickvals=list(ticks), ticktext=[" / ".join(k) for k in ticks.values()],
        showgrid=False, linecolor=GRID, ticks="", tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    fig.update_annotations(font=dict(size=13, color=INK_2))
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.12, x=0))
    return _style(fig, height=560)


def _station_table(stations: dict, streams: dict[str, list[str]]) -> str:
    desc = _describe(streams)
    rows = [
        {"Station": key, "Between": desc.get(key, ""),
         **{f"{lab} [{u}]": (None if (v := getattr(state, f)) is None else v * s) for f, (lab, u, s) in FIELDS.items()}}
        for key, state in stations.items()]
    return pd.DataFrame(rows).to_html(index=False, na_rep="—", float_format=lambda v: f"{v:,.4g}", classes="stations", border=0)


def _kpi_tiles(result: dict) -> str:
    tiles = []
    for key, value in result.items():
        if key == "stations":
            continue
        label, unit, scale = KPIS.get(key, (key, "", 1.0))
        if isinstance(value, (bool, np.bool_)):
            text = '<span class="ok">✓ Within</span>' if value else '<span class="bad">✕ Exceeded</span>'
        else:
            text = f"{value * scale:,.4g} <small>{unit}</small>"
        tiles.append(f'<div class="kpi"><div class="label">{label}</div><div class="value">{text}</div></div>')
    return "".join(tiles)


def build_engine_dashboard(result: dict, streams: dict[str, list[str]], title: str, save_path: str | Path, subtitle: str = "") -> Path:
    stations = result["stations"]
    pos = _layout(streams)
    # ponytail: plotly.js from CDN keeps the file ~100 kB but needs internet; include_plotlyjs=True for offline (+4.6 MB)
    schematic = _schematic(stations, streams, pos).to_html(full_html=False, include_plotlyjs="cdn", config={"displaylogo": False})
    profiles = _profiles(stations, streams, pos).to_html(full_html=False, include_plotlyjs=False, config={"displaylogo": False})

    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style></head>
<body>
<h1>{title}</h1><p class="sub">{subtitle}</p>
<div class="kpis">{_kpi_tiles(result)}</div>
<h2>Architecture — hover a station or component</h2><div class="card">{schematic}</div>
<h2>Station profiles</h2><div class="card">{profiles}</div>
<h2>Station data</h2><div class="card">{_station_table(stations, streams)}</div>
</body></html>"""

    save_path = Path(save_path)
    save_path.write_text(page, encoding="utf-8")
    return save_path


if __name__ == "__main__":
    from subsystems.propulsion.motors.helpers.gas_model import GasModel
    from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_nuclear_fuel_turbofan import SingleSpoolOpenCycleNuclearTurbofan
    from specifications.SKYF.engine import specs_open_cycle_nuclear as specs

    # Same cruise point as main_open_cycle_nuclear_engine.py
    T_atm = 250         # [K]
    P_atm = 100000      # [Pa]
    M_cruise = 0.8

    engine = SingleSpoolOpenCycleNuclearTurbofan(GasModel(), specs, P_atm)
    result = engine.run_point(T_0=T_atm, P_0=P_atm, M_0=M_cruise)

    # Station numbering follows run_point()
    streams = {
        "Core": ["0", "Inlet", "1", "Fan", "2", "Splitter", "25a", "Compressor", "3", "Reactor", "4", "Turbine", "5", "Nozzle", "6"],
        "Bypass": ["2", "Splitter", "25b", "Duct", "7", "Nozzle", "8"]}

    path = build_engine_dashboard(
        result, streams,
        title="Single-spool open-cycle nuclear turbofan",
        save_path=Path(__file__).with_name("single_spool_open_cycle_nuclear_turbofan.html"),
        subtitle=f"T0 {T_atm} K · P0 {P_atm / 1e3:g} kPa · M0 {M_cruise}")
    print(f"Dashboard written to {path}")
