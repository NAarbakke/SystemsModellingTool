"""
Generic flight vehicle rate controller.

The controller is vehicle-agnostic: it tracks commanded body rates and
outputs moment demands in N·m. A separate actuator model (which you write
for your specific vehicle) converts those moments into physical deflections.

    controller = RateController(kp=2.0, ki=0.3, kd=1.0)
    actuator = TVCActuator(thrust=30000, arm=-2.0, max_defl=radians(5))
    # or: actuator = FinActuator(...)
    # or: actuator = RCSActuator(...)

    moment_demand = controller.update(omega_cmd, omega, dt)
    force, moment = actuator.apply(moment_demand, flight_condition)
"""

import numpy as np


class RateController:
    """
    Three-axis PID rate controller.
    Input: commanded and actual body rates.
    Output: moment demand vector [Mx, My, Mz] in N·m.

    The gains here are angular-acceleration-level gains, not deflection-level.
    This means the same gains work regardless of actuator, as long as the
    moment_authority you pass to the actuator is correct.
    """

    def __init__(self, kp, ki, kd, max_moment, filter_alpha=0.1):
        """
        kp, ki, kd: scalar gains (applied identically to all three axes)
                    or length-3 arrays for per-axis gains
        max_moment: scalar or [Mx_max, My_max, Mz_max] — clamp output
        filter_alpha: derivative low-pass filter (0-1, lower = smoother)
        """
        self.kp = np.atleast_1d(np.float64(kp)) * np.ones(3)
        self.ki = np.atleast_1d(np.float64(ki)) * np.ones(3)
        self.kd = np.atleast_1d(np.float64(kd)) * np.ones(3)
        self.max_moment = np.atleast_1d(np.float64(max_moment)) * np.ones(3)
        self.alpha = filter_alpha

        self.integral = np.zeros(3)
        self.prev_error = np.zeros(3)
        self.prev_deriv = np.zeros(3)
        self.integral_limit = self.max_moment * 2.0

    def update(self, omega_cmd, omega, dt):
        """
        omega_cmd: [p, q, r] commanded body rates (rad/s)
        omega:     [p, q, r] actual body rates (rad/s)
        dt:        timestep (s)
        Returns:   [Mx, My, Mz] moment demand in body frame (N·m)
        """
        error = np.asarray(omega_cmd) - np.asarray(omega)

        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.integral_limit, self.integral_limit)

        raw_d = (error - self.prev_error) / dt if dt > 0 else np.zeros(3)
        self.prev_deriv = self.alpha * raw_d + (1 - self.alpha) * self.prev_deriv
        self.prev_error = error.copy()

        moment = self.kp * error + self.ki * self.integral + self.kd * self.prev_deriv
        return np.clip(moment, -self.max_moment, self.max_moment)

    def reset(self):
        self.integral[:] = 0
        self.prev_error[:] = 0
        self.prev_deriv[:] = 0


# ── Actuator implementations ──
#
# Each takes a moment demand and returns (force_body, moment_body).
# Write one for your vehicle. These three cover most cases.


class TVCActuator:
    """Thrust vector control — gimballed nozzle."""

    def __init__(self, thrust, arm, max_defl):
        """
        thrust:   engine thrust (N)
        arm:      nozzle offset from CG along body x, negative = behind (m)
        max_defl: max gimbal angle (rad)
        """
        self.thrust = thrust
        self.arm = arm
        self.max_defl = max_defl

    def apply(self, moment_demand, **kwargs):
        """Convert moment demand to TVC deflections, return force and moment."""
        T, d = self.thrust, self.arm

        # Invert the moment equation: My = d * (-T sin δ_pitch)
        # so δ_pitch = -arcsin(My / (d * T)), clamped
        max_moment = abs(d * T * np.sin(self.max_defl))
        my = np.clip(moment_demand[1], -max_moment, max_moment)
        mz = np.clip(moment_demand[2], -max_moment, max_moment)

        pitch_defl = -np.arcsin(my / (d * T)) if abs(d * T) > 0 else 0.0
        yaw_defl = np.arcsin(mz / (d * T)) if abs(d * T) > 0 else 0.0

        pitch_defl = np.clip(pitch_defl, -self.max_defl, self.max_defl)
        yaw_defl = np.clip(yaw_defl, -self.max_defl, self.max_defl)

        fx = T * np.cos(pitch_defl) * np.cos(yaw_defl)
        fy = T * np.sin(yaw_defl)
        fz = -T * np.sin(pitch_defl)

        force = np.array([fx, fy, fz])
        moment = np.array([0.0, d * fz, -d * fy])
        return force, moment


class FinActuator:
    """Aerodynamic control surfaces — fins, elevons, rudder, etc."""

    def __init__(self, max_defl):
        """
        max_defl: max fin deflection (rad)

        You must set control_effectiveness before calling apply().
        It's a 3x3 matrix mapping [δ_roll, δ_pitch, δ_yaw] to [Mx, My, Mz],
        scaled by dynamic pressure. Recompute it each step from your aero tables.
        """
        self.max_defl = max_defl
        self.control_effectiveness = np.eye(3)

    def apply(self, moment_demand, q_dyn=1.0, **kwargs):
        """
        Convert moment demand to fin deflections via the effectiveness matrix.
        q_dyn: current dynamic pressure (Pa) — needed because fin effectiveness
               scales with it.
        """
        B = self.control_effectiveness * q_dyn
        try:
            deflections = np.linalg.solve(B, moment_demand)
        except np.linalg.LinAlgError:
            deflections = np.zeros(3)

        deflections = np.clip(deflections, -self.max_defl, self.max_defl)
        moment = B @ deflections
        force = np.zeros(3)  # fins produce mostly moments; add lift/drag if needed
        return force, moment


class RCSActuator:
    """Reaction control system — on/off thrusters with moment arms."""

    def __init__(self, thrust_per_jet, arms):
        """
        thrust_per_jet: force per thruster (N)
        arms: [roll_arm, pitch_arm, yaw_arm] moment arms (m)
        """
        self.thrust = thrust_per_jet
        self.arms = np.asarray(arms)
        self.max_moment = self.thrust * self.arms

    def apply(self, moment_demand, **kwargs):
        """
        Bang-bang: fires thrusters if demand exceeds a deadband.
        Returns discrete moment in the demanded direction.
        """
        deadband = 0.05 * self.max_moment
        moment = np.zeros(3)
        for i in range(3):
            if moment_demand[i] > deadband[i]:
                moment[i] = self.max_moment[i]
            elif moment_demand[i] < -deadband[i]:
                moment[i] = -self.max_moment[i]

        force = np.zeros(3)  # RCS moment couples cancel net force (approximately)
        return force, moment
