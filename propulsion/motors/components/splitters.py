from propulsion.motors.components.component import Component
from propulsion.motors.helpers.gas_model import GasModel
from propulsion.motors.helpers.flow_state import FlowState


class CoreSplitter(Component):
    def __init__(self, bypass_ratio: float, gas_model: GasModel, name: str = "core_splitter") -> None:
        super().__init__(gas_model, name)
        self.beta = bypass_ratio

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        rho_in = flow.rho
        V_in = flow.V
        m_dot_in = flow.m_dot

        m_dot_total = m_dot_in
        m_dot_core = m_dot_total / (1 + self.beta)

        out = FlowState(
            Tt=Tt_in,
            Pt=Pt_in,
            rho=rho_in,
            V=V_in,
            m_dot=m_dot_core)

        return out



class BypassSplitter(Component):
    def __init__(self, bypass_ratio: float, gas_model: GasModel, name: str = "bypass_splitter") -> None:
        super().__init__(gas_model, name)
        self.beta = bypass_ratio

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        rho_in = flow.rho
        V_in = flow.V
        m_dot_in = flow.m_dot

        m_dot_total = m_dot_in
        m_dot_bypass = self.beta * m_dot_total / (1 + self.beta)

        out = FlowState(
            Tt=Tt_in,
            Pt=Pt_in,
            rho=rho_in,
            V=V_in,
            m_dot=m_dot_bypass)

        return out
