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

## Setup

Dependencies are listed in **`documentation/requirements.txt`** and are installed
into a project-local virtual environment (`.venv/`, gitignored), never into the
system Python. From the repository root (Windows):

```
python -m venv .venv
.venv\Scripts\activate
pip install -r documentation/requirements.txt
```

In VS Code, pick `.venv` via *Python: Select Interpreter*. When you add a
package, install it into `.venv` and add it to `documentation/requirements.txt`.

## Running

Entry-point scripts live at the repo root, e.g.:

```
python main_conventional_engine.py
python main_nuclear_engine.py
python evaluate_coolants.py
```

Run them from the repository root so the `subsystems`/`specifications`
namespace packages resolve correctly.

Engine dashboards (a to-scale engine drawing with flow plots underneath) live
in `interface/gui/`, named after their engine:

```
.venv\Scripts\python -m interface.gui.<engine>_dashboard_static                 (writes an HTML file)
.venv\Scripts\python -m streamlit run interface/gui/<engine>_dashboard.py       (live page with inputs)
```

## Status

Under active development. Several entry-point scripts currently reference
specification classes/fields (`specs`, `EngineSpecifications`,
`BlackBoxReactorSpecs`) that don't exist yet in `specifications/SKYF/engine.py`
— see `workflow/todo.md` for the current punch list.
