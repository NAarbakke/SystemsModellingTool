from dataclasses import dataclass


@dataclass
class InletSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    PR: float           # [-] total pressure recovery (Pt_out / Pt_in)
