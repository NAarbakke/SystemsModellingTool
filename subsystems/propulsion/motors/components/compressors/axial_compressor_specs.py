from dataclasses import dataclass


@dataclass
class AxialCompressorSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    The face velocity is set by exactly one of phi or M_face; the other is None.
    """
    PR: float           # [-]   total pressure ratio
    eta_poly: float     # [-]   polytropic efficiency
    #RPM: float          # [revs/min] - instead of U_tip
    U_tip: float        # [m/s] rotor tip speed
    psi: float          # [-]   stage loading coefficient = cp * delta_Tt_stage / U_mean^2
    phi: float | None = None        # [-]   flow coefficient = V_axial / U_mean
    M_face: float | None = None     # [-]   design point face Mach nr

    def __post_init__(self):
        if (self.phi is None) == (self.M_face is None):
            raise ValueError("AxialCompressorSpecs: set exactly one of phi or M_face")
