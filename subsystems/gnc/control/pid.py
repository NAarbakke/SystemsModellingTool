"""
RatePID — three-axis PID rate controller.

Adapted from the RateController in gnc_generic.py and extended with:
  - Attitude outer loop (cascaded P controller → rate inner loop)
  - Typed interface via GuidanceCommand / NavState / ControlOutput
  - Per-axis gain support

Architecture
------------
  "rate" mode (single loop):

      rate_error = target_rates - body_rates
           ↓ PID
      moment_demand

  "attitude" mode (cascaded):

      attitude_error = target_attitude - attitude   (with yaw wrap)
           ↓ P gain  (attitude_gains)
      rate_command  (inner loop setpoint)
           ↓ PID
      moment_demand

The attitude outer loop is a simple proportional controller — this is
standard for flight control (a P-only outer loop is stable and sufficient
when combined with a well-tuned inner rate loop).
"""

import numpy as np

from .base import ControllerBase
from ..types import GuidanceCommand, NavState, ControlOutput


class RatePID(ControllerBase):
    """
    Three-axis PID body-rate controller with optional attitude outer loop.

    Parameters
    ----------
    kp, ki, kd : scalar or length-3 array
        PID gains for the rate (inner) loop.
        Scalar → same gain on all three axes.
    max_moment : scalar or length-3 array
        Output clamp [N·m]. Also sets integral windup limit to 2× this value.
    attitude_gains : scalar or length-3 array, optional
        Proportional gains for the attitude outer loop (rad/s per rad).
        Only used when GuidanceCommand.mode == "attitude".
        Default 2.0 on all axes is a good starting point.
    filter_alpha : float
        Derivative low-pass filter coefficient (0-1).
        Lower = smoother but more lag. Default 0.1.
    """

    def __init__(
        self,
        kp,
        ki,
        kd,
        max_moment,
        attitude_gains=2.0,
        filter_alpha: float = 0.1,
    ):
        self.kp = np.atleast_1d(np.float64(kp)) * np.ones(3)
        self.ki = np.atleast_1d(np.float64(ki)) * np.ones(3)
        self.kd = np.atleast_1d(np.float64(kd)) * np.ones(3)
        self.max_moment     = np.atleast_1d(np.float64(max_moment)) * np.ones(3)
        self.attitude_gains = np.atleast_1d(np.float64(attitude_gains)) * np.ones(3)
        self.alpha          = float(filter_alpha)

        self.integral_limit = self.max_moment * 2.0
        self._integral  = np.zeros(3)
        self._prev_error = np.zeros(3)
        self._prev_deriv = np.zeros(3)

    # ── public interface ──────────────────────────────────────────────────────

    def update(
        self,
        command:   GuidanceCommand,
        nav_state: NavState,
        dt:        float,
    ) -> ControlOutput:
        """
        Run one control step.

        Returns a ControlOutput with moment_demand [Mx, My, Mz] N·m.
        force_demand and throttle_demand are passed through from the command.
        """
        rate_cmd = self._resolve_rate_command(command, nav_state)
        moment   = self._rate_pid(rate_cmd, nav_state.body_rates, dt)

        return ControlOutput(
            moment_demand   = moment,
            force_demand    = np.zeros(3),
            throttle_demand = command.target_throttle,
        )

    def reset(self):
        """Reset integrators and filter state."""
        self._integral[:]   = 0.0
        self._prev_error[:]  = 0.0
        self._prev_deriv[:]  = 0.0

    # ── private helpers ───────────────────────────────────────────────────────

    def _resolve_rate_command(
        self, command: GuidanceCommand, nav_state: NavState
    ) -> np.ndarray:
        """
        Return the rate setpoint for the inner loop.

        "rate"     → use guidance target_rates directly.
        "attitude" → run P outer loop: attitude error → rate command.
        """
        if command.mode == "rate":
            return command.target_rates.copy()

        if command.mode == "attitude":
            att_error = command.target_attitude - nav_state.attitude
            # Wrap yaw error to [-π, π]
            att_error[2] = _wrap_angle(att_error[2])
            return self.attitude_gains * att_error

        raise ValueError(f"Unknown guidance mode '{command.mode}'")

    def _rate_pid(
        self,
        rate_cmd: np.ndarray,
        body_rates: np.ndarray,
        dt: float,
    ) -> np.ndarray:
        """PID on rate error → moment demand."""
        error = rate_cmd - body_rates

        # Integral with anti-windup clamp
        self._integral += error * dt
        self._integral  = np.clip(self._integral, -self.integral_limit, self.integral_limit)

        # Derivative with low-pass filter
        if dt > 0:
            raw_d = (error - self._prev_error) / dt
        else:
            raw_d = np.zeros(3)
        self._prev_deriv = self.alpha * raw_d + (1.0 - self.alpha) * self._prev_deriv
        self._prev_error = error.copy()

        moment = self.kp * error + self.ki * self._integral + self.kd * self._prev_deriv
        return np.clip(moment, -self.max_moment, self.max_moment)


# ── helpers ───────────────────────────────────────────────────────────────────

def _wrap_angle(angle: float) -> float:
    """Wrap an angle to the range [-π, π]."""
    return (angle + np.pi) % (2 * np.pi) - np.pi
