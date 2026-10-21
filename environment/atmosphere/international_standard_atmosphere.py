import math
from environment.atmosphere.atmospheric_conditions import AtmosphericConditions


class InternationalStandardAtmosphere:
    """
    ISA (ICAO) up to 20 km: troposphere (linear lapse) + lower stratosphere (isothermal).
    """
    g_0 = 9.80665               # [m/s^2]
    R = 287.053                 # [J/(kg K)]
    T_sl = 288.15               # [K]  sea-level temperature
    P_sl = 101_325.0            # [Pa] sea-level pressure
    lapse_rate = 0.0065         # [K/m] troposphere
    h_tropopause = 11_000.0     # [m]
    h_max = 20_000.0            # [m]  top of the isothermal layer

    def conditions(self, h: float) -> AtmosphericConditions:
        """Static T and P at geopotential altitude h [m]."""
        if h > self.h_max:
            raise ValueError(f"h={h:.0f} m above ISA model limit {self.h_max:.0f} m")
        if h <= self.h_tropopause:
            return self._troposphere(h)
        return self._stratosphere(h)

    def _troposphere(self, h: float) -> AtmosphericConditions:
        T_0 = self.T_sl - self.lapse_rate * h
        P_0 = self.P_sl * (T_0 / self.T_sl) ** (self.g_0 / (self.lapse_rate * self.R))
        return AtmosphericConditions(T_0=T_0, P_0=P_0)

    def _stratosphere(self, h: float) -> AtmosphericConditions:
        tropopause = self._troposphere(self.h_tropopause)
        T_0 = tropopause.T_0
        P_0 = tropopause.P_0 * math.exp(-self.g_0 * (h - self.h_tropopause) / (self.R * T_0))
        return AtmosphericConditions(T_0=T_0, P_0=P_0)
