# Heat Exchanger Modelling Theory for Thermo-Hydraulic Cycle Integration

## 1. Introduction and Purpose

A heat exchanger (HX) in a closed Brayton cycle serves to transfer thermal energy from a heat source — in this context, a nuclear reactor coolant loop — to the cycle working fluid. The HX sits between the compressor outlet and turbine inlet: compressed air enters the cold side, absorbs heat from the reactor coolant, and exits at elevated temperature to drive the turbine. The reactor coolant circulates on the hot side, rejecting heat and returning to the core.

From a cycle integration standpoint, the HX is a **boundary condition provider**. Given inlet states on both sides, it must return:

- Cold side outlet total temperature $T_{c,out}$ — the turbine inlet temperature
- Cold side total pressure loss $\Delta P_c$
- Hot side outlet total temperature $T_{h,out}$
- Hot side total pressure loss $\Delta P_h$

The fidelity with which the HX model computes these quantities determines how accurately the overall cycle performance (thermal efficiency, specific thrust, turbine work) is predicted.

---

## 2. Fundamental Heat Transfer Resistance Chain

Heat flows from coolant to air through three resistances in series:

$$\frac{1}{UA} = \frac{1}{\eta_h h_h A_h} + \frac{t}{k_w A_w} + \frac{1}{\eta_c h_c A_c}$$

where $h$ is the convective heat transfer coefficient, $A$ is surface area, $\eta$ is surface efficiency (accounting for fins), $t$ is wall thickness, and $k_w$ is wall thermal conductivity.

For thin metallic walls (Inconel, titanium) typical of PCHEs and plate-fin exchangers, the conductive resistance $t/k_w A_w$ is negligible — typically less than 5% of total resistance. The dominant resistances are convective, particularly on the gas side. This means modelling effort should focus on accurately characterising $h_c$ and $h_h$ rather than wall conduction.

---

## 3. Modelling Hierarchy

Four levels of increasing fidelity are relevant for cycle integration. These are ranked below with justification.

### Level 1 — Fixed Effectiveness (ε-NTU, Lumped, No Geometry)

The HX is characterised entirely by a single prescribed effectiveness $\varepsilon$ and fixed fractional pressure drops on each side.

$$Q = \varepsilon \cdot C_{min} \cdot (T_{h,in} - T_{c,in})$$

$$T_{c,out} = T_{c,in} + \frac{Q}{\dot{m}_c c_{p,c}}, \quad T_{h,out} = T_{h,in} - \frac{Q}{\dot{m}_h c_{p,h}}$$

**Use case:** Rapid cycle scoping where HX geometry is not yet defined. $\varepsilon$ is an input assumption, not a prediction. No physical insight into whether the assumed performance is achievable.

**Limitations:** Cannot predict off-design behaviour. Assumes constant $c_p$ on both sides.

---

### Level 2 — Computed NTU from Geometry (ε-NTU, Lumped, With Geometry)

Geometry is specified (total surface area $A$, hydraulic diameter $D_h$, flow cross-sections). The overall heat transfer coefficient $U$ is computed from Nusselt correlations, and NTU is derived:

$$\text{NTU} = \frac{UA}{C_{min}}$$

For a counterflow arrangement, effectiveness is:

$$\varepsilon = \frac{1 - \exp[-\text{NTU}(1-C^*)]}{1 - C^* \exp[-\text{NTU}(1-C^*)]}$$

where $C^* = C_{min}/C_{max}$.

Pressure drop is computed from the Darcy-Weisbach relation using a friction factor correlation appropriate to the channel geometry.

**Use case:** Preliminary design — HX performance is predicted from geometry rather than assumed. Appropriate when fluid properties do not vary strongly along the flow length.

**Limitations:** Single $c_p$ value used for each fluid (evaluated at mean temperature). Introduces error when temperature span is large, as is typical in nuclear applications.

---

### Level 3 — 1D Discretised Counterflow (Recommended)

The HX length is divided into $N$ axial segments. Within each segment, fluid properties are evaluated at the local bulk temperature. The energy balance and heat transfer calculation are performed segment by segment, with the hot and cold streams marching in opposite directions.

For each segment $i$:

1. Evaluate local properties: $c_p$, $\mu$, $k$, $Pr$ at $T_{h,i}$ and $T_{c,i}$
2. Compute Reynolds number: $Re = \dot{m} D_h / (\mu A_{cs})$
3. Compute Nusselt number from appropriate correlation (e.g. Gnielinski for turbulent flow):
$$Nu = \frac{(f/8)(Re - 1000)Pr}{1 + 12.7\sqrt{f/8}(Pr^{2/3}-1)}$$
4. Compute local heat transfer coefficients: $h = Nu \cdot k / D_h$
5. Compute local overall conductance: $U_i = \left(\frac{1}{h_h} + \frac{t}{k_w} + \frac{1}{h_c}\right)^{-1}$
6. Compute heat transferred: $dQ_i = U_i \cdot dA_i \cdot (T_{h,i} - T_{c,i})$
7. Update temperatures: $T_{h,i+1} = T_{h,i} - dQ_i/(\dot{m}_h c_{p,h,i})$, $T_{c,i-1} = T_{c,i} + dQ_i/(\dot{m}_c c_{p,c,i})$
8. Accumulate pressure drop: $d(\Delta P) = f_i \cdot \frac{dL}{D_h} \cdot \frac{\rho u^2}{2}$

