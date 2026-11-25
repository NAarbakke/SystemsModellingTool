

class LoadFactor:
    """
    Computes the load factor (g-force) during various maneuvers given actual (or simulated) flight data
        - can thus not (yet) compute from first principles what a given design is capable of
            - this would require equations involving C_M_pitch, etc. (??)
    """
    def __init__(self, flight_data: FlightData):
        self.v = true_airspeed
        self.q = pitch_rate
    
    def pull_up_maneuver(self) -> float:
        """ 
        Computes load factor (g-force) during a pull-up (pitch-up) maneuver     
        """
        #n = 1 + v**2 / (r_turn * g)
        
        "Assumes angle of attack (alpha) is constant througout maneuver"
        n = 1 + (v * q) / g
        return n
        
    def pull_down_maneuver(self) -> float:
        """ 
        Computes load factor (g-force) during a pull-down (pitch-down) maneuver     
        """
        #n = 1 - v**2 / (r_turn * g)
        
        "Assumes angle of attack (alpha) is constant througout maneuver"
        n = 1 - (v * q) / g
        return n