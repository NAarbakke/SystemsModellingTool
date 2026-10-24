from __future__ import annotations
from typing import TYPE_CHECKING
from subsystems.propulsion.motors.helpers.flow_state import FlowState
import numpy as np

if TYPE_CHECKING:
    from environment.atmosphere.atmospheric_conditions import AtmosphericConditions
    from subsystems.propulsion.motors.helpers.gas_model import GasModel


def static_to_total(static: AtmosphericConditions, M: float, gas: GasModel) -> FlowState:
    """Total state of air at static T, P, rho moving at Mach M (reverse of total_to_static)"""
    T = static.T
    P = static.P
    gamma = gas.gamma(T)
    R = gas.R
    Tt = T * (1.0 + 0.5 * (gamma - 1.0) * M**2)
    Pt = P * (Tt / T) ** (gamma / (gamma - 1.0))
    rho_t = Pt / (R * Tt)
    V = np.sqrt(gamma * R * T) * M     # speed of sound is a static property: gamma at T

    out = FlowState(
        Tt=Tt,
        Pt=Pt,
        T=T,
        P=P,
        M=M,
        V=V,
        rho=static.rho,
        rho_t=rho_t)

    return out
