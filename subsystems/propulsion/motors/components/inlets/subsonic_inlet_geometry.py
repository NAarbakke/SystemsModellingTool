import numpy as np
from dataclasses import dataclass


@dataclass
class SubsonicInletGeometry:
    """
    Physical dimensions of a subsonic (pitot) inlet.
    No defaults for vehicle values: they come from a vehicle specification.
    """
    r_lip: float        # [m] lip (highlight) radius

    # Derived - computed from the inputs above so they can never disagree
    @property
    def A_lip(self) -> float:
        """Lip (highlight) area [m^2]"""
        return np.pi * self.r_lip**2
