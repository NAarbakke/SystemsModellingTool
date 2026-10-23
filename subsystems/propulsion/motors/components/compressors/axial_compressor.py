from dataclasses import replace

import numpy as np
from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.total_to_static import static_from_mach, static_from_mass_flow, static_from_velocity
from subsystems.propulsion.motors.components.compressors.axial_compressor_specs import AxialCompressorSpecs
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.components.compressors.annulus_type import AnnulusType


class AxialCompressor(Component):
    """
    Generic axial compressor
    """
    def __init__(self, specs: AxialCompressorSpecs, geometry: AxialCompressorGeometry, gas_model: GasModel, name: str = "Axial compressor"):
        super().__init__(gas_model, name, specs, geometry)

    def face(self, flow: FlowState) -> FlowState:
        """
        Static state and mass flow at the compressor face.
        First rotor in the engine (flow without m_dot): the compressor sets the face velocity (V_axial = phi * U_mean,
        or from M_face), and with it how much air the engine swallows.
        Behind a fan (flow with m_dot): the core flow is already set, so the face Mach follows from continuity.
        """
        if flow.m_dot is not None:
            return static_from_mass_flow(flow, flow.m_dot, self.geometry.A_face, self.gas)

        if self.specs.phi is not None:
            U_mean = self.specs.U_tip * self.geometry.r_mean / self.geometry.r_tip
            V_axial = self.specs.phi * U_mean
            face = static_from_velocity(flow, V_axial, self.gas)
        else:
            face = static_from_mach(flow, self.specs.M_face, self.gas)
        m_dot = face.rho * self.geometry.A_face * face.V

        out = replace(face, m_dot=m_dot)

        return out

    def process(self, flow: FlowState) -> FlowState:
        """Compress the face state (from face()) to the compressor exit."""
        Tt_in = flow.Tt
        Pt_in = flow.Pt

        # First guess with inlet gamma, then one pass with gamma and cp at the mean temperature
        gamma_in = self.gas.gamma(Tt_in)
        Tt_out = Tt_in * self.specs.PR ** ((gamma_in - 1.0) / (gamma_in * self.specs.eta_poly))
        Tt_mean = 0.5 * (Tt_in + Tt_out)
        gamma_mean = self.gas.gamma(Tt_mean)
        cp_mean = self.gas.cp(Tt_mean)

        Tt_out = Tt_in * self.specs.PR ** ((gamma_mean - 1.0) / (gamma_mean * self.specs.eta_poly))
        Pt_out = Pt_in * self.specs.PR
        work = cp_mean * (Tt_out - Tt_in)       # work per kg = delta h (positive: power input)

        self.last_work_per_kg = work

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            m_dot=flow.m_dot)

        return out


    def compute_geometry(self, flow_in: FlowState, flow_out: FlowState) -> AxialCompressorSizing:
        """
        March stage by stage until the stages deliver the required total temperature rise.
        Constant axial velocity is assumed, so the annulus area shrinks with 1/density
        (total density, Pt and Tt linked by the polytropic relation).
        """
        
        Tt_in = flow_in.Tt
        delta_Tt_comp = flow_out.Tt - Tt_in
        cp = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)
        omega = self.specs.U_tip / self.geometry.r_tip                    # [rad/s] shaft speed, set by the inlet tip speed

        Tt = Tt_in
        L_stage, r_hub_stage, r_tip_stage = [], [], []
        while Tt - Tt_in < delta_Tt_comp:
            # Annulus at stage entry
            A = self.geometry.A_face * (Tt / Tt_in) ** (1 - gamma * self.specs.eta_poly / (gamma - 1))
            r_hub, r_tip = self.solve_annulus(A)
            h = r_tip - r_hub
            r_hub_stage.append(float(r_hub))
            r_tip_stage.append(float(r_tip))

            # Stage = rotor + gap + stator + gap, chords from the local blade span
            c_rotor = h / self.geometry.AR_rotor
            c_stator = h / self.geometry.AR_stator
            L_stage.append(float((c_rotor + c_stator) * (1 + self.geometry.IRG_to_chord)))

            # Stage temperature rise from the stage loading coefficient at the local mean radius
            U_mean = omega * (r_hub + r_tip) / 2
            Tt += self.specs.psi * U_mean**2 / cp

        L = float(sum(L_stage)) + self.geometry.IGV_axial_chord_length + self.geometry.EGV_axial_chord_length

        out = AxialCompressorSizing(
            n_stages=len(L_stage),
            L_stage=L_stage,
            r_hub_stage=r_hub_stage,
            r_tip_stage=r_tip_stage,
            L=L)

        return out


    def solve_annulus(self, A: float) -> tuple[float, float]:
        """Hub and tip radius [m] for annulus area A [m^2], per the geometry's annulus type"""
        solver = {
            AnnulusType.CONSTANT_TIP: self.constant_tip_radius,
            AnnulusType.CONSTANT_MEAN: self.constant_mean_radius,
            AnnulusType.CONSTANT_HUB: self.constant_hub_radius,
        }[self.geometry.annulus_type]
        return solver(A)

    def constant_tip_radius(self, A: float) -> tuple[float, float]:
        r_tip = self.geometry.r_tip
        r_hub = np.sqrt(r_tip**2 - A / np.pi)
        return r_hub, r_tip

    def constant_mean_radius(self, A: float) -> tuple[float, float]:
        r_mean = self.geometry.r_mean
        h = A / (2 * np.pi * r_mean)        # A = 2 pi r_mean h
        return r_mean - h / 2, r_mean + h / 2

    def constant_hub_radius(self, A: float) -> tuple[float, float]:
        r_hub = self.geometry.r_hub
        r_tip = np.sqrt(r_hub**2 + A / np.pi)
        return r_hub, r_tip
