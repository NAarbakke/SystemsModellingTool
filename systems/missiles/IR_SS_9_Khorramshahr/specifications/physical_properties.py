import numpy as np
from dataclasses import dataclass

@dataclass
class PhysicalProperties:
    m_wet: float = 19500
    m_dry: float = 1800
    d: float = 1.5
    
    @property
    def MR(self) -> float:
        MR = self.m_wet / self.m_dry
        return MR
        
    @property
    def A(self) -> float:
        A = np.pi * (self.d / 2)**2
        return A
        
        
        
physical_properties = PhysicalProperties()