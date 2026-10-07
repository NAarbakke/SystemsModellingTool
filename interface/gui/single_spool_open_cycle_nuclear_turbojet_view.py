"""
The turbojet as both of its dashboards see it (dynamic: single_spool_open_cycle_nuclear_turbojet_dashboard.py, static: single_spool_open_cycle_nuclear_turbojet_dashboard_static.py).
"""
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.turbojets.single_spool_open_cycle_nuclear_turbojet import SingleSpoolOpenCycleNuclearTurbojet
from subsystems.propulsion.motors.turbojets.single_spool_open_cycle_nuclear_turbojet_specs import SingleSpoolOpenCycleNuclearTurbojetSpecifications

TITLE = "Single-spool open-cycle nuclear turbojet"

# Station numbering follows run_point()
STATIONS = {
    "0": "Freestream",
    "1": "Compressor face",
    "3": "Compressor exit",
    "4": "Reactor exit",
    "5": "Turbine exit",
    "6": "Nozzle exit"}

STREAMS = {"Core": list(STATIONS)}


def run_turbojet(specs: SingleSpoolOpenCycleNuclearTurbojetSpecifications, T_0: float, P_0: float, M_0: float) -> tuple[dict, AxialCompressorSizing]:
    """One operating point: the run_point() result and the compressor sized for it."""
    engine = SingleSpoolOpenCycleNuclearTurbojet(GasModel(), specs, P_0)
    result = engine.run_point(T_0=T_0, P_0=P_0, M_0=M_0)
    sizing = engine.compressor.compute_geometry(result["stations"]["1"], result["stations"]["3"])
    return result, sizing
