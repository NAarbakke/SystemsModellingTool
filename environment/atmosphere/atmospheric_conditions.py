from dataclasses import dataclass
from subsystems.propulsion.motors.helpers.gas_model import GasModel


@dataclass
class AtmosphericConditions:
    """
    Static state of the air the vehicle flies in (engine station 0).
    No defaults: values come from a vehicle specification (e.g. the FlightCondition in specifications/SKYF/flight_state/cruise.py).
    """
    T: float          # [K]  static temperature
    P: float          # [Pa] static pressure
    rho: float 

    def a(self, gas: GasModel) -> float:
        """Local speed of sound [m/s]."""
        a = (gas.gamma(self.T) * gas.R * self.T) ** 0.5
        return a
