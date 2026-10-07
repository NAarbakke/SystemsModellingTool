"""
Static turbofan dashboard: one operating point written to a single HTML file (a snapshot to keep or send).

Run from the repo root:  .venv/Scripts/python -m interface.gui.single_spool_open_cycle_nuclear_fuel_turbofan_dashboard_static
"""
from pathlib import Path

from graphics.turbofan_layout import turbofan_layout
from interface.gui.dashboard_view import ALL_PANELS, flow_figure, write_static_page
from specifications.SKYF.engine import specs_open_cycle_nuclear as specs
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_nuclear_fuel_turbofan import SingleSpoolOpenCycleNuclearTurbofan

TITLE = "Single-spool open-cycle nuclear turbofan"

# Station numbering follows run_point()
STREAMS = {
    "Core": ["0", "1", "2", "25a", "3", "4", "5", "6"],
    "Bypass": ["2", "25b", "7", "8"]}

if __name__ == "__main__":
    # Same cruise point as main_open_cycle_nuclear_engine.py
    T_0 = 250           # [K]
    P_0 = 100000        # [Pa]
    M_0 = 0.8

    engine = SingleSpoolOpenCycleNuclearTurbofan(GasModel(), specs, P_0)
    result = engine.run_point(T_0=T_0, P_0=P_0, M_0=M_0)
    sizing = engine.compressor.compute_geometry(result["stations"]["25a"], result["stations"]["3"])
    flow = flow_figure(turbofan_layout(specs, sizing), result["stations"], STREAMS, ALL_PANELS)

    path = write_static_page(
        TITLE, f"T₀ {T_0:g} K · P₀ {P_0 / 1e3:g} kPa · M₀ {M_0:g}", result, flow, specs.compressor_geometry, sizing,
        save_path=Path(__file__).with_name("single_spool_open_cycle_nuclear_fuel_turbofan_dashboard.html"))
    print(f"Dashboard written to {path}")
