"""Abstract base class for all guidance implementations."""

from abc import ABC, abstractmethod
from ..types import NavState, GuidanceCommand


class GuidanceBase(ABC):
    """
    Guidance subsystem interface.

    A guidance implementation receives the current navigation state plus any
    external inputs (pilot commands, mission waypoints, target position, …)
    and produces a GuidanceCommand for the controller to track.

    Concrete implementations:
      CommandGuidance      — passes external rate/attitude setpoints straight through
      WaypointGuidance     — steers toward a sequence of 3-D waypoints (future)
      ProportionalNav      — proportional navigation for pursuit / intercept (future)
    """

    @abstractmethod
    def update(self, nav_state: NavState, **kwargs) -> GuidanceCommand:
        """
        Compute and return guidance commands.

        Parameters
        ----------
        nav_state : NavState
            Current estimated (or truth) navigation state from Navigation.
        **kwargs
            Implementation-specific inputs, e.g. pilot stick inputs,
            target position, mission segment index, …
        """
        ...
