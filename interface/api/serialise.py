"""
Engine views and operating points as JSON for the web frontends.

Python keeps every geometry decision: shapes go out as bands (an x array with a lower and an upper radius curve),
upper half only - the frontend mirrors them about the centreline and paints them. Numbers stay SI except tiles,
which arrive formatted.
"""
from dataclasses import asdict, fields

import numpy as np

from graphics.core_layout import compressor_rows
from graphics.engine_illustration import FREESTREAM_LENGTH, LABEL_ROOM, LINER_INSET, N_ROD_LINES, EngineLayout, GasPath
from interface.gui.dashboard_view import PANELS, EngineView, Snapshot, Tile, performance_tiles, sizing_tiles
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_sizing import AxialCompressorSizing
from subsystems.propulsion.motors.helpers.flow_state import FlowState


def _num(v) -> float | None:
    """JSON-safe float, 5 significant figures; NaN / inf -> None."""
    if v is None:
        return None
    v = float(v)
    return float(f"{v:.5g}") if np.isfinite(v) else None


def _nums(a) -> list[float | None]:
    return [_num(v) for v in a]


def _band(x, lo, hi) -> dict:
    return {"x": _nums(x), "lo": _nums(lo), "hi": _nums(hi)}


def _row(x_0: float, x_1: float, path: GasPath) -> dict:
    """A blade row spanning the local annulus."""
    return _band([x_0, x_1], *path.radii([x_0, x_1]))


#---- Engine definitions ----#
def engine_summary(key: str, label: str, view: EngineView) -> dict:
    return {
        "id": key,
        "label": label,
        "title": view.title,
        "inputs": [
            {"group": group, "items": [
                {k: v for k, v in asdict(i).items() if v is not None}
                | ({"options": [{"value": k, "label": v} for k, v in i.options.items()]} if i.options else {})
                for i in items]}
            for group, items in view.inputs.items()],
        "panels": [
            {"name": name, "unit": unit, "scale": scale,
             "series": [{"field": f, "symbol": s, "kind": (k or "").lower() or None} for f, s, k in series]}
            for name, (unit, scale, series) in PANELS.items()]}
#----------------------------#


#---- One operating point ----#
def _tiles(items: list[Tile]) -> list[dict]:
    return [asdict(t) for t in items]


def _station(key: str, name: str, x: float, state: FlowState) -> dict:
    return {"key": key, "name": name, "x": _num(x)} | {f.name: _num(getattr(state, f.name)) for f in fields(FlowState)}


def _layout(layout: EngineLayout, stations: dict[str, FlowState]) -> dict:
    out = {
        "x_range": [_num(-FREESTREAM_LENGTH - 0.12), _num(layout.x_end + FREESTREAM_LENGTH + 0.05)],
        "r_max": _num(layout.r_max),
        "label_room": LABEL_ROOM,
        "gas_paths": [
            _band(p.x, p.r_inner, p.r_outer) | {"stops": [{"x": _num(layout.station_x[k]), "Tt": _num(stations[k].Tt)} for k in p.stations]}
            for p in layout.gas_paths],
        "solids": [_band(x, lo, hi) | {"kind": kind} for x, lo, hi, kind in layout.solids],
        "rotors": [_row(*r) for r in layout.rotors],
        "stators": [_row(*r) for r in layout.stators],
        "labels": [{"text": t, "x": _num(x), "r": _num(r)} for t, x, r in layout.labels],
        "rods": None,
        "liner": None}

    if layout.rods:
        x_0, x_1, path = layout.rods
        out["rods"] = {"x0": _num(x_0), "x1": _num(x_1), "r": _nums(np.linspace(*path.radii(x_0), N_ROD_LINES + 2)[1:-1])}
    if layout.liner:
        x_0, x_1, path = layout.liner
        r_in, r_out = path.radii([x_0, x_1])
        h = r_out - r_in
        out["liner"] = _band([x_0, x_1], r_in + LINER_INSET * h, r_out - LINER_INSET * h)
    return out


def _compressor(geometry: AxialCompressorGeometry, sizing: AxialCompressorSizing) -> dict:
    """Half cross-section, x = 0 at the compressor face."""
    x_stage, rotors, stators = compressor_rows(geometry, sizing, x_face=0.0)
    x = np.array([0.0, *x_stage, sizing.L])
    r_hub = np.array([sizing.r_hub_stage[0], *sizing.r_hub_stage, sizing.r_hub_stage[-1], sizing.r_hub_stage[-1]])
    r_tip = np.array([sizing.r_tip_stage[0], *sizing.r_tip_stage, sizing.r_tip_stage[-1], sizing.r_tip_stage[-1]])

    def row(x_0, x_1):
        ends = [x_0, x_1]
        return _band(ends, np.interp(ends, x, r_hub), np.interp(ends, x, r_tip))

    spans = [("IGV", 0.0, x_stage[0])]
    spans += [(f"Stage {i + 1}", x_stage[i], x_stage[i + 1]) for i in range(sizing.n_stages)]
    spans += [("EGV", x_stage[-1], sizing.L)]
    return {
        "length": _num(sizing.L),
        "annulus": _band(x, r_hub, r_tip),
        "rotors": [row(*r) for r in rotors],
        "stators": [row(*r) for r in stators],
        "spans": [{"name": n, "x0": _num(a), "x1": _num(b)} for n, a, b in spans],
        "stages": [
            {"n": i + 1, "length": _num(L), "r_hub": _num(h), "r_tip": _num(t)}
            for i, (L, h, t) in enumerate(zip(sizing.L_stage, sizing.r_hub_stage, sizing.r_tip_stage))]}


def snapshot(view: EngineView, snap: Snapshot) -> dict:
    out = {"title": view.title, "subtitle": snap.subtitle, "error": snap.error}
    if snap.error:
        return out
    stations = snap.result["stations"]
    return out | {
        "kpis": _tiles(performance_tiles(snap.result)),
        "stations": [_station(k, view.stations.get(k, k), snap.layout.station_x[k], stations[k]) for k in stations],
        "streams": view.streams,
        "layout": _layout(snap.layout, stations),
        "sizing": _tiles(sizing_tiles(snap.sizing)),
        "compressor": _compressor(snap.geometry, snap.sizing)}
#-----------------------------#
