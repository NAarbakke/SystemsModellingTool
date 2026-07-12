"""
CommandGuidance — direct command / manual setpoint guidance.

This is the simplest guidance law: an external source (pilot, autopilot
outer loop, test script) supplies rate or attitude setpoints, and
CommandGuidance passes them straight to the controller unchanged.

It is the correct starting point for:
  - Piloted simulation (stick inputs → rate commands)
  - Step-response testing of the control loop
  - Any scenario where you want to bypass trajectory planning

Usage
-----
    guidance = CommandGuidance(mode="rate")

    # Fly level with a 5 °/s pitch-up command:
    from math import radians
    cmd = guidance.update(nav_state, rate_cmd=[0, radians(5), 0])

    # Or hold an attitude (requires controller to support "attitude" mode):
    from math import radians
    cmd = guidance.update(nav_state,
                          mode="attitude",
                          attitude_cmd=[0, radians(5), 0])
"""

import numpy as np

from .base import GuidanceBase
from ..types import NavState, GuidanceCommand


class CommandGuidance(GuidanceBase):
    """
    Passes external setpoints directly to the controller with no modification.

    Parameters
    ----------
    default_mode : str
        "rate" or "attitude" — used when no `mode` kwarg is supplied to update().
    """

    def __init__(self, default_mode: str = "rate"):
        if default_mode not in ("rate", "attitude"):
            raise ValueError("default_mode must be 'rate' or 'attitude'")
        self.default_mode = default_mode

    def update(
        self,
        nav_state: NavState,
        rate_cmd=None,
        attitude_cmd=None,
        throttle_cmd: float = 0.0,
        mode: str = None,
    ) -> GuidanceCommand:
        """
        Parameters
        ----------
        nav_state : NavState
            Current nav state (unused here, but available for subclasses or
            limit-checking extensions).
        rate_cmd : array-like [p, q, r] rad/s, optional
            Commanded body rates. Used when mode == "rate".
        attitude_cmd : array-like [phi, theta, psi] rad, optional
            Commanded Euler angles. Used when mode == "attitude".
        throttle_cmd : float, optional
            Normalised throttle demand 0-1.
        mode : str, optional
            Override the instance default_mode for this call.
        """
        active_mode = mode if mode is not None else self.default_mode

        target_rates    = np.asarray(rate_cmd,    dtype=float) if rate_cmd    is not None else np.zeros(3)
        target_attitude = np.asarray(attitude_cmd, dtype=float) if attitude_cmd is not None else np.zeros(3)

        return GuidanceCommand(
            mode             = active_mode,
            target_rates     = target_rates,
            target_attitude  = target_attitude,
            target_throttle  = float(throttle_cmd),
        )
