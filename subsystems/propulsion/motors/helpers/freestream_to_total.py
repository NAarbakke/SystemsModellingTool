from typing import TYPE_CHECKING
from subsystems.propulsion.motors.helpers.flow_state import FlowState
import numpy as np

if TYPE_CHECKING:
    from subsystems.propulsion.motors.helpers.gas_model import GasModel


def freestream_to_total(T_0: float, P_0: float, M_0: float, gas: "GasModel") -> FlowState:
    #gamma_0 = self.gas.gamma(T_0)
    #R = self.gas.R
    gamma_0 = gas.gamma(T_0)
    R = gas.R
    Tt_0 = T_0 * (1.0 + 0.5 * (gamma_0 - 1.0) * M_0**2)
    Pt_0 = P_0 * (Tt_0 / T_0) ** (gamma_0 / (gamma_0 - 1.0))
    rho_t_0 = Pt_0 / (R * Tt_0)     #check if can do with total quantities
    #cp_t_0 = self.gas.cp(Tt_0)
    gamma_t_0 = gas.gamma(Tt_0)    #this the way to do it? gamma from total temp?
    V_0 = np.sqrt(gamma_t_0 * R * T_0) * M_0    #not actually total, be aware. but this is good

    out = FlowState(
        Tt=Tt_0,
        Pt=Pt_0,
        V=V_0,
        rho=rho_t_0)

    return out
