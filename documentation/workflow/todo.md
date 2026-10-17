# Custom frontends: FastAPI + React site and FastAPI + Svelte site

Decisions (user, 2026-10-16): Dash/NiceGUI look generic; build one site per stack to compare: React + Vite + Tailwind +
shadcn, and Svelte + Vite. Dark theme in the Vercel/Geist spirit but not generic. Both sites share one design and one API.

## Plan
### API (Python, FastAPI) - `interface/api/`
- [x] `serialise.py`: Snapshot -> JSON (KPI tiles, stations with every FlowState field, EngineLayout geometry with blade-row
      radii resolved, compressor stages, panel definitions); engine input definitions -> JSON
- [x] `app.py`: `GET /api/engines`, `POST /api/engines/{id}/evaluate`; serves the built sites at `/react/` and `/svelte/`
- [x] fastapi + uvicorn into `.venv` and `documentation/requirements.txt`

### Design (same for both sites)
- [x] Black page, near-black surfaces, hairline borders, Geist Sans / Geist Mono (bundled, offline), tabular numbers
- [x] One accent: the heat scale; engine as SVG with a Tt gradient along the gas path on a dot grid
- [x] Shared axial axis: engine on top, station plots below; crosshair snaps to stations, live station readout
- [x] Sidebar: engine switch, grouped sliders with mono readouts, live recompute while dragging (in-flight requests cancelled)

### Sites
- [x] `interface/web/react/`: Vite + React + TypeScript + Tailwind + shadcn/ui (slider, toggle group, select)
- [x] `interface/web/svelte/`: Vite + Svelte 5 + TypeScript, scoped CSS
- [x] Vite dev proxy `/api` -> FastAPI; build output served by FastAPI

### Verify
- [x] API: both engines evaluate; bad input -> clear error
- [x] Both sites build; headless screenshots of each (conventional + nuclear); slider drag recomputes

## Review
- API: `GET /api/engines`, `POST /api/engines/{id}/evaluate` (~1 ms per point); unknown engine -> 404, unknown input -> 422,
  model exception -> `error` field. Payload ~13-15 kB. Serves `/react/`, `/svelte/` from each site's `dist/`.
- Both sites build (React: tsc + vite; Svelte: svelte-check 0 errors + vite). Verified in headless Edge: page loads,
  "Nuclear" switches engine, keyboard on the Mach slider 0.80 -> 0.85 recomputes live (both sites: 30.04 kN,
  "1 changed from SKYF spec"), crosshair hover lights the station across drawing, plots and readout. Screenshots checked.
- shadcn CLI (4.22 latest, 4.21) hung installing a bogus `cn` package -> wrote the three shadcn components by hand
  (same source form the CLI produces) on radix-ui; removed the stray `cn`/`shadcn`/`tw-animate-css` deps. npm audit: 0.
- Dash and NiceGUI apps removed (user: both ugly); Plotly drawing code in `graphics/` kept (unused by the sites).

---

# Turbojet dashboards: Dash (main) + NiceGUI (look comparison)

Decisions (user, 2026-10-16): dynamic only (static HTML removed); Dash replaces Streamlit; dashboards for a
conventional and a nuclear turbojet; a NiceGUI version of the same to compare looks.

## Plan
### Model: conventional turbojet (new, mirrors the nuclear one with the reactor swapped for the combustor)
- [x] `turbojets/single_spool_open_cycle_liquid_fuel_turbojet_specs.py`: inlet, compressor, compressor_geometry, combustor, turbine, nozzle
- [x] `turbojets/single_spool_open_cycle_liquid_fuel_turbojet.py`: stations 0-1-3-4-5-6, m_dot from compressor face,
      thrust with fuel mass (`m_dot_exit*V_exit - m_dot_air*V_0 + (P_6-P_0)*A`), returns F_total, Power, TSFC, m_dot_fuel
- [x] `specifications/SKYF/engine.py`: `specs_open_cycle_liquid_fuel_turbojet` from the existing SKYF component values

### Graphics: core layout works for either heat source
- [x] `core_layout()` takes the heat-section length instead of reactor specs; fuel rods drawn only for the reactor
      (`EngineLayout.rods` / `liner` optional - the combustor gets a flame tube); combustor length nominal (no geometry in the model yet)
- [x] `turbojet_layout()` labels the heat section "Reactor" or "Combustor"

### Framework-neutral engine views (shared by Dash and NiceGUI - inputs defined once)
- [x] `interface/gui/<engine>_view.py` per turbojet: TITLE, STATIONS, STREAMS, `run(specs, T_0, P_0, M_0)`,
      INPUTS (label, range, step, default, which spec field it sets) and `apply_inputs(base, values) -> specs`
