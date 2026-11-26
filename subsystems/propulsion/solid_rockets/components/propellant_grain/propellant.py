from dataclasses import dataclass


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
