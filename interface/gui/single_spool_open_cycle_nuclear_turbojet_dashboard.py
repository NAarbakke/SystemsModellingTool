"""
Dynamic turbojet dashboard: change the operating point or the design in the sidebar and everything recomputes.

Run from the repo root:  .venv/Scripts/python -m streamlit run interface/gui/single_spool_open_cycle_nuclear_turbojet_dashboard.py
"""
from dataclasses import replace

import numpy as np
import streamlit as st

from graphics.compressor_illustration import compressor_figure
from graphics.turbojet_layout import turbojet_layout
from interface.gui.dashboard_view import ALL_PANELS, CSS, FLOW_NOTE, flow_figure, performance_tiles, sizing_tiles
from interface.gui.single_spool_open_cycle_nuclear_turbojet_view import STATIONS, STREAMS, TITLE, run_turbojet
from specifications.SKYF.engine import specs_open_cycle_nuclear_turbojet as base
from subsystems.propulsion.motors.components.compressors.annulus_type import AnnulusType

PLOTLY_CONFIG = {"displaylogo": False}

st.set_page_config(page_title=TITLE, layout="wide")
st.html(f"<style>{CSS}</style>")

# ---- Inputs: defaults are the SKYF specification ----
with st.sidebar:
    st.header("Flight condition")
    M_0 = st.slider("Mach number M₀", 0.10, 0.95, 0.80, 0.01)
    T_0 = st.slider("Static temperature T₀ [K]", 200.0, 320.0, 250.0, 1.0)
    P_0 = st.slider("Static pressure P₀ [kPa]", 20.0, 110.0, 100.0, 1.0) * 1e3

    st.header("Compressor")
    PR = st.slider("Pressure ratio", 1.2, 12.0, base.compressor.PR, 0.1)
    eta_poly = st.slider("Polytropic efficiency", 0.80, 0.95, base.compressor.eta_poly, 0.01)
    psi = st.slider("Stage loading ψ", 0.20, 0.50, base.compressor.psi, 0.01)
    U_tip = st.slider("Tip speed [m/s]", 250.0, 500.0, base.compressor.U_tip, 10.0)
    r_tip = st.slider("Inlet tip radius [m]", 0.15, 0.60, base.compressor_geometry.r_tip, 0.01)
    hub_to_tip = st.slider("Inlet hub-to-tip ratio", 0.30, 0.80, base.compressor_geometry.hub_to_tip, 0.01)
    annulus_type = st.selectbox(
        "Annulus", list(AnnulusType), index=list(AnnulusType).index(base.compressor_geometry.annulus_type),
        format_func=lambda a: a.name.replace("_", " ").capitalize())

    st.header("Reactor")
    T_tet = st.slider("Turbine entry temperature [K]", 800.0, 1800.0, base.reactor.T_tet, 10.0)

    st.header("Nozzle")
    A_exit = st.slider("Exit area [m²]", 0.05, 0.60, base.nozzle.A_exit, 0.01)

specs = replace(
    base,
    compressor=replace(base.compressor, PR=PR, eta_poly=eta_poly, psi=psi, U_tip=U_tip),
    compressor_geometry=replace(base.compressor_geometry, r_tip=r_tip, r_hub=hub_to_tip * r_tip, annulus_type=annulus_type),
    reactor=replace(base.reactor, T_tet=T_tet),
    nozzle=replace(base.nozzle, A_exit=A_exit))

result, sizing = run_turbojet(specs, T_0, P_0, M_0)

# ---- Page ----
st.title(TITLE)
st.caption(f"T₀ {T_0:g} K · P₀ {P_0 / 1e3:g} kPa · M₀ {M_0:g}")

if not np.isfinite(result["F_total"]):
    st.error("No valid operating point: the nozzle total pressure is below ambient, so the flow cannot expand. "
             "Lower the pressure ratio or raise the turbine entry temperature.")
    st.stop()

st.html(performance_tiles(result))

st.subheader("Flow through the engine")
panels = st.pills("Quantities", ALL_PANELS, selection_mode="multi", default=["Temperature", "Pressure", "Velocity", "Mass flow"])
panels = [p for p in ALL_PANELS if p in panels]     # keep the fixed order whatever the click order
flow = flow_figure(turbojet_layout(specs, sizing), result["stations"], STREAMS, panels, STATIONS)
st.plotly_chart(flow, theme=None, width="stretch", config=PLOTLY_CONFIG)
st.caption(FLOW_NOTE)

st.subheader("Compressor sizing")
st.html(sizing_tiles(sizing))
st.plotly_chart(compressor_figure(specs.compressor_geometry, sizing), theme=None, width="stretch", config=PLOTLY_CONFIG)
