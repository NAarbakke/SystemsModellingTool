import numpy as np
from numpy.matlib import sqrt
from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from specifications.SKYF.engine import CoreNozzleSpecs, BypassNozzleSpecs


#class ConvergentDivergentNozzle:

#class DeLavalNozzle:



class ConvergentNozzle(Component):
    """
    Simple convergent nozzle with isentropic efficiency.
    """

    def __init__(self, specs: CoreNozzleSpecs | BypassNozzleSpecs, P_atm: float, gas_model: GasModel, name: str = "convergent nozzle"):
        super().__init__(gas_model, name)
        self.eta_isen = specs.eta_isen
        self.thoat_area = specs.area
        self.exit_area = specs.area
        self.C_discharge = specs.C_discharge
        self.P_atm = P_atm

    def process(self, flow: FlowState) -> FlowState:
        """
        Expand from inlet total state to ambient (or choke).
        Returns exit FlowState with static quantities and velocity.
        """
        self.last_inlet = flow
        Tt_in = flow.Tt
        Pt_in = flow.Pt

        cp = self.gas.cp(Tt_in)
        gamma = self.gas.gamma(Tt_in)
        R = self.gas.R

        # critical pressure ratio (P_c / P*) = (Pt_in / P*)
        PR_crit = ((gamma + 1) / 2)**(gamma / (gamma - 1))

        if (Pt_in / self.P_atm) > PR_crit:
            # choked, so M_exit = 1 = M_throat
            M_exit = 1.0
            #T_throat = Tt_in * (2 / (gamma + 1)) # = T_exit
            #P_throat = Pt_in * (2 / (gamma + 1))**(gamma / (gamma - 1))
            #P_exit = P_throat # > P_atm
            T_exit = Tt_in / (1.0 + 0.5 * (gamma - 1.0) * M_exit**2)
            cp_exit = self.gas.cp(T_exit)
            P_exit = Pt_in / ((1.0 + 0.5 * (gamma - 1.0) * M_exit**2)**(gamma / (gamma - 1)))
            V_exit_ideal = np.sqrt(2.0 * (cp * Tt_in - cp_exit * T_exit))
            #V_exit_ideal = np.sqrt(gamma * R * T_thoat)   # alternative eq.    ###use updated R(T_throat)
            V_exit = np.sqrt(self.eta_isen) * V_exit_ideal # = C_velocity * V_exit_ideal, where C_velocity = 0.92 - 0.98
            #m_dot = ((Pt_in * A_throat) / np.sqrt(Tt_in)) * np.sqrt(gamma / R) * (2 / (gamma + 1))**((gamma + 1) / (2 * (gamma - 1)))
        else:
            # unchoked, so P_exit = P_atm
            P_exit = self.P_atm
            M_exit = np.sqrt((2 / (gamma - 1)) * ((Pt_in / P_exit)**((gamma - 1) / gamma) - 1))
            #T_exit = Tt_in * (P_exit / Pt_in) ** ((gamma - 1.0) / gamma)   #alternative eq.
            T_exit = Tt_in / (1.0 + 0.5 * (gamma - 1.0) * M_exit**2)
            cp_exit = self.gas.cp(T_exit)
            V_exit_ideal = np.sqrt(2.0 * (cp * Tt_in - cp_exit * T_exit))
            #V_exit_ideal = np.sqrt(2 * cp * Tt_in * (1 - (P_exit / Pt_in)**((gamma - 1) / gamma)))
            #V_exit_ideal = M_exit * np.sqrt(gamma * R * T_exit)    #alternative eq.    #use updated R
            V_exit = np.sqrt(self.eta_isen) * V_exit_ideal
            #m_dot = rho_exit * V_exit * A_throat
            #m_dot = ((Pt_in * A_throat) / np.sqrt(R * Tt_in)) * M_exit * np.sqrt(gamma) * (1 + 0.5 * (gamma - 1) * M_exit**2)**(- (gamma + 1) / (2 * (gamma - 1)))

        rho_exit = P_exit / (R * T_exit)
        #A_needed = m_dot / (rho_exit * V_exit)
        # You can compare A_needed vs self.area for consistency
        m_dot_actual = self.C_discharge * flow.m_dot

        out = FlowState(
            Tt=Tt_in,
            Pt=Pt_in,
            m_dot=m_dot_actual,
            T=T_exit,
            P=P_exit,
            rho=rho_exit,
            V=V_exit,
            M=M_exit)

        self.last_exit = out
        return out
