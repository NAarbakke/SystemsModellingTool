from dataclasses import dataclass


@dataclass
class FanSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    PR: float           # [-] total pressure ratio
    eta_poly: float     # [-] polytropic efficiency
    r_tip: float        # [m] tip radius
    r_hub: float        # [m] hub radius
