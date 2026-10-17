"""
The engine models over HTTP for the web dashboard (interface/web/react/), and the built site itself.

Run from the repo root:  .venv/Scripts/python -m interface.api.app
    API docs   http://127.0.0.1:8000/docs
    Dashboard  http://127.0.0.1:8000/   (after `npm run build` in interface/web/react)
"""
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from interface.api.serialise import engine_summary, snapshot
from interface.gui.dashboard_view import EngineView
from interface.gui.single_spool_open_cycle_liquid_fuel_turbojet_view import VIEW as CONVENTIONAL
from interface.gui.single_spool_open_cycle_nuclear_turbojet_view import VIEW as NUCLEAR

ENGINES: dict[str, tuple[str, EngineView]] = {
    "conventional": ("Conventional", CONVENTIONAL),
    "nuclear": ("Nuclear", NUCLEAR)}

SITE = Path(__file__).parents[1] / "web" / "react" / "dist"

app = FastAPI(title="Systems Modelling Tool API")


@app.get("/api/engines")
def engines() -> list[dict]:
    """Every engine with its inputs (defaults from the vehicle specification) and the plot panels."""
    return [engine_summary(key, label, view) for key, (label, view) in ENGINES.items()]


@app.post("/api/engines/{engine}/evaluate")
def evaluate(engine: str, values: dict[str, Any]) -> dict:
    """One operating point. Missing input values fall back to the defaults."""
    if engine not in ENGINES:
        raise HTTPException(404, f"Unknown engine '{engine}'. Known: {', '.join(ENGINES)}")
    view = ENGINES[engine][1]
    unknown = set(values) - set(view.defaults)
    if unknown:
        raise HTTPException(422, f"Unknown inputs for {engine}: {', '.join(sorted(unknown))}")
    try:
        snap = view.evaluate(view.defaults | values)
    except Exception as e:      # the model raising is an operating point it cannot run, not a server fault
        return {"title": view.title, "subtitle": "", "error": f"The model could not run this point: {e}"}
    return snapshot(view, snap)


# Built site, if present
if SITE.is_dir():
    app.mount("/react", StaticFiles(directory=SITE, html=True), name="react")


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/react/" if SITE.is_dir() else "/docs")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
