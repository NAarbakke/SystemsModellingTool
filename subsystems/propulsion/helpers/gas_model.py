class GasModel:
    """
    Very simple gas model: cp(T), gamma(T), R.
    You can later replace cp() with a polynomial and gamma(T) accordingly.
    """

    def __init__(self, R: float = 287.0):
        self.R = R

    #def R_spec(self, R_universal: float = 8.31446261815324):
     #   M = cea_stuff
     #   M_avg use? think so
      #  R_spec = R_universal / M
       # return R_spec

    def cp(self, T: float) -> float:
        # Placeholder: constant cp. Replace with cp(T) if you like.
        cp = 1004.5
        return cp

    def gamma(self, T: float) -> float:
        cp = self.cp(T)
        cv = cp - self.R
        gamma = cp / cv
        return gamma

    def a(self) -> float:
        a = 340.29  #at sea level for now, later consider altitude
        return a

    # def c_p_exhaust(self, T: float, f: float) -> float:
    # not cea
