import plotly.graph_objects as go

def plot_two_quantities(x, y1, y2, name1="Quantity 1", name2="Quantity 2", x_label="X-axis", y_label="Y-axis", title="Plot"):
    """
    Plots two quantities on the same figure using Plotly with a white background.

    Parameters:
        x (array-like): Values for the x-axis.
        y1 (array-like): First quantity to plot.
        y2 (array-like): Second quantity to plot.
        name1 (str): Legend label for y1.
        name2 (str): Legend label for y2.
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        title (str): Plot title.
    """

    fig = go.Figure()

    # Add first trace
    fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', name=name1))

    # Add second trace
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name=name2))

    # Layout styling (white background)
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        legend=dict(bgcolor='white'))

    # Make axes lines visible
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)

    fig.show()
