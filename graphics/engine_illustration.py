"""
Side-view cross-section of an engine, drawn to scale with axes in metres: gas paths coloured by total
temperature, solid parts, blade rows, fuel rods and station markers.

An engine describes itself as an EngineLayout (turbojet_layout.py, turbofan_layout.py); draw_engine() draws it.
"""
from dataclasses import dataclass

import numpy as np
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

from graphics.theme import AXIS, BODY, CASING, HEAT, INK, INK_2, MUTED, SURFACE

FREESTREAM_LENGTH = 0.25    # [m] station 0 sits this far ahead of the inlet lip (x = 0)
CASING_THICKNESS = 0.012    # [m] nominal
N_ROD_LINES = 7             # fuel rods drawn per half - symbolic, not the rod count
LABEL_ROOM = 0.14           # [m] space above and below the engine for station numbers and component names

ROTOR = "rgba(255, 255, 255, 0.70)"
STATOR = "rgba(255, 255, 255, 0.30)"
ROD = "rgba(255, 255, 255, 0.35)"


@dataclass
class GasPath:
    """One stream's flow annulus, sampled along the engine axis [m]."""
    stations: list[str]     # stations along it, upstream to downstream - they set its colour
    x: np.ndarray
    r_inner: np.ndarray
    r_outer: np.ndarray

    def radii(self, x) -> tuple[np.ndarray, np.ndarray]:
        return np.interp(x, self.x, self.r_inner), np.interp(x, self.x, self.r_outer)


@dataclass
class EngineLayout:
    """Where everything sits. x = 0 at the inlet lip, radii from the centreline, all in metres."""
    station_x: dict[str, float]                             # station -> axial position
    gas_paths: list[GasPath]
    solids: list[tuple[np.ndarray, np.ndarray, np.ndarray, str]]    # (x, r_low, r_high, fill colour)
    rotors: list[tuple[float, float, GasPath]]              # blade rows as (start, end, the path they span)
    stators: list[tuple[float, float, GasPath]]
    rods: tuple[float, float, GasPath]                      # fuel rod bundle
    labels: list[tuple[str, float, float | None]]           # (text, x, radius) - radius None puts it below the engine

    @property
    def x_end(self) -> float:
        return max(self.station_x.values())

    @property
    def r_max(self) -> float:
        return float(max(r_high.max() for _, _, r_high, _ in self.solids))


def gas_path(stations: list[str], x_inner, r_inner, x_outer, r_outer) -> GasPath:
    """Build a GasPath from the breakpoints of its inner and outer wall (piecewise linear)."""
    x_0, x_1 = max(x_inner[0], x_outer[0]), min(x_inner[-1], x_outer[-1])
    x = np.unique(np.concatenate([np.linspace(x_0, x_1, int(60 * (x_1 - x_0)) + 2), x_inner, x_outer]))
    return GasPath(stations, x, np.interp(x, x_inner, r_inner), np.interp(x, x_outer, r_outer))


def band(x, r_low, r_high, mirror: bool = True) -> str:
    """SVG path of the band between two radius curves, mirrored about the centreline by default."""
    def half(sign):
        pts = [*zip(x, sign * np.asarray(r_low)), *zip(x[::-1], sign * np.asarray(r_high)[::-1])]
        return "M " + " L ".join(f"{px:.4f},{py:.4f}" for px, py in pts) + " Z"
    return half(1) + " " + half(-1) if mirror else half(1)


