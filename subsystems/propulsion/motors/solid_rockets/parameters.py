from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Propellant:
    """Solid propellant formulation and burn-rate law (r_dot = a_coeff * P_chamber**n_coeff)."""
    a_coeff: float              # [m/s] burn rate coefficient (grain composition dependent)
    n_coeff: float              # [-] pressure exponent (grain composition dependent)

    fuel: str                   # NASA CEA thermo database name
    oxidizer: str               # NASA CEA thermo database name
    T_fuel: float               # [K] reactant temperature
    T_oxidizer: float           # [K] reactant temperature
    MR: float                   # [-] mixture ratio passed to CEA

    # Grain composition (mass fractions) and constituent densities [kg/m3]
    f_oxidizer: float
    f_fuel: float
    f_binder: float
    rho_oxidizer: float
    rho_fuel: float
    rho_binder: float

    @property
    def rho_grain(self) -> float:
        """[kg/m3] grain density as mixed."""
        return 1 / ((self.f_oxidizer / self.rho_oxidizer) + (self.f_fuel / self.rho_fuel) + (self.f_binder / self.rho_binder))


@dataclass(frozen=True)
class MotorCase:
    d: float                    # [m] outer diameter
    L: float                    # [m] length, without nozzle
    t_casing: float             # [m] casing wall thickness
    t_liner: float              # [m]
    t_insulation: float         # [m]


@dataclass(frozen=True)
class TubularGrain:
    """Cylindrical bore burning radially outward, end faces inhibited."""
    r_in_0: float               # [m] initial bore radius
    r_out: float                # [m] outer grain radius
    L: float                    # [m] grain length

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


@dataclass(frozen=True)
class NozzleGeometry:
    d_throat: float             # [m]
    d_exit: float               # [m]
    n_nozzle: float             # [-] nozzle efficiency

    @property
    def A_throat(self) -> float:
        return np.pi * (self.d_throat / 2)**2

    @property
    def A_exit(self) -> float:
        return np.pi * (self.d_exit / 2)**2

    @property
    def exp_ratio(self) -> float:
        return self.A_exit / self.A_throat
