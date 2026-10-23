from dataclasses import replace

from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.total_to_static import static_from_mach
from subsystems.propulsion.motors.components.compressors.fan_specs import FanSpecs
import numpy as np


class Fan(Component):
    """
    Generic fan
    """
    def __init__(self, specs: FanSpecs, gas_model: GasModel, name: str = "fan"):
        super().__init__(gas_model, name, specs=specs)
        self.PR_fan = specs.PR
        self.eta_poly_fan = specs.eta_poly
        self.r_fan_tip = specs.r_tip
        self.r_fan_hub = specs.r_hub

    def face(self, flow: FlowState) -> FlowState:
        """
        Static state and total mass flow at the fan face.
        The fan sets the face Mach number, and with it how much air the engine swallows.
        """
        A_fan = np.pi * (self.r_fan_tip**2 - self.r_fan_hub**2)
        face = static_from_mach(flow, self.specs.M_face, self.gas)
        m_dot_total = face.rho * A_fan * face.V

        out = replace(face, m_dot=m_dot_total)

        return out

    def process(self, flow: FlowState) -> FlowState:
        """Compress the face state (from face()) to the fan exit."""
        Tt_in = flow.Tt
        Pt_in = flow.Pt

        # First guess with inlet gamma, then one pass with gamma and cp at the mean temperature
        gamma_in = self.gas.gamma(Tt_in)
        Tt_out = Tt_in * self.PR_fan ** ((gamma_in - 1.0) / (gamma_in * self.eta_poly_fan))
        Tt_mean = 0.5 * (Tt_in + Tt_out)
        gamma_mean = self.gas.gamma(Tt_mean)
        cp_mean = self.gas.cp(Tt_mean)

        Tt_out = Tt_in * self.PR_fan ** ((gamma_mean - 1.0) / (gamma_mean * self.eta_poly_fan))
        Pt_out = Pt_in * self.PR_fan
        work = cp_mean * (Tt_out - Tt_in)       # work per kg = delta h (positive: power input)

        self.last_work_per_kg = work

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            m_dot=flow.m_dot)

        return out
