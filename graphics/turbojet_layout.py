"""
Layout of the single-spool open-cycle nuclear turbojet: inlet -> core (see core_layout.py).
The inlet length is nominal - the model has no geometry for it yet.
"""
import numpy as np

from graphics.core_layout import core_layout
from graphics.engine_illustration import CASING_THICKNESS, FREESTREAM_LENGTH, EngineLayout, gas_path
from graphics.theme import BODY, CASING
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.turbojets.single_spool_open_cycle_nuclear_turbojet_specs import SingleSpoolOpenCycleNuclearTurbojetSpecifications

INLET_LENGTH = 0.35     # [m] nominal


def turbojet_layout(specs: SingleSpoolOpenCycleNuclearTurbojetSpecifications, sizing: AxialCompressorSizing) -> EngineLayout:
    x_1 = INLET_LENGTH
    core = core_layout(specs.compressor_geometry, sizing, specs.reactor, specs.nozzle, x_face=x_1)

    # Spinner grows from the lip to the compressor hub; the casing runs straight into the compressor
    path = gas_path(
        ["0", "1", "3", "4", "5", "6"],
        [0.0, *core.x_inner], [0.0, *core.r_inner],
        [0.0, *core.x_outer], [core.r_outer[0], *core.r_outer])

    return EngineLayout(
        station_x={"0": -FREESTREAM_LENGTH, "1": x_1, "3": core.x_3, "4": core.x_4, "5": core.x_5, "6": core.x_6},
        gas_paths=[path],
        solids=[
            (path.x, np.zeros_like(path.x), path.r_inner, BODY),
            (path.x, path.r_outer, path.r_outer + CASING_THICKNESS, CASING)],
        rotors=[(x_0, x_1, path) for x_0, x_1 in core.rotors],
        stators=[(x_0, x_1, path) for x_0, x_1 in core.stators],
        rods=(*core.rods, path),
        labels=[
            ("Inlet", 0.5 * x_1, None),
            ("Compressor", 0.5 * (x_1 + core.x_3), None),
            ("Reactor", 0.5 * (core.x_3 + core.x_4), None),
            ("Turbine", 0.5 * (core.x_4 + core.x_5), None),
            ("Nozzle", 0.5 * (core.x_5 + core.x_6), None)])
