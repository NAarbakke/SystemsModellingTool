from dataclasses import dataclass
from subsystems.propulsion.motors.helpers.gas_model import GasModel


@dataclass
class AtmosphericConditions:
    """
    Static state of the air the vehicle flies in (engine station 0).
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/initial_conditions/atmosphere.py).
    """
    T_0: float          # [K]  static temperature
    P_0: float          # [Pa] static pressure

    def a_0(self, gas: GasModel) -> float:
        """Local speed of sound [m/s]."""
        a_0 = (gas.gamma(self.T_0) * gas.R * self.T_0) ** 0.5
        return a_0
