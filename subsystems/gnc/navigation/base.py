"""Abstract base class for all navigation implementations."""

from abc import ABC, abstractmethod
from ..types import NavState


class NavigationBase(ABC):
    """
    Navigation subsystem interface.

    A navigation implementation takes raw inputs (sim state vector, sensor
    measurements, etc.) and produces a NavState that the rest of the GNC
    pipeline can work with.

    Concrete implementations:
      DirectStateNav  — reads truth directly from the simulation state vector
      EKFNav          — fuses IMU + GPS measurements (future)
      INSNav          — inertial navigation with drift (future)
    """

    @abstractmethod
    def update(self, *args, **kwargs) -> NavState:
        """
        Process inputs and return the current navigation state.
        The signature is intentionally open: concrete classes declare whatever
        inputs they need (state vector, sensor packets, dt, ...).
        """
        ...
