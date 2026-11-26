from dataclasses import dataclass


@dataclass
class HeatExchangerSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    T_cold_out: float       # [K]    target cold-side (air) outlet temperature
    hot_fluid: str          # [-]    reactor coolant, e.g. "helium"
    T_hot_in: float         # [K]    reactor coolant inlet temperature
    P_hot: float            # [Pa]   reactor coolant loop pressure
    mdot_hot: float         # [kg/s] reactor coolant mass flow rate
    wall_material: str      # [-]    e.g. "inconel_617"
    t_wall: float           # [m]    wall thickness
    n_channels_cold: int    # [-]
    n_channels_hot: int     # [-]
    D_h_cold: float         # [m]    hydraulic diameter, cold channels
    D_h_hot: float          # [m]    hydraulic diameter, hot channels
    n_segments: int         # [-]    axial discretisation segments
