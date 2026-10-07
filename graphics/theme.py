"""
Dark theme shared by every figure and page: colours, font and the base plotly styling.
"""
import plotly.graph_objects as go

# Surfaces and ink
PAGE = "#0d0d0d"
SURFACE = "#1a1a19"
INK = "#ffffff"
INK_2 = "#c3c2b7"
MUTED = "#898781"
GRID = "#2c2c2a"
AXIS = "#383835"
BORDER = "rgba(255, 255, 255, 0.10)"

# Series (categorical slots, fixed order) and status
BLUE = "#3987e5"
AQUA = "#199e70"
GOOD = "#0ca30c"
CRITICAL = "#d03b3b"

# Total temperature: one hue, dark (cold) -> bright (hot)
HEAT = [[0.0, "#3b2418"], [0.35, "#8f3a17"], [0.7, "#e2672c"], [1.0, "#ffd08a"]]

# Solid parts of the engine
BODY = "#33332f"
CASING = "#6b6a64"

FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def style(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=70, r=30, t=30, b=40),
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(family=FONT, color=INK_2, size=12),
        hoverlabel=dict(bgcolor="#262624", bordercolor=AXIS, font=dict(family=FONT, color=INK, size=12)),
        legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", font=dict(color=INK_2)))
    fig.update_xaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False, tickfont=dict(color=MUTED))
    return fig