Iteration (typically 2–3 outer loops) is required because cold side temperature profile depends on hot side and vice versa.

**Use case:** The recommended level for propulsion cycle integration at preliminary/detailed design. Captures property variation along the flow length with negligible additional code complexity. $N = 20$–$50$ segments is sufficient for convergence.

**Justification:** For a nuclear turbofan application, reactor outlet temperatures of 800–1000°C and compressor outlet temperatures of 300–400°C give a temperature span where $c_p$ of air varies by ~10%. Assuming constant $c_p$ at this level directly propagates error into the turbine inlet temperature, affecting turbine work and cycle efficiency predictions. Level 3 eliminates this error at minimal cost.

---

### Level 4 — Per-Channel Modelling

Individual channels are modelled explicitly. For a well-designed HX, all channels of each fluid are geometrically identical and carry equal flow — per-channel modelling recovers the same result as Level 3 applied to a single representative channel. This level is only justified for maldistribution studies, manufacturing defect analysis, or detailed thermal stress calculations.

**Not recommended for cycle integration.**

---

### Level 5 — CFD / Conjugate Heat Transfer

Full three-dimensional computational fluid dynamics, typically with conjugate heat transfer (CHT) solving fluid flow and solid conduction simultaneously within the channel geometry. Reynolds-Averaged Navier-Stokes (RANS) turbulence models (k-ω SST, realizable k-ε) are standard for channel-scale simulations; Large Eddy Simulation (LES) is used where turbulence structure matters, such as in the wavy/zigzag channels of PCHEs where secondary flow patterns dominate heat transfer enhancement.

A typical Level 5 workflow for HX channel analysis:

1. Model a representative unit cell (one or a few channels per fluid, with symmetry boundary conditions) rather than the full HX
2. Apply periodic boundary conditions in the transverse directions to represent the infinite array of identical channels
3. Specify mass flux and inlet temperature; extract local wall heat flux, bulk temperature rise, and pressure drop
4. Post-process to extract effective $Nu$ and $f$ as functions of $Re$ — these become the validated correlations fed into Level 2/3 models

**Primary use cases:**
- **Correlation development and validation** — deriving geometry-specific $Nu$ and $f$ correlations for novel channel shapes (e.g. wavy PCHE channels, louvred fins) where literature correlations do not exist or are insufficiently validated
- **Thermal stress analysis** — resolving local temperature gradients in the solid to assess fatigue life, particularly relevant in the high-temperature nuclear application where thermal cycling is severe
- **Maldistribution and manifold design** — assessing flow uniformity at the HX inlet/outlet headers, which affects whether the uniform-channel assumption in Levels 2–4 holds
- **Optimisation of channel geometry** — parametric sweeps of channel angle, amplitude, or fin geometry to maximise $Nu/f^{1/3}$ (the standard performance index)

**Computational cost:** A single RANS unit cell simulation at one operating point typically requires hours to days on an HPC cluster depending on mesh resolution and channel complexity. This makes CFD unsuitable for embedding within a cycle iteration loop but entirely appropriate as an offline tool to characterise the HX geometry once, with results feeding the faster models above.

**Not used for cycle integration.** CFD is the foundation on which the correlations used in Levels 2 and 3 are built or validated — it sits upstream of the cycle model, not inside it.

---

## 4. Channel Representation

For both PCHE and compact plate-fin designs, the correct decomposition is:

- **Distribute along the flow direction** (axial segments) — captures the physically important variation in driving temperature difference and fluid properties
- **Lump across channels** — channels are identical by design; no information is lost by treating each fluid side as a single representative channel scaled by total flow area

The channel count enters the model only implicitly through the total heat transfer surface area $A$ and total flow cross-sectional area $A_{cs}$. These are the natural geometry inputs for cycle-level modelling.

---

## 5. Nusselt and Friction Factor Correlations

Correlation choice should match channel geometry:

| Geometry | Nusselt Correlation | Friction Factor |
|---|---|---|
| Circular / near-circular (PCHE) | Gnielinski (turbulent), Shah & London (laminar) | Churchill (all Re) |
| Offset-strip fin (plate-fin) | Manglik & Bergles | Manglik & Bergles |
| Wavy / zigzag channel (PCHE) | Nusselt enhanced by 20–50% over straight | Friction enhanced similarly |

For zigzag or wavy PCHE channels, geometry-specific correlations from vendor data or CFD-validated fits should replace generic correlations where available, as the enhancement over straight channels is significant and geometry-dependent.

---

## 6. Integration Interface Summary

The HX model exposes the following interface to the cycle solver:

**Inputs:**
- $\dot{m}_c$, $T_{c,in}$, $P_{c,in}$ — from compressor model
- $\dot{m}_h$, $T_{h,in}$, $P_{h,in}$ — from reactor model
- HX geometry parameters: $A$, $D_h$, $L$, $A_{cs,c}$, $A_{cs,h}$

**Outputs:**
- $T_{c,out}$, $P_{c,out}$ — to turbine model
- $T_{h,out}$, $P_{h,out}$ — to reactor loop
- $Q_{total}$ — for energy balance verification

The HX model is called within the cycle iteration loop and should converge internally before returning outputs. A tolerance of $\Delta T < 0.1$ K on outlet temperatures is appropriate for most applications.
