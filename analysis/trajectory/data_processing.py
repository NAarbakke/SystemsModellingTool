

class PositionData:
    def __init__(self, state_vector):
        self.state_vector = state_vector
        
    #def coodinates_lat_long_alt(self, ):
     #   latitude_deg = 
      #  longitude_deg =
       # altitude_m = 
        
    def pos_north_east_alt(self):
        "Generic for flat earth"
        for i, element in enumerate(t):
            pos_north[i, 0] = state_vector[9, i]
            pos_east[i, 0] = state_vector[10, i]
            altitude[i, 0] = -state_vector[11, i]  
        
        
        
class FlightData:
    def __init__(self, state_vector):
        self.state_vector = state_vector
        
        
    def system_data(self):
        for i, element in enumerate(t):
            true_airspeed[i, 0] = np.sqrt(state_vector[0, i]**2 + state_vector[1, i]**2 + state_vector[2, i]**2)            
            Mach_nr[i, 0] = true_airspeed[i, 0] / sound_speed[i, 0]
        
        
    def system_orientation(self):
        for i, element in enumerate(t):
            true_airspeed[i, 0] = np.sqrt(state_vector[0, i]**2 + state_vector[1, i]**2 + state_vector[2, i]**2)

            if state_vector[0, i] == 0 and state_vector[2, i] == 0:
                w_over_u = 0
            else:
                w_over_u = state_vector[2, i] / state_vector[0, i]

            alpha[i, 0] = np.atan(w_over_u)

            if state_vector[1, i] == 0 and true_airspeed[i, 0] == 0:
                v_over_VT = 0
            else:
                v_over_VT = state_vector[1, i] / true_airspeed[i, 0]

            beta[i, 0] = np.asin(v_over_VT)


    def air_data(self):
        for i, element in enumerate(t):
            rho_atm[i, 0], P_atm[i, 0], sound_speed[i, 0], g[i, 0] = get_environmental_conditions(altitude[i, 0])

        

class PerformanceData:
    def __init__(self, force_vector):
        self.force_vector = force_vector
        
    def total_impulse(self):
        I_tot = self.force_vector[3]
        return I_tot
    
    def specific_impulse_simulated(self):
        I_sp = I_tot / (g_0 * stage1_parameters.m_grain)
        return I_sp
    
    def specific_impulse_static_fire(self):
        I_sp = I_tot_static_fire / (g_0 * propellant_mass_burned)
        return I_sp