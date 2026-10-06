from dataclasses import dataclass


@dataclass
class FlowState:
    """
    Holds the gas state at a station, mostly in total (stagnation) form.
    Static quantities are optional / derived.
    """

    Tt: float                           # total temperature [K]
    Pt: float                           # total pressure [Pa]

    # Optional static properties (ignore if not needed)
    T: float | None = None              # static temperature [K]
    P: float | None = None              # static pressure [Pa]
    M: float | None = None              # Mach number [-]
    V: float | None = None              # velocity [m/s]
    rho: float | None = None            # static density [kg/m^3]
    rho_t: float | None = None          # total density [kg/m^3]
    m_dot: float | None = None          # mass flow rate [kg/s]
#remove m_dot?? cause not a flow state property really