- [x] `dashboard_view.py`: tiles as data (label, value, unit, status) instead of HTML strings; KPIs gain TSFC and fuel flow

### Frontends
- [x] Dash: `interface/gui/dash_app.py` - one app, engine picker (Conventional / Nuclear), sidebar inputs built from INPUTS,
      callbacks recompute only on input change; styling in `interface/gui/assets/style.css` (dark theme from `graphics/theme.py`)
- [x] NiceGUI: `interface/gui/nicegui_app.py` - same page and inputs, Tailwind/Quasar styling, for comparison
- [x] Remove Streamlit dashboard, `.streamlit/`, streamlit dependency; add dash + nicegui to `documentation/requirements.txt`
- [x] README / CLAUDE.md: two run commands, a few lines

### Verify
- [x] Both engine models run at the SKYF cruise point (T 250 K, P 100 kPa, M 0.8); numbers sane (thrust > 0, TSFC plausible)
- [x] Both apps start, serve the page, and recompute on an input change (Dash callback test + headless screenshot of each)

## Review
- Conventional turbojet at SKYF cruise: F 28.4 kN, TSFC 55.5 g/(kN·s) (~2.0 lb/lbf/h, plausible at compressor PR 2),
  fuel 1.58 kg/s. Nuclear turbojet unchanged: F 28.1 kN, Q_reactor 63.9 MW, within limits.
- Dash: update callback exercised over HTTP (nuclear, M 0.8 -> 0.5 and T_tet 1200 -> 1500 K: 28.1 -> 21.3 kN).
- Both apps: headless Edge loads the page, clicks "Nuclear", page switches engine (title + reactor tiles); screenshots checked.
- Dash 4 components themed through its `--Dash-*` CSS variables; slider readouts are a clientside callback (no server trip).
- NiceGUI recomputes on slider release, not during drag; bound to 127.0.0.1 (its default is every interface).
- Turbofan layout still builds after the core_layout change (regression check, F 37.9 kN).
- Noted, not changed: the nozzle model's m_dot drops at station 6 (discharge coefficient applied to mass flow) - pre-existing.

---

# Axial compressor: component-owned Specs / Geometry / Sizing

Decision (user, 2026-10-01): templates live with the component, values live in `specifications/SKYF/`.
Imports flow one way: `specifications/` → `subsystems/`, never back.

## Plan
- [x] `axial_compressor_specs.py`: `AxialCompressorSpecs` (PR, eta_poly, phi, psi, U_tip), no defaults
- [x] `axial_compressor_geometry.py`: inputs only (radii, aspect ratios, IGV/EGV chords); span, chords, r_mean as derived properties
- [x] `axial_compressor_sizing.py`: `AxialCompressorSizing` result (U_mean, V_axial, M_rel_tip, n_stages, L_stage, L)
- [x] `axial_compressor.py`: import from the three files above (no `specifications` import), module-level sketch folded into `compute_geometry()`, stubs made valid
- [x] `specifications/SKYF/engine.py`: drop circular import, open-cycle spec gets `AxialCompressorSpecs` + `AxialCompressorGeometry` values
- [x] Open-cycle nuclear turbofan passes geometry to `AxialCompressor`
- [x] Verify: `main_nuclear_engine.py` and `main_open_cycle_nuclear_engine.py` run in `.venv`; `compute_geometry()` returns sane numbers

## Review
- Circular import gone: no component imports `specifications/` for the axial compressor; `engine.py` imports the templates.
- `main_nuclear_engine.py` runs end to end (F_total 49.9 kN). Also needed a stale-path fix in `heat_exchangers.py`
  (`materials.` → `properties.materials.`, left over from the restructure).
- Open-cycle engine: `run_point()` runs; sizing at cruise → U_mean 262 m/s, V_axial 131 m/s, M_rel_tip 1.09, 4 stages, L 0.76 m.
  `main_open_cycle_nuclear_engine.py` then stops in the pgf plot: LaTeX package `underscore.sty` isn't installed (TeX setup, not code).
- Missing spec values raise TypeError (no defaults) — verified.
- SKYF compressor geometry values are placeholders (r_tip 0.30, r_hub 0.15, AR 2.0/2.5, IGV/EGV 0.04 m).

## Deferred
- `CentrifugalCompressor` and other components still import their specs from `specifications/SKYF/engine.py` — same pattern can be applied.

---

# Engine station dashboard (graphics/)

