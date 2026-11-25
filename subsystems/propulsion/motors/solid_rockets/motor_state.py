from dataclasses import dataclass

from subsystems.propulsion.shared.flow_state import FlowState


@dataclass
class MotorState:
    """
    Complete motor snapshot at a single timestep: the flow state at each
    key station of the motor (chamber, throat, exit) plus the grain
    regression state and derived performance quantities.
    """
    time: float                     # Elapsed time [s]
    chamber: FlowState              # Chamber conditions
    throat: FlowState               # Nozzle throat conditions
    exit: FlowState                 # Nozzle exit plane conditions

    # Grain regression state
    r_burn: float               # Regression depth [m]
    A_burn: float               # Burn area [m^2]
    r_dot_burn: float           # Burn rate [m/s]

    # Performance
    c_star: float               # Characteristic velocity [m/s]
