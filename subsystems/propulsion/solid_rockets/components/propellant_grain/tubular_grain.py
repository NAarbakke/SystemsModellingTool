from dataclasses import dataclass

import numpy as np

from subsystems.propulsion.motors.solid_rockets.components.motor_case.motor_case import MotorCase


@dataclass(frozen=True)
class TubularGrain:
    """Case-bonded cylindrical bore burning radially outward, end faces inhibited."""
    r_in_0: float               # [m] initial bore radius
    L: float                    # [m] grain length
    case: MotorCase             # the grain is cast into this case, which sets its outer radius

    @property
    def r_out(self) -> float:
        """[m] outer grain radius, set by the case bore."""
        return self.case.d_inner / 2

    @property
    def A_cross(self) -> float:
        """[m2] initial cross-sectional (annulus) area."""
        return np.pi * (self.r_out**2 - self.r_in_0**2)

    @property
    def V(self) -> float:
        """[m3] initial grain volume."""
        return self.L * self.A_cross

    @property
    def L_D_ratio(self) -> float:
        """[-] characterises whether erosive burning is an effect."""
        return self.L / (2 * self.r_out)
