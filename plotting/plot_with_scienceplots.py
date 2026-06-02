import matplotlib.pyplot as plt
import scienceplots  # noqa: F401 – registers styles on import


def plot_station_properties(stations, x_attr, y_attr,
                            x_label=None, y_label=None, title=None,
                            annotate=True, save_path=None):
    """Plot one flow property against another across engine stations.

    Parameters
    ----------
    stations : dict[str, FlowState]
        The ``result["stations"]`` dict from ``run_point``.
    x_attr, y_attr : str
        FlowState attribute names to plot (e.g. ``"Tt"``, ``"Pt"``).
    x_label, y_label : str, optional
        Axis labels.  Defaults to the attribute name.
    title : str, optional
        Plot title.
    annotate : bool
        If True, label each point with its station number.
    save_path : str, optional
        If given, save the figure to this path (supports .png, .pdf, .pgf).
    """
    x_vals, y_vals, labels = [], [], []
    for station, state in stations.items():
        x = getattr(state, x_attr)
        y = getattr(state, y_attr)
        if x is not None and y is not None:
            x_vals.append(x)
            y_vals.append(y)
            labels.append(station)

    with plt.style.context(["science", "grid"]):
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
