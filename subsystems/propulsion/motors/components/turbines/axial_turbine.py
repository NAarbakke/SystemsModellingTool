from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.components.turbines.stage import TurbineStage
from subsystems.propulsion.motors.components.turbines.axial_turbine_specs import AxialTurbineSpecs

#add stage length stuff

#Stage based
class Turbine2(Component):
    """
    Generic turbine consisting of a sequence of TurbineStage objects.
    """

    def __init__(self, stages: list[TurbineStage], gas_model: GasModel, name: str = "turbine"):
        super().__init__(gas_model, name)
        self.stages = stages

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        current = flow
        for stage in self.stages:
            current = stage.process(current)
        self.last_exit = current
        return current

    #@property
    #def total_work_per_kg(self) -> float:
     #   return sum(stage.last_work_per_kg for stage in self.stages)

    @property
    def overall_pressure_ratio(self) -> float:
        if not self.stages:
            return 1.0
        Pt_in = self.stages[0].last_inlet.Pt if self.stages[0].last_inlet else None
        Pt_out = self.stages[-1].last_exit.Pt if self.stages[-1].last_exit else None
        if Pt_in is None or Pt_out is None:
            return float("nan")
        return Pt_out / Pt_in



class AxialTurbine(Component):
    def __init__(self, specs: AxialTurbineSpecs, gas_model: GasModel, fan: "Fan" = None, compressor: "Compressor" = None, name: str = ""):
        super().__init__(gas_model, name)
        self.eta_poly = specs.eta_poly
        self.eta_mech = specs.eta_mech
        self.fan = fan
        self.compressor = compressor

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        m_dot = flow.m_dot

        cp = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)

        fan_work = self.fan.last_work_per_kg
        compressor_work = self.compressor.last_work_per_kg
        turbine_work = (fan_work + compressor_work) / self.eta_mech

        Tt_out = Tt_in - (turbine_work / cp)
        Pt_out = Pt_in * (Tt_out / Tt_in)**(gamma / ((gamma - 1) * self.eta_poly))

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            m_dot=m_dot)

        self.last_exit = out
        return out
