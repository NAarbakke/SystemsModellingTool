# Heat Exchanger Coolant Selection Requirements

Requirements and considerations for selecting a reactor coolant for the
closed-cycle nuclear turbofan heat exchanger (air-to-coolant counterflow).

---

## 1. Thermophysical Properties

These properties are directly used by the HX sizing model
(`propulsion/motors/components/heat_exchangers.py`) and determine heat exchanger
geometry, performance, and pressure drops.

| Property | Symbol | Why it matters |
|---|---|---|
| Thermal conductivity | k [W/(m·K)] | Drives the hot-side convection coefficient h. Higher k → higher U → smaller HX area. Liquid metals (Na: ~60 W/mK) dominate over molten salts (~0.5–1) and gases (~0.3). |
| Specific heat capacity | cp [J/(kg·K)] | Heat carried per unit mass flow. Higher cp → lower required mdot or smaller coolant ΔT for a given heat duty. |
| Density | ρ [kg/m³] | Affects channel flow velocity, Reynolds number, and pressure drop. Also directly sets coolant loop mass (see §2). |
| Dynamic viscosity | μ [Pa·s] | Determines Reynolds number and friction factor. High μ (molten salts at lower temperatures) increases pumping power and may push flow into the laminar regime, degrading heat transfer. |
| Prandtl number | Pr = μ·cp/k | Selects the applicable heat transfer correlation: Pr < 0.1 → Lyon-Martinelli (liquid metals), Re < 2300 → Nu = 4.36 (laminar), Re ≥ 2300 → Gnielinski (turbulent gases/salts). |
| Volumetric heat capacity | ρ·cp [J/(m³·K)] | Energy transported per unit volume of coolant. Higher ρ·cp → smaller pipe and header cross-sections for the same thermal power. |

---

## 2. Weight-Critical Properties (Aircraft Application)

For a flight vehicle, system mass is as important as thermal performance.

### 2.1 Coolant Inventory Mass

Total coolant mass = ρ × V_loop, where V_loop is the total internal volume of
the reactor-to-HX piping, headers, and channels. LBE (ρ ≈ 10,000 kg/m³) vs
helium (ρ ≈ 1 kg/m³) can mean hundreds of kilograms of difference. This is
arguably the single biggest discriminator for airborne nuclear propulsion.

### 2.2 Pumping Power

Parasitic shaft power required to circulate the coolant:

    P_pump = ΔP_hot × (mdot_hot / ρ) / η_pump

This power is drawn from the turbine and directly reduces net thrust. Low
viscosity and low density (for gases) or high density with low friction (for
liquid metals) are favourable.

### 2.3 Shielding Mass

Coolants that become radioactive under neutron irradiation (e.g. sodium →
Na-24, t½ = 15 h) require radiation shielding around the entire coolant loop,
not just the reactor. This adds significant structural mass. Inert coolants
(helium) or low-activation coolants (FLiBe) are preferable from a shielding
standpoint.

---

## 3. Operational Limits

### 3.1 Melting / Freezing Point

If the coolant freezes anywhere in the loop (e.g. during low-power cruise,
shutdown, or cold soak at altitude), flow is blocked and the reactor loses its
heat sink. Molten salts are vulnerable here:

- FLiNaK: melts at ~727 K
- FLiBe: melts at ~732 K
- Sodium: melts at ~371 K
- NaK eutectic: melts at ~262 K (lowest — stays liquid at room temperature)

Design must ensure the coldest point in the loop always exceeds the freezing
point, including during transients and emergency shutdown.

### 3.2 Boiling Point / Vapour Pressure

If the coolant boils inside the reactor core, local heat transfer collapses
(film boiling / dryout). The boiling point at system pressure sets the maximum
allowable coolant temperature. This also determines the minimum loop pressure
required to maintain single-phase flow at T_hot_in.

### 3.3 Valid Correlation Ranges

Each property correlation has a stated validity range. Operating outside it
produces unphysical results. Current ranges (from `possible_coolants.py`):

