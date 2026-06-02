import matplotlib.pyplot as plt
import tikzplotlib


def plot_station_properties(stations, x_attr, y_attr,
                            x_label=None, y_label=None, title=None,
                            annotate=True, save_path=None):
    """Plot one flow property against another across engine stations.

    Builds a matplotlib figure then converts it to a .tex file
    containing \\begin{tikzpicture}...\\end{tikzpicture} code.
    """
    x_vals, y_vals, labels = [], [], []
    for station, state in stations.items():
        x = getattr(state, x_attr)
        y = getattr(state, y_attr)
        if x is not None and y is not None:
            x_vals.append(x)
            y_vals.append(y)
            labels.append(station)

    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals, marker="o", zorder=3)
    ax.grid(True, linewidth=0.5, alpha=0.7)

    if annotate:
        for x, y, lbl in zip(x_vals, y_vals, labels):
            ax.annotate(lbl, (x, y), textcoords="offset points",
                        xytext=(6, 6), fontsize=8)

    ax.set_xlabel(x_label or x_attr)
    ax.set_ylabel(y_label or y_attr)
    if title:
        ax.set_title(title)

    fig.tight_layout()
    tikzplotlib.save(save_path or "station_plot.tex")
    plt.close(fig)
