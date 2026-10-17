"""
Side-view cross-section of an engine, to scale in metres: gas paths, solid parts, blade rows, fuel rods or
combustor liner, and station positions.

An engine describes itself as an EngineLayout (turbojet_layout.py, turbofan_layout.py); the web dashboard draws it
(interface/api/serialise.py sends it).
"""
from dataclasses import dataclass

import numpy as np

FREESTREAM_LENGTH = 0.25    # [m] station 0 sits this far ahead of the inlet lip (x = 0)
CASING_THICKNESS = 0.012    # [m] nominal
N_ROD_LINES = 7             # fuel rods drawn per half - symbolic, not the rod count
LABEL_ROOM = 0.14           # [m] space above and below the engine for station numbers and component names

LINER_INSET = 0.25          # [-] liner sits this fraction of the annulus height in from each wall

# Kinds of solid part
BODY = "body"               # hub, shaft, core cowl
CASING = "casing"           # outer casing, nacelle


@dataclass
class GasPath:
    """One stream's flow annulus, sampled along the engine axis [m]."""
    stations: list[str]     # stations along it, upstream to downstream - they set its colour
    x: np.ndarray
    r_inner: np.ndarray
    r_outer: np.ndarray

    def radii(self, x) -> tuple[np.ndarray, np.ndarray]:
        return np.interp(x, self.x, self.r_inner), np.interp(x, self.x, self.r_outer)


@dataclass
class EngineLayout:
    """Where everything sits. x = 0 at the inlet lip, radii from the centreline, all in metres."""
    station_x: dict[str, float]                             # station -> axial position
    gas_paths: list[GasPath]
    solids: list[tuple[np.ndarray, np.ndarray, np.ndarray, str]]    # (x, r_low, r_high, BODY / CASING)
    rotors: list[tuple[float, float, GasPath]]              # blade rows as (start, end, the path they span)
    stators: list[tuple[float, float, GasPath]]
    labels: list[tuple[str, float, float | None]]           # (text, x, radius) - radius None puts it below the engine
    rods: tuple[float, float, GasPath] | None = None        # fuel rod bundle (reactor)
    liner: tuple[float, float, GasPath] | None = None       # flame tube (combustor)

    @property
    def x_end(self) -> float:
        return max(self.station_x.values())

    @property
    def r_max(self) -> float:
        return float(max(r_high.max() for _, _, r_high, _ in self.solids))


def gas_path(stations: list[str], x_inner, r_inner, x_outer, r_outer) -> GasPath:
    """Build a GasPath from the breakpoints of its inner and outer wall (piecewise linear)."""
    x_0, x_1 = max(x_inner[0], x_outer[0]), min(x_inner[-1], x_outer[-1])
    x = np.unique(np.concatenate([np.linspace(x_0, x_1, int(60 * (x_1 - x_0)) + 2), x_inner, x_outer]))
    return GasPath(stations, x, np.interp(x, x_inner, r_inner), np.interp(x, x_outer, r_outer))
