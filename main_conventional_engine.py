import pandas as pd
from plotting.plot_with_scienceplots import plot_station_properties as plot_scienceplots
from plotting.plot_with_rcparams import plot_station_properties as plot_rcparams
from plotting.plot_with_pgf import plot_station_properties as plot_pgf
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_liquid_fuel_turbofan import SingleSpoolOpenCycleLiquidFuelTurbofan
from specifications.SKYF.engine import specs

if __name__ == "__main__":
    gas = GasModel()
    V_cruise = 270
    M_cruise = 0.8
    T_atm = 250
    P_atm = 100000

    skyf_engine = SingleSpoolOpenCycleLiquidFuelTurbofan(gas, specs, P_atm)

    result = skyf_engine.run_point(
        T_0=T_atm,      # K
        P_0=P_atm,      # Pa
        M_0=M_cruise)

    station_labels = {
        "0": "Freestream",
        "1": "Inlet exit",
        "2": "Fan exit",
        "3": "Compressor exit",
        "4": "Combustor exit",
        "5": "Turbine exit",
        "6": "Core nozzle exit",
        "7": "Bypass duct exit",
        "8": "Bypass nozzle exit"}

    perf = pd.DataFrame({
        "Parameter": ["F_total", "F_core", "F_bypass", "Power", "TSFC", "m_dot_fuel"],
        "Value": [
            result["F_total"],
            result["F_core"],
            result["F_bypass"],
            result["Power"],
            result["TSFC"],
            result["m_dot_fuel"],
        ],
        "Unit": ["N", "N", "N", "W", "kg/(N.s)", "kg/s"]})

    # --- Station data ---
    rows = []
    for station, state in result["stations"].items():
        rows.append({
            "Station": station,
            "Description": station_labels.get(station, ""),
            "Tt [K]": state.Tt,
            "Pt [Pa]": state.Pt,
            "T [K]": state.T,
            "P [Pa]": state.P,
            "M [-]": state.M,
            "V [m/s]": state.V,
            "rho [kg/m3]": state.rho,
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

    plot_args = dict(
        stations=result["stations"],
        x_attr="Tt", y_attr="Pt",
        x_label=r"$T_t$ [K]",
        y_label=r"$P_t$ [Pa]",
    )

    # Option 4: SciencePlots (interactive window)
    plot_scienceplots(**plot_args, title="SciencePlots")

    # Option 3: rcParams / Computer Modern (interactive window)
    plot_rcparams(**plot_args, title="rcParams (Computer Modern)")

    # Option 1: pgf backend (saves .pgf file, no interactive window)
    plot_pgf(**plot_args, title="pgf backend", save_path="station_plot.pgf")
    print("pgf output saved to: station_plot.pgf")
