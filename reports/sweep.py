"""
Off-design sweep: one input varied over its range, every other input held at the design point.
"""
from dataclasses import dataclass

import numpy as np

from interface.gui.dashboard_view import Input
from reports.report import Case


@dataclass
class Sweep:
    input: Input
    x: list[float]
    results: list[dict | None]      # run_point() scalars per x; None where the point is not physical

    def series(self, key: str, scale: float = 1.0) -> list[float | None]:
        return [None if r is None or not np.isfinite(r[key]) else float(r[key]) * scale for r in self.results]

    @property
    def n_failed(self) -> int:
        return sum(r is None for r in self.results)


def run_sweep(case: Case, key: str, n: int = 25) -> Sweep:
    inp = next((i for group in case.view.inputs.values() for i in group if i.key == key), None)
    if inp is None or inp.options:
        raise ValueError(f"'{key}' is not a numeric input of {case.view.title}")
    x = [float(v) for v in np.linspace(inp.lo, inp.hi, n)]
    results = []
    for v in x:
        try:
            snap = case.view.evaluate(case.values | {key: v})
        except Exception:       # the model raising is a point it cannot run
            snap = None
        ok = snap is not None and not snap.error
        results.append({k: v for k, v in snap.result.items() if k != "stations"} if ok else None)
    return Sweep(inp, x, results)
