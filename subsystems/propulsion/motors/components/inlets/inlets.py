from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.gas_model import GasModel


class Inlet(Component):
    """
    Simple inlet: preserves Tt, drops Pt by a pressure recovery factor PR_inlet.
    """

    def __init__(self, specs: InletSpecs, gas_model: GasModel, name: str = "inlet"):
        super().__init__(gas_model, name)
        self.PR_inlet = specs.PR

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        V_in = flow.V
        rho_in = flow.rho

        Tt_out = Tt_in
        Pt_out = self.PR_inlet * Pt_in
        V_out = V_in        #for now
        rho_out = rho_in    #for now

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            V=V_out,
            rho=rho_out)

        self.last_exit = out
        return out  # self.last_exit? insstead
