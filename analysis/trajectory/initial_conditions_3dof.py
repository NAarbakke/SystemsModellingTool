from dataclasses import dataclass

@dataclass
class InitialConditions3DoF:
    u_0: float = 1e-8
    v_0: float = 0
    w_0: float = 0
    
    x_0: float = 0
    y_0: float = 0
    z_0: float = 0
    
    m_0: float
    