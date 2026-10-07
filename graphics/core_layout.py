"""
Layout of the part every nuclear engine here shares: axial compressor -> reactor -> turbine -> convergent nozzle.

To scale where the model has geometry: compressor annulus and blade rows (AxialCompressorGeometry +
AxialCompressorSizing), reactor length (fuel rod length), nozzle exit radius (A_exit).
Nominal where it has none yet: turbine and nozzle lengths, shaft radius, casing radius aft of the compressor.
"""
from dataclasses import dataclass

import numpy as np

from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle_specs import ConvergentNozzleSpecs
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor_specs import FastNeutronReactorSpecs

# Nominal dimensions - not modelled yet
TURBINE_LENGTH = 0.30       # [m]
NOZZLE_LENGTH = 0.40        # [m]
TRANSITION_LENGTH = 0.08    # [m] hub fairing into / out of the reactor
SHAFT_TO_CASING = 0.12      # [-] shaft radius / casing radius


@dataclass
class CoreLayout:
    """Axial positions [m] of the core stations, wall breakpoints from compressor face to nozzle exit, and what sits inside."""
    x_3: float      # compressor exit
    x_4: float      # reactor exit
    x_5: float      # turbine exit
    x_6: float      # nozzle exit
    x_inner: list[float]
    r_inner: list[float]
    x_outer: list[float]
    r_outer: list[float]
    rotors: list[tuple[float, float]]
    stators: list[tuple[float, float]]
    rods: tuple[float, float]


def compressor_rows(geometry: AxialCompressorGeometry, sizing: AxialCompressorSizing, x_face: float):
    """
    Stage entry positions (plus the EGV entry) and the blade rows as (start, end):
    IGV, then rotor + stator per stage (chords from the local blade span), then EGV.
    """
    x_stage = x_face + geometry.IGV_axial_chord_length + np.concatenate([[0.0], np.cumsum(sizing.L_stage)])
    rotors, stators = [], [(x_face, x_stage[0])]
    for x_s, r_hub, r_tip in zip(x_stage, sizing.r_hub_stage, sizing.r_tip_stage):
        c_rotor = (r_tip - r_hub) / geometry.AR_rotor
        c_stator = (r_tip - r_hub) / geometry.AR_stator
        x_stator = x_s + c_rotor * (1 + geometry.IRG_to_chord)
        rotors.append((x_s, x_s + c_rotor))
        stators.append((x_stator, x_stator + c_stator))
    stators.append((x_stage[-1], x_face + sizing.L))
    return x_stage, rotors, stators


def core_layout(geometry: AxialCompressorGeometry, sizing: AxialCompressorSizing, reactor: FastNeutronReactorSpecs,
                nozzle: ConvergentNozzleSpecs, x_face: float) -> CoreLayout:
    """Core layout with the compressor face at x_face."""
    r_case = geometry.r_tip
    r_shaft = SHAFT_TO_CASING * r_case
    r_exit = float(np.sqrt(nozzle.A_exit / np.pi))

    x_3 = x_face + sizing.L
    x_4 = x_3 + reactor.fuel_rod_length
    x_5 = x_4 + TURBINE_LENGTH
    x_6 = x_5 + NOZZLE_LENGTH

    # Annulus is held constant through the EGV, so the last stage's radii repeat at the EGV entry
    x_stage, rotors, stators = compressor_rows(geometry, sizing, x_face)
    r_hub = [*sizing.r_hub_stage, sizing.r_hub_stage[-1]]
    r_tip = [*sizing.r_tip_stage, sizing.r_tip_stage[-1]]

    # Turbine: one nominal stage
    stators.append((x_4 + 0.10 * TURBINE_LENGTH, x_4 + 0.40 * TURBINE_LENGTH))
    rotors.append((x_4 + 0.55 * TURBINE_LENGTH, x_4 + 0.85 * TURBINE_LENGTH))

    return CoreLayout(
        x_3=x_3, x_4=x_4, x_5=x_5, x_6=x_6,
        x_inner=[x_face, *x_stage, x_3, x_3 + TRANSITION_LENGTH, x_4 - TRANSITION_LENGTH, x_4, x_5, x_5 + 0.6 * NOZZLE_LENGTH, x_6],
        r_inner=[r_hub[0], *r_hub, r_hub[-1], r_shaft, r_shaft, r_hub[-1], r_hub[-1], 0.0, 0.0],
        x_outer=[x_face, *x_stage, x_3, x_3 + TRANSITION_LENGTH, x_5, x_6],
        r_outer=[r_tip[0], *r_tip, r_tip[-1], r_case, r_case, r_exit],
        rotors=rotors,
        stators=stators,
        rods=(x_3 + TRANSITION_LENGTH, x_4 - TRANSITION_LENGTH))
