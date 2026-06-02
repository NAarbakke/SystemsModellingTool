"""
Evaluate candidate coolants for the SKYF closed-cycle nuclear turbofan.

For each coolant in propulsion.coolants.possible_coolants.FLUIDS (excluding air),
this script:
  1. Checks whether the coolant's valid temperature range covers the operating
     conditions (T_hot_in from the spec, estimated T_hot_out from energy balance).
  2. Runs the full engine model via SingleSpoolClosedCycleNuclearTurbofan.
  3. Extracts heat-exchanger sizing results from the HX component.
  4. Computes a comparative score based on HX area (compact = good),
     pressure drops, coolant-side heat transfer, and effectiveness.
  5. Prints a summary table ranking coolants by suitability.
"""

import numpy as np
import pandas as pd
from dataclasses import replace
from propulsion.motors.helpers.gas_model import GasModel
from propulsion.motors.nuclear_fuel_turbofans import SingleSpoolClosedCycleNuclearTurbofan
from propulsion.coolants.possible_coolants import FLUIDS
from propulsion.motors.components.heat_exchangers import HeatExchanger
from system_specifications.SKYF.engine import specs, HeatExchangerSpecs

# ── Operating conditions (same as main_nuclear_engine.py) ──────────────
M_CRUISE = 0.8
T_ATM    = 250.0   # K
P_ATM    = 100_000  # Pa

# Coolants to evaluate (everything except air — air is the cold side)
COOLANT_NAMES = [name for name in FLUIDS if name != "air"]

# Valid temperature ranges for each coolant (K)
# Sources: IAEA-THPH, Fink & Leibowitz, INL/EXT-10-18297, OECD/NEA Handbook
VALID_RANGES = {
    "sodium":  (371,  1155),
    "nak":     (262,  1058),
    "flinak":  (727,  1570),
    "flibe":   (732,  1400),
    "helium":  (50,   3000),   # gas — no phase-change limits
    "lbe":     (398,  1943),
}


def check_temperature_feasibility(coolant_name, T_hot_in, T_hot_out_est):
    """Return (ok, warning_msg) for temperature range check."""
    lo, hi = VALID_RANGES.get(coolant_name, (0, 1e6))
    issues = []
    if T_hot_in > hi:
        issues.append(f"T_hot_in={T_hot_in:.0f} K exceeds upper limit {hi:.0f} K")
    if T_hot_out_est < lo:
        issues.append(f"T_hot_out~{T_hot_out_est:.0f} K below lower limit {lo:.0f} K")
    if T_hot_in < lo:
        issues.append(f"T_hot_in={T_hot_in:.0f} K below melting/lower limit {lo:.0f} K")
    return (len(issues) == 0, "; ".join(issues) if issues else "OK")


def estimate_T_hot_out(coolant_name, T_hot_in, P_hot, mdot_hot,
                       T_cold_in, T_cold_out, P_cold, mdot_cold):
    """Quick energy-balance estimate of coolant outlet temperature."""
    from propulsion.motors.helpers.air_properties import air_properties
    cp_cold = air_properties(0.5 * (T_cold_in + T_cold_out), P_cold)["cp"]
    Q = mdot_cold * cp_cold * (T_cold_out - T_cold_in)

    props_fn = FLUIDS[coolant_name]
    cp_hot = props_fn(T_hot_in, P_hot)["cp"]
    T_hot_out = T_hot_in - Q / (mdot_hot * cp_hot)
    # refine once
    cp_hot = props_fn(0.5 * (T_hot_in + T_hot_out), P_hot)["cp"]
    T_hot_out = T_hot_in - Q / (mdot_hot * cp_hot)
    return T_hot_out, Q


def run_engine_with_coolant(coolant_name):
    """Run the full engine model with a given coolant. Returns (engine, result) or (None, error_str)."""
    gas = GasModel()
    try:
        s = replace(specs, hx=replace(specs.hx, hot_fluid=coolant_name))
        engine = SingleSpoolClosedCycleNuclearTurbofan(gas, s, P_ATM)
        result = engine.run_point(T_0=T_ATM, P_0=P_ATM, M_0=M_CRUISE)
        return engine, result
    except Exception as e:
        return None, str(e)


