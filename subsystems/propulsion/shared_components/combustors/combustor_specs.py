from dataclasses import dataclass


@dataclass
class CombustorSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    PR_loss: float      # [-]    total pressure loss factor (Pt_out / Pt_in)
    eta: float          # [-]    combustion efficiency
    LHV: float          # [J/kg] fuel lower heating value
    T_tet: float        # [K]    turbine entry temperature
