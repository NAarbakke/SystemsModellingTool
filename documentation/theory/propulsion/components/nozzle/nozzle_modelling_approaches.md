# Rocket & Turbofan Nozzle Thrust Analysis

## A First-Principles Reference Manual

**Scope:** Theoretical foundations for computing thrust from convergent and convergent-divergent nozzles, given chamber conditions, nozzle geometry, and propellant properties.

---

## Table of Contents

1. [Nomenclature](#1-nomenclature)
2. [Fundamental Thrust Equation](#2-fundamental-thrust-equation)
3. [Isentropic Flow Relations](#3-isentropic-flow-relations)
4. [Convergent Nozzle Analysis](#4-convergent-nozzle-analysis)
5. [Convergent-Divergent Nozzle Analysis](#5-convergent-divergent-nozzle-analysis)
6. [Exit Velocity Formulations](#6-exit-velocity-formulations)
7. [Real Gas Properties & Chemical Equilibrium](#7-real-gas-properties--chemical-equilibrium)
8. [Variable γ Treatment](#8-variable-γ-treatment)
9. [Loss Mechanisms & Correction Factors](#9-loss-mechanisms--correction-factors)
10. [NASA CEA Methodology](#10-nasa-cea-methodology)
11. [Complete Computational Procedure](#11-complete-computational-procedure)
12. [Turbofan Nozzle Specifics](#12-turbofan-nozzle-specifics)
13. [Quick Reference Tables](#13-quick-reference-tables)

---

## 1. Nomenclature

### Primary Symbols

| Symbol | Definition | Units |
|--------|------------|-------|
| $T_0$, $p_0$ | Chamber (stagnation) total temperature and pressure | K, Pa |
| $T$, $p$, $\rho$ | Static temperature, pressure, density | K, Pa, kg/m³ |
| $T^*$, $p^*$ | Critical (sonic) temperature and pressure | K, Pa |
| $T_e$, $p_e$ | Exit temperature and pressure | K, Pa |
| $A_t$ | Throat area | m² |
| $A_e$ | Exit area | m² |
| $\epsilon$ | Area ratio $A_e/A_t$ | — |
| $\dot{m}$ | Mass flow rate | kg/s |
| $v$ | Flow velocity | m/s |
| $v_e$ | Exit velocity | m/s |
| $a$ | Local speed of sound | m/s |
| $M$ | Mach number | — |
| $\gamma$ | Ratio of specific heats $c_p/c_v$ | — |
| $R$ | Specific gas constant | J/(kg·K) |
| $R_u$ | Universal gas constant (8314 J/(kmol·K)) | J/(kmol·K) |
| $\bar{M}_w$ | Mean molecular weight | kg/kmol |
| $p_a$ | Ambient pressure | Pa |
| $F$ | Thrust | N |
| $h$ | Specific enthalpy | J/kg |
| $h_0$ | Total (stagnation) enthalpy | J/kg |
| $s$ | Specific entropy | J/(kg·K) |
| $c_p$, $c_v$ | Specific heats at constant pressure/volume | J/(kg·K) |

### Performance Parameters

| Symbol | Definition | Units |
|--------|------------|-------|
| $I_{sp}$ | Specific impulse | s |
| $c^*$ | Characteristic velocity | m/s |
| $C_F$ | Thrust coefficient | — |
| $C_d$ | Discharge coefficient | — |
| $C_v$ | Velocity coefficient | — |
| $\lambda$ | Divergence efficiency | — |
| $\eta_n$ | Isentropic nozzle efficiency | — |
| $\eta_{poly}$ | Polytropic efficiency | — |
| $\Gamma$ | Vandenkerckhove function | — |

### Subscripts

| Subscript | Meaning |
|-----------|---------|
| 0 | Stagnation/total/chamber conditions |
| t | Throat |
| e | Exit |
| a | Ambient |
| s | Isentropic |
| * | Critical (sonic) conditions |

---

## 2. Fundamental Thrust Equation

Thrust arises from momentum flux plus pressure imbalance at the nozzle exit. From control volume momentum analysis:

$$\boxed{F = \dot{m} v_e + (p_e - p_a) A_e}$$

**Components:**
- **Momentum thrust:** $\dot{m} v_e$ — dominant term
- **Pressure thrust:** $(p_e - p_a) A_e$ — significant when $p_e \neq p_a$

**Expansion regimes:**
- **Perfectly expanded:** $p_e = p_a$ (design condition, maximum efficiency)
- **Underexpanded:** $p_e > p_a$ (nozzle too short; positive pressure thrust)
- **Overexpanded:** $p_e < p_a$ (nozzle too long; negative pressure thrust, possible shock)

---

## 3. Isentropic Flow Relations

For an ideal gas undergoing isentropic (adiabatic, reversible) expansion with constant $\gamma$:

### Temperature Ratio
$$\frac{T_0}{T} = 1 + \frac{\gamma - 1}{2} M^2$$

### Pressure Ratio
$$\frac{p_0}{p} = \left(1 + \frac{\gamma - 1}{2} M^2\right)^{\frac{\gamma}{\gamma - 1}}$$

### Density Ratio
$$\frac{\rho_0}{\rho} = \left(1 + \frac{\gamma - 1}{2} M^2\right)^{\frac{1}{\gamma - 1}}$$

### Area-Mach Relation
$$\frac{A}{A_t} = \frac{1}{M} \left[ \frac{2}{\gamma + 1} \left(1 + \frac{\gamma - 1}{2} M^2 \right) \right]^{\frac{\gamma + 1}{2(\gamma - 1)}}$$

### Critical Ratios (at $M = 1$)

$$\frac{T^*}{T_0} = \frac{2}{\gamma + 1}$$

$$\frac{p^*}{p_0} = \left( \frac{2}{\gamma + 1} \right)^{\frac{\gamma}{\gamma - 1}}$$

$$\frac{\rho^*}{\rho_0} = \left( \frac{2}{\gamma + 1} \right)^{\frac{1}{\gamma - 1}}$$

| γ | $p^*/p_0$ | $T^*/T_0$ | $\rho^*/\rho_0$ |
|---|-----------|-----------|-----------------|
| 1.20 | 0.5644 | 0.9091 | 0.6209 |
| 1.25 | 0.5549 | 0.8889 | 0.6243 |
| 1.30 | 0.5457 | 0.8696 | 0.6276 |
| 1.33 | 0.5404 | 0.8584 | 0.6295 |
| 1.40 | 0.5283 | 0.8333 | 0.6340 |

---

## 4. Convergent Nozzle Analysis

### 4.1 Choking Criterion

A convergent nozzle chokes when the pressure ratio exceeds the critical value:

$$\frac{p_0}{p_a} \geq \left( \frac{\gamma + 1}{2} \right)^{\frac{\gamma}{\gamma - 1}}$$

| γ | Critical pressure ratio |
|---|------------------------|
| 1.20 | 1.772 |
| 1.30 | 1.832 |
| 1.40 | 1.893 |

### 4.2 Choked Flow ($M_e = 1$)

When choked, exit conditions are sonic and independent of downstream pressure:

$$T_e = T^* = \frac{2 T_0}{\gamma + 1}$$

$$p_e = p^* = p_0 \left( \frac{2}{\gamma + 1} \right)^{\frac{\gamma}{\gamma - 1}}$$

$$v_e = a^* = \sqrt{\gamma R T^*} = \sqrt{\frac{2\gamma}{\gamma + 1} R T_0}$$

**Mass flow rate (maximum):**

$$\dot{m} = \frac{p_0 A_t}{\sqrt{T_0}} \sqrt{\frac{\gamma}{R}} \left( \frac{2}{\gamma + 1} \right)^{\frac{\gamma + 1}{2(\gamma - 1)}}$$

Or using the Vandenkerckhove function:

$$\dot{m} = \frac{p_0 A_t \, \Gamma}{\sqrt{R T_0}}$$

where:

$$\Gamma = \sqrt{\gamma} \left( \frac{2}{\gamma + 1} \right)^{\frac{\gamma + 1}{2(\gamma - 1)}}$$

| γ | Γ |
|---|---|
| 1.20 | 0.6471 |
| 1.25 | 0.6530 |
| 1.30 | 0.6586 |
| 1.40 | 0.6847 |

**Thrust (choked convergent):**

$$F = \dot{m} v_e + (p^* - p_a) A_t$$

### 4.3 Unchoked Flow ($M_e < 1$)

When the nozzle is unchoked:

$$\frac{p_0}{p_a} < \left( \frac{\gamma + 1}{2} \right)^{\frac{\gamma}{\gamma - 1}}$$

**Exit pressure equals ambient:**

$$p_e = p_a$$

**Exit Mach number (solve from pressure ratio):**

$$M_e = \sqrt{\frac{2}{\gamma - 1} \left[ \left( \frac{p_0}{p_a} \right)^{\frac{\gamma - 1}{\gamma}} - 1 \right]}$$

**Exit temperature:**

$$T_e = \frac{T_0}{1 + \frac{\gamma - 1}{2} M_e^2}$$

**Exit velocity:**

$$v_e = M_e \sqrt{\gamma R T_e}$$

Or directly from energy:

$$v_e = \sqrt{2 c_p T_0 \left[ 1 - \left( \frac{p_a}{p_0} \right)^{\frac{\gamma - 1}{\gamma}} \right]}$$

**Mass flow rate (unchoked):**

$$\dot{m} = \rho_e v_e A_e = \frac{p_a}{R T_e} v_e A_e$$

Or:

$$\dot{m} = \frac{p_0 A_e}{\sqrt{R T_0}} \cdot M_e \cdot \sqrt{\gamma} \cdot \left( 1 + \frac{\gamma - 1}{2} M_e^2 \right)^{-\frac{\gamma + 1}{2(\gamma - 1)}}$$

**Thrust (unchoked convergent):**

Since $p_e = p_a$:

$$F = \dot{m} \cdot v_e$$

### 4.4 Summary: Choked vs Unchoked

| Quantity | Choked | Unchoked |
|----------|--------|----------|
| $M_e$ | 1 | $< 1$, varies with $p_0/p_a$ |
| $p_e$ | $p^* = p_0 \left(\frac{2}{\gamma+1}\right)^{\frac{\gamma}{\gamma-1}}$ | $p_a$ |
| $\dot{m}$ | Maximum, fixed by $p_0$, $T_0$, $A_t$ | Below maximum, varies with $p_0/p_a$ |
| Pressure thrust | $(p^* - p_a) A_e > 0$ | 0 |

---

## 5. Convergent-Divergent Nozzle Analysis

### 5.1 Operating Principle

The divergent section allows continued supersonic acceleration past $M = 1$, converting more thermal energy to kinetic energy.

### 5.2 Exit Mach Number

Given area ratio $\epsilon = A_e / A_t$, solve the area-Mach relation for $M_e > 1$:

$$\epsilon = \frac{1}{M_e} \left[ \frac{2}{\gamma + 1} \left(1 + \frac{\gamma - 1}{2} M_e^2 \right) \right]^{\frac{\gamma + 1}{2(\gamma - 1)}}$$

This is transcendental and must be solved numerically.

### 5.3 Exit Conditions (Isentropic)

$$T_e = \frac{T_0}{1 + \frac{\gamma - 1}{2} M_e^2}$$

$$p_e = \frac{p_0}{\left(1 + \frac{\gamma - 1}{2} M_e^2 \right)^{\frac{\gamma}{\gamma - 1}}}$$

$$v_e = M_e \sqrt{\gamma R T_e}$$

Or directly:

$$v_e = \sqrt{\frac{2\gamma}{\gamma - 1} R T_0 \left[1 - \left(\frac{p_e}{p_0}\right)^{\frac{\gamma-1}{\gamma}}\right]}$$

### 5.4 Thrust

$$F = \dot{m} v_e + (p_e - p_a) A_e$$

where $\dot{m}$ is determined by throat conditions (choked flow).

### 5.5 Characteristic Velocity and Thrust Coefficient

**Characteristic velocity** (chamber/throat performance):

$$c^* = \frac{p_0 A_t}{\dot{m}} = \frac{\sqrt{R T_0}}{\Gamma}$$

**Thrust coefficient** (nozzle expansion performance):

$$C_F = \frac{F}{p_0 A_t}$$

**Ideal thrust coefficient:**

$$C_{F,ideal} = \Gamma \sqrt{\frac{2\gamma^2}{\gamma - 1} \left[ 1 - \left( \frac{p_e}{p_0} \right)^{\frac{\gamma - 1}{\gamma}} \right]} + \frac{p_e - p_a}{p_0} \cdot \epsilon$$

**Thrust decomposition:**

$$F = c^* \cdot C_F \cdot \dot{m} = C_F \cdot p_0 A_t$$

---

## 6. Exit Velocity Formulations

Multiple equivalent expressions exist, each useful in different contexts:

### Form 1: Enthalpy (Most Fundamental)

$$\boxed{v_e = \sqrt{2(h_0 - h_e)} = \sqrt{2 \Delta h}}$$

**Exact** — makes no assumption about $\gamma$ being constant. Use with enthalpy tables or NASA polynomials.

For calorically perfect gas ($c_p$ constant):

$$v_e = \sqrt{2 c_p (T_0 - T_e)}$$

### Form 2: Pressure Ratio (Constant γ)

$$v_e = \sqrt{\frac{2\gamma}{\gamma - 1} R T_0 \left[1 - \left(\frac{p_e}{p_0}\right)^{\frac{\gamma-1}{\gamma}}\right]}$$

Equivalent forms:

$$v_e = \sqrt{\frac{2\gamma}{\gamma - 1} \frac{p_0}{\rho_0} \left[1 - \left(\frac{p_e}{p_0}\right)^{\frac{\gamma-1}{\gamma}}\right]}$$

### Form 3: Mach Number

$$v_e = M_e \sqrt{\gamma R T_e} = M_e \cdot a_e$$

### Form 4: Polytropic (Non-Isentropic)

For real expansion with losses, use polytropic exponent $n < \gamma$:

$$v_e = \sqrt{\frac{2n}{n - 1} R T_0 \left[1 - \left(\frac{p_e}{p_0}\right)^{\frac{n-1}{n}}\right]}$$

### Summary Table

| Form | Equation | Assumptions |
|------|----------|-------------|
| Enthalpy | $v_e = \sqrt{2(h_0 - h_e)}$ | None — always valid |
| Temperature | $v_e = \sqrt{2 c_p (T_0 - T_e)}$ | Constant $c_p$ |
| Pressure ratio | $v_e = \sqrt{\frac{2\gamma}{\gamma-1} R T_0 \left[1 - \left(\frac{p_e}{p_0}\right)^{\frac{\gamma-1}{\gamma}}\right]}$ | Constant $\gamma$ |
| Mach | $v_e = M_e \sqrt{\gamma R T_e}$ | Need $M_e$, $T_e$ |
| Polytropic | Same as pressure ratio with $n$ | Constant $n$ |

---

## 7. Real Gas Properties & Chemical Equilibrium

### 7.1 Why Real Gas Treatment Matters

Combustion products are mixtures (H₂O, CO₂, CO, H₂, OH, O₂, N₂, etc.) whose:
- Composition shifts with temperature and pressure
- Properties ($\gamma$, $c_p$, $R$) vary through the nozzle
- Molecular weight affects performance significantly

### 7.2 Mixture Properties

**Mean molecular weight:**

$$\bar{M}_w = \left( \sum_i \frac{Y_i}{M_{w,i}} \right)^{-1}$$

where $Y_i$ is mass fraction of species $i$.

**Specific gas constant:**

$$R = \frac{R_u}{\bar{M}_w}$$

**Mixture specific heat:**

$$c_p = \sum_i Y_i \cdot c_{p,i}(T)$$

**Ratio of specific heats:**

$$\gamma = \frac{c_p}{c_v} = \frac{c_p}{c_p - R}$$

### 7.3 NASA Polynomial Thermodynamic Data

Species properties come from 7-coefficient NASA polynomials:

$$\frac{c_p}{R} = a_1 + a_2 T + a_3 T^2 + a_4 T^3 + a_5 T^4$$

$$\frac{h}{RT} = a_1 + \frac{a_2}{2} T + \frac{a_3}{3} T^2 + \frac{a_4}{4} T^3 + \frac{a_5}{5} T^4 + \frac{a_6}{T}$$

$$\frac{s}{R} = a_1 \ln T + a_2 T + \frac{a_3}{2} T^2 + \frac{a_4}{3} T^3 + \frac{a_5}{4} T^4 + a_7$$

### 7.4 Frozen vs Equilibrium Flow

**Equilibrium flow:**
- Composition continuously re-equilibrates as T and p change
- Upper bound on performance
- Assumes infinite reaction rates

**Frozen flow:**
- Composition fixed at some point (typically throat)
- Lower bound on performance
- Assumes zero reaction rates downstream of freeze point

**Reality:** Between these bounds, depending on reaction kinetics and residence time.

### 7.5 Equilibrium Calculation

Chemical equilibrium is found by minimizing Gibbs free energy:

$$G = \sum_j n_j \mu_j$$

subject to element conservation constraints. NASA CEA uses this approach with Newton iteration.

---

## 8. Variable γ Treatment

### 8.1 When Constant γ Fails

For hot rocket exhaust, $\gamma$ may vary from ~1.15 in the chamber to ~1.25 at the exit. The closed-form isentropic relations assume constant $\gamma$ and introduce errors of 2-5%.

### 8.2 Effective γ Approach

Use a carefully chosen average:

$$\gamma_{eff} = \frac{\gamma_{chamber} + \gamma_{exit}}{2}$$

Or the effective $\gamma$ for the expansion process:

$$\gamma_{eff} = \frac{\ln(p_0/p_e)}{\ln(p_0/p_e) - \ln(\rho_0/\rho_e)}$$

### 8.3 Entropy Method (What CEA Does)

Instead of integrating ODEs, use thermodynamic tables and the entropy constraint:

**Define entropy function:**

$$\phi(T) = \int_{T_{ref}}^{T} \frac{c_p(T')}{T'} dT'$$

**Entropy at any state:**

$$s(T,p) = \phi(T) - R \ln\frac{p}{p_{ref}}$$

**Isentropic constraint:**

$$s(T_e, p_e) = s(T_0, p_0) = s_0$$

**Solution procedure at each nozzle station with known $p$:**

1. Given constraint: $s(T, p) = s_0$
2. Solve: $\phi(T) = s_0 + R \ln(p/p_{ref})$
3. Invert $\phi(T)$ to find $T$ (Newton iteration)
4. Compute: $h = h(T)$, $v = \sqrt{2(h_0 - h)}$, $\rho = p/(RT)$, $a = \sqrt{\gamma(T) R T}$, $M = v/a$

**Finding the throat:** Iterate on $p$ until $M = 1$.

**Finding exit for given area ratio:** Iterate on $p_e$ until continuity $\rho_e v_e A_e = \dot{m}$ is satisfied.

### 8.4 Direct ODE Integration

For non-isentropic cases (friction, heat transfer), integrate:

$$\frac{dM^2}{dx} = M^2 \frac{\left(1 + \frac{\gamma-1}{2}M^2\right)}{\left(1 - M^2\right)} \left[ -\frac{2}{A}\frac{dA}{dx} + \frac{1 + \gamma M^2}{1 + \frac{\gamma-1}{2}M^2} \frac{1}{\gamma} \frac{d\gamma}{dx} \right]$$

The throat ($M = 1$) is a singularity requiring special treatment (L'Hôpital or asymptotic expansion).

---

## 9. Loss Mechanisms & Correction Factors

### 9.1 Overview of Correction Factors

Real nozzles don't achieve isentropic performance. Empirical coefficients correct for this:

| Factor | Definition | Typical Range |
|--------|------------|---------------|
| $C_d$ | Discharge coefficient: $\dot{m}_{actual}/\dot{m}_{ideal}$ | 0.95–0.99 |
| $C_v$ | Velocity coefficient: $v_{e,actual}/v_{e,ideal}$ | 0.92–0.99 |
| $\lambda$ | Divergence factor | 0.97–0.995 |
| $\eta_n$ | Isentropic efficiency: $v_e^2/v_{e,s}^2$ | 0.85–0.99 |

### 9.2 Divergence Loss Factor

Corrects for non-axial exit velocity. **Applies only to momentum thrust:**

$$F = \lambda \cdot \dot{m} v_e + (p_e - p_a) A_e$$

**Conical nozzle:**

$$\lambda = \frac{1 + \cos\alpha}{2}$$

where $\alpha$ is the half-angle.

| Nozzle Type | Half-Angle | λ |
|-------------|------------|---|
| Conical, 15° | 15° | 0.983 |
| Conical, 20° | 20° | 0.970 |
| Bell (80% length) | — | 0.985–0.990 |
| Bell (optimized) | — | 0.995+ |

### 9.3 Isentropic Nozzle Efficiency

$$\eta_n = \frac{v_e^2}{v_{e,s}^2} = \frac{h_0 - h_e}{h_0 - h_{e,s}}$$

**Application methods:**

**Method 1 — Correct velocity:**

$$v_{e,actual} = \sqrt{\eta_n} \cdot v_{e,isentropic}$$

Note: $C_v = \sqrt{\eta_n}$

**Method 2 — Correct enthalpy:**

$$h_{e,actual} = h_0 - \eta_n(h_0 - h_{e,s})$$
$$v_{e,actual} = \sqrt{2(h_0 - h_{e,actual})}$$

### 9.4 Polytropic Efficiency

Model real expansion as polytropic ($pv^n = \text{const}$) with $n < \gamma$:

**Relationship:**

$$\eta_{poly} = \frac{n-1}{n} \cdot \frac{\gamma}{\gamma - 1}$$

Or:

$$n = \frac{\gamma \eta_{poly}}{\gamma \eta_{poly} - \gamma + 1}$$

**Velocity equation:**

$$v_e = \sqrt{\frac{2n}{n - 1} R T_0 \left[1 - \left(\frac{p_e}{p_0}\right)^{\frac{n-1}{n}}\right]}$$

**Relationship between efficiencies:**

$$\eta_n = \frac{1 - (p_e/p_0)^{\frac{n-1}{n}}}{1 - (p_e/p_0)^{\frac{\gamma-1}{\gamma}}}$$

For small pressure ratios: $\eta_n \approx \eta_{poly}$. They diverge for large expansion ratios.

### 9.5 Comprehensive Thrust with Corrections

$$F = \lambda \cdot C_v \cdot \dot{m} \cdot v_{e,ideal} + (p_e - p_a) A_e$$

where:

$$\dot{m} = C_d \cdot \dot{m}_{ideal}$$

### 9.6 What Correction Factors Capture (and Don't)

**Partially captured by $\eta_n$, $C_v$:**
- Boundary layer friction
- Flow non-uniformity
- Turbulence (indirect)
- Minor shocks

**NOT captured:**
| Loss Mechanism | Reason |
|----------------|--------|
| Heat transfer to walls | Reduces $h_0$ upstream — not a nozzle efficiency |
| Combustion inefficiency | Affects $T_0$, composition |
| Two-phase flow | Particle lag, thermal non-equilibrium |
| Chemical kinetics | Need frozen/equilibrium bounds |
| Film cooling | Mass addition at lower enthalpy |
| Severe shock losses | Highly nonlinear |
| Flow separation | Catastrophic; no simple coefficient |

### 9.7 Typical Loss Budget (Well-Designed Rocket)

| Loss Source | Typical $I_{sp}$ Loss | Notes |
|-------------|----------------------|-------|
| Divergence | 0.5–1.5% | Geometry dependent |
| Boundary layer | 0.5–2% | Strong Re dependence |
| Chemical kinetics | 1–4% | Propellant dependent |
| Two-phase (if applicable) | 1–5% | Particles, condensation |
| Combustion inefficiency | 1–3% | Injector design |
| **Total** | **4–12%** | High-performance: 4–6% |

---

## 10. NASA CEA Methodology

### 10.1 What CEA Does

NASA CEA (Chemical Equilibrium with Applications) solves chemical equilibrium via Gibbs free energy minimization, then applies results to rocket performance.

**Key insight:** CEA uses isentropic expansion but handles variable $\gamma$ properly by re-equilibrating at constant entropy — not by using closed-form $pv^\gamma = \text{const}$ relations.

### 10.2 CEA Calculation Procedure

1. **Chamber:** Solve equilibrium at $(h_0, p_0)$ → get $T_c$, composition, $s_c$
2. **Throat:** Solve equilibrium at $(s_c, p_t)$, iterate $p_t$ until $M = 1$
3. **Exit:** Solve equilibrium at $(s_c, p_e)$ for specified $p_e$ or area ratio

Each station is an "sp" problem (entropy-pressure) — not ODE integration.

### 10.3 CEA Assumptions

- One-dimensional flow
- Continuity, energy, momentum conservation
- Zero velocity at chamber inlet
- Isentropic nozzle expansion
- Homogeneous mixing
- Ideal gas law
- Zero lag between condensed and gaseous species

### 10.4 Frozen vs Equilibrium in CEA

**Equilibrium:** Instantaneous chemical equilibrium during expansion (upper performance bound).

**Frozen:** Composition fixed after specified point (lower bound). Typically frozen at throat for conservative estimates.

### 10.5 CEA Outputs Relevant to Thrust

- $T$, $p$, $\rho$ at each station
- $\gamma$, $c_p$, molecular weight
- Mach number, sonic velocity
- $c^*$ (characteristic velocity)
- $C_F$ (thrust coefficient)
- $I_{sp}$ (specific impulse)

**Important:** CEA results are ideal (100% efficiency). Real losses must be applied separately.

---

## 11. Complete Computational Procedure

### 11.1 Inputs Required

- Chamber conditions: $p_0$, $T_0$
- Propellant: fuel type, oxidizer type, mixture ratio (O/F)
- Nozzle geometry: $A_t$, $A_e$ (or $\epsilon = A_e/A_t$), contour
- Ambient pressure: $p_a$

### 11.2 Level 1: Quick Estimate (Constant γ)

1. Estimate $\gamma \approx 1.2$ (rocket) or $1.33$ (turbofan)
2. Estimate $\bar{M}_w$ from propellant chemistry
3. Compute $R = R_u / \bar{M}_w$
4. Solve area-Mach for $M_e$
5. Compute $T_e$, $p_e$, $v_e$ from isentropic relations
6. Compute $\dot{m}$ from choked flow equation
7. Compute $F = \dot{m} v_e + (p_e - p_a) A_e$
8. Apply $\eta_{total} \approx 0.92-0.97$ for real performance

**Accuracy:** ±5-10%

### 11.3 Level 2: CEA-Based Analysis

1. Run NASA CEA with propellants, $p_0$, area ratios
2. Get equilibrium or frozen $T_e$, $p_e$, $v_e$, $\dot{m}$
3. Compute ideal $F$ and $I_{sp}$
4. Apply correction factors:
   - $C_d$ for mass flow
   - $\lambda$ for divergence
   - $C_v$ or $\eta_n$ for velocity losses

**Accuracy:** ±2-5%

### 11.4 Level 3: Detailed CFD

For highest accuracy:
- Navier-Stokes with real gas properties
- Turbulence modeling (k-ε, SST)
- Finite-rate chemistry (if needed)
- Conjugate heat transfer
- Particle tracking (two-phase)

**Accuracy:** ±1-2% (with validation)

### 11.5 Validation Hierarchy

| Level | Method | Uncertainty | Use |
|-------|--------|-------------|-----|
| 1 | Constant-γ isentropic | ±10% | Concept screening |
| 2 | CEA + corrections | ±5% | Preliminary design |
| 3 | CFD | ±2% | Detailed design |
| 4 | Test data | Baseline | Qualification |

---

## 12. Turbofan Nozzle Specifics

### 12.1 Key Differences from Rockets

| Parameter | Rocket | Turbofan |
|-----------|--------|----------|
| Pressure ratio $p_0/p_a$ | 50–200+ | 1.5–4 |
| Chamber temperature | 2500–3500 K | 600–900 K (1500–2000 K with afterburner) |
| $\gamma$ | 1.15–1.25 | 1.30–1.40 |
| Nozzle type | Convergent-divergent | Often convergent only |
| Optimal exit Mach | 2–4+ | ~1 |

### 12.2 Convergent-Only is Often Optimal

For moderate pressure ratios, $M_e \approx 1$ is optimal. A divergent section provides diminishing returns and adds weight/complexity.

### 12.3 Variable Geometry

Many turbofan nozzles adjust $A_e$ for:
- Matching different throttle settings
- Optimizing expansion at varying altitudes
- Accommodating afterburner operation

### 12.4 Two-Stream Considerations

Turbofans have core and bypass flows:
- May mix before a common nozzle
- May have separate nozzles
- Different $\gamma$: ~1.33 for core, ~1.4 for bypass
- Bypass ratio affects overall performance

**Gross thrust (separate nozzles):**

$$F_{gross} = \dot{m}_{core} v_{e,core} + \dot{m}_{bypass} v_{e,bypass}$$

---

## 13. Quick Reference Tables

### 13.1 Critical Pressure Ratios

| γ | $(p_0/p^*)_{critical}$ | $T^*/T_0$ | Γ |
|---|------------------------|-----------|---|
| 1.15 | 1.736 | 0.930 | 0.6377 |
| 1.20 | 1.772 | 0.909 | 0.6471 |
| 1.25 | 1.809 | 0.889 | 0.6560 |
| 1.30 | 1.846 | 0.870 | 0.6643 |
| 1.33 | 1.869 | 0.858 | 0.6696 |
| 1.40 | 1.893 | 0.833 | 0.6847 |

### 13.2 Typical Correction Factors

| Factor | Poor Nozzle | Average | Well-Designed | Optimized Bell |
|--------|-------------|---------|---------------|----------------|
| $C_d$ | 0.92 | 0.96 | 0.98 | 0.99 |
| $C_v$ | 0.92 | 0.96 | 0.98 | 0.99 |
| $\lambda$ | 0.93 | 0.97 | 0.985 | 0.995 |
| $\eta_n$ | 0.85 | 0.92 | 0.96 | 0.98 |

### 13.3 Propellant Performance (Representative)

| Propellant | $T_0$ (K) | $\bar{M}_w$ (kg/kmol) | $\gamma$ | $I_{sp,vac}$ (s) |
|------------|-----------|----------------------|----------|------------------|
| LOX/LH2 | 3250 | 10 | 1.20 | 450 |
| LOX/RP-1 | 3500 | 22 | 1.22 | 350 |
| LOX/CH4 | 3400 | 18 | 1.20 | 365 |
| N2O4/UDMH | 3200 | 22 | 1.24 | 330 |
| Solid (AP/Al) | 3400 | 28 | 1.17 | 280 |

### 13.4 Unit Conversions

| Quantity | SI | Imperial |
|----------|-----|----------|
| Pressure | 1 bar = 100 kPa | = 14.504 psi |
| Specific impulse | $I_{sp}$ (s) | $I_{sp} = v_e / g_0$ |
| $g_0$ | 9.80665 m/s² | 32.174 ft/s² |

### 13.5 Method Selection Guide

| Scenario | Recommended Approach |
|----------|---------------------|
| Quick sizing | Constant-γ isentropic |
| Trade studies | CEA equilibrium |
| Conservative estimate | CEA frozen at throat |
| Detailed design | CFD + CEA validation |
| Flight qualification | Hot-fire test data |

---

## Appendix A: Key Equations Summary

### Fundamental Thrust
$$F = \dot{m} v_e + (p_e - p_a) A_e$$

### Choked Mass Flow
$$\dot{m} = \frac{p_0 A_t \Gamma}{\sqrt{R T_0}}$$

### Vandenkerckhove Function
$$\Gamma = \sqrt{\gamma} \left( \frac{2}{\gamma + 1} \right)^{\frac{\gamma + 1}{2(\gamma - 1)}}$$

### Exit Velocity (General)
$$v_e = \sqrt{2(h_0 - h_e)}$$

### Exit Velocity (Constant γ)
$$v_e = \sqrt{\frac{2\gamma}{\gamma - 1} R T_0 \left[1 - \left(\frac{p_e}{p_0}\right)^{\frac{\gamma-1}{\gamma}}\right]}$$

### Isentropic Temperature Ratio
$$\frac{T_0}{T} = 1 + \frac{\gamma - 1}{2} M^2$$

### Isentropic Pressure Ratio
$$\frac{p_0}{p} = \left(1 + \frac{\gamma - 1}{2} M^2\right)^{\frac{\gamma}{\gamma - 1}}$$

### Area-Mach Relation
$$\frac{A}{A_t} = \frac{1}{M} \left[ \frac{2}{\gamma + 1} \left(1 + \frac{\gamma - 1}{2} M^2 \right) \right]^{\frac{\gamma + 1}{2(\gamma - 1)}}$$

### Thrust Coefficient
$$C_F = \frac{F}{p_0 A_t}$$

### Characteristic Velocity
$$c^* = \frac{p_0 A_t}{\dot{m}} = \frac{\sqrt{R T_0}}{\Gamma}$$

### Specific Impulse
$$I_{sp} = \frac{F}{\dot{m} g_0} = \frac{v_e}{g_0} + \frac{(p_e - p_a) A_e}{\dot{m} g_0}$$

### Divergence Factor (Conical)
$$\lambda = \frac{1 + \cos\alpha}{2}$$

### Corrected Thrust
$$F = \lambda \cdot C_v \cdot \dot{m}_{ideal} \cdot C_d \cdot v_{e,ideal} + (p_e - p_a) A_e$$

---

## Appendix B: References

1. NASA RP-1311: "Computer Program for Calculation of Complex Chemical Equilibrium Compositions and Applications" — Gordon & McBride, 1994

2. Sutton, G.P. & Biblarz, O.: "Rocket Propulsion Elements" — Standard textbook

3. Hill, P. & Peterson, C.: "Mechanics and Thermodynamics of Propulsion" — Covers both rockets and air-breathing engines

4. NASA CEA Online: https://cearun.grc.nasa.gov/

---

*Document compiled from first-principles analysis and NASA CEA methodology review.*
