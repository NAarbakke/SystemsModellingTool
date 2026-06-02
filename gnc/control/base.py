"""Abstract base class for all controller implementations."""

from abc import ABC, abstractmethod
from ..types import GuidanceCommand, NavState, ControlOutput


class ControllerBase(ABC):
    """
    Controller subsystem interface.

    A controller receives guidance commands and the current navigation state,
    and produces actuator demands (moments and forces).

    The controller is intentionally vehicle-agnostic: it outputs *demanded*
    moments and forces. A separate actuator model (TVC, fins, RCS, …) that
    lives in the vehicle model converts those demands into physical deflections.

    Concrete implementations:
      RatePID       — three-axis PID rate controller (inner loop)
      AttitudePID   — cascaded attitude + rate PID (outer + inner loops) (future)
      LQR           — linear-quadratic regulator (future)
    """

    @abstractmethod
    def update(self, command: GuidanceCommand, nav_state: NavState, dt: float) -> ControlOutput:
        """
        Compute actuator demands for this timestep.

        Parameters
        ----------
        command   : GuidanceCommand from guidance subsystem
        nav_state : NavState from navigation subsystem
        dt        : timestep in seconds
        """
        ...

    @abstractmethod
    def reset(self):
        """Reset all integrators and filter states (e.g. on mode change)."""
        ...
