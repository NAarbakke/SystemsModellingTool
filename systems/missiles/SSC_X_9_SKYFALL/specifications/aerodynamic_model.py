from dataclasses import dataclass

@dataclass#(frozen=True)
class AerodynamicModel:     #simplified for now
    C_D_0: float = 0.1
    C_S_0: float = 0.1
    C_L_0: float = 0.1
    
    C_D_alpha: float = 0.1
    C_S_alpha: float = 0.1
    C_L_alpha: float = 0.1
    
    #Wing
    #C_L_wing_alpha
    
    #Tail
    #C_L_tail_alpha



#make aerodynamic_data_from_excel.py to get matrix 



missile_aerodynamic_model = AerodynamicModel()