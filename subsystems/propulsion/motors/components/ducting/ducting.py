from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from specifications.SKYF.engine import DuctSpecs

class Duct(Component):
    def __init__(self, specs: DuctSpecs, gas_model: GasModel, name: str = "duct"):
        super().__init__(gas_model, name)
        self.PR_loss = specs.PR_loss

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        m_dot = flow.m_dot

        Tt_out = Tt_in
        Pt_out = self.PR_loss * Pt_in

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            m_dot=m_dot)

        self.last_exit = out
        return out
