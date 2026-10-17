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

Turbojet dashboards (conventional and nuclear: a to-scale engine drawing with
flow plots underneath, live inputs) are a web site in `interface/web/react/` (React +
Vite + Tailwind + shadcn/ui) on top of a FastAPI server in `interface/api/`.
Build the site once (needs Node.js), then one command serves everything:

```
cd interface\web\react && npm install && npm run build
.venv\Scripts\python -m interface.api.app
    http://127.0.0.1:8000/    (dashboard)    http://127.0.0.1:8000/docs    (API)
```

While editing the site, keep the API running and use `npm run dev` in its folder
(http://localhost:5173/react/) for instant reload.

## Status

Under active development. Several entry-point scripts currently reference
specification classes/fields (`specs`, `EngineSpecifications`,
`BlackBoxReactorSpecs`) that don't exist yet in `specifications/SKYF/engine.py`
— see `workflow/todo.md` for the current punch list.
