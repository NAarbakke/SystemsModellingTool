from dataclasses import dataclass


@dataclass
class AxialCompressorSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    PR: float           # [-]   total pressure ratio
    eta_poly: float     # [-]   polytropic efficiency
    #RPM: float          # [revs/min] - instead of U_tip
    U_tip: float        # [m/s] rotor tip speed
    #psy: float          # [-]   flow coefficient = V_axial / U_mean (not really needed as it is set implicitly through V_axial and U_tip, r_mean)
    phi: float          # [-]   stage loading coefficient = cp * delta_Tt_stage / U_mean^2


