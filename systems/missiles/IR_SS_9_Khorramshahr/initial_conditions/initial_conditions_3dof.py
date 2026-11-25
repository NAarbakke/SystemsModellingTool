from analysis.trajectory.initial_conditions_3dof import InitialConditions3DoF
from systems.missiles.IR_SS_9_Khorramshahr.specifications.physical_properties import physical_properties


launch_angle = 30                                                               # [deg] 

u_0_body = 1e-6                                                                 # avoiding division by 0
v_0_body = 0
w_0_body = 0

x_0_ned = 0
y_0_ned = 0
z_0_ned = 0

m_0 = physical_properties.m_wet



initial_conditions_3dof = InitialConditions3DoF(
    u_0_body,
    v_0_body,
    w_0_body,

    x_0_ned,
    y_0_ned,
    z_0_ned,

    m_0)