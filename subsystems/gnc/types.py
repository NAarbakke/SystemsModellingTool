"""
Shared data types that flow between GNC subsystems.

Data flows in one direction through the pipeline each timestep:

    sim state vector
         |
    NavigationBase.update()  →  NavState
                                    |
                          GuidanceBase.update()  →  GuidanceCommand
                                                          |
                                             ControllerBase.update()  →  ControlOutput
                                                                               |
                                                                       vehicle / actuator model
"""

from dataclasses import dataclass, field
import numpy as np


@dataclass
class NavState:
    """
    Estimated (or truth) navigation state.
    Produced by Navigation, consumed by Guidance and Control.

    Convention: body frame for velocities and rates; NED for position/velocity_ned.
    All angles in radians.
    """
    position:       np.ndarray = field(default_factory=lambda: np.zeros(3))
    # [x, y, z] m from origin (flat-Earth) or [lat_rad, lon_rad, alt_m]

    velocity_body:  np.ndarray = field(default_factory=lambda: np.zeros(3))
    # [u, v, w] m/s — forward, right, down in body frame

    velocity_ned:   np.ndarray = field(default_factory=lambda: np.zeros(3))
    # [vN, vE, vD] m/s — north, east, down

    attitude:       np.ndarray = field(default_factory=lambda: np.zeros(3))
    # [phi, theta, psi] rad — roll, pitch, yaw (3-2-1 Euler)

    body_rates:     np.ndarray = field(default_factory=lambda: np.zeros(3))
    # [p, q, r] rad/s — roll rate, pitch rate, yaw rate

    timestamp:      float = 0.0
    # simulation time at which this state was valid (s)


@dataclass
class GuidanceCommand:
    """
    Reference commands produced by Guidance, consumed by the Controller.

    `mode` selects which fields the controller should close a loop on:
      "rate"     → track target_rates  (inner loop only)
      "attitude" → track target_attitude → cascade into rate loop
    """
    mode:             str         = "rate"

    target_rates:     np.ndarray  = field(default_factory=lambda: np.zeros(3))
    # [p_cmd, q_cmd, r_cmd] rad/s

    target_attitude:  np.ndarray  = field(default_factory=lambda: np.zeros(3))
    # [phi_cmd, theta_cmd, psi_cmd] rad

    target_throttle:  float       = 0.0
    # normalised 0-1; passed through to vehicle — not used by base PID


@dataclass
class ControlOutput:
    """
    Actuator demands produced by the Controller.
    Consumed by the vehicle / actuator model (outside GNC).
    """
    moment_demand:   np.ndarray = field(default_factory=lambda: np.zeros(3))
    # [Mx, My, Mz] N·m — body-frame moment demands

    force_demand:    np.ndarray = field(default_factory=lambda: np.zeros(3))
    # [Fx, Fy, Fz] N  — body-frame force demands (e.g. thrust vector offset)

    throttle_demand: float      = 0.0
    # normalised 0-1 — passed through from GuidanceCommand.target_throttle
