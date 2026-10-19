"""
Meridional (half) section of the axial compressor: annulus, blade rows and stage spans, x = 0 at the face.
Paints the dashboard's compressor geometry (interface/api/serialise.py).
"""
from reports.elements.plot import Axis, Figure, Line, Polygon, Text
from reports.figures.engine_section import outline
from reports.latex import escape


def compressor_annulus(point: dict) -> Figure:
    comp = point["compressor"]
    r_top = max(comp["annulus"]["hi"])

    annulus = comp["annulus"]
    hub = {"x": annulus["x"], "lo": [0.0] * len(annulus["x"]), "hi": annulus["lo"]}
    marks = [Polygon(*outline(hub), style="fill=body, draw=black!60, line width=0.3pt", command=r"\filldraw"),
             Polygon(*outline(annulus), style="fill=total!12, draw=black!60, line width=0.3pt", command=r"\filldraw")]
    marks += [Polygon(*outline(r), style="fill=black!75") for r in comp["rotors"]]
    marks += [Polygon(*outline(r), style="fill=white, draw=black!75, line width=0.3pt", command=r"\filldraw")
              for r in comp["stators"]]
    for span in comp["spans"]:
        stage = span["name"].startswith("Stage ")       # stages by number; IGV / EGV are narrow, so upright
        marks.append(Line([span["x0"], span["x0"]], [0, r_top + 0.03], style="black!40, densely dotted, forget plot"))
        marks.append(Text((span["x0"] + span["x1"]) / 2, r_top + 0.03, escape(span["name"].removeprefix("Stage ")),
                          style=r"above, font=\scriptsize" if stage else r"rotate=90, anchor=west, font=\scriptsize"))
    marks.append(Line([0, comp["length"]], [0, 0], style="black!60, dash dot, thin, forget plot"))

    axis = Axis(marks, {
        "width": r"0.7\textwidth", "axis equal image": None, "xmin": -0.02, "xmax": comp["length"] + 0.02,
        "ymin": 0, "ymax": r_top + 0.1, "clip": "false", "xlabel": r"Axial position from face [m]", "ylabel": r"Radius $r$ [m]"})
    caption = (r"Meridional section of the axial compressor: annulus, rotors (filled) and stators (open). "
               r"Numbers mark the stages; IGV and EGV are the inlet and exit guide vanes.")
    return Figure(axis, caption, "compressor-annulus")
