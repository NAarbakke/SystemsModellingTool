"""
The closed-cycle nuclear turbofan as a dashboard sees it: its stations, its inputs and one operating point per set of
input values. The reactor heats a coolant loop; a heat exchanger passes the heat to the core air.
"""
from dataclasses import replace

import numpy as np

from graphics.turbofan_layout import turbofan_layout
from interface.gui.component_inputs import (
    apply_centrifugal_compressor, apply_convergent_nozzle, apply_fan, apply_heat_exchanger,
    centrifugal_compressor_inputs, convergent_nozzle_inputs, fan_inputs, heat_exchanger_inputs)
from interface.gui.dashboard_view import FLIGHT_INPUTS, NO_EXPANSION, EngineView, Snapshot, flight_subtitle, freestream
from specifications.SKYF.engine import specs_closed_cycle_nuclear as base
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.turbofans.single_spool_closed_cycle_nuclear_fuel_turbofan import SingleSpoolClosedCycleNuclearTurbofan

# Station numbering follows run_point()
STATIONS = {
    "0": "Freestream",
    "1": "Inlet exit",
    "2": "Fan exit",
    "25a": "Core splitter exit",
    "25b": "Bypass splitter exit",
    "3": "Compressor exit",
    "4": "Heat exchanger exit",
    "5": "Turbine exit",
    "6": "Core nozzle exit",
    "7": "Bypass duct exit",
    "8": "Bypass nozzle exit"}


def evaluate(values: dict) -> Snapshot:
    specs = replace(
        base, bypass_ratio=values["bypass_ratio"], fan=apply_fan(base.fan, values),
        compressor=apply_centrifugal_compressor(base.compressor, values), hx=apply_heat_exchanger(base.hx, values),
        core_nozzle=apply_convergent_nozzle(base.core_nozzle, values),
        bypass_nozzle=apply_convergent_nozzle(base.bypass_nozzle, values, key="A_exit_bypass"))

    gas = GasModel()
    flow = freestream(values, gas)
    engine = SingleSpoolClosedCycleNuclearTurbofan(gas, specs, flow["P_0"])
    result = engine.run_point(**flow)
    return Snapshot(
        result, turbofan_layout(specs), flight_subtitle(values, flow),
        error=None if np.isfinite(result["F_total"]) else NO_EXPANSION)


VIEW = EngineView(
    title="Single-spool closed-cycle nuclear turbofan",
    stations=STATIONS,
    streams={"Core": ["0", "1", "2", "25a", "3", "4", "5", "6"], "Bypass": ["2", "25b", "7", "8"]},
    inputs={
        "Flight condition": FLIGHT_INPUTS,
        "Fan": fan_inputs(base.fan, base.bypass_ratio),
        "Compressor": centrifugal_compressor_inputs(base.compressor),
        "Heat exchanger": heat_exchanger_inputs(base.hx),
        "Core nozzle": convergent_nozzle_inputs(base.core_nozzle),
        "Bypass nozzle": convergent_nozzle_inputs(base.bypass_nozzle, key="A_exit_bypass", hi=1.5)},
    evaluate=evaluate)
