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
