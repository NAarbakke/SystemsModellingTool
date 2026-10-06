from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.components.inlets.subsonic_inlet_specs import SubsonicInletSpecs


class SubsonicInlet(Component):
    """
    Simple inlet: preserves Tt, drops Pt by a pressure recovery factor PR_inlet.
    """

    def __init__(self, specs: SubsonicInletSpecs, gas_model: GasModel, name: str = "inlet"):
        super().__init__(gas_model, name)
        self.PR_inlet = specs.PR

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        V_in = flow.V
        rho_in = flow.rho
        rho_t_in = flow.rho_t

        Tt_out = Tt_in
        Pt_out = self.PR_inlet * Pt_in
        V_out = V_in        #for now - need to use continuity in future, hence need mass flow (from nozzle is best)
        rho_out = rho_in    #for now
        rho_t_out = self.PR_inlet * rho_t_in    # Tt unchanged, so rho_t scales with Pt

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            V=V_out,
            rho=rho_out,
            rho_t=rho_t_out)

        self.last_exit = out
        return out  # self.last_exit? insstead
