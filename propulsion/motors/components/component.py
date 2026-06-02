from abc import ABC, abstractmethod

from propulsion.motors.helpers.flow_state import FlowState
from propulsion.motors.helpers.gas_model import GasModel


class Component(ABC):
    """
    Base class for any engine component.

    Conceptually, it transforms a FlowState, whose primary quantities of interest are:
      - Tt (total temperature)
      - Pt (total pressure)
      - cp, gamma (thermo properties)
      # not use - m_dot (mass flow)
    """

    def __init__(self, gas_model: GasModel, name: str = ""):
        self.gas = gas_model
        self.name = name
        self.last_inlet: FlowState | None = None
        self.last_exit: FlowState | None = None

    @abstractmethod
    def process(self, flow: FlowState) -> FlowState:
        """
        Take inlet FlowState -> return outlet FlowState.
        """
        pass
