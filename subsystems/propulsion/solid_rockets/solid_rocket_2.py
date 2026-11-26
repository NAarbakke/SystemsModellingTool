


class SolidRocket:
    def __init__(self, grain_geometry: GrainGeometry, propellant: PropellantParameters, nozzle_geometry: NozzleGeometry):
        self.combustion_chamber = CombustionChamber(grain_geometry, propellant)
        self.nozzle = ConvergentDiverentConicalNozzle(nozzle_geometry)         # generic nozzle - specify Conical in Tsirkon class?
        
        
    def ideal_thrust(self, t) -> float:
        m_dot = self.combustion_chamber.compute_chamber_state(t)[0]     #get value like this?
        V_exit = self.combustion_chamber.compute_chamber_state(t)[1]
        P_exit = self.nozzle.compute_exit_state[2]
        A_exit = self.nozzle.A_exit
        P_atm = # call get atm function
        F_thrust_ideal = m_dot * V_exit + (P_exit - P_atm) * A_exit
        return F_thrust_ideal
        
    def mass(self) -> float:
        m = m_wet - m_dot * dt  # or put in Aiframe class? yes
        return m