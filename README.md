# Systems Modelling Tool

A modular systems-engineering codebase for modelling flight vehicles (missiles,
cruise vehicles) and their propulsion, GNC, and actuation subsystems.

The code is organised to mirror the physical hierarchy of the vehicles it
models: parts → subcomponents → subsystems → systems.

```
systems/          Top-level vehicle assemblies (e.g. cruise_missile.py)
subsystems/        Physical subsystems the systems are built from
  actuators/        Fins, TVC, RCS
  dynamics/          Equations of motion
  gnc/               Guidance, Navigation, Control
  propulsion/        Engine components (inlets, compressors, turbines,
                      combustors, heat exchangers, reactors, nozzles, ...)
                      and assembled turbofan/rocket motor models
specifications/     Per-vehicle spec/parameter sets (e.g. SKYF/)
verifier/           Simulation/model verification tooling
materials/           Shared material property data
plotting/           Plotting utilities
docs/               Architecture, conventions, and theory documentation
workflow/           Task planning notes (todo.md, lessons.md)
```

## Running

Entry-point scripts live at the repo root, e.g.:

```
python main_conventional_engine.py
python main_nuclear_engine.py
python evaluate_coolants.py
```

Run them from the repository root so the `subsystems`/`specifications`
namespace packages resolve correctly.

## Status

Under active development. Several entry-point scripts currently reference
specification classes/fields (`specs`, `EngineSpecifications`,
`BlackBoxReactorSpecs`) that don't exist yet in `specifications/SKYF/engine.py`
— see `workflow/todo.md` for the current punch list.
