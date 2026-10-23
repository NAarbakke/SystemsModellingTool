"""
The closed-cycle nuclear turbofan as a dashboard sees it: its stations, its inputs and one operating point per set of
input values. The reactor heats a coolant loop; a heat exchanger passes the heat to the core air.
"""
from dataclasses import replace

import numpy as np

from graphics.turbofan_layout import turbofan_layout
from interface.gui.component_inputs import (
    apply_axial_compressor, apply_convergent_nozzle, apply_fan, apply_heat_exchanger, apply_inlet,
    axial_compressor_inputs, convergent_nozzle_inputs, fan_inputs, heat_exchanger_inputs, inlet_inputs)
from interface.gui.dashboard_view import NO_EXPANSION, EngineView, Snapshot, flight_subtitle
from specifications.SKYF.engine import specs_closed_cycle_nuclear as base
from specifications.SKYF.flight_state.cruise import cruise
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.stations import stations
from subsystems.propulsion.motors.turbofans.single_spool_closed_cycle_nuclear_fuel_turbofan import SingleSpoolClosedCycleNuclearTurbofan

STATIONS = stations("0", "1", "2", "25", "3", "4", "5", "9", "13", "17", "19")


def evaluate(values: dict) -> Snapshot:
    inlet, inlet_geometry = apply_inlet(base.subsonic_inlet, base.subsonic_inlet_geometry, values)
    compressor, geometry = apply_axial_compressor(base.compressor, base.compressor_geometry, values)
    specs = replace(
        base, bypass_ratio=values["bypass_ratio"], subsonic_inlet=inlet, subsonic_inlet_geometry=inlet_geometry,
        fan=apply_fan(base.fan, values), compressor=compressor, compressor_geometry=geometry,
        hx=apply_heat_exchanger(base.hx, values),
        core_nozzle=apply_convergent_nozzle(base.core_nozzle, values),
        bypass_nozzle=apply_convergent_nozzle(base.bypass_nozzle, values, key="A_exit_bypass"))

    engine = SingleSpoolClosedCycleNuclearTurbofan(GasModel(), specs)
    result = engine.run_point(cruise)
    sizing = engine.compressor.compute_geometry(result["stations"]["25"], result["stations"]["3"])
    return Snapshot(
        result, turbofan_layout(specs, sizing), flight_subtitle(cruise), geometry, sizing,
        error=None if np.isfinite(result["Thrust"]) else NO_EXPANSION)


VIEW = EngineView(
    title="Single-spool closed-cycle nuclear turbofan",
    stations=STATIONS,
    streams={"Core": ["0", "1", "2", "25", "3", "4", "5", "9"], "Bypass": ["2", "13", "17", "19"]},
    inputs={
        "Inlet": inlet_inputs(base.subsonic_inlet, base.subsonic_inlet_geometry),
        "Fan": fan_inputs(base.fan, base.bypass_ratio),
        "Compressor": axial_compressor_inputs(base.compressor, base.compressor_geometry),
        "Heat exchanger": heat_exchanger_inputs(base.hx),
        "Core nozzle": convergent_nozzle_inputs(base.core_nozzle),
        "Bypass nozzle": convergent_nozzle_inputs(base.bypass_nozzle, key="A_exit_bypass", hi=1.5)},
    evaluate=evaluate)
