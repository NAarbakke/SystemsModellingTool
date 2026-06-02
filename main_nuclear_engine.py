import pandas as pd
from propulsion.motors.helpers.gas_model import GasModel
from propulsion.motors.nuclear_fuel_turbofans import SingleSpoolClosedCycleNuclearTurbofan
from system_specifications.SKYF.engine import specs

if __name__ == "__main__":
    gas = GasModel()
    V_cruise = 270
    M_cruise = 0.8
    T_atm = 250
    P_atm = 100000

    skyf_engine = SingleSpoolClosedCycleNuclearTurbofan(gas, specs, P_atm)

    result = skyf_engine.run_point(
        T_0=T_atm,      # K
        P_0=P_atm,      # Pa
        M_0=M_cruise)

    station_labels = {
        "0":   "Freestream",
        "1":   "Inlet exit",
        "2":   "Fan exit",
        "25a": "Core splitter exit",
        "25b": "Bypass splitter exit",
        "3":   "HX entry (compressor exit)",
        "4":   "HX exit (turbine entry)",
        "5":   "Turbine exit",
        "6":   "Core nozzle exit",
        "7":   "Bypass duct exit",
        "8":   "Bypass nozzle exit",
    }

    perf = pd.DataFrame({
        "Parameter": ["F_total", "F_core", "F_bypass", "Power", "Q_reactor"],
        "Value": [
            result["F_total"],
            result["F_core"],
            result["F_bypass"],
            result["Power"],
            result["Q_reactor"],
        ],
        "Unit": ["N", "N", "N", "W", "W"]})

    # --- Station data ---
    rows = []
    for station, state in result["stations"].items():
        rows.append({
            "Station":      station,
            "Description":  station_labels.get(station, ""),
            "Tt [K]":       state.Tt,
            "Pt [Pa]":      state.Pt,
            "T [K]":        state.T,
            "P [Pa]":       state.P,
            "M [-]":        state.M,
            "V [m/s]":      state.V,
            "rho [kg/m3]":  state.rho,
            "m_dot [kg/s]": state.m_dot,
        })
    stations_df = pd.DataFrame(rows).set_index("Station")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.float_format", "{:.4f}".format)

    print("\n=== Engine Performance ===")
    print(perf.to_string(index=False))
    print("\n=== Station Data ===")
    print(stations_df)
