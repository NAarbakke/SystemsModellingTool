from dataclasses import dataclass


@dataclass
class CentrifugalCompressorSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    PR: float           # [-] total pressure ratio
    eta_poly: float     # [-] polytropic efficiency
