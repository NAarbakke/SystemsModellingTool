

class ZeroDimensionalModel:
    """
    Assumes m_dot_burn = m_dot_nozzle throughout (steady state equilibrium)
    
    Unknown parameters that must be optimized for using SID:
        a_coeff     xx < xx < xx
        n_coeff     < 1
    """
    def __init__(self, state: CombustionChamberState, grain_geometry: GrainGeometry, propellant: PropellantParameters, motor_geometry: MotorGeometry):
        self.state = state

        self.grain_geometry = BATES(GrainGeometry)     # should be able to choose which ever grain geo - choice of BATES should live in Tsirkon class? to keep this one generic
        
        self.a_coeff = propellant.a_coeff
        self.A_throat = motor_geometry.A_throat
        #A_exit somewhere - actually no, remove from eqs


    def compute_chamber_state(self, t, state: FlowState) -> np.array:         # issue wit this method: i have not converged/solved for my actual pressure
        P_chamber = state.P_chamber
        r_burn = state.r_burn
        A_burn = state.A_burn = self.grain_geometry.A_burn(r_burn)  #how to solve this one? maybe i dont need A_burn in state dataclass
        
        while A_burn > 0:
            T_chamber = #cea 
            gamma = #cea 
            R = #cea 
            
            r_dot_burn = self.a_coeff * P_chamber ** self.n_coeff
            r_burn = r_dot_burn * t 
            A_burn = grain_geometry.A_burn(r_burn)
            c_star_theoretical = np.sqrt(((R * T_chamber) / gamma) * ((gamma + 1) / 2)**((gamma + 1) / (gamma - 1)))
            P_chamber = ((self.rho_grain * A_burn * self.a_coeff * c_star_theoretical) / self.A_throat) ** (1 / (1 - self.n_coeff))
            V_burned = grain_geometry.V_burned(r_burn)
            m_dot_burn = self.rho_grain * 
            
            #avoid this method cause it relies on inputting P_atm
            C_f_ideal = np.sqrt(((2 * gamma**2) / (gamma - 1)) * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1)) * (1 - (P_exit / P_chamber)**((gamma - 1) / gamma))) + (A_exit / A_throat) * ((P_exit - P_atm) / P_chamber)
            F_thrust_ideal = C_f_ideal * P_chamber * A_throat
            F_thrust_ideal = m_dot * V_exit + (P_exit - P_atm) * A_exit
            
        return P_chamber    #output instead m_dot, V_exit
    
    
    
    
m_dot_grain = rho_grain * A_burn * r_dot_burn