from dataclasses import dataclass


@dataclass
class DuctSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    PR_loss: float      # [-] total pressure loss factor (Pt_out / Pt_in)
