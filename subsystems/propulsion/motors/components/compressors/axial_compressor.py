import numpy as np
from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from specifications.SKYF.engine import CompressorSpecs
from subsystems.propulsion.motors.components.compressors.compressor_geometry import AxialCompressorGeometry



    
# put in specs
phi = 0.35      # stage loading coefficient
psy = 0.5       # flow coefficient  = V_axial / U_mean

U_mean = V_axial / psy


# at compressor inlet: 
V_1 = V_axial
T_1 = Tt_1 - V_1 ** 2 / (2 * cp)
P_1 = Pt_1 * (T_1 / Tt_1) ** (gamma / (gamma - 1))
rho_1 = P_1 / (R * T_1)

U_tip = 350     # [m/s]    
W_tip = np.sqrt(V_axial**2 + U_tip**2)      # velocity of flow as seen by blade
M_rel_tip = W_tip / self.gas.a(Tt_in)




def solve_annulus_geometry():
    return #array of r_hub vals at each stage entry


#make ui interface to test values
# node js + plotly, toggleable plots

class AxialCompressor(Component):
    """
    Generic axial compressor
    """
    def __init__(self, specs: CompressorSpecs, geometry: AxialCompressorGeometry, gas_model: GasModel, name: str = "Axial compressor"):
        super().__init__(gas_model, name)
        self.PR_comp = specs.PR
        self.eta_poly_comp = specs.eta_poly
        self.v = geometry.r_hub / geometry.r_tip       # 0.4 - 0.6 at front stage ish
        self.A_inlet = np.pi * geometry.r_tip**2 * (1 - v**2)

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt
        V_in = flow.V
        V_axial = V_in
        #m_dot = flow.m_dot
        m_dot_in = flow.rho * self.A_inlet * V_axial
        m_dot_out = m_dot_in    # for now

        cp_in = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)

        Tt_out = Tt_in * self.PR_comp ** ((gamma - 1.0) / (gamma * self.eta_poly_comp))
        Pt_out = Pt_in * self.PR_comp
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
        

    def compute_geometry(self, specs: CompressorSpecs, geometry: AxialCompressorGeometry) -> AxialCompressorGeometry:
        L_stage = geometry.c_rotor_axial + geometry.c_stator_axial + geometry.IRG 

        r_mean = (geometry.r_tip + geometry.r_hub) / 2
        U_mean = omega * r_mean
        
        delta_Tt_stage = specs.phi * U_mean**2 / self.gas.cp()
        delta_Tt_comp = Tt_out - Tt_in
        n_stages = delta_Tt_comp / delta_Tt_stage
        
        stage_lenghts = []
        for n in n_stages:
            stage_lenghts.append(L_stage)
        L = sum(stage_lenghts) + ... + geometry.IGV + geometry.EGV 

        out = AxialCompressorGeometry(
            L_stage=L_stage,
            L=L,
            n_stages=n_stages)
        
        return out


    def compute_geometry_constant_hub_radius():
    
    def constant_mean_radius():
    
    def constant_tip_radius()
