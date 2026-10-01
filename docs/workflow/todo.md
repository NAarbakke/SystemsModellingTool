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