def get_hx_result(engine):
    """Extract the HXResult stored on the engine's heat-exchanger component."""
    return engine.heat_exchanger.last_hx_result


def evaluate_coolant_properties(coolant_name, T_hot_in, P_hot):
    """Evaluate raw thermophysical properties at the inlet temperature."""
    return FLUIDS[coolant_name](T_hot_in, P_hot)


def main():
    # Run the baseline (helium) first to get compressor-exit conditions
    # for the energy-balance feasibility check.
    print("Running baseline engine (helium) to establish air-side conditions...")
    baseline_engine, baseline_result = run_engine_with_coolant("helium")
    if baseline_engine is None:
        print(f"Baseline failed: {baseline_result}")
        return

    station3 = baseline_result["stations"]["3"]
    T_cold_in = station3.Tt
    P_cold    = station3.Pt
    mdot_cold = station3.m_dot
    print(f"  Compressor exit: T={T_cold_in:.1f} K, P={P_cold:.0f} Pa, "
          f"mdot={mdot_cold:.2f} kg/s\n")

    # ── Evaluate each coolant ──────────────────────────────────────────
    rows = []

    for name in COOLANT_NAMES:
        print(f"Evaluating: {name} ... ", end="", flush=True)

        # Temperature feasibility
        T_hot_out_est, Q_est = estimate_T_hot_out(
            name, specs.hx.T_hot_in, specs.hx.P_hot, specs.hx.mdot_hot,
            T_cold_in, specs.hx.T_cold_out, P_cold, mdot_cold)

        ok, msg = check_temperature_feasibility(name, specs.hx.T_hot_in, T_hot_out_est)

        if not ok:
            print(f"SKIPPED ({msg})")
            rows.append(dict(
                coolant=name, feasible=False, warning=msg,
                F_total=np.nan, Q_reactor=np.nan,
                HX_area=np.nan, U_avg=np.nan, effectiveness=np.nan,
                dP_cold=np.nan, dP_hot=np.nan, T_hot_out=np.nan,
                rho_coolant=np.nan, cp_coolant=np.nan,
                k_coolant=np.nan, Pr_coolant=np.nan,
            ))
            continue

        # Run full engine
        engine, result = run_engine_with_coolant(name)
        if engine is None:
            print(f"FAILED ({result})")
            rows.append(dict(
                coolant=name, feasible=False, warning=str(result),
                F_total=np.nan, Q_reactor=np.nan,
                HX_area=np.nan, U_avg=np.nan, effectiveness=np.nan,
                dP_cold=np.nan, dP_hot=np.nan, T_hot_out=np.nan,
                rho_coolant=np.nan, cp_coolant=np.nan,
                k_coolant=np.nan, Pr_coolant=np.nan,
            ))
            continue

        # HX result
        hx = get_hx_result(engine)
        if hx is None:
            print("no HX result found")
            continue

        # Coolant properties at inlet
        props = evaluate_coolant_properties(name, specs.hx.T_hot_in, specs.hx.P_hot)

        rows.append(dict(
            coolant=name,
            feasible=True,
            warning=msg,
            F_total=result["F_total"],
            Q_reactor=result["Q_reactor"],
            HX_area=hx.A,
            U_avg=hx.U_avg,
            effectiveness=hx.effectiveness,
            dP_cold=hx.dP_cold,
            dP_hot=hx.dP_hot,
            T_hot_out=hx.T_hot_out,
            rho_coolant=props["rho"],
            cp_coolant=props["cp"],
            k_coolant=props["k"],
            Pr_coolant=props["Pr"],
        ))
        print("OK")

    # ── Build results table ────────────────────────────────────────────
    df = pd.DataFrame(rows)

    # ── Ranking (lower is better for area and dP, higher for U and eff) ──
    feasible = df[df["feasible"]].copy()
    if len(feasible) > 0:
        def norm_min(s):  # lower is better -> 0 = best
            rng = s.max() - s.min()
            return (s - s.min()) / rng if rng > 0 else pd.Series(0, index=s.index)

        def norm_max(s):  # higher is better -> 0 = best
            return 1 - norm_min(s)

        feasible["score"] = (
            0.35 * norm_min(feasible["HX_area"])       # compact HX is critical for flight
          + 0.25 * norm_max(feasible["U_avg"])          # better heat transfer
          + 0.15 * norm_min(feasible["dP_hot"])         # less pumping power needed
          + 0.15 * norm_min(feasible["dP_cold"])        # less air-side loss
          + 0.10 * norm_max(feasible["effectiveness"])  # thermal efficiency
        )
        feasible = feasible.sort_values("score", ascending=False)

    # ── Print results ──────────────────────────────────────────────────
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 220)
    pd.set_option("display.float_format", "{:.4f}".format)

    print("\n" + "=" * 90)
    print("  COOLANT EVALUATION — SKYF Nuclear Turbofan Heat Exchanger")
    print("=" * 90)
    print(f"  Operating point: M={M_CRUISE}, T_atm={T_ATM} K, P_atm={P_ATM} Pa")
    print(f"  Reactor coolant: T_hot_in={specs.hx.T_hot_in} K, P_hot={specs.hx.P_hot/1e6:.1f} MPa, "
          f"mdot_hot={specs.hx.mdot_hot} kg/s")
    print(f"  Target TET: {specs.hx.T_cold_out} K")
    print(f"  Wall material: {specs.hx.wall_material}, t_wall={specs.hx.t_wall*1e3:.1f} mm")
    print()

    # Coolant properties comparison
    print("-" * 90)
    print("  COOLANT THERMOPHYSICAL PROPERTIES (at T_hot_in = {:.0f} K)".format(specs.hx.T_hot_in))
    print("-" * 90)
    props_df = df[["coolant", "feasible", "rho_coolant", "cp_coolant",
                   "k_coolant", "Pr_coolant"]].copy()
    props_df.columns = ["Coolant", "Feasible", "rho [kg/m3]", "cp [J/(kg K)]",
                        "k [W/(m K)]", "Pr [-]"]
    print(props_df.to_string(index=False))
    print()

    # HX sizing comparison
    if len(feasible) > 0:
        print("-" * 90)
        print("  HEAT EXCHANGER SIZING RESULTS")
        print("-" * 90)
        hx_df = feasible[["coolant", "HX_area", "U_avg", "effectiveness",
                          "dP_cold", "dP_hot", "T_hot_out"]].copy()
        hx_df.columns = ["Coolant", "A [m2]", "U_avg [W/(m2 K)]", "eff [-]",
                         "dP_cold [Pa]", "dP_hot [Pa]", "T_hot_out [K]"]
        print(hx_df.to_string(index=False))
        print()

        # Engine performance
        print("-" * 90)
        print("  ENGINE PERFORMANCE")
        print("-" * 90)
        perf_df = feasible[["coolant", "F_total", "Q_reactor"]].copy()
        perf_df.columns = ["Coolant", "F_total [N]", "Q_reactor [W]"]
        print(perf_df.to_string(index=False))
        print()

        # Final ranking
        print("-" * 90)
        print("  SUITABILITY RANKING")
        print("  (weights: HX compactness 35%, heat transfer 25%, "
              "hot-side dP 15%, cold-side dP 15%, effectiveness 10%)")
        print("-" * 90)
        rank_df = feasible[["coolant", "HX_area", "U_avg", "dP_hot", "score"]].copy()
        rank_df.columns = ["Coolant", "A [m2]", "U_avg [W/(m2 K)]",
                           "dP_hot [Pa]", "Score"]
        rank_df = rank_df.reset_index(drop=True)
        rank_df.index = range(1, len(rank_df) + 1)
        rank_df.index.name = "Rank"
        print(rank_df.to_string())
        print()
        best = feasible.iloc[0]["coolant"]
        print(f"  >>> Best coolant for this configuration: {best.upper()}")

    # Temperature warnings
    infeasible = df[~df["feasible"]]
    if len(infeasible) > 0:
        print()
        print("-" * 90)
        print("  INFEASIBLE COOLANTS (temperature range violations)")
        print("-" * 90)
        for _, row in infeasible.iterrows():
            print(f"  {row['coolant']:12s}  {row['warning']}")

    print()


if __name__ == "__main__":
    main()
