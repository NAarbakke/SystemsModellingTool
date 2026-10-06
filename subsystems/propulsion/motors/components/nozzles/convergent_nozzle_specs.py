from dataclasses import dataclass


@dataclass
class ConvergentNozzleSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    eta_isen: float     # [-]   isentropic efficiency
    A_exit: float       # [m^2] exit area
    C_discharge: float  # [-]   discharge coefficient
