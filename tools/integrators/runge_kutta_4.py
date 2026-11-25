
def runge_kutta_4(f, t, x, y, dt, vehicle_parameters, aerodynamic_model, motor_burn_profile):
    """ Classic explicit 4th-order Runge-Kutta scheme
    Input arguments
        f: function representing the RHS of an equation (dx/dt = f(t, x))
        t: vector of points in time at which the solution will be approximated
        x: the numerically approximated solution data to the diff. eq., f
        y: additional array of sorts
        dt: time step in sec
        vehicle_parameters: vehicle specifications
        aerodynamic_model: 
        motor_burn_profile:

    Returns
        t: vector of points in time at which the solution will be approximated
        x: the numerically approximated solution data to the diff. eq., f
        y: additional array of some sort
    """

    N = len(t)
    for i in range(N-1):
        t_inst = t[i]
        Xi = x[:, i]
        
        print(f"Instanteneous time: {t_inst}") 
        print(f"State vector: {Xi}")

        k1, _ = f(t_inst, Xi, vehicle_parameters, aerodynamic_model, motor_burn_profile, t)
        k2, _ = f(t_inst + (dt / 2), Xi + (dt / 2) * k1, vehicle_parameters, aerodynamic_model, motor_burn_profile, t)
        k3, _ = f(t_inst + (dt / 2), Xi + (dt / 2) * k2, vehicle_parameters, aerodynamic_model, motor_burn_profile, t)
        k4, _ = f(t_inst + dt, Xi + dt * k3, vehicle_parameters, aerodynamic_model, motor_burn_profile, t)

        x[:, i + 1] = Xi + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

        y[:, i + 1] = f(t_inst, Xi, vehicle_parameters, aerodynamic_model, motor_burn_profile, t)[1]

    return t, x, y

