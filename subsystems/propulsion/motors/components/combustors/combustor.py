from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from specifications.SKYF.engine import CombustorSpecs


class Combustor(Component):
    """
    Simple combustor with:
      - total pressure loss PR_loss
      - combustion efficiency eta_comb
      - fuel lower heating value LHV
    You specify T_tet; this solves for fuel/air ratio f.
    """

    def __init__(self, specs: CombustorSpecs, gas_model: GasModel, name: str = "combustor"):
        super().__init__(gas_model, name)
        self.PR_loss = specs.PR_loss
        self.eta_comb = specs.eta
        self.LHV = specs.LHV
        self.T_tet = specs.T_tet
        self.last_fuel_air_ratio: float = 0.0
        self.last_fuel_flow: float = 0.0

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        cp_in = self.gas.cp(Tt_in)
        # Simplified constant cp model for products; you can refine
        cp_out = self.gas.cp(self.T_tet)

        # Solve for fuel/air ratio f (textbook burner equation)
        f = (cp_out * self.T_tet - cp_in * Tt_in) / (self.eta_comb * self.LHV - cp_out * self.T_tet)
        self.last_fuel_air_ratio = f

        m_dot_out = flow.m_dot * (1.0 + f)
        Pt_out = self.PR_loss * Pt_in
        m_dot_fuel = flow.m_dot * f
        self.last_fuel_flow = m_dot_fuel

        out = FlowState(
            Tt=self.T_tet,
            Pt=Pt_out,
            m_dot=m_dot_out)

        self.last_exit = out
        return out
