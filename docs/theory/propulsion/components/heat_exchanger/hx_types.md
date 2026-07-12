# Heat Exchanger Types: Reference for Aircraft Applications

---

## 1. Double-Pipe (Shell-and-Tube, Simple)

Two concentric tubes; one fluid in the inner pipe, the other in the annular gap. Can be arranged co- or counter-flow.

```
Hot →  ══════════════════════════════════  → Hot out
       │  ← ← ← ← ← ← ← ← ← ← ← ← ←  │
Cold ← ╚══════════════════════════════════╝ ← Cold in
```

**Pros**
- Extremely simple to manufacture and maintain
- Robust; handles high pressure and temperature
- Well-understood pressure drop and heat transfer behaviour

**Cons**
- Very low surface area density (~50–150 m²/m³)
- Heavy and bulky for a given heat duty
- Poor scalability — multiple units needed for large duties

**Aircraft relevance:** Essentially unsuitable as a primary HX in propulsion systems. Occasionally used for small auxiliary duties (oil cooling, bleed air conditioning) where simplicity outweighs weight penalty. The low surface area density is a fatal flaw for propulsion-scale heat duties in an airframe.

---

## 2. Shell-and-Tube

A bundle of tubes inside a cylindrical shell. One fluid flows through the tubes, the other through the shell, directed by baffles. Multiple pass configurations possible.

```
        Baffle  Baffle  Baffle
Shell → ┌──┬──────┬──────┬──┐ → Shell out
        │ ═╪═ ═╪═ ═╪═ ═╪═ │
        │ ═╪═ ═╪═ ═╪═ ═╪═ │  ← Tube bundle
        │ ═╪═ ═╪═ ═╪═ ═╪═ │
Tube →  └──┴──────┴──────┴──┘ → Tube out
```

**Pros**
- Highly mature technology; extensive design codes (TEMA)
- Handles very high pressures and temperatures
- Wide range of material options
- Easy to clean tube side

**Cons**
- Low-to-moderate surface area density (~100–300 m²/m³)
- Heavy; large footprint
- Baffled shell side has relatively poor heat transfer per unit pressure drop

**Aircraft relevance:** Standard in ground-based power plant and marine applications. Too heavy and bulky for airborne propulsion use. Possibly acceptable in very large nuclear-powered aircraft concepts where absolute weight is less constrained, but still inferior to compact alternatives. Primarily seen in aircraft in small ancillary roles.

---

## 3. Plate-and-Frame (Gasketed)

Corrugated metal plates clamped in a frame with elastomeric gaskets defining flow channels. Fluids alternate between plates in counterflow.

```
         ┌─────────────────────┐
Hot  →   │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ → Hot out
         │░░░░░░░░░░░░░░░░░░░░░│
Cold ←   │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Cold in
         │░░░░░░░░░░░░░░░░░░░░░│
         └─────────────────────┘
         (▓ = hot channel, ░ = cold channel)
```

**Pros**
- High surface area density (~200–500 m²/m³)
- Easily cleaned and reconfigured (add/remove plates)
- Very high heat transfer coefficients due to corrugation-induced turbulence
- Low material cost

**Cons**
- Gaskets limit temperature (<~200°C) and pressure (<~25 bar)
- Not suitable for gas-to-gas duties at high pressure
- Gasket degradation in aggressive chemical or radiation environments
- Vibration can compromise gasket integrity

**Aircraft relevance:** Eliminated from propulsion consideration by temperature and pressure constraints. Air at compressor outlet may already exceed gasket temperature limits. No tolerance for gasket failure in an airborne nuclear system. May appear in ground support equipment or low-temperature auxiliary systems.

---

## 4. Brazed Plate Heat Exchanger

Similar geometry to plate-and-frame but plates are vacuum-brazed together — no gaskets. Typically copper- or nickel-brazed.

```
         ┌─────────────────────┐
Hot  →   │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ → Hot out
         ├─────────────────────┤  ← Brazed joint
Cold ←   │░░░░░░░░░░░░░░░░░░░░░│ ← Cold in
         ├─────────────────────┤
Hot  →   │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ → Hot out
         └─────────────────────┘
```

**Pros**
- Higher pressure capability than gasketed (~45 bar)
- Compact and lightweight
- No gaskets; more reliable
- Good thermal effectiveness

**Cons**
- Temperature limited by braze material (~200°C copper, ~900°C nickel braze)
- Cannot be disassembled for cleaning or repair
- Susceptible to fouling in narrow channels
- Copper brazing incompatible with ammonia or certain coolants

**Aircraft relevance:** Nickel-brazed variants are credible for moderate-temperature aircraft applications (fuel/oil coolers, environmental control). For the high-temperature nuclear propulsion application, copper brazing is ruled out by temperature; nickel brazing approaches the limit. Diffusion-bonded alternatives (PCHE) offer superior performance at the same temperature range.

