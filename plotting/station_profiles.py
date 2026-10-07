"""
FlowState quantities against station, one panel per quantity, stacked so they share the engine's axial axis.
Total and static values of the same quantity share a panel; colour says which, line style says which stream.
"""
import plotly.graph_objects as go

from graphics.theme import AQUA, BLUE, INK_2, MUTED, SURFACE

TOTAL, STATIC = "Total", "Static"
COLOURS = {TOTAL: BLUE, STATIC: AQUA, None: INK_2}
DASHES = ["solid", "dot"]       # per stream, in order

# panel -> (display unit, SI -> display scale, [(FlowState field, symbol, total / static / neither)])
PANELS = {
    "Temperature": ("K", 1.0, [("Tt", "Tt", TOTAL), ("T", "T", STATIC)]),
    "Pressure": ("kPa", 1e-3, [("Pt", "Pt", TOTAL), ("P", "P", STATIC)]),
    "Density": ("kg/m³", 1.0, [("rho_t", "ρt", TOTAL), ("rho", "ρ", STATIC)]),
    "Velocity": ("m/s", 1.0, [("V", "V", None)]),
    "Mach number": ("-", 1.0, [("M", "M", None)]),
    "Mass flow": ("kg/s", 1.0, [("m_dot", "ṁ", None)])}


def add_station_profiles(fig: go.Figure, stations: dict, station_x: dict[str, float], streams: dict[str, list[str]],
                         panels: list[str], first_row: int = 1) -> go.Figure:
    """
    Add one subplot row per panel, starting at first_row. Stations sit at their axial position station_x.
    streams: stream name -> its stations, upstream to downstream, e.g. {"Core": ["0", "1", ...], "Bypass": ["2", "25b", ...]}
    """
    in_legend = set()

    for row, panel in enumerate(panels, start=first_row):
        unit, scale, series = PANELS[panel]
        for dash, (stream, keys) in zip(DASHES, streams.items()):
            suffix = f" · {stream}" if len(streams) > 1 else ""
            for field, symbol, kind in series:
                # None (not computed by the model at that station) -> gap, never an interpolated line
                y = [None if (v := getattr(stations[k], field)) is None else v * scale for k in keys]
                fig.add_trace(go.Scatter(
                    x=[station_x[k] for k in keys], y=y, name=kind or panel, mode="lines+markers",
                    legendgroup=kind, showlegend=kind is not None and kind not in in_legend,
                    line=dict(color=COLOURS[kind], width=2, dash=dash), marker=dict(size=8, line=dict(color=SURFACE, width=2)),
                    hovertemplate=f"{symbol}{suffix}  %{{y:,.4g}} {unit}<extra></extra>"),
                    row=row, col=1)
                in_legend.add(kind)
        fig.update_yaxes(title=dict(text=f"{panel} [{unit}]", font=dict(color=MUTED, size=12)), row=row, col=1)

    # Line style key, only when there is more than one stream
    if len(streams) > 1 and panels:
        for dash, stream in zip(DASHES, streams):
            fig.add_trace(go.Scatter(
                x=[None], y=[None], name=stream, mode="lines", hoverinfo="skip", line=dict(color=INK_2, width=2, dash=dash)),
                row=first_row, col=1)
    return fig
