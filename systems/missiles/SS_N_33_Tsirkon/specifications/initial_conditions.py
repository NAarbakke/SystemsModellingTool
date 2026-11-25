import numpy as np # type: ignore
from systems.missiles.SS_N_33_Tsirkon.specifications import vehicle_parameters
from tools.calculations.conversion_factors import deg2rad

#Initial conditions - may be loaded from an aircraft trim routine 
launch_angle = 80                       #try modify                                        #[deg] 

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

F_drag = 0
F_sideforce = 0
F_lift = 0 
F_thrust_x_body = 0
F_gravity_z_ned = 0
M_aero_x_body = 0
M_aero_y_body = 0
M_aero_z_body = 0


#Make into vector for inital state
state_vector_0 = np.array([
    u_0_body,
    v_0_body,
    w_0_body,
    p_0_body,
    q_0_body,
    r_0_body,
    phi_0,
    theta_0,
    psi_0,
    x_0_ned,
    y_0_ned,
    z_0_ned])#,
    #m_0])

force_vector_0 = np.array([
    F_drag,
    F_sideforce,
    F_lift,
    F_thrust_x_body, 
    F_gravity_z_ned,
    M_aero_x_body,
    M_aero_y_body,
    M_aero_z_body])

