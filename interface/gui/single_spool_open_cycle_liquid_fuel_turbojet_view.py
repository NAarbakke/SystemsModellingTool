"""
The conventional (liquid fuel) turbojet as a dashboard sees it: its stations, its inputs and one operating point
per set of input values.
"""
from dataclasses import replace

import numpy as np

from graphics.turbojet_layout import turbojet_layout
from interface.gui.component_inputs import (
    apply_axial_compressor, apply_combustor, apply_convergent_nozzle, apply_inlet, axial_compressor_inputs,
    combustor_inputs, convergent_nozzle_inputs, inlet_inputs)
from interface.gui.dashboard_view import NO_EXPANSION, EngineView, Snapshot, flight_subtitle
from specifications.SKYF.engine import specs_open_cycle_liquid_fuel_turbojet as base
from specifications.SKYF.flight_state.cruise import cruise
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.stations import stations
from subsystems.propulsion.motors.turbojets.single_spool_open_cycle_liquid_fuel_turbojet import SingleSpoolOpenCycleLiquidFuelTurbojet

STATIONS = stations("0", "1", "2", "3", "4", "5", "9")


def evaluate(values: dict) -> Snapshot:
    inlet, inlet_geometry = apply_inlet(base.subsonic_inlet, base.subsonic_inlet_geometry, values)
    compressor, geometry = apply_axial_compressor(base.compressor, base.compressor_geometry, values)
    specs = replace(
        base, subsonic_inlet=inlet, subsonic_inlet_geometry=inlet_geometry, compressor=compressor,
        compressor_geometry=geometry, combustor=apply_combustor(base.combustor, values),
        nozzle=apply_convergent_nozzle(base.nozzle, values))

    engine = SingleSpoolOpenCycleLiquidFuelTurbojet(GasModel(), specs)
    result = engine.run_point(cruise)
    sizing = engine.compressor.compute_geometry(result["stations"]["2"], result["stations"]["3"])
    return Snapshot(
        result, turbojet_layout(specs, sizing), flight_subtitle(cruise), geometry, sizing,
        error=None if np.isfinite(result["Thrust"]) else NO_EXPANSION)


VIEW = EngineView(
    title="Single-spool open-cycle liquid fuel turbojet",
    stations=STATIONS,
    streams={"Core": list(STATIONS)},
    inputs={
        "Inlet": inlet_inputs(base.subsonic_inlet, base.subsonic_inlet_geometry),
        "Compressor": axial_compressor_inputs(base.compressor, base.compressor_geometry),
        "Combustor": combustor_inputs(base.combustor),
        "Nozzle": convergent_nozzle_inputs(base.nozzle)},
    evaluate=evaluate)
