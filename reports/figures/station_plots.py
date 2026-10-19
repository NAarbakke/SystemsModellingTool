"""
Flow quantities against station, one panel per quantity (the dashboard's PANELS), total and static together.
The x axis is the axial position, so spacing follows the engine and the panels line up with the cross-section.
"""
from reports.elements.plot import ABOVE, Axis, Figure, GroupPlot, Line
from reports.latex import FIELD_SYMBOLS, escape

STYLES = {
    "total": "color=total, thick, mark=*, mark size=1.6pt",
    "static": "color=static, thick, densely dashed, mark=o, mark size=1.6pt",
    None: "color=total, thick, mark=*, mark size=1.6pt"}


def station_plots(engine: dict, point: dict, streams: dict[str, list[str]]) -> Figure:
    by_key = {s["key"]: s for s in point["stations"]}
    x_all = [s["x"] for s in point["stations"]]
    xtick = "{" + ",".join(f"{x:g}" for x in x_all) + "}"
    xticklabels = "{" + ",".join(escape(s["key"]) for s in point["stations"]) + "}"
    columns = 2
    panels = engine["panels"]

    axes = []
    for i, panel in enumerate(panels):
        marks = []
        for stream, keys in streams.items():
            stations = [by_key[k] for k in keys if k in by_key]
            for series in panel["series"]:
                kind = series["kind"]
                legend = None
                if i == 0 and kind and stream == next(iter(streams)):
                    legend = kind.capitalize()
                marks.append(Line(
                    [s["x"] for s in stations],
                    [None if s[series["field"]] is None else s[series["field"]] * panel["scale"] for s in stations],
                    style=STYLES[kind], legend=legend))
        unit = f" [{escape(panel['unit'])}]" if panel["unit"] not in ("", "-") else ""
        symbols = ", ".join(FIELD_SYMBOLS[s["field"]] for s in panel["series"])
        options = {"ylabel": f"{{{escape(panel['name'])} {symbols}{unit}}}", "xtick": xtick, "xticklabels": xticklabels,
                   "ymajorgrids": None, "xmajorgrids": None}
        if i >= len(panels) - columns:
            options["xlabel"] = "Station"
        if i == 0:
            options["legend style"] = ABOVE
        axes.append(Axis(marks, options))

    pad = 0.04 * (max(x_all) - min(x_all))
    drawing = GroupPlot(axes, columns, {"width": r"0.47\textwidth", "height": "4.6cm", "scaled y ticks": "false",
                                        "xmin": min(x_all) - pad, "xmax": max(x_all) + pad,
                                        "yticklabel style": "{/pgf/number format/fixed}"})
    caption = (r"Flow state along the engine. Solid lines: total (stagnation) quantities; dashed: static. "
               r"Stations are placed at their axial position, as in \autoref{fig:engine-section}.")
    return Figure(drawing, caption, "station-plots")
