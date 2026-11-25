import numpy as np
from analysis.combustion.cea.cea_functions import get_combustion_product_conditions_from_CEA


def solve_P_chamber(P_chamber_guess, rho_grain, a_coeff, n_coeff, A_burn, A_throat, c_star_theoretical, tol=1e-3, max_iter=50):                                                                     #does this method make sense
    P_chamber = P_chamber_guess
    for _ in range(max_iter):
        r_dot_burn = a_coeff * (P_chamber**n_coeff)
        #print(f"r_dot_burn:", r_dot_burn)
        m_dot_grain = rho_grain * A_burn * r_dot_burn
        #print(f"m_dot_grain:", m_dot_grain)
        m_dot_nozzle = (P_chamber * A_throat) / c_star_theoretical                                #get mass flow out this way??
        #print(f"m_dot_nozzle:", m_dot_nozzle)

        error = abs(m_dot_grain - m_dot_nozzle) / m_dot_grain
        #print(f"error:", error)
        if error < tol:
            return P_chamber
        
        #N-R update
        dP = 0.01 * P_chamber
        r_dot_burn_dP = a_coeff * (P_chamber + dP)**n_coeff
        #print(f"r_dot_burn_dP:", r_dot_burn_dP)
        m_dot_grain_dP = rho_grain * A_burn * r_dot_burn_dP
        #print(f"m_dot_grain_dP:", m_dot_grain_dP)
        dm_dP = (m_dot_grain_dP - m_dot_grain) / dP
        #print(f"dm_dp:", dm_dP)
        P_chamber += (m_dot_grain - m_dot_nozzle) / ((dm_dP + A_throat) / c_star_theoretical)     #does this make sense? works now after changing to +=
        #print(f"P_c:", P_c)
    return P_chamber

def solve_M_exit_2(exp_ratio, gamma, tol=1e-3):                                                                                                                                #N-R method - needs correction
    M = 1.2  #initial guess
    while True:
        f = (1 / M) * ((2 / (gamma + 1)) * (1 + ((gamma - 1) / 2) * M**2))**((gamma + 1) / (2 * (gamma - 1))) - exp_ratio                                                                        
        print(f"f:", f)                                     
        df_dM = -(1 / M**2) * ((2/(gamma + 1)) * (1 + ((gamma - 1) / 2) * M**2))**((gamma + 1) / (2 * (gamma - 1))) * (1 + ((gamma + 1) / (2 * (gamma - 1))) * (gamma - 1) * M**2)              #check
        print(f"df_dM:", df_dM)
        M_new = M - (f / df_dM)
        print(f"M_new:", M_new)
        error = (M_new - M) / M_new
        print(abs(error))
        if abs(error) < tol: 
            return M_new
        M = M_new

def solve_M_exit(exp_ratio, gamma, tol=1e-3):                                                                                                                                  #simple iterator for supersonic solution
    M = 1.1     #initial guess
    while True:
        exp_ratio_calc = (1 / M) * ((2 / (gamma + 1)) * (1 + ((gamma - 1) / 2) * M**2))**((gamma + 1) / (2 * (gamma - 1)))
        error = (exp_ratio - exp_ratio_calc) / exp_ratio
        if abs(error) < tol:
            #print(f"M_e:", M)
            return M
        M += 0.001



