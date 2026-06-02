"""
GNC assembler — wires together Navigation, Guidance, and Control subsystems.

The pipeline per timestep is:

    sim state vector  ──►  Navigation.update()  ──►  NavState
                                                          │
                                               Guidance.update()  ──►  GuidanceCommand
                                                                              │
                                                              Controller.update()  ──►  ControlOutput
                                                                                              │
                                                                              vehicle / actuator model

Quickstart
----------
    from gnc import GNC
    from gnc.navigation import DirectStateNav
    from gnc.guidance   import CommandGuidance
    from gnc.control    import RatePID
    from math import radians

    nav        = DirectStateNav()
    guidance   = CommandGuidance(default_mode="rate")
    controller = RatePID(kp=2.0, ki=0.3, kd=0.5, max_moment=100.0)

    gnc = GNC(nav, guidance, controller)

    # Each simulation timestep:
    control_out = gnc.update(
        state_vector = sim.state,
        dt           = sim.dt,
        t            = sim.t,
        rate_cmd     = [0.0, radians(5), 0.0],   # 5 °/s pitch-up
    )

    vehicle.apply_moments(control_out.moment_demand)
"""

from .navigation.base import NavigationBase
from .guidance.base   import GuidanceBase
from .control.base    import ControllerBase
from .types           import NavState, GuidanceCommand, ControlOutput


class GNC:
    """
    Assembles and runs the GNC pipeline.

    Parameters
    ----------
    navigation : NavigationBase
        Navigation subsystem instance.
    guidance   : GuidanceBase
        Guidance subsystem instance.
    controller : ControllerBase
        Control subsystem instance.

    The assembler does not prescribe which concrete implementations to use —
    swap any subsystem by passing a different object that inherits from the
    appropriate base class.
    """

    def __init__(
        self,
        navigation: NavigationBase,
        guidance:   GuidanceBase,
        controller: ControllerBase,
    ):
        self.navigation = navigation
        self.guidance   = guidance
        self.controller = controller

        # Last computed states — useful for logging / debugging
        self.nav_state:      NavState       = None
        self.guidance_cmd:   GuidanceCommand = None
        self.control_output: ControlOutput  = None

    def update(self, state_vector, dt: float, t: float = 0.0, **guidance_kwargs) -> ControlOutput:
        """
        Run one complete GNC cycle.

        Parameters
        ----------
        state_vector : array-like
            Simulator state array; passed directly to Navigation.update().
        dt : float
            Simulation timestep in seconds.
        t : float
            Current simulation time in seconds (passed to Navigation for timestamps).
        **guidance_kwargs
            Any keyword arguments forwarded to Guidance.update(), e.g.
            rate_cmd, attitude_cmd, throttle_cmd, mode, waypoint, …

        Returns
        -------
        ControlOutput
            Actuator demands to pass to the vehicle model.
        """
        self.nav_state    = self.navigation.update(state_vector, t)
        self.guidance_cmd = self.guidance.update(self.nav_state, **guidance_kwargs)
        self.control_output = self.controller.update(self.guidance_cmd, self.nav_state, dt)
        return self.control_output

    def reset(self):
        """Reset all stateful subsystems (call on mode change or re-initialisation)."""
        self.controller.reset()
        self.nav_state      = None
        self.guidance_cmd   = None
        self.control_output = None
