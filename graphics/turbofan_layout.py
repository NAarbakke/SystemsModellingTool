"""
Layout of the single-spool turbofans (open-cycle nuclear, closed-cycle nuclear, liquid fuel):
inlet -> fan -> splitter -> core (see core_layout.py), with the bypass duct and nozzle wrapped around the core.

To scale: fan hub and tip radius, the splitter radius (from the bypass ratio, uniform flow at the fan exit) and the
bypass nozzle exit area. Nominal: every length outside the core, and the thickness of the cowl and nacelle.
"""
import numpy as np

from graphics.core_layout import COMBUSTOR_LENGTH, HEAT_EXCHANGER_LENGTH, centrifugal_core_layout, core_layout
from graphics.engine_illustration import BODY, CASING, CASING_THICKNESS, FREESTREAM_LENGTH, EngineLayout, GasPath, gas_path
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.turbofans.single_spool_closed_cycle_nuclear_fuel_turbofan_specs import SingleSpoolClosedCycleNuclearTurbofanSpecs
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_liquid_fuel_turbofan_specs import SingleSpoolOpenCycleLiquidFuelTurbofanSpecs
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_nuclear_fuel_turbofan_specs import SingleSpoolOpenCycleNuclearTurbofanSpecs

TurbofanSpecs = (SingleSpoolOpenCycleNuclearTurbofanSpecs | SingleSpoolClosedCycleNuclearTurbofanSpecs
                          | SingleSpoolOpenCycleLiquidFuelTurbofanSpecs)

# Nominal dimensions - not modelled yet
INLET_LENGTH = 0.35             # [m]
FAN_LENGTH = 0.15               # [m]
SPLITTER_LENGTH = 0.20          # [m] fan exit to compressor face
BYPASS_DUCT_AFT = 0.40          # [m] the bypass duct ends this far aft of the compressor exit
BYPASS_NOZZLE_LENGTH = 0.35     # [m]
COWL_THICKNESS = 0.03           # [m] core cowl, between the core and the bypass duct
NACELLE_THICKNESS = 0.02        # [m]


def _heat_section(specs: TurbofanSpecs) -> tuple[str, float]:
    """Name and length [m] of the core's heat section."""
    if isinstance(specs, SingleSpoolOpenCycleNuclearTurbofanSpecs):
        return "Reactor", specs.reactor.fuel_rod_length
    if isinstance(specs, SingleSpoolClosedCycleNuclearTurbofanSpecs):
        return "Heat exchanger", HEAT_EXCHANGER_LENGTH
    return "Combustor", COMBUSTOR_LENGTH


def turbofan_layout(specs: TurbofanSpecs, sizing: AxialCompressorSizing | None = None) -> EngineLayout:
    """sizing: the axial compressor as sized at the operating point; None draws a nominal centrifugal compressor."""
    fan = specs.fan
    heat, L_heat = _heat_section(specs)
    x_2 = INLET_LENGTH              # fan face; the lip (station 1) is at x = 0
    x_13 = x_2 + FAN_LENGTH         # fan exit (13 is its bypass side; the core side has the same totals)
    x_25 = x_13 + SPLITTER_LENGTH   # compressor face

    # Splitter lip: the core takes 1 / (1 + bypass ratio) of the fan annulus area
    r_split = float(np.sqrt(fan.r_hub**2 + (fan.r_tip**2 - fan.r_hub**2) / (1 + specs.bypass_ratio)))

    if sizing is None:
        core = centrifugal_core_layout(fan.r_hub, r_split, L_heat, specs.core_nozzle, x_face=x_25)
    else:
        core = core_layout(specs.compressor_geometry, sizing, L_heat, specs.core_nozzle, x_face=x_25)
    x_17 = core.x_3 + BYPASS_DUCT_AFT
    x_19 = x_17 + BYPASS_NOZZLE_LENGTH

    front = gas_path(["0", "1", "2", "13"], [0.0, x_2, x_13], [0.0, fan.r_hub, fan.r_hub], [0.0, x_13], [fan.r_tip, fan.r_tip])
    core_path = gas_path(
        ["13", "25", "3", "4", "5", "9"],
        [x_13, *core.x_inner], [fan.r_hub, *core.r_inner],
        [x_13, *core.x_outer], [r_split, *core.r_outer])

    # Core cowl: sharp at the splitter lip, full thickness along the bypass duct, thin casing aft of the bypass nozzle
    cowl = np.interp(core_path.x, [x_13, x_25, x_19, core.x_9], [0.0, COWL_THICKNESS, COWL_THICKNESS, CASING_THICKNESS])
    r_cowl = core_path.r_outer + cowl

    # Bypass: around the cowl, outer wall at the fan tip radius until the nozzle sets the exit area
    x_b = np.unique(np.concatenate([core_path.x[core_path.x <= x_19], [x_17, x_19]]))
    r_b_inner = np.interp(x_b, core_path.x, r_cowl)
    r_b_exit = float(np.sqrt(r_b_inner[-1]**2 + specs.bypass_nozzle.A_exit / np.pi))
    bypass = GasPath(["13", "17", "19"], x_b, r_b_inner, np.interp(x_b, [x_13, x_17, x_19], [fan.r_tip, fan.r_tip, r_b_exit]))

    x_nacelle = np.concatenate([front.x, bypass.x])
    r_nacelle = np.concatenate([front.r_outer, bypass.r_outer])
    r_b_mid = 0.5 * (r_b_inner[0] + fan.r_tip) + 0.5 * COWL_THICKNESS

    return EngineLayout(
        station_x={
            "0": -FREESTREAM_LENGTH, "1": 0.0, "2": x_2, "25": x_25, "3": core.x_3, "4": core.x_4, "5": core.x_5,
            "9": core.x_9, "13": x_13, "17": x_17, "19": x_19},
        gas_paths=[front, core_path, bypass],
        solids=[
            (front.x, np.zeros_like(front.x), front.r_inner, BODY),
            (core_path.x, np.zeros_like(core_path.x), core_path.r_inner, BODY),
            (core_path.x, core_path.r_outer, r_cowl, BODY),
            (x_nacelle, r_nacelle, r_nacelle + NACELLE_THICKNESS, CASING)],
        rotors=[(x_2 + 0.02, x_13 - 0.04, front), *[(x_0, x_1, core_path) for x_0, x_1 in core.rotors]],
        stators=[(x_0, x_1, core_path) for x_0, x_1 in core.stators],
        rods=(*core.heat, core_path) if heat == "Reactor" else None,
        liner=(*core.heat, core_path) if heat == "Combustor" else None,
        labels=[
            ("Inlet", 0.5 * x_2, None),
            ("Fan", 0.5 * (x_2 + x_13), None),
            ("Compressor", 0.5 * (x_25 + core.x_3), None),
            (heat, 0.5 * (core.x_3 + core.x_4), None),
            ("Turbine", 0.5 * (core.x_4 + core.x_5), None),
            ("Nozzle", 0.5 * (core.x_5 + core.x_9), None),
            ("Bypass duct", 0.5 * (x_25 + x_17), r_b_mid),
            ("Bypass nozzle", 0.5 * (x_17 + x_19), r_b_mid)])
