import numpy as np
from propulsion.motors.helpers.air_properties import air_properties

def sodium_properties(T, P=2e5):
    """Liquid sodium.  Valid 371 - 1155 K.
    Sources: Fink & Leibowitz (1995), IAEA-THPH (2008)."""
    rho = 219.0 + 275.32 * (1 - T / 2503.7) + 511.58 * (1 - T / 2503.7)**0.5
    cp  = (1658.2 - 0.8479 * T + 4.454e-4 * T**2 - 2.993e-8 * T**3)
    mu  = np.exp(-6.4406 - 0.3958 * np.log(T) + 556.835 / T) * 1e-3
    k   = 124.67 - 0.11381 * T + 5.5226e-5 * T**2 - 1.1842e-8 * T**3
    Pr  = mu * cp / k
    return dict(rho=rho, cp=cp, mu=mu, k=k, Pr=Pr)


def nak_properties(T, P=2e5):
    """NaK eutectic (78% K, 22% Na).  Valid 262 - 1058 K.
    Source: IAEA-THPH, Lyon (1952)."""
    rho = 855.3 - 0.2245 * T
    cp  = (1089.8 - 0.4168 * T)
    mu  = np.exp(-6.261 - 0.4026 * np.log(T) + 530.6 / T) * 1e-3
    k   = 25.6 + 0.0119 * T - 2.551e-6 * T**2
    Pr  = mu * cp / k
    return dict(rho=rho, cp=cp, mu=mu, k=k, Pr=Pr)


def flinak_properties(T, P=2e5):
    """FLiNaK molten salt (LiF-NaF-KF).  Valid 727 - 1570 K.
    Source: INL/EXT-10-18297."""
    rho = 2579.3 - 0.624 * T
    cp  = 1884.0                   # nearly constant
    mu  = 2.487e-5 * np.exp(4478.62 / T)
    k   = 0.36 + 5.6e-4 * T
    Pr  = mu * cp / k
    return dict(rho=rho, cp=cp, mu=mu, k=k, Pr=Pr)


def helium_properties(T, P=50e5):
    """Helium gas.  Useful as a gas-cooled reactor comparison."""
    R = 2077.1  # J/(kg K)
    rho = P / (R * T)
    cp  = 5193.0                   # constant
    mu  = 1.985e-5 * (T / 293.15)**0.647
    k   = 0.1513 * (T / 293.15)**0.664
    Pr  = mu * cp / k
    return dict(rho=rho, cp=cp, mu=mu, k=k, Pr=Pr)


def flibe_properties(T, P=2e5):
    """FLiBe molten salt (LiF-BeF2).  Valid 732 - 1400 K.
    Source: INL/EXT-10-18297."""
    rho = 2415.6 - 0.49072 * T
    cp  = 2386.0
    mu  = 1.16e-4 * np.exp(3755.0 / T)
    k   = 1.1
    Pr  = mu * cp / k
    return dict(rho=rho, cp=cp, mu=mu, k=k, Pr=Pr)


def lbe_properties(T, P=2e5):
    """Lead-bismuth eutectic.  Valid 398 - 1943 K.
    Source: OECD/NEA Handbook (2015)."""
    rho = 11065.0 - 1.293 * T
    cp  = 159.0 - 2.72e-2 * T + 7.12e-6 * T**2
    mu  = 4.94e-4 * np.exp(754.1 / T)
    k   = 3.284 + 1.617e-2 * T - 2.305e-6 * T**2
    Pr  = mu * cp / k
    return dict(rho=rho, cp=cp, mu=mu, k=k, Pr=Pr)



FLUIDS = {
    "air":     air_properties,
    "sodium":  sodium_properties,
    "nak":     nak_properties,
    "flinak":  flinak_properties,
    "flibe":   flibe_properties,
    "helium":  helium_properties,
    "lbe":     lbe_properties}