Decisions (user, 2026-09-11): static Plotly HTML (no new deps); use an existing engine — the turbojet file is
empty — so `SingleSpoolOpenCycleNuclearTurbofan`; user fixes the WIP import blocker themselves.

## Plan
- [x] `graphics/engine_dashboard.py`: `build_engine_dashboard(result, streams, title, save_path, subtitle)` → one HTML file
  - [x] KPI row: every scalar in the `run_point()` result (thrust, power, Q_reactor, power density, heat flux, limits)
  - [x] Architecture schematic: component boxes between stations, one row per stream (core, bypass), box colour = exit Tt, hover a station = its full FlowState, hover a box = Tt/Pt in → out
  - [x] Station table: every FlowState field, blank where the model leaves it `None`
  - [x] Tt / Pt / ṁ / V along each stream (gaps, never interpolated, where the model doesn't compute a value)
- [x] `__main__`: run the open-cycle nuclear turbofan at the `main_open_cycle_nuclear_engine.py` cruise point, stream layout defined there
- [x] Verify: run the real turbofan outside the repo with the WIP axial-compressor import stubbed in memory (no repo files touched), render the HTML, screenshot it in headless Edge

## Review
- Engine-agnostic: a new engine only needs its `streams` list (alternating station / component names, matching
  `run_point()` station keys). Branches (bypass) start at their parent station and are drawn as elbows.
- Verified on real model output (F_total 48.99 kN, Q_reactor 99.72 MW, 11 stations). Asserts: 8 KPI tiles, 11 station
  rows, `None` → "—". Screenshots checked for label collisions and overflow. Stream colours validated with the dataviz
  palette validator (all checks pass).
- Plotly.js is loaded from CDN (file ~35 kB, needs internet to view). Light theme only.
- `python -m graphics.engine_dashboard` fails until the engine.py import blocker below is fixed. Nothing else is needed after that.

## Blocked / deferred (user)
- `specifications/SKYF/engine.py` line 2 imports `CompressorGeometry` from WIP `axial_compressor.py` (IndentationError) → every engine module fails to import → the dashboard's `__main__` can't run until that's fixed
- Turbojet `m_dot` source (no fan to set it) → later

---

# Reconnect script references after directory restructuring

## Plan
- [x] Map every deleted old dotted import path to its new location under `subsystems/` / `specifications/`
- [x] Fix imports in all moved `subsystems/propulsion/**` component, helper, and turbofan files
- [x] Restore the entirely-missing import block in `single_spool_closed_cycle_nuclear_fuel_turbofan.py`
- [x] Fix imports in root scripts: `main_conventional_engine.py`, `main_nuclear_engine.py`, `evaluate_coolants.py`
- [x] Verify every touched module actually imports cleanly from the repo root

## Review
All broken references caused by the manual restructuring (`propulsion/` → `subsystems/propulsion/`,
`system_specifications/` → `specifications/`, component files split into per-component subfolders,
`nuclear_fuel_turbofans.py` split into open/closed-cycle files) are now reconnected. 19 files edited,
all pure import-path fixes — no class/function renamed, no logic touched.

Verified by importing each touched module directly (`python -c "import subsystems...`) from repo root.

**Pre-existing bugs found during verification, left untouched (out of scope — predate the restructuring,
confirmed present in `git show HEAD:...` too):**
- `specifications/SKYF/engine.py` defines `specs_open_cycle` but no bare `specs`, and no `EngineSpecifications`
  class — yet `main_conventional_engine.py`, `main_nuclear_engine.py`, `evaluate_coolants.py`, and
  `single_spool_open_cycle_liquid_fuel_turbofan.py` import one of those two missing names.
- `subsystems/propulsion/motors/components/reactors/reactors.py`'s `BlackBoxReactor.__init__` type-hints
  a `BlackBoxReactorSpecs` that was never defined/imported (only `ReactorSpecs` exists) — breaks importing
  the reactors module, which cascades into the open-cycle nuclear turbofan.
- `main_open_cycle_nuclear_engine.py` is a 3-line unfinished draft (no import, incomplete statement) —
  left as-is rather than guessing the intended script.
- `subsystems/gnc/control/control.py` and `subsystems/gnc/navigation/navigation.py` have pre-existing
  syntax errors (unfinished function bodies) — not imported anywhere, unrelated to this fix.

### Decision
- User picked React; the Svelte site is deleted. The API serves React at `/react/` and `/` redirects there.
- Fixed: the page grid stretched past `100vh` and clipped the compressor section (`grid-rows-[minmax(0,1fr)]`).