---

## 5. Compact Plate-Fin Heat Exchanger

Corrugated or formed fin material bonded between flat parting sheets, creating very high surface area density. Fin geometries include plain, wavy, offset-strip (OSF), louvred, and perforated.

```
  Parting sheet  →  ─────────────────────
  Fin layer      →  /\/\/\/\/\/\/\/\/\/\/\   ← Hot side fins
  Parting sheet  →  ─────────────────────
  Fin layer      →  \/\/\/\/\/\/\/\/\/\/\/   ← Cold side fins
  Parting sheet  →  ─────────────────────
                    ←— Flow direction —→
```

**Pros**
- Very high surface area density (500–2000 m²/m³)
- Excellent weight-to-performance ratio
- Fin geometry can be tailored (OSF gives high h at cost of higher ΔP)
- Well-established in aerospace (widely used in cryogenic and aircraft ECS)

**Cons**
- Pressure capability limited by parting sheet thickness (~100 bar max, typically lower)
- Aluminium alloys common — temperature limited to ~200°C; high-temp alloys increase cost and weight
- Narrow passages susceptible to fouling and blockage
- Difficult to clean or repair once brazed

**Aircraft relevance:** The established workhorse for aerospace heat exchangers at moderate temperatures. Used extensively in environmental control systems (ECS) and cryogenic fuel systems. For high-temperature nuclear propulsion, high-temperature alloy (Inconel) plate-fin exchangers are viable but challenged by manufacturing complexity. Offset-strip fin geometry offers the best $Nu/f^{1/3}$ of any passive surface.

---

## 6. Printed Circuit Heat Exchanger (PCHE)

Fluid channels are photochemically etched into flat metal plates, which are then diffusion-bonded into a monolithic block. Channel geometries include straight, zigzag, wavy, and S-shaped.

```
  Plate 1 (hot)  →  ──●──●──●──●──●──●──
                      channels etched in
  Plate 2 (cold) →  ──○──○──○──○──○──○──
                      (opposing direction)
  Plate 3 (hot)  →  ──●──●──●──●──●──●──

  ● = hot channel cross-section (semicircular, ~0.5–2mm)
  ○ = cold channel cross-section
```

**Pros**
- Highest surface area density of metallic HXs (1000–5000 m²/m³)
- Monolithic diffusion-bonded block — no joints, no gaskets, exceptional structural integrity
- Handles very high pressures (up to ~600 bar) and temperatures (material-limited, >900°C in Inconel)
- Compatible with corrosive and radioactive coolants
- Excellent vibration resistance

**Cons**
- High manufacturing cost (photochemical etching + diffusion bonding)
- Cannot be cleaned or repaired once bonded
- Small channels susceptible to fouling — requires clean working fluids
- Zigzag channels give high heat transfer but also high pressure drop; requires careful optimisation

**Aircraft relevance:** The leading candidate for high-temperature nuclear propulsion HX duties. The combination of extreme compactness, pressure integrity, high-temperature alloy compatibility, and absence of leak paths directly addresses the most critical aircraft constraints. Diffusion-bonded Inconel or titanium PCHEs are the state of the art for space and advanced nuclear applications. The primary concern is channel fouling from coolant chemistry products, driving requirement for careful coolant management.

---

## 7. Spiral Heat Exchanger

Two flat plates rolled into a spiral, creating two concentric spiral flow paths. True counterflow is achievable.

```
         ╔═══════════════╗
Hot  →   ║  ╔═════════╗  ║  → Hot out
         ║  ║ ╔═════╗ ║  ║
Cold ←   ║  ║ ║     ║ ║  ║  ← Cold in
         ║  ║ ╚═════╝ ║  ║
         ║  ╚═════════╝  ║
         ╚═══════════════╝
```

**Pros**
- True counterflow in a compact cylindrical form
- Self-cleaning due to high wall shear; handles slurries and fouling fluids
- Single flow path — low risk of maldistribution

**Cons**
- Moderate surface area density (~200–500 m²/m³)
- Pressure limited by rolled construction (~15–20 bar typical)
- Cannot be mechanically cleaned or disassembled easily
- Cylindrical form factor may not suit all installations

**Aircraft relevance:** Limited applicability. Pressure limitations and moderate compactness make it non-competitive with PCHE or plate-fin for propulsion duties. The self-cleaning characteristic is irrelevant in clean gas circuits. Cylindrical form could suit engine nacelle packaging but offers no performance advantage over alternatives.

---

## 8. Regenerative / Rotary Heat Exchanger (Ljungström)

A porous or corrugated matrix wheel rotates between hot and cold gas streams, alternately absorbing and releasing heat. Used exclusively for gas-to-gas heat recovery.

