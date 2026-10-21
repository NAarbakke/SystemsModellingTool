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
graphics/           Engine layout geometry (to scale) for the dashboard
interface/          FastAPI server (api/) and the React dashboard (gui/react/)
reports/            PDF engineering reports (LaTeX + pgfplots)
documentation/      Architecture, conventions, and theory documentation;
                      requirements.txt; workflow/ task notes (todo.md, lessons.md)
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

Run everything from the repository root so the `subsystems`/`specifications`
namespace packages resolve correctly.

Every engine (turbojets and turbofans, listed in `interface/gui/engines.py`) runs
through the same view, so the CLI, the TUI and the dashboard show the same numbers.
One operating point in the terminal, performance and station tables:

```
.venv\Scripts\python -m interface.cli.run --engine nuclear_turbofan
.venv\Scripts\python -m interface.cli.run --engine nuclear_turbofan --set h_0=5000 --set V_0=250
.venv\Scripts\python -m interface.cli.run --engine nuclear_turbofan --inputs
```

Inputs default to the SKYF specification (`specifications/SKYF/`); the flight
condition is altitude and airspeed, with temperature and pressure from the ISA.
The TUI (`python -m interface.tui.reports_app`) shows the same tables live and
builds PDF reports. Studies live in `analysis/`, e.g.
`.venv\Scripts\python -m analysis.heat_transfer.evaluate_coolants`.

Engine dashboards (a to-scale engine drawing with flow plots underneath, live
inputs) are a web site in `interface/gui/react/` (React +
Vite + Tailwind + shadcn/ui) on top of a FastAPI server in `interface/api/`.
Build the site once (needs Node.js), then one command serves everything:

```
cd interface\gui\react && npm install && npm run build
.venv\Scripts\python -m interface.api.app
    http://127.0.0.1:8000/    (dashboard)    http://127.0.0.1:8000/docs    (API)
```

While editing the site, keep the API running and use `npm run dev` in its folder
(http://localhost:5173/react/) for instant reload.

PDF engine reports (design point, station flow state, compressor, off-design sweeps) are
LaTeX with pgfplots figures; they need TeX Live (`latexmk`, `xelatex`) on PATH:

```
.venv\Scripts\python -m reports.build                      # -> reports/output/conventional.pdf
.venv\Scripts\python -m reports.build --set M_0=0.7 --sweep M_0 T_tet
```

The same reports from a terminal UI (`.venv\Scripts\python -m interface.tui.reports_app`) or the
dashboard's **Export report** button (current slider values, via `POST /api/engines/{id}/report`).

## Status

Under active development. Several entry-point scripts currently reference
specification classes/fields (`specs`, `EngineSpecifications`,
`BlackBoxReactorSpecs`) that don't exist yet in `specifications/SKYF/engine.py`
— see `workflow/todo.md` for the current punch list.
