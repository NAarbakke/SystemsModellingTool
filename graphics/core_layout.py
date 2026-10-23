"""
Layout of the core every engine here shares: compressor -> heat section -> turbine -> convergent nozzle.
The compressor is axial (to scale) or centrifugal (nominal); the heat section is a reactor, a combustor or a heat
exchanger, and the caller gives its length.

To scale where the model has geometry: axial compressor annulus and blade rows (AxialCompressorGeometry +
AxialCompressorSizing), reactor length (fuel rod length), nozzle exit radius (A_exit).
Nominal where it has none yet: centrifugal compressor, combustor, heat exchanger, turbine and nozzle lengths, shaft
radius, casing radius aft of the compressor.
"""
from dataclasses import dataclass

import numpy as np

from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle_specs import ConvergentNozzleSpecs

# Nominal dimensions - not modelled yet
COMBUSTOR_LENGTH = 0.40     # [m]
HEAT_EXCHANGER_LENGTH = 0.60    # [m]
CENTRIFUGAL_LENGTH = 0.25   # [m] impeller + diffuser
TURBINE_LENGTH = 0.30       # [m]
NOZZLE_LENGTH = 0.40        # [m]
TRANSITION_LENGTH = 0.08    # [m] hub fairing into / out of the heat section
SHAFT_TO_CASING = 0.12      # [-] shaft radius / casing radius


@dataclass
class CoreLayout:
    """
    Axial positions [m] of the core stations (SAE ARP755 numbers, see helpers/stations.py), wall breakpoints from
    compressor face to nozzle exit, and what sits inside.
    """
    x_3: float      # compressor exit
    x_4: float      # turbine entry (heat section exit)
    x_5: float      # turbine exit
    x_9: float      # nozzle exit
    x_inner: list[float]
    r_inner: list[float]
    x_outer: list[float]
    r_outer: list[float]
    rotors: list[tuple[float, float]]
    stators: list[tuple[float, float]]
    heat: tuple[float, float]   # heat section between the hub fairings (fuel rods / combustor liner)


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


def core_layout(geometry: AxialCompressorGeometry, sizing: AxialCompressorSizing, L_heat: float,
                nozzle: ConvergentNozzleSpecs, x_face: float) -> CoreLayout:
    """Core with a sized axial compressor, its face at x_face, and a heat section L_heat [m] long."""
    # Annulus is held constant through the EGV, so the last stage's radii repeat at the EGV entry
    x_stage, rotors, stators = compressor_rows(geometry, sizing, x_face)
    r_hub = [*sizing.r_hub_stage, sizing.r_hub_stage[-1]]
    r_tip = [*sizing.r_tip_stage, sizing.r_tip_stage[-1]]
    return _core(
        x_face + sizing.L, [x_face, *x_stage], [r_hub[0], *r_hub], [r_tip[0], *r_tip], geometry.r_tip,
        rotors, stators, L_heat, nozzle)


def centrifugal_core_layout(r_hub: float, r_tip: float, L_heat: float, nozzle: ConvergentNozzleSpecs,
                            x_face: float) -> CoreLayout:
    """Core with a nominal centrifugal compressor (impeller + diffuser in the face annulus r_hub..r_tip)."""
    L = CENTRIFUGAL_LENGTH
    rotors = [(x_face + 0.10 * L, x_face + 0.55 * L)]
    stators = [(x_face + 0.65 * L, x_face + 0.90 * L)]
    return _core(x_face + L, [x_face], [r_hub], [r_tip], r_tip, rotors, stators, L_heat, nozzle)


def _core(x_3: float, x_c: list[float], r_hub_c: list[float], r_tip_c: list[float], r_case: float,
          rotors: list, stators: list, L_heat: float, nozzle: ConvergentNozzleSpecs) -> CoreLayout:
    """Heat section, turbine and nozzle aft of a compressor whose walls are given by x_c, r_hub_c, r_tip_c."""
    r_shaft = SHAFT_TO_CASING * r_case
    r_exit = float(np.sqrt(nozzle.A_exit / np.pi))

    x_4 = x_3 + L_heat
    x_5 = x_4 + TURBINE_LENGTH
    x_9 = x_5 + NOZZLE_LENGTH

    # Turbine: one nominal stage
    stators.append((x_4 + 0.10 * TURBINE_LENGTH, x_4 + 0.40 * TURBINE_LENGTH))
    rotors.append((x_4 + 0.55 * TURBINE_LENGTH, x_4 + 0.85 * TURBINE_LENGTH))

    return CoreLayout(
        x_3=x_3, x_4=x_4, x_5=x_5, x_9=x_9,
        x_inner=[*x_c, x_3, x_3 + TRANSITION_LENGTH, x_4 - TRANSITION_LENGTH, x_4, x_5, x_5 + 0.6 * NOZZLE_LENGTH, x_9],
        r_inner=[*r_hub_c, r_hub_c[-1], r_shaft, r_shaft, r_hub_c[-1], r_hub_c[-1], 0.0, 0.0],
        x_outer=[*x_c, x_3, x_3 + TRANSITION_LENGTH, x_5, x_9],
        r_outer=[*r_tip_c, r_tip_c[-1], r_case, r_case, r_exit],
        rotors=rotors,
        stators=stators,
        heat=(x_3 + TRANSITION_LENGTH, x_4 - TRANSITION_LENGTH))
