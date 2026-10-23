from dataclasses import replace
from typing import TYPE_CHECKING
from subsystems.propulsion.motors.helpers.flow_state import FlowState
import numpy as np

if TYPE_CHECKING:
    from subsystems.propulsion.motors.helpers.gas_model import GasModel


def static_from_velocity(flow: FlowState, V: float, gas: GasModel) -> FlowState:
    """Static state at a station where the flow moves at V [m/s], from its totals (reverse of static_to_total)"""
    cp = gas.cp(flow.Tt)
    gamma = gas.gamma(flow.Tt)
    R = gas.R
    T = flow.Tt - V**2 / (2.0 * cp)
    P = flow.Pt * (T / flow.Tt) ** (gamma / (gamma - 1.0))
    M = V / np.sqrt(gamma * R * T)

    out = replace(flow, T=T, P=P, M=M, V=V, rho=P / (R * T), rho_t=flow.Pt / (R * flow.Tt))

    return out


def static_from_mach(flow: FlowState, M: float, gas: GasModel) -> FlowState:
    """Static state at a station where the flow moves at Mach M, from its totals"""
    gamma = gas.gamma(flow.Tt)
    R = gas.R
    T = flow.Tt / (1.0 + 0.5 * (gamma - 1.0) * M**2)
    P = flow.Pt * (T / flow.Tt) ** (gamma / (gamma - 1.0))
    V = M * np.sqrt(gamma * R * T)

    out = replace(flow, T=T, P=P, M=M, V=V, rho=P / (R * T), rho_t=flow.Pt / (R * flow.Tt))

    return out


def static_from_mass_flow(flow: FlowState, m_dot: float, A: float, gas: GasModel) -> FlowState:
    """
    Static state at a station of area A [m^2] passing m_dot [kg/s], from its totals (subsonic solution).
    Continuity: m_dot = A * Pt * sqrt(gamma / (R * Tt)) * M * (1 + (gamma - 1) / 2 * M^2)^(-(gamma + 1) / (2 * (gamma - 1)))
    """
    gamma = gas.gamma(flow.Tt)
    R = gas.R

    def mass_flow(M: float) -> float:
        return (A * flow.Pt * np.sqrt(gamma / (R * flow.Tt)) * M
                * (1.0 + 0.5 * (gamma - 1.0) * M**2) ** (-(gamma + 1.0) / (2.0 * (gamma - 1.0))))

    if m_dot > mass_flow(1.0):
        raise ValueError(f"{A:.3g} m^2 chokes at {mass_flow(1.0):.3g} kg/s, below the {m_dot:.3g} kg/s it has to pass")

    # Subsonic branch: mass flow rises monotonically with M from 0 to 1, so bisect
    M_low, M_high = 0.0, 1.0
    for _ in range(60):
        M = 0.5 * (M_low + M_high)
        if mass_flow(M) < m_dot:
            M_low = M
        else:
            M_high = M

    out = replace(static_from_mach(flow, M, gas), m_dot=m_dot)

    return out
