
def air_properties(T, P=1013250.0):
    """Air properties from polynomial fits.  Valid 250 - 1500 K."""
    R = 287.05  # J/(kg K)

    rho = P / (R * T)

    # Specific heat [J/(kg K)] - varies ~15% over your range
    cp = (1057.5 - 0.3657 * T + 8.503e-4 * T**2
          - 3.509e-7 * T**3 + 5.21e-11 * T**4)

    # Viscosity [Pa s] - Sutherland's law
    mu = 1.716e-5 * (T / 273.15)**1.5 * 383.55 / (T + 110.4)

    # Thermal conductivity [W/(m K)]
    k = -3.933e-3 + 1.018e-4 * T - 4.857e-8 * T**2 + 1.546e-11 * T**3

    Pr = mu * cp / k
    return dict(rho=rho, cp=cp, mu=mu, k=k, Pr=Pr)
