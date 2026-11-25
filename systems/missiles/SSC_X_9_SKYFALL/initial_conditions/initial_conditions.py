from dataclasses import dataclass, fields
from typing import Optional
import numpy as np # type: ignore

from tools.calculations.conversion_factors import deg2rad


@dataclass#(frozen=True)
class InitialConditions:    #or make initialConditions3dof, 6doF, 6dofSperical, 6dofOblate?

    #----------State vector----------

    #Velocity components (x, y, z) in body reference frame - uses body frame for 3-DoF model too although system orientation is always aligned with velocity vector 
    u_0_body: float = 1e-6      #avoiding division by 0 initially
    v_0_body: float = 0
    w_0_body: float = 0

    #Angluar velocity components (roll, pitch, yaw) in body reference frame - for 3-DoF model these are ignored
    p_0_body: Optional[float] = None
    q_0_body: Optional[float] = None
    r_0_body: Optional[float] = None

    #Euler angles (roll, pitch, yaw) - for 3-DoF model these are ignored
    phi_0: Optional[float] = None
    theta_0: Optional[float] = None
    psi_0: Optional[float] = None

    #Position components in north, east, down (NED) reference frame 
    x_0_ned: float = 0
    y_0_ned: float = 0
    z_0_ned: float = 0

    @property #makes it accessible like an attribute - rather than calling with parantheses at end, like: .state_vector_0()
    def state_vector_0(self) -> np.ndarray:
        filled_values = [getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None]      #only passes variables that have a value, i.e is not None
        state_vector_0 = np.array(filled_values, dtype=float)
        
        #state_vector_0 = np.array([
         #   self.u_0_body,
          #  self.v_0_body,
           # self.w_0_body,
            #self.p_0_body,
            #self.q_0_body,
            #self.r_0_body,
            #self.phi_0,
            #self.theta_0,
            #self.psi_0,
            #self.x_0_ned,
            #self.y_0_ned,
            #self.z_0_ned])
        
        return state_vector_0

    #----------Force vector----------

    #Relevant forces
    F_drag_0: float = 0
    F_sideforce_0: float = 0
    F_lift_0: float = 0
    F_thrust_x_0_body: float = 0
    F_gravity_z_ned: float = 0

    #Relevant moments
    M_aero_x_0_body: Optional[float] = None
    M_aero_y_0_body: Optional[float] = None
    M_aero_z_0_body: Optional[float] = None

    @property
    def force_vector_0(self) -> np.ndarray:
        filled_values = [getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None]
        force_vector_0 = np.array(filled_values, dtype=float)
        #force_vector_0 = np.array([
         #   self.F_drag_0,
          #  self.F_sideforce_0,
           # self.F_lift_0,
            #self.F_thrust_x_0_body, 
            #self.F_gravity_z_ned,
            #self.M_aero_x_0_body,
            #self.M_aero_y_0_body,
            #self.M_aero_z_0_body])
        
        return force_vector_0




launch_angle = 30                                                               #[deg] 

u_0_body = 1e-6                                                                 #avoiding division by 0
v_0_body = 0
w_0_body = 0

p_0_body = 0 * deg2rad
q_0_body = 0 * deg2rad
r_0_body = 0 * deg2rad

phi_0 = 0 * deg2rad
theta_0 = launch_angle * deg2rad                                                #launch angle
psi_0 = 0 * deg2rad

x_0_ned = 0
y_0_ned = 0
z_0_ned = 0

#m_0 = vehicle_parameters.m_wet

F_drag_0 = 0
F_sideforce_0 = 0
F_lift_0 = 0 
F_thrust_x_0_body = 0
F_gravity_z_ned = 0

M_aero_x_0_body = 0
M_aero_y_0_body = 0
M_aero_z_0_body = 0




initial_conditions_3dof = InitialConditions(
    u_0_body,
    v_0_body,
    w_0_body,

    x_0_ned,
    y_0_ned,
    z_0_ned,

    F_drag_0,
    F_sideforce_0,
    F_lift_0,
    F_thrust_x_0_body,
    F_gravity_z_ned)

