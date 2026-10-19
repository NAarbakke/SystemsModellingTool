"""
The engine models over HTTP for the web dashboard (interface/gui/react/), and the built site itself.

Run from the repo root:  .venv/Scripts/python -m interface.api.app
    API docs   http://127.0.0.1:8000/docs
    Dashboard  http://127.0.0.1:8000/   (after `npm run build` in interface/gui/react)
"""
import tempfile
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from interface.api.serialise import engine_summary, snapshot
from interface.gui.engines import ENGINES
from reports.build import DEFAULT_POINTS, DEFAULT_SWEEPS, build_report
from reports.report import ReportError

SITE = Path(__file__).parent.parent / "gui" / "react" / "dist"

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


class ReportRequest(BaseModel):
    values: dict[str, Any] = {}
    sweeps: list[str] = DEFAULT_SWEEPS
    points: int = DEFAULT_POINTS


@app.post("/api/engines/{engine}/report", response_class=Response, responses={200: {"content": {"application/pdf": {}}}})
def report(engine: str, request: ReportRequest) -> Response:
    """The PDF engineering report for one design point (reports/), built fresh; takes ~15-30 s."""
    if engine not in ENGINES:
        raise HTTPException(404, f"Unknown engine '{engine}'. Known: {', '.join(ENGINES)}")
    with tempfile.TemporaryDirectory() as work:       # one folder per request: builds can run side by side
        try:
            pdf = build_report(engine, request.values, request.sweeps, max(3, request.points), Path(work) / f"{engine}.pdf")
        except ReportError as e:
            raise HTTPException(422, str(e).splitlines()[0])
        content = pdf.read_bytes()
    return Response(content, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{engine}_report.pdf"'})


# Built site, if present
if SITE.is_dir():
    app.mount("/react", StaticFiles(directory=SITE, html=True), name="react")


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/react/" if SITE.is_dir() else "/docs")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
