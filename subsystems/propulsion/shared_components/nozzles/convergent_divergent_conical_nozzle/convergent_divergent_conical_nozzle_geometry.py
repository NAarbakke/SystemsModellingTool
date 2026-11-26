from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ConvergentDivergentConicalNozzleGeometry:
    d_throat: float             # [m]
    d_exit: float               # [m]
    half_cone_angle: float      # [degrees]

    @property
    def A_throat(self) -> float:
        return np.pi * (self.d_throat / 2)**2

    @property
    def A_exit(self) -> float:
        return np.pi * (self.d_exit / 2)**2

    @property
    def exp_ratio(self) -> float:
        return self.A_exit / self.A_throat
