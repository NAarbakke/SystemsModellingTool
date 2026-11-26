import numpy as np


class BATES:
    """
    BATES internal geometry:
        Cylindrical bore burning outward, with both end faces burning
        
    r_burn = r_dot_burn * t      [m]
    """
    def __init__(self, geometry: GrainGeometry):
        self.R_inner = geometry.R_inner
        self.R_outer = geometry.R_outer
        self.L_initial = geometry.L_initial
        
    def A_burn(self, r_burn):
        R = self.R_inner + r_burn
        L = self.L_initial - 2*r_burn
        if R >= self.R_outer or L <=0 return 0.0
        A_burn = 2*np.pi * R * L + 2*np.pi * (self.R_outer**2 - R**2)
        return A_burn
        
    def V_burned(self, r_burn):
        R = min(self.R_inner + r_burn, self.R_outer)
        L = max(self.L_initial - 2*r_burn, 0)
        V_burned = np.pi * self.R_outer**2 * self.L_initial - np.pi * R**2 * L
        return V_burned
        