"""
The nuclear turbojet as a dashboard sees it: its stations, its inputs and one operating point per set of input values.
"""
from dataclasses import replace

import numpy as np

from graphics.turbojet_layout import turbojet_layout
from interface.gui.component_inputs import (
    apply_axial_compressor, apply_convergent_nozzle, apply_reactor, axial_compressor_inputs, convergent_nozzle_inputs,
    reactor_inputs)
from interface.gui.dashboard_view import FLIGHT_INPUTS, NO_EXPANSION, EngineView, Snapshot, flight_subtitle, freestream
from specifications.SKYF.engine import specs_open_cycle_nuclear_turbojet as base
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.turbojets.single_spool_open_cycle_nuclear_turbojet import SingleSpoolOpenCycleNuclearTurbojet

# Station numbering follows run_point()
STATIONS = {
    "0": "Freestream",
    "1": "Compressor face",
    "3": "Compressor exit",
    "4": "Reactor exit",
    "5": "Turbine exit",
    "6": "Nozzle exit"}


def evaluate(values: dict) -> Snapshot:
    compressor, geometry = apply_axial_compressor(base.compressor, base.compressor_geometry, values)
    specs = replace(
        base, compressor=compressor, compressor_geometry=geometry,
        reactor=apply_reactor(base.reactor, values), nozzle=apply_convergent_nozzle(base.nozzle, values))

    gas = GasModel()
    flow = freestream(values, gas)
    engine = SingleSpoolOpenCycleNuclearTurbojet(gas, specs, flow["P_0"])
    result = engine.run_point(**flow)
    sizing = engine.compressor.compute_geometry(result["stations"]["1"], result["stations"]["3"])
    return Snapshot(
        result, turbojet_layout(specs, sizing), flight_subtitle(values, flow), geometry, sizing,
        error=None if np.isfinite(result["F_total"]) else NO_EXPANSION)


VIEW = EngineView(
    title="Single-spool open-cycle nuclear turbojet",
    stations=STATIONS,
    streams={"Core": list(STATIONS)},
    inputs={
        "Flight condition": FLIGHT_INPUTS,
        "Compressor": axial_compressor_inputs(base.compressor, base.compressor_geometry),
        "Reactor": reactor_inputs(base.reactor),
        "Nozzle": convergent_nozzle_inputs(base.nozzle)},
    evaluate=evaluate)