```
           Hot gas duct          Cold gas duct
               ↓                      ↑
          ┌────────┐            ┌────────┐
          │▓▓▓▓▓▓▓▓│            │░░░░░░░░│
          │▓▓▓▓▓▓▓▓│  ← Wheel → │░░░░░░░░│
          │▓▓▓▓▓▓▓▓│  rotating  │░░░░░░░░│
          └────────┘            └────────┘
               ↑                      ↓
           Hot gas out           Cold gas out
```

**Pros**
- Very high effectiveness achievable (>95%)
- Compact for gas-to-gas duties
- Low pressure drop relative to effectiveness
- Can handle very large volumetric flow rates

**Cons**
- Moving parts — mechanical complexity, bearing wear, sealing challenges
- Cross-contamination between streams (carry-over and leakage through seals)
- Not suitable for liquid coolants or pressurised streams
- Seals degrade over time; maintenance intensive

**Aircraft relevance:** Used in some turboprop and APU exhaust heat recovery applications. Cross-contamination is a critical concern in a nuclear application — any leakage of radioactive coolant into the air stream is unacceptable. Moving parts in a high-vibration environment with no maintenance access compounds the reliability concern. Effectively ruled out for nuclear propulsion HX duty.

---

## 9. Heat Pipe Heat Exchanger

Arrays of heat pipes — sealed tubes containing a working fluid that evaporates at the hot end and condenses at the cold end — transfer heat between two separated gas streams with no moving parts.

```
  Hot gas →  [ evaporator section | ← ← ← | condenser section ]  ← Cold gas
             [     (liquid evap.) |  vapour |    (vapour cond.)  ]
             [                   | ← wick →|                    ]
                                  Heat pipe
```

**Pros**
- No cross-contamination — streams are fully isolated
- No moving parts; highly reliable
- Can transport heat over distances; flexible layout
- Isothermal condenser/evaporator behaviour gives uniform temperature distribution

**Cons**
- Low surface area density
- Heat pipe working fluid limits temperature range (water to ~300°C, liquid metal heat pipes for high temp)
- Gravity-dependent orientation for some wick designs (less so for arterial wicks)
- Low effective conductance compared to direct-contact HXs

**Aircraft relevance:** Niche applications in thermal management of electronics and avionics. For propulsion-scale heat transfer, heat pipe arrays are too bulky and have insufficient heat flux density. Liquid metal heat pipes could theoretically serve in high-temperature nuclear applications but are far from mature for this duty. The complete stream isolation is attractive for nuclear safety but insufficient to offset the performance penalty.

---

## 10. Microchannel / Minichannel Heat Exchanger

Hydraulic diameters below ~1 mm (microchannel) or 1–3 mm (minichannel), typically fabricated by extrusion (aluminium automotive condensers) or additive manufacturing. Distinct from PCHE in fabrication route and typical material.

```
  ┌──────────────────────────────────────┐
  │ |  |  |  |  |  |  |  |  |  |  |  | │  ← Extruded multi-port tube
  └──────────────────────────────────────┘
    ↑  each slot is a microchannel (~0.5mm wide)
```

**Pros**
- Extremely high surface area density
- High heat transfer coefficients — thin boundary layers
- Lightweight, especially in aluminium
- Additively manufactured variants allow complex 3D geometries

**Cons**
- Very high pressure drop in small channels
- Extremely susceptible to fouling and blockage
- Aluminium limits temperature and pressure; high-temp alloy microchannels are expensive
- Maldistribution difficult to avoid at manifold

**Aircraft relevance:** Widely used in automotive and aerospace thermal management (RAM air coolers, avionics cooling). Aluminium variants are unsuitable for high-temperature propulsion. Additively manufactured Inconel microchannel HXs are an emerging technology with strong potential for nuclear propulsion — offering PCHE-like performance density with greater geometric freedom. Currently limited by AM surface roughness and material property consistency, but a credible future candidate.

---

## Summary Table

| HX Type | Surface Area Density | Max Temp | Max Pressure | Moving Parts | Aircraft Propulsion Viability |
|---|---|---|---|---|---|
| Double-pipe | Low | High | High | No | Very low |
| Shell-and-tube | Low–moderate | High | High | No | Low |
| Gasketed plate | Moderate–high | Low | Low | No | Very low |
| Brazed plate | Moderate–high | Moderate | Moderate | No | Low–moderate |
| Compact plate-fin | High | Moderate–high | Moderate | No | High |
| PCHE | Very high | High | Very high | No | Very high |
| Spiral | Moderate | Moderate | Low | No | Low |
| Rotary regenerator | High (gas-gas) | High | Low | Yes | Low (nuclear: ruled out) |
| Heat pipe | Low | High (LM) | Low | No | Low |
| Microchannel / AM | Very high | Moderate–high | Moderate | No | Moderate–high (emerging) |
