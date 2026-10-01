from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from specifications.SKYF.engine import CompressorSpecs


class CentrifugalCompressor(Component):
    def __init__(self, specs: CompressorSpecs, gas_model: GasModel, name: str = ""):
        super().__init__(gas_model, name)
        self.PR = specs.PR
        self.eta_poly = specs.eta_poly

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        m_dot = flow.m_dot

        cp_in = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)

        Tt_out = Tt_in * self.PR ** ((gamma - 1.0) / (gamma * self.eta_poly))
        Pt_out = Pt_in * self.PR
        cp_out = self.gas.cp(Tt_out)
        #work = cp * (Tt_out - Tt_in)  # work per kg (positive: power input)
        work = cp_out * Tt_out - cp_in * Tt_in

        self.last_work_per_kg = work

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            m_dot=m_dot)

        self.last_exit = out
        return out



        #impellor
        # diffuser

