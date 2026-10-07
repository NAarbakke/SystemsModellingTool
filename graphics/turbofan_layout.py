"""
Layout of the single-spool open-cycle nuclear turbofan: inlet -> fan -> splitter -> core (see core_layout.py),
with the bypass duct and nozzle wrapped around the core.

To scale: fan hub and tip radius, the splitter radius (from the bypass ratio, uniform flow at the fan exit) and the
bypass nozzle exit area. Nominal: every length outside the core, and the thickness of the cowl and nacelle.
"""
import numpy as np

from graphics.core_layout import core_layout
from graphics.engine_illustration import CASING_THICKNESS, FREESTREAM_LENGTH, EngineLayout, GasPath, gas_path
from graphics.theme import BODY, CASING
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_nuclear_fuel_turbofan_specs import SingleSpoolOpenCycleNuclearTurbofanSpecifications

# Nominal dimensions - not modelled yet
INLET_LENGTH = 0.35             # [m]
FAN_LENGTH = 0.15               # [m]
SPLITTER_LENGTH = 0.20          # [m] fan exit to compressor face
BYPASS_DUCT_AFT = 0.40          # [m] the bypass duct ends this far aft of the compressor exit
BYPASS_NOZZLE_LENGTH = 0.35     # [m]
COWL_THICKNESS = 0.03           # [m] core cowl, between the core and the bypass duct
NACELLE_THICKNESS = 0.02        # [m]


def turbofan_layout(specs: SingleSpoolOpenCycleNuclearTurbofanSpecifications, sizing: AxialCompressorSizing) -> EngineLayout:
    fan = specs.fan
    x_1 = INLET_LENGTH
    x_2 = x_1 + FAN_LENGTH
    x_25 = x_2 + SPLITTER_LENGTH
    core = core_layout(specs.compressor_geometry, sizing, specs.reactor, specs.core_nozzle, x_face=x_25)
    x_7 = core.x_3 + BYPASS_DUCT_AFT
    x_8 = x_7 + BYPASS_NOZZLE_LENGTH

    # Splitter lip: the core takes 1 / (1 + bypass ratio) of the fan annulus area
    r_split = float(np.sqrt(fan.r_hub**2 + (fan.r_tip**2 - fan.r_hub**2) / (1 + specs.bypass_ratio)))

    front = gas_path(["0", "1", "2"], [0.0, x_1, x_2], [0.0, fan.r_hub, fan.r_hub], [0.0, x_2], [fan.r_tip, fan.r_tip])
    core_path = gas_path(
        ["2", "25a", "3", "4", "5", "6"],
        [x_2, *core.x_inner], [fan.r_hub, *core.r_inner],
        [x_2, *core.x_outer], [r_split, *core.r_outer])

    # Core cowl: sharp at the splitter lip, full thickness along the bypass duct, thin casing aft of the bypass nozzle
    cowl = np.interp(core_path.x, [x_2, x_25, x_8, core.x_6], [0.0, COWL_THICKNESS, COWL_THICKNESS, CASING_THICKNESS])
    r_cowl = core_path.r_outer + cowl

    # Bypass: around the cowl, outer wall at the fan tip radius until the nozzle sets the exit area
    x_b = np.unique(np.concatenate([core_path.x[core_path.x <= x_8], [x_7, x_8]]))
    r_b_inner = np.interp(x_b, core_path.x, r_cowl)
    r_b_exit = float(np.sqrt(r_b_inner[-1]**2 + specs.bypass_nozzle.A_exit / np.pi))
    bypass = GasPath(["2", "25b", "7", "8"], x_b, r_b_inner, np.interp(x_b, [x_2, x_7, x_8], [fan.r_tip, fan.r_tip, r_b_exit]))

    x_nacelle = np.concatenate([front.x, bypass.x])
    r_nacelle = np.concatenate([front.r_outer, bypass.r_outer])
    r_b_mid = 0.5 * (r_b_inner[0] + fan.r_tip) + 0.5 * COWL_THICKNESS

    return EngineLayout(
        station_x={
            "0": -FREESTREAM_LENGTH, "1": x_1, "2": x_2, "25a": x_25, "25b": x_25,
            "3": core.x_3, "4": core.x_4, "5": core.x_5, "6": core.x_6, "7": x_7, "8": x_8},
        gas_paths=[front, core_path, bypass],
        solids=[
            (front.x, np.zeros_like(front.x), front.r_inner, BODY),
            (core_path.x, np.zeros_like(core_path.x), core_path.r_inner, BODY),
            (core_path.x, core_path.r_outer, r_cowl, BODY),
            (x_nacelle, r_nacelle, r_nacelle + NACELLE_THICKNESS, CASING)],
        rotors=[(x_1 + 0.02, x_2 - 0.04, front), *[(x_0, x_1, core_path) for x_0, x_1 in core.rotors]],
        stators=[(x_0, x_1, core_path) for x_0, x_1 in core.stators],
        rods=(*core.rods, core_path),
        labels=[
            ("Inlet", 0.5 * x_1, None),
            ("Fan", 0.5 * (x_1 + x_2), None),
            ("Compressor", 0.5 * (x_25 + core.x_3), None),
            ("Reactor", 0.5 * (core.x_3 + core.x_4), None),
            ("Turbine", 0.5 * (core.x_4 + core.x_5), None),
            ("Nozzle", 0.5 * (core.x_5 + core.x_6), None),
            ("Bypass duct", 0.5 * (x_25 + x_7), r_b_mid),
            ("Bypass nozzle", 0.5 * (x_7 + x_8), r_b_mid)])
