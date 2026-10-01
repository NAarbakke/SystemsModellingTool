import numpy as np
from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.components.compressors.axial_compressor_specs import AxialCompressorSpecs
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.components.compressors.annulus_type import AnnulusType




#make ui interface to test values
# node js + plotly, toggleable plots

class AxialCompressor(Component):
    """
    Generic axial compressor
    """
    def __init__(self, specs: AxialCompressorSpecs, geometry: AxialCompressorGeometry, gas_model: GasModel, name: str = "Axial compressor"):
        super().__init__(gas_model, name)
        self.specs = specs
        self.geometry = geometry
        self.PR = specs.PR
        self.eta_poly = specs.eta_poly
        self.v = geometry.hub_to_tip       
        self.A_inlet = np.pi * geometry.r_tip**2 * (1 - self.v**2)

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        m_dot = flow.m_dot
        #m_dot_in = flow.rho * self.A_inlet * V_axial   # once V_axial comes from the annulus

        cp_in = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)

        Tt_out = Tt_in * self.PR ** ((gamma - 1.0) / (gamma * self.eta_poly))
        Pt_out = Pt_in * self.PR
        cp_out = self.gas.cp(Tt_out)
        #work = cp * (Tt_out - Tt_in)  # work per kg (positive: power input)
        work = cp_out * Tt_out - cp_in * Tt_in      #wrong apparently

        self.last_work_per_kg = work

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out,
            m_dot=m_dot)

        self.last_exit = out
        return out


    def compute_geometry(self, flow_in: FlowState, flow_out: FlowState) -> AxialCompressorSizing:
        """
        March stage by stage until the stages deliver the required total temperature rise.
        Constant axial velocity is assumed, so the annulus area shrinks with 1/density
        (total density, Pt and Tt linked by the polytropic relation).
        """
        specs = self.specs
        geometry = self.geometry
        Tt_in = flow_in.Tt
        delta_Tt_comp = flow_out.Tt - Tt_in
        cp = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)
        omega = specs.U_tip / geometry.r_tip                    # [rad/s] shaft speed, set by the inlet tip speed
        area_exponent = 1 - gamma * self.eta_poly / (gamma - 1)     # A/A_in = (Tt/Tt_in)^area_exponent

        Tt = Tt_in
        L_stage = []
        while Tt - Tt_in < delta_Tt_comp:
            # Annulus at stage entry
            A = self.A_inlet * (Tt / Tt_in) ** area_exponent
            r_hub, r_tip = self.solve_annulus(A)
            h = r_tip - r_hub

            # Stage = rotor + gap + stator + gap, chords from the local blade span
            c_rotor = h / geometry.AR_rotor
            c_stator = h / geometry.AR_stator
            L_stage.append(float((c_rotor + c_stator) * (1 + geometry.IRG_to_chord)))

            # Stage temperature rise from the stage loading coefficient at the local mean radius
            U_mean = omega * (r_hub + r_tip) / 2
            Tt += specs.phi * U_mean**2 / cp

        L = float(sum(L_stage)) + geometry.IGV_axial_chord_length + geometry.EGV_axial_chord_length

        out = AxialCompressorSizing(
            n_stages=len(L_stage),
            L_stage=L_stage,
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
