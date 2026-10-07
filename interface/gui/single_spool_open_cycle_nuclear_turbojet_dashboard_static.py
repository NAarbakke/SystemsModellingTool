"""
Static turbojet dashboard: one operating point written to a single HTML file (a snapshot to keep or send).

Run from the repo root:  .venv/Scripts/python -m interface.gui.single_spool_open_cycle_nuclear_turbojet_dashboard_static
"""
from pathlib import Path

from graphics.turbojet_layout import turbojet_layout
from interface.gui.dashboard_view import ALL_PANELS, flow_figure, write_static_page
from interface.gui.single_spool_open_cycle_nuclear_turbojet_view import STATIONS, STREAMS, TITLE, run_turbojet
from specifications.SKYF.engine import specs_open_cycle_nuclear_turbojet as specs

if __name__ == "__main__":
    # Same cruise point as main_open_cycle_nuclear_engine.py
    T_0 = 250           # [K]
    P_0 = 100000        # [Pa]
    M_0 = 0.8

    result, sizing = run_turbojet(specs, T_0, P_0, M_0)
    flow = flow_figure(turbojet_layout(specs, sizing), result["stations"], STREAMS, ALL_PANELS, STATIONS)

    path = write_static_page(
        TITLE, f"T₀ {T_0:g} K · P₀ {P_0 / 1e3:g} kPa · M₀ {M_0:g}", result, flow, specs.compressor_geometry, sizing,
        save_path=Path(__file__).with_name("single_spool_open_cycle_nuclear_turbojet_dashboard.html"))
    print(f"Dashboard written to {path}")
