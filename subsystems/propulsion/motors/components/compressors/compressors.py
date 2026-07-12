from dataclasses import dataclass
from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from specifications.SKYF.engine import CompressorSpecs, FanSpecs
import numpy as np


@dataclass
class CompressorGeometry:
    r_tip: float
    r_hub: float
#do this??


#add length computatuons based on stage characteristics and count

class AxialCompressor(Component):
    """
    Generic axial compressor
    """
    def __init__(self, specs: CompressorSpecs, gas_model: GasModel, name: str = "compressor"):
        super().__init__(gas_model, name)
        self.PR_comp = specs.PR
        self.eta_poly_comp = specs.eta_poly

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        m_dot = flow.m_dot

        cp_in = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)

        Tt_out = Tt_in * self.PR_comp ** ((gamma - 1.0) / (gamma * self.eta_poly_comp))
        Pt_out = Pt_in * self.PR_comp
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



class Fan(Component):
    """
    Generic fan
    """
    def __init__(self, specs: FanSpecs, gas_model: GasModel, name: str = "fan"):
        super().__init__(gas_model, name)
        self.PR_fan = specs.PR
        self.eta_poly_fan = specs.eta_poly
        self.r_fan_tip = specs.r_tip
        self.r_fan_hub = specs.r_hub

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        rho_in = flow.rho
        V_in = flow.V

        cp_in = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)

        A_fan = np.pi * (self.r_fan_tip**2 - self.r_fan_hub**2)
        m_dot_total = rho_in * A_fan * V_in
        #m_dot = flow.m_dot if computing m_dot in inlet

        Tt_out = Tt_in * self.PR_fan ** ((gamma - 1.0) / (gamma * self.eta_poly_fan))
        Pt_out = Pt_in * self.PR_fan
        cp_out = self.gas.cp(Tt_out)
        #work = cp * (Tt_out - Tt_in)  # work per kg (positive: power input)
        work = cp_out * Tt_out - cp_in * Tt_in

        self.last_work_per_kg = work

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            m_dot=m_dot_total)

        self.last_exit = out
        return out


    #def compute_geometry
