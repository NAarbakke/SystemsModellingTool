"""
One operating point as text tables - the numbers every front end prints (CLI, TUI), with the dashboard's labels,
units and scales (dashboard_view.KPIS, dashboard_view.PANELS). Rows are plain strings: each front end only lays
them out.
"""
import numpy as np

from interface.gui.dashboard_view import PANELS, EngineView, Snapshot, performance_tiles

# Station table: one column per FlowState quantity on the dashboard's station plots
# (header, FlowState field, SI -> display scale)
STATION_COLUMNS = [
    (f"{symbol} [{unit}]", field, scale)
    for unit, scale, series in PANELS.values() for field, symbol, _ in series]


def _cell(value, scale: float) -> str:
    return "–" if value is None or not np.isfinite(value) else f"{value * scale:.5g}"


def performance_rows(snap: Snapshot) -> list[tuple[str, str, str]]:
    """(quantity, value, unit) per run_point() scalar, as the dashboard tiles show them."""
    return [(t.label, t.value, t.unit) for t in performance_tiles(snap.result)]


def station_header() -> list[str]:
    return ["Station", "Name", *(header for header, _, _ in STATION_COLUMNS)]


def station_rows(view: EngineView, snap: Snapshot) -> list[list[str]]:
    """One row per station, in run_point() order."""
    return [
        [key, view.stations.get(key, ""), *(_cell(getattr(state, field), scale) for _, field, scale in STATION_COLUMNS)]
        for key, state in snap.result["stations"].items()]