def compute_motor_characteristics(dt, R, grain, nozzle, propellant_parameters, n_prop):
    """
    Input arguments
        dt: time step                                   [s]
        R: universal gas constant                       [J/mol K]
        grain: TubularGrain
            r_in_0: initial inner grain radius          [m]
            r_out: outer grain radius                   [m]
            L: grain length                             [m]
        nozzle: NozzleGeometry
            A_throat: nozzle throat area                [m2]
            A_exit: nozzle end area                     [m2]
            n_nozzle: nozzle efficiency                 [-]
        propellant_parameters: Propellant
            MR: fuel mass ratio?
            fuel: name of fuel, fex 'Al'
            oxidizer: name of oxidizer, fex 'AP'
            a_coeff: burn rate coefficient              [m/s]
            n_coeff: pressure exponent                  [-]
            rho_grain: grain density as mixed           [kg/m3]
        n_prop: propellant efficiency (lumped)          [-]

    Returns
        motor_characteristics:??
            t: time vector from 0 to t_burn             [s]
            t_burn: burn time                           [s]
            --F_thrust: thrust values per time step       [N]
            m_dot: mass flow rate at each time step     [kg/s]
            u_exit: exhaust velocity at each time step     [m/s]
            P_exit: exhaust pressure at each time step     [Pa]
            P_chamber: chamber pressure at each time step     [Pa]
            --I_tot: total impulse over thrust period     [Ns]
            --I_sp_sim: specific impulse -vacuum/ambient? [s]
    """

    print("The function compute_motor_characteristics is being called")

    r_grain_in = grain.r_in_0
    A_burn = 2 * np.pi * r_grain_in * grain.L                                                                                                              #[m2] initialse burn area
    exp_ratio = nozzle.A_exit / nozzle.A_throat

    P_chamber = 5e6                                                                                                                                                               #[Pa] 5 MPa as initial guess
    cea_output = get_combustion_product_conditions_from_CEA(P_chamber, propellant_parameters.MR, exp_ratio, propellant_parameters.fuel, propellant_parameters.oxidizer, propellant_parameters.T_fuel, propellant_parameters.T_oxidizer, frozen_condition=False, frozen_throat_condition=False)
    T_chamber = cea_output[0]
    gamma_chamber = cea_output[6]
    gamma = gamma_chamber
    M_w_chamber = cea_output[3]
    M_w = M_w_chamber
    c_star_theoretical = cea_output[10]

    time = 0
    t = [0]
    #F_thrust = [0]
    m_dot_history = [0]
    u_exit_history = [0]
    P_exit_history = [0]
    P_chamber_history = [0]

    while r_grain_in < grain.r_out:
        time += dt

        #------FIND/UPDATE CHAMBER PRESSURE---------
        P_chamber = solve_P_chamber(P_chamber, propellant_parameters.rho_grain, propellant_parameters.a_coeff, propellant_parameters.n_coeff, A_burn, nozzle.A_throat, c_star_theoretical)       #check the diff. eq. way of achieving mass flow conservation
        
        #-----COMBUSTION AND CHAMBER CONDITIONS-----    #propellant combustion product properties --> define exact combustion product composition (how do i automate this for many propellant types and mixes) -- could precompute using OpenMotor/BurnSim/ProPEP then import table and interpolate
        cea_output = get_combustion_product_conditions_from_CEA(P_chamber, propellant_parameters.MR, exp_ratio, propellant_parameters.fuel, propellant_parameters.oxidizer, propellant_parameters.T_fuel, propellant_parameters.T_oxidizer, frozen_condition=False, frozen_throat_condition=False)    
        T_chamber = cea_output[0]
        gamma_chamber = cea_output[6]
        gamma = gamma_chamber                                                                                                                                                     #use chamber, throat or exit?
        M_w_chamber = cea_output[3]
        M_w = M_w_chamber
        c_star_theoretical = cea_output[10]
        
        #------BURN RATE LAW------------------------
        r_dot_burn = propellant_parameters.a_coeff * (P_chamber**propellant_parameters.n_coeff)                                                                                   #[m/s] implement erosive burning later                                                                 
        A_burn = 2 * np.pi * r_grain_in * grain.L                                                                                                     #[m2] cylindrical grain, time dependent
        m_dot = propellant_parameters.rho_grain * A_burn * r_dot_burn                                                                                                       #[kg/s]
        r_burn = r_dot_burn * dt                                                                                                                                            #[m] regression depth
        r_grain_in += r_burn                                                                                                                                                #[m]
        
        #------EXPANSION THROUGH NOZZLE--------------
        M_exit = solve_M_exit(exp_ratio, gamma)
        #u_exit = c_star_theoretical * np.sqrt((2 * gamma**2 / (gamma - 1)) * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1)))                                                              #check this expression, derive??? WRONG, right?
        P_exit = P_chamber * ((1 + ((gamma - 1) / 2) * M_exit**2))**(-gamma / (gamma - 1))                                                                                              #isentropic (assumption)                                                                                    
        T_exit = T_chamber * (1 / (1 + ((gamma - 1) / 2) * M_exit**2))
        u_exit_ideal = M_exit * np.sqrt(gamma * (R / M_w) * T_exit)
        u_exit = nozzle.n_nozzle * n_prop * u_exit_ideal                                                                                               #conduct more detailed loss analysis
        
        #-------------------------------------------
        #F_thr = m_dot * u_exit + (P_exit - P_atm) * A_nozzle                                                                                                                     #pressure term (P_chamber - P_atm) * A_throat?
        #-------------------------------------------
        
        t.append(time)
        #F_thrust.append(F_thr)
        m_dot_history.append(m_dot)
        u_exit_history.append(u_exit)
        P_exit_history.append(P_exit)  
        P_chamber_history.append(P_chamber)   

    t_burn = t[len(t) - 1]                                                                                                                                                  #i think subract 1?
    #I_tot = sum(F_thrust)
    #I_sp_sim = I_tot / (g_0 * m_grain)
    #print(f"I_sp from simulation: {I_sp_simulated} s")

    return t, t_burn, m_dot_history, u_exit_history, P_exit_history, P_chamber_history#, F_thrust, I_tot, I_sp_sim
