from dataclasses import dataclass


@dataclass
class FlowState:
    """
    Thermodynamic state of a fluid at a single station along a flow path,
    at a single instant in time.

    Quantities are STATIC unless suffixed with '0' (stagnation/total).

    Generic enough to describe a station in any fluid component
    (nozzle, combustor, pump, turbine, etc.).
    """
    P: float            # Static pressure [Pa]
    T: float            # Static temperature [K]
    M: float            # Mach number [-]
    gamma: float        # Specific heat ratio [-]
    R: float            # Specific gas constant [J/kg/K]
    m_dot: float        # Mass flow rate [kg/s]
    A: float            # Cross-sectional area [m^2]

    h: float | None = None      # Specific enthalpy [J/kg] (for work-transfer analysis)
    s: float | None = None      # Specific entropy [J/kg/K] (for loss tracking)

    @property
    def u(self) -> float:
        """Flow velocity [m/s]."""
        return self.M * (self.gamma * self.R * self.T) ** 0.5

    @property
    def rho(self) -> float:
        """Static density [kg/m^3]."""
        return self.P / (self.R * self.T)

    @property
    def Pt(self) -> float:
        """Total (stagnation) pressure [Pa]."""
        return self.P * (1 + ((self.gamma - 1) / 2) * self.M**2) ** (self.gamma / (self.gamma - 1))

    @property
    def Tt(self) -> float:
        """Total (stagnation) temperature [K]."""
        return self.T * (1 + ((self.gamma - 1) / 2) * self.M**2)
