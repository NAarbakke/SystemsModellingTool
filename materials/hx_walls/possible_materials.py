
WALLS = {
    "inconel_617": {
        "k":   lambda T: 10.1 + 0.0175 * T,   # W/(m K)
        "rho": 8360.0,                          # kg/m^3
    },
    "haynes_230": {
        "k":   lambda T: 8.4 + 0.0178 * T,
        "rho": 8970.0,
    },
    "ss_316": {
        "k":   lambda T: 11.5 + 0.0135 * T,
        "rho": 7990.0,
    },
    "sic": {
        "k":   lambda T: max(15, 300 - 0.21 * T),
        "rho": 3210.0,
    },
}
