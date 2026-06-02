import matplotlib.pyplot as plt


def plot_station_properties(stations, x_attr, y_attr,
                            x_label=None, y_label=None, title=None,
                            annotate=True, save_path=None):
    """Plot one flow property against another across engine stations.

    Uses custom rcParams to mimic the pgfplots aesthetic (Computer Modern
    fonts, clean axes, grid) without requiring LaTeX output.
    """
    x_vals, y_vals, labels = [], [], []
    for station, state in stations.items():
        x = getattr(state, x_attr)
        y = getattr(state, y_attr)
        if x is not None and y is not None:
            x_vals.append(x)
            y_vals.append(y)
            labels.append(station)

    style = {
        "font.family": "serif",
        "font.serif": ["CMU Serif", "Computer Modern Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "axes.grid": True,
        "grid.alpha": 0.7,
        "grid.linewidth": 0.5,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "lines.linewidth": 1.2,
        "lines.markersize": 5,
        "figure.figsize": (5, 3.5),
    }

    with plt.rc_context(style):
        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals, marker="o", zorder=3)

        if annotate:
            for x, y, lbl in zip(x_vals, y_vals, labels):
                ax.annotate(lbl, (x, y), textcoords="offset points",
                            xytext=(6, 6), fontsize=8)

        ax.set_xlabel(x_label or x_attr)
        ax.set_ylabel(y_label or y_attr)
        if title:
            ax.set_title(title)

        fig.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=300)
        plt.show()
