from abc import ABC, abstractmethod

from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.gas_model import GasModel


class Component(ABC):
    """
    Base class for any engine component.

    Conceptually, it transforms a FlowState, whose primary quantities of interest are:
      - Tt (total temperature)
      - Pt (total pressure)
      - cp, gamma (thermo properties)
      - m_dot (mass flow)

    specs (performance characteristics) and geometry (physical dimensions) are optional:
    not every component has them defined yet.
    """

    def __init__(self, gas_model: GasModel, name: str = "", specs: object | None = None, geometry: object | None = None):
        self.gas = gas_model
        self.name = name
        self.specs = specs
        self.geometry = geometry

    @abstractmethod
    def process(self, flow: FlowState) -> FlowState:
        """
        Take inlet FlowState -> return outlet FlowState.
        """
        pass