| Coolant | T_min [K] | T_max [K] | Source |
|---|---|---|---|
| Sodium | 371 | 1155 | Fink & Leibowitz (1995), IAEA-THPH |
| NaK | 262 | 1058 | IAEA-THPH, Lyon (1952) |
| FLiNaK | 727 | 1570 | INL/EXT-10-18297 |
| FLiBe | 732 | 1400 | INL/EXT-10-18297 |
| Helium | ~50 | ~3000 | Ideal gas (no phase change) |
| LBE | 398 | 1943 | OECD/NEA Handbook (2015) |

---

## 4. Chemical Compatibility and Safety

### 4.1 Reactivity with Air and Water

Sodium and NaK ignite spontaneously on contact with air or water. A coolant
leak in a flight vehicle is a fire/explosion hazard. Double-walled containment
or intermediate heat transfer loops are standard mitigations in ground reactors,
but add mass and complexity for aircraft.

### 4.2 Corrosion

Molten fluoride salts (FLiNaK, FLiBe) are highly corrosive to most nickel
superalloys at high temperature. Compatible materials include Hastelloy-N and
certain SiC composites, which may not be optimal for HX wall duty.

LBE causes liquid metal embrittlement and lead dissolution in ferritic and
austenitic steels. Requires oxygen-controlled coolant chemistry or specialised
coatings.

### 4.3 Toxicity

- LBE: lead and bismuth are toxic; containment integrity is critical
- FLiBe: contains beryllium fluoride — beryllium compounds are highly toxic
  if released
- Sodium/NaK: caustic reaction products (NaOH) on contact with moisture

---

## 5. Figures of Merit

Useful single-number comparisons for preliminary screening:

### 5.1 Turbulent-Flow HX Compactness FoM

For turbulent forced convection in channels (Dittus-Boelter-type scaling):

    FoM_turb = k^0.6 · ρ^0.8 · cp^0.4 / μ^0.4

Higher values → smaller HX for the same heat duty. Liquid metals score highest.

### 5.2 Specific Heat Transport Capacity

    q_vol = ρ · cp · ΔT_allowable

Heat transported per unit volume of coolant flow, for a given allowable
temperature swing. Useful for sizing piping.

### 5.3 Mass-Penalised Score

For aircraft, combine thermal performance with weight:

    Score = f(HX_compactness, pumping_power, coolant_loop_mass, shielding_mass)

Weighting depends on mission profile (range vs. speed vs. endurance).

---

## 6. Recommendations for Future Work

1. **Add coolant loop mass estimation** to `evaluate_coolants.py`. Requires a
   loop volume model (pipe lengths, header volumes, HX channel inventory).
   Even a rough parametric estimate (e.g. V_loop ∝ A_HX × D_h) would
   differentiate helium from LBE by orders of magnitude.

2. **Add pumping power calculation**. The HX model already outputs ΔP_hot;
   converting to shaft power (ΔP × V̇ / η_pump) and subtracting from turbine
   output gives net thrust impact.

3. **Add shielding mass model** for activated coolants. Even a simple lookup
   (e.g. cm of lead equivalent per coolant type) would capture the first-order
   weight penalty for sodium loops.

4. **Parametric sweeps over mdot_hot and T_hot_in**. Different coolants may
   have different optimal operating points. The current evaluation fixes these
   from the spec, which favours whichever coolant the spec was designed around.

5. **Corrosion compatibility matrix**. Cross-reference each coolant against
   the available wall materials in `materials/hx_walls/possible_materials.py`
   to flag incompatible pairings before running the engine model.

6. **Off-design and transient behaviour**. Evaluate coolant performance at
   takeoff, climb, and idle conditions — not just cruise. Freezing risk for
   molten salts is highest during low-power or shutdown transients.

7. **Intermediate loop consideration**. For reactive coolants (Na, NaK),
   evaluate whether a secondary inert loop (e.g. helium or NaK → He → air)
   is worth the mass and thermal penalty to eliminate the air-contact risk.
