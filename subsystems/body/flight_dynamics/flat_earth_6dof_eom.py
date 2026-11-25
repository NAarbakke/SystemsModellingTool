import numpy as np 
from environment.atmosphere.get_environmental_conditions import get_environmental_conditions
from subsystems.body.aerodynamics.coefficients import C_D, C_S, C_L, C_l, C_m, C_n


def flat_earth_6dof_eom(t_inst, state_vector, vehicle_parameters, aerodynamic_model, motor_burn_profile, t):
    """
    Input arguments
        t_inst: instantenous time, scalar [s]
        state_vector: state vector at time t, numpy array [various]
            state_vector[0] = u_body, axial (x-dir) velocity wrt. inertial ref. frame resolved in body-fixed coord.system [m/s]          correct to say axial vel. wrt. to inertial frame, resolved in body frame??? what if it flies at an AoA, then a axial vel. in body frame is vertical in inertial frame???
            state_vector[1] = v_body, laterial (y-dir) velocity wrt. inertial ref. frame resolved in body-fixed coor. system [m/s]
            state_vector[2] = w_body, vertical (z-dir) velocity wrt. inertial ref. frame resolved in body-fixed coor. system [m/s]
            ----------------------------------------------------------------------------------------------------------------------
            state_vector[3] = p_body, roll angluar velocity in body-fixed coord. system wrt. inertial ref. frame [rad/s]
            state_vector[4] = q_body, pitch angluar velocity in body-fixed coord. system wrt. inertial ref. frame [rad/s]
            state_vector[5] = r_body, yaw angluar velocity in body-fixed coord. system wrt. inertial ref. frame [rad/s]
            ----------------------------------------------------------------------------------------------------------------------
            state_vector[6] = phi, roll angle [rad]                                                                                         ref. frame????
            state_vector[7] = theta, pitch angle [rad]
            state_vector[8] = psi, yaw angle [rad]
            ----------------------------------------------------------------------------------------------------------------------
            state_vector[9] = x_ned, x-axis position resolved in NED coord. system, from origin point T (north direction) [m]
            state_vector[10] = y_ned, y-axis position resolved in NED coord. system, from origin point T (east direction) [m]
            state_vector[11] = z_ned, z-axis position resolved in NED coord. system, from origin point T (down direction) [m]
            ----------------------------------------------------------------------------------------------------------------------
            state_vector[12] = m, instanteneous mass [kg]
        vehicle_parameters: aircraft model data containing various parameters
        aerodynamic_model: complete aerodynamic model containing coefficients
        motor_burn_profile: parameters characterising the motor

    Returns
        state_vector_dot: time derivative of each state in state vector (RHS of governing equation)
        force_vector: at each time step
            F_drag
            F_sideforce
            F_lift
            F_thrust_x_body
            F_gravity_z_ned
    """

    print("The function flat_earth_6dof_eom is being called")

    state_vector_dot = np.zeros_like(state_vector, dtype=np.float64)
    force_vector = np.zeros((8,), dtype=np.float64)

    #idx_t_inst = np.where(t == t_inst)
    #idx_nearest = lambda array, value: (np.abs(array - value)).argmin()
    idx_t_inst = lambda array, value: max(0, np.searchsorted(array, value, side='right') - 1)       #returns the floor (rounded down) index
    #print(idx_t_inst(t, t_inst))

    u_body = state_vector[0]
    v_body = state_vector[1]
    w_body = state_vector[2]
    p_body = state_vector[3]
    q_body = state_vector[4]
    r_body = state_vector[5]
    phi = state_vector[6]
    theta = state_vector[7]
    psi = state_vector[8]
    x_ned = state_vector[9]
    y_ned = state_vector[10]
    z_ned = state_vector[11]
    #m = state_vector[12]

    #if t_inst == t_burn:
     #   m -= stage1_parameters.m_dry

    m = vehicle_parameters.m[idx_t_inst(t, t_inst)]

    Jxz_body = vehicle_parameters.Jxz                            #need to specify ref. frame??
    Jxx_body = vehicle_parameters.Jxx
    Jyy_body = vehicle_parameters.Jyy                            #these also change with time, how to deal with
    Jzz_body = vehicle_parameters.Jzz

    #Pre-compute sin, cos and tan of euler angles
    cos_phi = np.cos(phi)
    cos_theta = np.cos(theta)
    cos_psi = np.cos(psi)
    sin_phi = np.sin(phi)
    sin_theta = np.sin(theta)
    sin_psi = np.sin(psi)
    tan_phi = np.tan(phi)
    tan_theta = np.tan(theta)
    tan_psi = np.tan(psi)

    #Environmental model
    altitude = z_ned                                                                            #why minus? or not minus, like now
    rho_atm, P_atm, sound_speed, g_z_ned = get_environmental_conditions(altitude)

    #Air data calcs
    true_airspeed = np.sqrt(u_body**2 + v_body**2 + w_body**2)
    dynamic_pressure = 0.5 * rho_atm * true_airspeed**2

    if u_body == 0 and w_body == 0:
        w_over_u = 0
    else:
        w_over_u = w_body / u_body

    if true_airspeed == 0 and v_body == 0:
        v_over_VT = 0
    else:
        v_over_VT = v_body / true_airspeed

    alpha = np.atan(w_over_u)
    beta = np.asin(v_over_VT)
    #gamma

    sin_alpha = np.sin(alpha)
    sin_beta = np.sin(beta)
    cos_alpha = np.cos(alpha)
    cos_beta = np.cos(beta)

    #Gravitational force in NED frame
    F_gravity_z_ned = m * g_z_ned 

    #Gravitational acceleration (body-fixed ref. frame)
    g_x_body = -sin_theta * g_z_ned
    g_y_body = sin_phi * cos_theta * g_z_ned
    g_z_body = cos_phi * cos_theta * g_z_ned

    #Aerodynamic forces (wind frame)
    F_drag = C_D(alpha, aerodynamic_model) * dynamic_pressure * vehicle_parameters.A_ref                                  # = F_aero_x_wind                use function: C_D(alpha, beta, mach, etc.) to extract right nr from matrix coefficient format
    F_sideforce = C_S(beta, aerodynamic_model) * dynamic_pressure * vehicle_parameters.A_ref                             # = F_aero_y_wind
    F_lift = C_L(alpha, aerodynamic_model) * dynamic_pressure * vehicle_parameters.A_ref                                  # = F_aero_z_wind

    #Aerodynamic forces (body frame)
    F_aero_x_body = -(cos_alpha * cos_beta * F_drag - cos_alpha * sin_beta * F_sideforce - sin_alpha * F_lift)
    F_aero_y_body = -(sin_beta * F_drag + cos_beta * F_sideforce)
    F_aero_z_body = -(sin_alpha * cos_beta * F_drag - sin_alpha * sin_beta * F_sideforce + cos_alpha * F_lift)              #check if minus before sin_alpha

    #Propulsion forces (body frame)
    F_thrust_x_body = motor_burn_profile.m_dot[idx_t_inst(t, t_inst)] * motor_burn_profile.u_e[idx_t_inst(t, t_inst)] + (motor_burn_profile.P_e[idx_t_inst(t, t_inst)] - P_atm) * motor_burn_profile.A_nozzle[idx_t_inst(t, t_inst)]  #why is it negative initially?#change eq. based on vehicle type (or can the same eq. be used for all?? think so)
    F_thrust_y_body = 0
    F_thrust_z_body = 0

    #Aerodynamic moments (body frame)
    M_aero_x_body = C_l(alpha, aerodynamic_model) * dynamic_pressure * vehicle_parameters.A_ref * vehicle_parameters.b_ref           
    M_aero_y_body = C_m(alpha, aerodynamic_model, q_body, vehicle_parameters.c_ref, true_airspeed) * dynamic_pressure * vehicle_parameters.A_ref * vehicle_parameters.c_ref
    M_aero_z_body = C_n(alpha, aerodynamic_model) * dynamic_pressure * vehicle_parameters.A_ref * vehicle_parameters.b_ref

    #Propulsion moments (body frame)
    #from thrusters

    #Anglular acc. eq. denominator
    Den = Jxx_body * Jxz_body - Jxz_body**2

    #Translational acceleration
    state_vector_dot[0] = ((F_thrust_x_body + F_aero_x_body) / m) + g_x_body - (w_body * q_body) + (v_body * r_body)                            #add thrust - revist eq. to find correct sign
    state_vector_dot[1] = ((F_thrust_y_body + F_aero_y_body) / m) + g_y_body - (u_body * r_body) + (w_body * p_body)
    state_vector_dot[2] = ((F_thrust_z_body + F_aero_z_body) / m) + g_z_body - (v_body * p_body) + (u_body * q_body)

    #Rotational acceleration
    state_vector_dot[3] = (Jxz_body * (Jxx_body - Jyy_body + Jzz_body) * p_body * q_body - (Jzz_body * (Jzz_body - Jyy_body) + Jxz_body**2) * q_body * r_body + (Jzz_body * M_aero_x_body) + (Jxz_body * M_aero_z_body)) / Den
    state_vector_dot[4] = ((Jzz_body - Jxx_body) * p_body * r_body - Jxz_body * (p_body**2 - r_body**2) + M_aero_y_body) / Jyy_body
    state_vector_dot[5] = ((Jxx_body * (Jxx_body - Jyy_body) + Jxz_body**2) * p_body * q_body + (Jxz_body * (Jxx_body - Jyy_body + Jzz_body)) * q_body * r_body + (Jxz_body * M_aero_x_body) + (Jxz_body * M_aero_z_body)) / Den
    
    #Euler kinematic equations (angluar velocity)
    state_vector_dot[6] = p_body + sin_phi * tan_theta * q_body + cos_phi * tan_theta * r_body
    state_vector_dot[7] = cos_phi * q_body - sin_phi * r_body
    state_vector_dot[8] = sin_phi / cos_theta * q_body + cos_phi / cos_theta * r_body

    #Position/navigation eqs (translational velocity)
    state_vector_dot[9] = cos_theta * cos_psi * u_body + (-cos_phi * sin_psi + sin_phi * sin_theta * cos_psi) * v_body + (sin_phi * sin_psi + cos_phi * sin_theta * cos_psi) * w_body
    state_vector_dot[10] = cos_theta * sin_psi * u_body + (cos_phi * cos_psi + sin_phi * sin_theta * sin_psi) * v_body + (-sin_phi * cos_psi + cos_phi * sin_theta * sin_psi) * w_body
    state_vector_dot[11] = -sin_theta * u_body + sin_phi * cos_theta * v_body + cos_phi * cos_theta * w_body 

    #Translational and rotational inertia derivatives
    #state_vector_dot[12] = -motor_burn_profile.m_dot[idx_t_inst(t, t_inst)]
    #state_vector_dot[13] = 

    #Stored forces
    force_vector[0] = F_drag
    force_vector[1] = F_sideforce
    force_vector[2] = F_lift
    force_vector[3] = F_thrust_x_body
    force_vector[4] = F_gravity_z_ned
    force_vector[5] = M_aero_x_body
    force_vector[6] = M_aero_y_body
    force_vector[7] = M_aero_z_body

    return state_vector_dot, force_vector
