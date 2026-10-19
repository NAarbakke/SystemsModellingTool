"""
Performance against the swept input, one panel per output, design point marked.
"""
from interface.gui.dashboard_view import KPIS
from reports.elements.plot import ABOVE, Axis, Figure, GroupPlot, Line
from reports.latex import escape, in_sentence, split_unit
from reports.sweep import Sweep


def kpi_label(key: str) -> str:
    label, unit, _ = KPIS.get(key, (key, "", 1.0))
    return escape(label) + (f" [{escape(unit)}]" if unit else "")


def sweep_plot(sweep: Sweep, outputs: list[str], design: dict, x_design: float) -> Figure:
    name, unit = split_unit(sweep.input.label)
    xlabel = escape(name) + (f" [{escape(unit)}]" if unit else "")
    axes = []
    for i, key in enumerate(outputs):
        scale = KPIS.get(key, (key, "", 1.0))[2]
        marks = [
            Line(sweep.x, sweep.series(key, scale), style="color=total, thick, no markers", legend="Off-design" if i == 0 else None),
            Line([x_design], [design[key] * scale], style="only marks, mark=*, mark size=2.2pt, color=static",
                 legend="Design point" if i == 0 else None)]
        options = {"xlabel": f"{{{xlabel}}}", "ylabel": f"{{{kpi_label(key)}}}", "grid": "major"}
        if i == 0:
            options["legend style"] = ABOVE
        axes.append(Axis(marks, options))

    drawing = GroupPlot(axes, 2, {"width": r"0.47\textwidth", "height": "5.2cm", "scaled y ticks": "false",
                                  "yticklabel style": "{/pgf/number format/fixed}"})
    caption = (rf"Off-design performance against {escape(in_sentence(name))}, all other inputs at the design "
               r"point (\autoref{tab:inputs}).")
    if sweep.n_failed:
        caption += f" Gaps: {sweep.n_failed} of {len(sweep.x)} points are not physical."
    return Figure(drawing, caption, f"sweep-{sweep.input.key.replace('_', '-')}")
