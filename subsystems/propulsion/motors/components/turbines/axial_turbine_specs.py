from dataclasses import dataclass


@dataclass
class AxialTurbineSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    eta_poly: float     # [-] polytropic efficiency
    eta_mech: float     # [-] mechanical (shaft) efficiency
