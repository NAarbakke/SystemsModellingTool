import numpy as np
from environment.atmosphere.get_environmental_conditions import get_environmental_conditions
from subsystems.body.aerodynamics.coefficients import C_D, C_S, C_L


#propulsion class thing instead of motor burn profile

def flat_earth_3dof_eom(t_inst, state_vector, vehicle_parameters, aerodynamic_model, motor_burn_profile, t):
    """
    Input arguments
        t_inst: instantenous time, scalar [s]
        state_vector: state vector at time t, numpy array [various]
            state_vector[0] = u_body, axial (x-dir) velocity wrt. inertial ref. frame resolved in body-fixed coord.system [m/s]          correct to say axial vel. wrt. to inertial frame, resolved in body frame??? what if it flies at an AoA, then a axial vel. in body frame is vertical in inertial frame???
            state_vector[1] = v_body, laterial (y-dir) velocity wrt. inertial ref. frame resolved in body-fixed coor. system [m/s]       use body ref frame even tho it does not have any meaning when working only in 3-DoF
            state_vector[2] = w_body, vertical (z-dir) velocity wrt. inertial ref. frame resolved in body-fixed coor. system [m/s]
            ----------------------------------------------------------------------------------------------------------------------
            state_vector[3] = x_ned, x-axis position resolved in NED coord. system, from origin point T (north direction) [m]
            state_vector[4] = y_ned, y-axis position resolved in NED coord. system, from origin point T (east direction) [m]
            state_vector[5] = z_ned, z-axis position resolved in NED coord. system, from origin point T (down direction) [m]
            ----------------------------------------------------------------------------------------------------------------------
            state_vector[6] = m, instanteneous mass [kg]
        vehicle_parameters: aircraft model data containing various parameters
        aerodynamic_model: complete aerodynamic model containing coefficients
        motor_burn_profile: parameters characterising the motor

    Returns
        state_vector_dot: time derivative of each state in state vector (RHS of governing equation)
            a_x (u_dot_body)
            a_y
            a_z
            u
            v
            w
        force_vector: at each time step
            F_drag
            F_sideforce
            F_lift
            F_thrust
            F_gravity_z_ned
    """

    print("The function flat_earth_3dof_eom is being called")

    state_vector_dot = np.zeros_like(state_vector, dtype=np.float64)
    force_vector = np.zeros((8,), dtype=np.float64)

    #idx_t_inst = np.where(t == t_inst)
    #idx_nearest = lambda array, value: (np.abs(array - value)).argmin()
    idx_t_inst = lambda array, value: max(0, np.searchsorted(array, value, side='right') - 1)       #returns the floor (rounded down) index
    #print(idx_t_inst(t, t_inst))

    u_body = state_vector[0]
    v_body = state_vector[1]
    w_body = state_vector[2]
    x_ned = state_vector[3]
    y_ned = state_vector[4]
    z_ned = state_vector[5]
    #m = state_vector[6]

    #if t_inst == t_burn:
     #   m -= stage1_parameters.m_dry

    m = vehicle_parameters.m[idx_t_inst(t, t_inst)]

    #Environmental model
    altitude = z_ned                                                                            #why minus? or not minus, like now
    rho_atm, P_atm, sound_speed, g_z_ned = get_environmental_conditions(altitude)

    #Air data calcs
    true_airspeed = np.sqrt(u_body**2 + v_body**2 + w_body**2)
    dynamic_pressure = 0.5 * rho_atm * true_airspeed**2

    #Angles of attack and sideslip set to 0 by default - 3-DoF assumes alignment with velocity vector
    alpha = 0
    beta = 0
    #gamma

    #Gravitational force in NED frame
    F_gravity_z_ned = m * g_z_ned 

    #Aerodynamic forces (wind frame)
    F_drag = C_D(alpha, aerodynamic_model) * dynamic_pressure * vehicle_parameters.A_ref                                  # = F_aero_x_wind
    F_sideforce = C_S(beta, aerodynamic_model) * dynamic_pressure * vehicle_parameters.A_ref                              # = F_aero_y_wind
    F_lift = C_L(alpha, aerodynamic_model) * dynamic_pressure * vehicle_parameters.A_ref                                  # = F_aero_z_wind

    #Propulsion forces (body frame)
    F_thrust = motor_burn_profile.m_dot[idx_t_inst(t, t_inst)] * motor_burn_profile.u_e[idx_t_inst(t, t_inst)] + (motor_burn_profile.P_e[idx_t_inst(t, t_inst)] - P_atm) * motor_burn_profile.A_nozzle[idx_t_inst(t, t_inst)]  #why is it negative initially? #change eq. based on vehicle type (or can the same eq. be used for all?? think so)

    #Translational acceleration
    state_vector_dot[0] = ((F_thrust - F_drag) / m)                          #minus sign right?
    state_vector_dot[1] = (F_sideforce / m) 
    state_vector_dot[2] = (F_lift / m) + g_z_ned

    #Position/navigation eqs (translational velocity)
    state_vector_dot[3] = u_body
    state_vector_dot[4] = v_body
    state_vector_dot[5] = w_body 

    #Stored forces
    force_vector[0] = F_drag
    force_vector[1] = F_sideforce
    force_vector[2] = F_lift
    force_vector[3] = F_thrust
    force_vector[4] = F_gravity_z_ned

    return state_vector_dot, force_vector
