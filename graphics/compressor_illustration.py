"""
The sized axial compressor (AxialCompressor.compute_geometry()) as a to-scale half cross-section:
annulus, blade rows and stage boundaries, with axes in metres. Hover a stage for its numbers.
"""
import numpy as np
import plotly.graph_objects as go

from graphics.core_layout import compressor_rows
from graphics.engine_illustration import CASING_THICKNESS, ROTOR, STATOR, band
from graphics.theme import AXIS, BODY, CASING, INK_2, MUTED, style
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing

ANNULUS = "rgba(57, 135, 229, 0.22)"    # gas path, tinted with the series blue


def compressor_figure(geometry: AxialCompressorGeometry, sizing: AxialCompressorSizing) -> go.Figure:
    """x = 0 at the compressor face."""
    x_stage, rotors, stators = compressor_rows(geometry, sizing, x_face=0.0)
    x = np.array([0.0, *x_stage, sizing.L])
    r_hub = np.array([sizing.r_hub_stage[0], *sizing.r_hub_stage, sizing.r_hub_stage[-1], sizing.r_hub_stage[-1]])
    r_tip = np.array([sizing.r_tip_stage[0], *sizing.r_tip_stage, sizing.r_tip_stage[-1], sizing.r_tip_stage[-1]])
    r_max = float(r_tip.max()) + CASING_THICKNESS
    fig = go.Figure()

    def add(path, fill, line=None):
        fig.add_shape(type="path", path=path, fillcolor=fill, line=dict(color=line or fill, width=1), layer="below")

    add(band(x, r_hub, r_tip, mirror=False), ANNULUS)
    for rows, fill in ((stators, STATOR), (rotors, ROTOR)):
        for x_0, x_1 in rows:
            ends = [x_0, x_1]
            add(band(ends, np.interp(ends, x, r_hub), np.interp(ends, x, r_tip), mirror=False), fill)
    add(band(x, np.zeros_like(x), r_hub, mirror=False), BODY, line=CASING)
    add(band(x, r_tip, r_tip + CASING_THICKNESS, mirror=False), CASING)

    # Stage boundaries, each stage labelled with its length
    for x_s in x_stage:
        fig.add_shape(type="line", x0=x_s, x1=x_s, y0=0, y1=r_max + 0.02, line=dict(color=AXIS, width=1), layer="below")
    spans = [("IGV", 0.0, x_stage[0])]
    spans += [(f"Stage {i + 1}", x_stage[i], x_stage[i + 1]) for i in range(sizing.n_stages)]
    spans += [("EGV", x_stage[-1], sizing.L)]
    for name, x_0, x_1 in spans:
        fig.add_annotation(
            x=0.5 * (x_0 + x_1), y=r_max + 0.02, yanchor="bottom", showarrow=False,
            text=f"{name}<br><b>{(x_1 - x_0) * 1e3:.0f} mm</b>", font=dict(color=INK_2, size=11))

    # One hover target per stage
    fig.add_trace(go.Scatter(
        x=[0.5 * (x_stage[i] + x_stage[i + 1]) for i in range(sizing.n_stages)],
        y=[0.5 * (r_h + r_t) for r_h, r_t in zip(sizing.r_hub_stage, sizing.r_tip_stage)],
        customdata=[
            (i + 1, L * 1e3, r_h, r_t, r_t - r_h)
            for i, (L, r_h, r_t) in enumerate(zip(sizing.L_stage, sizing.r_hub_stage, sizing.r_tip_stage))],
        mode="markers", marker=dict(size=40, opacity=0), showlegend=False,
        hovertemplate=(
            "<b>Stage %{customdata[0]}</b><br>Length %{customdata[1]:.1f} mm<br>Hub radius %{customdata[2]:.3f} m<br>"
            "Tip radius %{customdata[3]:.3f} m<br>Blade span %{customdata[4]:.3f} m<extra></extra>")))

    # Legend for the blade rows
    for name, fill in (("Rotor", ROTOR), ("Stator / guide vane", STATOR)):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=name, marker=dict(symbol="square", size=11, color=fill)))

    fig.update_xaxes(
        title=dict(text="Axial position from the compressor face [m]", font=dict(color=MUTED, size=12)),
        range=[-0.04, sizing.L + 0.04], showgrid=False, ticks="outside", tickcolor=AXIS)
    fig.update_yaxes(
        title=dict(text="Radius [m]", font=dict(color=MUTED, size=12)), range=[0, r_max + 0.09],
        scaleanchor="x", scaleratio=1, showgrid=False, ticks="outside", tickcolor=AXIS, fixedrange=True)
    return style(fig, height=440).update_layout(margin=dict(t=40), legend=dict(x=1, xanchor="right"))
