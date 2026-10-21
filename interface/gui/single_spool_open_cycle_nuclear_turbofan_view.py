"""
The open-cycle nuclear turbofan as a dashboard sees it: its stations, its inputs and one operating point per set of
input values.
"""
from dataclasses import replace

import numpy as np

from graphics.turbofan_layout import turbofan_layout
from interface.gui.component_inputs import (
    apply_axial_compressor, apply_convergent_nozzle, apply_fan, apply_reactor, axial_compressor_inputs,
    convergent_nozzle_inputs, fan_inputs, reactor_inputs)
from interface.gui.dashboard_view import NO_EXPANSION, EngineView, Snapshot, flight_subtitle, freestream
from specifications.SKYF.engine import specs_open_cycle_nuclear as base
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_nuclear_fuel_turbofan import SingleSpoolOpenCycleNuclearTurbofan

# Station numbering follows run_point()
STATIONS = {
    "0": "Freestream",
    "1": "Inlet exit",
    "2": "Fan exit",
    "25a": "Core splitter exit",
    "25b": "Bypass splitter exit",
    "3": "Compressor exit",
    "4": "Reactor exit",
    "5": "Turbine exit",
    "6": "Core nozzle exit",
    "7": "Bypass duct exit",
    "8": "Bypass nozzle exit"}


def evaluate(values: dict) -> Snapshot:
    compressor, geometry = apply_axial_compressor(base.compressor, base.compressor_geometry, values)
    specs = replace(
        base, bypass_ratio=values["bypass_ratio"], fan=apply_fan(base.fan, values),
        compressor=compressor, compressor_geometry=geometry, reactor=apply_reactor(base.reactor, values),
        core_nozzle=apply_convergent_nozzle(base.core_nozzle, values),
        bypass_nozzle=apply_convergent_nozzle(base.bypass_nozzle, values, key="A_exit_bypass"))

    gas = GasModel()
    flow = freestream(gas)
    engine = SingleSpoolOpenCycleNuclearTurbofan(gas, specs, flow["P_0"])
    result = engine.run_point(**flow)
    sizing = engine.compressor.compute_geometry(result["stations"]["25a"], result["stations"]["3"])
    return Snapshot(
        result, turbofan_layout(specs, sizing), flight_subtitle(flow), geometry, sizing,
        error=None if np.isfinite(result["F_total"]) else NO_EXPANSION)


VIEW = EngineView(
    title="Single-spool open-cycle nuclear turbofan",
    stations=STATIONS,
    streams={"Core": ["0", "1", "2", "25a", "3", "4", "5", "6"], "Bypass": ["2", "25b", "7", "8"]},
    inputs={
        "Fan": fan_inputs(base.fan, base.bypass_ratio),
        "Compressor": axial_compressor_inputs(base.compressor, base.compressor_geometry),
        "Reactor": reactor_inputs(base.reactor),
        "Core nozzle": convergent_nozzle_inputs(base.core_nozzle),
        "Bypass nozzle": convergent_nozzle_inputs(base.bypass_nozzle, key="A_exit_bypass", hi=1.5)},
    evaluate=evaluate)
