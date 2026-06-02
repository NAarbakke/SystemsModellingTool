from propulsion.motors.components.component import Component
from propulsion.motors.helpers.flow_state import FlowState
from propulsion.motors.helpers.gas_model import GasModel


class TurbineStage(Component):
    """
    A single turbine stage, inheriting from Component.
    It uses a stage pressure ratio and polytropic efficiency, acting on *total* quantities Tt, Pt.
    """

    def __init__(self, eta_poly: float, gas_model: GasModel, name: str = "turbine stage"):
        super().__init__(gas_model, name)  # last_inlet, last_exit too?
        #self.PR_stage = PR_stage  # Pt_out / Pt_in
        self.eta_poly = eta_poly

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        cp = flow.cp
        gamma = flow.gamma

        Tt_out = Tt_in * self.PR_stage ** ((gamma - 1.0) * self.eta_poly / gamma)   #not find this way, see notes
        Pt_out = Pt_in * self.PR_stage      #shoudl find from temp drop, not this way
        work = cp * (Tt_in - Tt_out)  # work per kg (positive: power extracted)

        self.last_work_per_kg = work

        # Update thermodynamic properties at new Tt
        cp_out = self.gas.cp(Tt_out)
        gamma_out = self.gas.gamma(Tt_out)

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            # m_dot=flow.m_dot,
            cp=cp_out,
            gamma=gamma_out,
            R=self.gas.R)

        self.last_exit = out
        return out


class CompressorStage(Component):
    """
    A single compressor stage, inheriting from Component.
    It uses a stage pressure ratio and polytropic efficiency, acting on *total* quantities Tt, Pt.
    """

    def __init__(self, PR_comp_stage: float, eta_poly_stage: float, gas_model: GasModel, name: str = "compressor stage"):
        super().__init__(gas_model, name)  # last_inlet, last_exit too?
        self.PR_comp_stage = PR_comp_stage  # Pt_out / Pt_in
        self.eta_poly_stage = eta_poly_stage

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        cp = flow.cp
        gamma = flow.gamma

        Tt_out = Tt_in * self.PR_comp_stage ** ((gamma - 1.0) / (gamma * self.eta_poly_stage))
        Pt_out = Pt_in * self.PR_comp_stage
        work = cp * (Tt_out - Tt_in)  # work per kg (positive: power input)
        # or keep since c_p changes throughout the stage?

        self.last_work_per_kg = work

        # Update thermodynamic properties at new Tt
        cp_out = self.gas.cp(Tt_out)
        gamma_out = self.gas.gamma(Tt_out)

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            # m_dot=flow.m_dot,
            cp=cp_out,
            gamma=gamma_out,
            R=self.gas.R)

        self.last_exit = out
        return out
