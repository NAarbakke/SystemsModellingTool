"""
Half cross-section of the engine to scale, gas path shaded by total temperature. Paints the dashboard's layout
(interface/api/serialise.py) - no geometry decided here.
"""
import numpy as np

from reports.elements.plot import Axis, Band, Figure, Line, Polygon, Text
from reports.latex import escape

SOLID_COLOURS = {"body": "body", "casing": "casing"}


def outline(band: dict) -> tuple[list, list]:
    """A band as a closed outline: along the upper curve, back along the lower."""
    return band["x"] + band["x"][::-1], band["hi"] + band["lo"][::-1]


def _ticks(r_max: float) -> str:
    step = 0.1 if r_max < 0.6 else 0.2
    return "{" + ",".join(f"{r:.1f}" for r in np.arange(0.0, r_max + 1e-9, step)) + "}"


def engine_section(point: dict) -> Figure:
    layout = point["layout"]
    r_max, room = layout["r_max"], layout["label_room"]
    stops = [s for p in layout["gas_paths"] for s in p["stops"]]
    Tt = [s["Tt"] for s in stops]

    marks = []
    for path in layout["gas_paths"]:
        stop_x, stop_Tt = [s["x"] for s in path["stops"]], [s["Tt"] for s in path["stops"]]
        marks.append(Band(path["x"], path["lo"], path["hi"], list(np.interp(path["x"], stop_x, stop_Tt))))
    for solid in layout["solids"]:
        marks.append(Polygon(*outline(solid), style=f"fill={SOLID_COLOURS[solid['kind']]}, draw=black!60, line width=0.3pt",
                             command=r"\filldraw"))
    for row in layout["rotors"]:
        marks.append(Polygon(*outline(row), style="fill=black!75"))
    for row in layout["stators"]:
        marks.append(Polygon(*outline(row), style="fill=white, draw=black!75, line width=0.3pt", command=r"\filldraw"))
    if layout["liner"]:
        marks.append(Polygon(*outline(layout["liner"]), style="draw=black!80, line width=0.6pt", command=r"\draw"))
    if layout["rods"]:
        rods = layout["rods"]
        marks += [Line([rods["x0"], rods["x1"]], [r, r], style="black!80, line width=0.6pt, forget plot") for r in rods["r"]]

    # Centreline, stations above, component names below
    marks.append(Line(layout["x_range"], [0, 0], style="black!60, dash dot, thin, forget plot"))
    for s in point["stations"]:
        marks.append(Line([s["x"], s["x"]], [0, r_max + 0.02], style="black!45, densely dashed, very thin, forget plot"))
        marks.append(Text(s["x"], r_max + 0.02, escape(s["key"]), style=r"above, font=\footnotesize"))
    for label in layout["labels"]:
        y = -room / 2 if label["r"] is None else label["r"]
        marks.append(Text(label["x"], y, escape(label["text"]), style=r"font=\footnotesize"))

    axis = Axis(marks, {
        "width": r"0.8\textwidth", "axis equal image": None,
        "xmin": layout["x_range"][0], "xmax": layout["x_range"][1], "ymin": -room, "ymax": r_max + room,
        "ytick": _ticks(r_max), "xlabel": r"Axial position $x$ [m]", "ylabel": r"Radius $r$ [m]",
        "point meta min": min(Tt), "point meta max": max(Tt), "colorbar": None,
        "colorbar style": r"{ylabel={Total temperature $T_t$ [K]}, width=0.25cm, tick label style={font=\footnotesize}}"})
    caption = (r"Half cross-section of the engine to scale, gas path shaded by total temperature $T_t$. "
               r"Numbers mark the stations of \autoref{tab:stations}; filled blades are rotors, open blades stators.")
    return Figure(axis, caption, "engine-section")
