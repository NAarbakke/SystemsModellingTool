from dataclasses import dataclass


@dataclass
class BlackBoxReactorSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    PR_loss: float      # [-] total pressure loss factor (Pt_out / Pt_in)
    T_tet: float        # [K] turbine entry temperature (air heated to this)
