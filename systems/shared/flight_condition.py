from dataclasses import dataclass
from environment.atmosphere.atmospheric_conditions import AtmosphericConditions
from environment.atmosphere.international_standard_atmosphere import InternationalStandardAtmosphere
from subsystems.propulsion.motors.helpers.gas_model import GasModel


@dataclass(frozen=True)
class FlightCondition:
    """Where and how fast the vehicle flies: altitude, airspeed and the static air around it."""

    h: float                            # [m]   geopotential altitude
    V: float                            # [m/s] true airspeed
    M: float                            # [-]   flight Mach number
    atmosphere: AtmosphericConditions   # static T, P, rho at h

    @classmethod
    def from_altitude(cls, h: float, V: float, isa: InternationalStandardAtmosphere, gas: GasModel) -> "FlightCondition":
        """Flight state at altitude h and airspeed V, with the air taken from the ISA."""
        atmosphere = isa.conditions(h)
        M = V / atmosphere.a(gas)
        return cls(h=h, V=V, M=M, atmosphere=atmosphere)

    @property
    def q(self) -> float:
        """Dynamic pressure [Pa]."""
        q = 0.5 * self.atmosphere.rho * self.V ** 2
        return q
