class Vehicle:
    """
    Assembles physical subsystems and steps the vehicle forward in time.

    Pipeline per timestep:

        GNC ControlOutput (moment_demand, throttle_demand)
             │
        Actuators.update(commands, dt)  →  actual deflections (with lag/limits)
             │
        Propulsion.update(throttle, dt)  →  thrust force vector
             │
        Aero.update(state, deflections, atmosphere)  →  aero forces/moments
             │
        Dynamics.step(total_forces, total_moments, dt)  →  new state vector
    """

    def __init__(self, dynamics, aero, propulsion, actuators):
        self.dynamics   = dynamics
        self.aero       = aero
        self.propulsion = propulsion
        self.actuators  = actuators

    def step(self, control_output, dt, atmosphere=None):
        # 1. Actuators: convert demanded moments → actual deflections
        deflections = self.actuators.update(control_output.moment_demand, dt)

        # 2. Propulsion: thrust from throttle command
        thrust = self.propulsion.update(control_output.throttle_demand, dt)

        # 3. Aero: forces/moments from current state + deflections
        state = self.dynamics.state
        aero_force, aero_moment = self.aero.update(state, deflections, atmosphere)

        # 4. Sum all forces and moments
        total_force  = thrust + aero_force
        total_moment = aero_moment  # actuator moments folded into aero or added here

        # 5. Integrate dynamics
        self.dynamics.step(total_force, total_moment, dt)

        return self.dynamics.state


# ── build ──
gnc     = GNC(DirectStateNav(), CommandGuidance("rate"), RatePID(...))
vehicle = Vehicle(SixDoF(...), CoefficientAero(...), ConstantThrust(...), TVCActuator(...))

# ── sim loop ──
for t in np.arange(0, t_end, dt):
    control_out = gnc.update(vehicle.dynamics.state, dt, t,
                             rate_cmd=[0, 0.1, 0])

    vehicle.step(control_out, dt, atmosphere)