def draw_engine(fig: go.Figure, layout: EngineLayout, stations: dict) -> go.Figure:
    """Draw the engine into the figure's first subplot (axes x / y)."""
    Tt_lo, Tt_hi = min(s.Tt for s in stations.values()), max(s.Tt for s in stations.values())
    r_max = layout.r_max
    shapes = []

    def add(path, fill, line=None):
        shapes.append(dict(type="path", path=path, xref="x", yref="y", fillcolor=fill, line=dict(color=line or fill, width=1)))

    # Station lines, behind everything
    for x_s in set(layout.station_x.values()):
        shapes.append(dict(type="line", x0=x_s, x1=x_s, y0=-r_max, y1=r_max + 0.5 * LABEL_ROOM, xref="x", yref="y", line=dict(color=AXIS, width=1)))

    # Gas paths: thin slices coloured by the local total temperature (linear between stations)
    for path in layout.gas_paths:
        Tt = np.interp(path.x, [layout.station_x[k] for k in path.stations], [stations[k].Tt for k in path.stations])
        for i in range(len(path.x) - 1):
            t = (0.5 * (Tt[i] + Tt[i + 1]) - Tt_lo) / ((Tt_hi - Tt_lo) or 1.0)
            add(band(path.x[i:i + 2], path.r_inner[i:i + 2], path.r_outer[i:i + 2]), sample_colorscale(HEAT, [t])[0])

    # Fuel rods
    x_0, x_1, path = layout.rods
    r_rods = np.linspace(*path.radii(x_0), N_ROD_LINES + 2)[1:-1]
    for r in [*r_rods, *-r_rods]:
        shapes.append(dict(type="line", x0=x_0, x1=x_1, y0=r, y1=r, xref="x", yref="y", line=dict(color=ROD, width=1.5)))

    # Blade rows span the local annulus
    for rows, fill in ((layout.stators, STATOR), (layout.rotors, ROTOR)):
        for x_0, x_1, path in rows:
            add(band([x_0, x_1], *path.radii([x_0, x_1])), fill)

    for x, r_low, r_high, fill in layout.solids:
        add(band(x, r_low, r_high), fill, line=CASING)
    fig.update_layout(shapes=[*fig.layout.shapes, *shapes])

    # Station numbers above (stations at the same position share a label), component names below or inside
    for x_s in set(layout.station_x.values()):
        keys = [k for k, x_k in layout.station_x.items() if x_k == x_s]
        fig.add_annotation(
            x=x_s, y=r_max + 0.5 * LABEL_ROOM, text=f"<b>{' / '.join(keys)}</b>", showarrow=False, xref="x", yref="y",
            font=dict(color=INK, size=12), bgcolor=SURFACE, bordercolor=AXIS, borderpad=3)
    for text, x_l, r in layout.labels:
        fig.add_annotation(
            x=x_l, y=-r_max - 0.5 * LABEL_ROOM if r is None else r, text=text, showarrow=False, xref="x", yref="y",
            font=dict(color=INK_2 if r is None else INK, size=12))

    # Flow direction: into the first gas path, out of every path that ends in the atmosphere
    starts = {p.x[0] for p in layout.gas_paths}
    arrows = [(layout.gas_paths[0], 0, -1)] + [(p, -1, 1) for p in layout.gas_paths if p.x[-1] not in starts]
    for path, end, side in arrows:
        r = 0.5 * (path.r_inner[end] + path.r_outer[end])
        x_near, x_far = path.x[end] + side * 0.03, path.x[end] + side * (FREESTREAM_LENGTH - 0.03)
        x_head, x_tail = (x_far, x_near) if side > 0 else (x_near, x_far)
        for y in (-r, r):
            fig.add_annotation(
                x=x_head, ax=x_tail, y=y, ay=y, xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5, arrowcolor=MUTED, text="")

    # Colour scale for the gas paths (an empty trace is the only way to get a colour bar next to shapes)
    y_lo, y_hi = fig.layout.yaxis.domain or (0.0, 1.0)
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers", hoverinfo="skip", showlegend=False,
        marker=dict(
            color=[Tt_lo], colorscale=HEAT, cmin=Tt_lo, cmax=Tt_hi, showscale=True,
            colorbar=dict(
                title=dict(text="Tt [K]", font=dict(color=INK_2)), thickness=8, outlinewidth=0,
                len=0.8 * (y_hi - y_lo), y=0.5 * (y_lo + y_hi), tickfont=dict(color=MUTED)))),
        row=1, col=1)

    # Axes in metres; equal scale on both so the drawing is true to shape
    step = 0.1 if r_max < 0.45 else 0.2
    ticks = np.arange(-np.floor(r_max / step), np.floor(r_max / step) + 1) * step
    fig.update_yaxes(
        title=dict(text="Radius [m]", font=dict(color=MUTED, size=12)), tickvals=ticks, ticktext=[f"{abs(t):.1f}" for t in ticks],
        scaleanchor="x", scaleratio=1, range=[-r_max - LABEL_ROOM, r_max + LABEL_ROOM],
        showgrid=False, fixedrange=True, row=1, col=1)
    fig.update_xaxes(
        title=dict(text="Axial position from the inlet lip [m]", font=dict(color=MUTED, size=12)), side="top",
        tickmode="linear", tick0=0.0, dtick=0.5, ticks="outside", tickcolor=AXIS, showticklabels=True, showgrid=False,
        row=1, col=1)
    return fig
