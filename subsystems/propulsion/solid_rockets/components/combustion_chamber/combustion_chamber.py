from dataclasses import dataclass

@dataclass
class CombustionChamberState:
    P_chamber: float = 5e6      # Chmaber pressure [MPa] - 5 MPa initial guess
    r_burn: float = 0           # Burn radius [m]
    
    A_burn: float || None 
    T_chamber: float || None
    #V_burned?
    #gamma?
    #R?




class CombustionChamber:
    def __init__(self, state: CombustionChamberState):
        self.zero_dimensional_model = ZeroDimensionalModel(GrainGeometry, PropellantParameters, MotorGeometry)
        
        
    def compute_chamber_state(self) -> CombustionChamberState:
        state = self.zero_dimensional_model.compute_chamber_state(t)
        return CombustionChamberState(
            P_chamber = state[0],
            
        )