"""
DirectStateNav — navigation that reads truth directly from the simulator
state vector.

This is the simplest possible navigation: no sensor noise, no estimation,
no latency. It is the correct starting point for a simulator where you
want to test guidance and control in isolation before adding sensor models.

State vector layout
-------------------
The mapping from flat array indices to physical quantities is configurable
via StateVectorLayout. The default matches a common 12-state flat-Earth model:

  Index   Field         Units
  -----   -----------   -----
    0     u             m/s   (body-frame forward velocity)
    1     v             m/s   (body-frame lateral velocity, +right)
    2     w             m/s   (body-frame vertical velocity, +down)
    3     p             rad/s (roll rate)
    4     q             rad/s (pitch rate)
    5     r             rad/s (yaw rate)
    6     phi           rad   (roll angle)
    7     theta         rad   (pitch angle)
    8     psi           rad   (yaw angle)
    9     x             m     (north / inertial x)
   10     y             m     (east  / inertial y)
   11     z             m     (down  / inertial z, positive down)

Override indices by passing a custom StateVectorLayout if your simulator
uses a different ordering.
"""

from dataclasses import dataclass
import numpy as np

from .base import NavigationBase
from ..types import NavState


@dataclass
class StateVectorLayout:
    """
    Index mapping from the flat simulation state vector to named fields.
    Change the defaults here to match your simulator's state ordering.
    """
    # Body-frame velocities
    u:     int = 0
    v:     int = 1
    w:     int = 2
    # Body-frame angular rates
    p:     int = 3
    q:     int = 4
    r:     int = 5
    # Euler angles (3-2-1: roll, pitch, yaw)
    phi:   int = 6
    theta: int = 7
    psi:   int = 8
    # Position (flat-Earth NED: north, east, down)
    x:     int = 9
    y:     int = 10
    z:     int = 11


class DirectStateNav(NavigationBase):
    """
    Navigation that reads truth directly from the simulation state vector.

    Usage
    -----
        layout = StateVectorLayout()          # use defaults, or customise
        nav = DirectStateNav(layout)

        # each timestep:
        nav_state = nav.update(state_vector, t)

    Parameters
    ----------
    layout : StateVectorLayout
        Index mapping; defaults to the 12-state flat-Earth convention above.
    """

    def __init__(self, layout: StateVectorLayout = None):
        self.layout = layout or StateVectorLayout()

    def update(self, state_vector, t: float = 0.0) -> NavState:
        """
        Extract a NavState from the flat state vector.

        Parameters
        ----------
        state_vector : array-like, length >= 12
            The simulator's current state array.
        t : float
            Current simulation time in seconds.
        """
        sv = np.asarray(state_vector, dtype=float)
        L  = self.layout

        velocity_body = np.array([sv[L.u], sv[L.v], sv[L.w]])
        body_rates    = np.array([sv[L.p], sv[L.q], sv[L.r]])
        attitude      = np.array([sv[L.phi], sv[L.theta], sv[L.psi]])
        position      = np.array([sv[L.x], sv[L.y], sv[L.z]])

        # Rotate body velocity to NED for convenience (Euler 3-2-1)
        velocity_ned = _body_to_ned(velocity_body, attitude)

        return NavState(
            position      = position,
            velocity_body = velocity_body,
            velocity_ned  = velocity_ned,
            attitude      = attitude,
            body_rates    = body_rates,
            timestamp     = t,
        )


# ── helpers ──────────────────────────────────────────────────────────────────

def _body_to_ned(v_body: np.ndarray, euler: np.ndarray) -> np.ndarray:
    """Rotate a vector from body frame to NED using 3-2-1 Euler angles."""
    phi, theta, psi = euler
    cphi, sphi     = np.cos(phi),   np.sin(phi)
    cth,  sth      = np.cos(theta), np.sin(theta)
    cpsi, spsi     = np.cos(psi),   np.sin(psi)

    # Direction-cosine matrix body → NED (transpose of NED → body)
    Cbn = np.array([
        [cth*cpsi,  sphi*sth*cpsi - cphi*spsi,  cphi*sth*cpsi + sphi*spsi],
        [cth*spsi,  sphi*sth*spsi + cphi*cpsi,  cphi*sth*spsi - sphi*cpsi],
        [-sth,      sphi*cth,                   cphi*cth                 ],
    ])
    return Cbn @ v_body
