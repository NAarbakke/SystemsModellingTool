
def forward_euler(f, t, x, y, dt, vehicle_parameters, aerodynamic_model, motor_burn_profile):
    """
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

    for i in range(1, len(t)):                          #from tutorial, i starts at 1
        t_inst = t[i]
        print(t_inst)                             
        #x[:, i + 1] = x[:, i] + f(t_inst, x[:, i], vehicle_parameters, aerodynamic_model, motor_burn_profile, t)[0] * dt           
        #or    
        print(x[:, i-1])
        x[:, i] = x[:, i - 1] + f(t_inst, x[:, i - 1], vehicle_parameters, aerodynamic_model, motor_burn_profile, t)[0] * dt
        
        y[:, i] = f(t_inst, x[:, i - 1], vehicle_parameters, aerodynamic_model, motor_burn_profile, t)[1]

    return t, x, y
