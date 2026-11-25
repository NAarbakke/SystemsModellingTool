import numpy as np
from environment.constants import g_0
from graphics.plots.plot_xy import plot_xy
from graphics.plots.plot_xy_matplotlib import plot_xy_matplotlib
from systems.missiles.AS_23_KODIAK.parameter_estimations import L_D_max_vel
from systems.missiles.AS_23_KODIAK.specifications.specifications import m


# make generic, put specifics into system class


m_AS_23_KODIAK = m
m = np.arange(2000, 10001, 500)

L_D_max_vel_AS_23_KODIAK = L_D_max_vel

#L_D_cruise = np.arange(3, 13, 2)
L_D_cruise = [L_D_max_vel_AS_23_KODIAK, 6, 7, 8, 9, 10]

labels = []
labels.append(f"L/D = {L_D_max_vel_AS_23_KODIAK:.1f} (AS-23 @ Mach 0.79)")
for i in range(len(L_D_cruise) - 1):
    labels.append(f"L/D = {L_D_cruise[i + 1]:.1f}")


T_cruise_req = []

for i in range(len(L_D_cruise)):
    T_cruise_req_entry = (m * g_0) / L_D_cruise[i]
    T_cruise_req.append(T_cruise_req_entry)


plot_xy(
        x=m, 
        y=T_cruise_req, 
        labels=labels, 
        title="Thrust requirement vs Missile mass @ cruise velocity", 
        x_label="Missile mass [kg]", 
        y_label="Thrust requirement [N]", 
        line_colors=["#0065ad", "#af0000",  "#ad0096", "#e6cf00", "#00a824", "#009e9e"], 
        marker_colors=["#0065ad", "#af0000",  "#ad0096", "#e6cf00", "#00a824", "#009e9e"],
        font_family="Calibri",  # Will use Calibri on Windows, fallback elsewhere
        font_size=18,
        title_font_size=24,
        xaxis_precision=0,      # Mass as integers (2000, 2500...)
        yaxis_precision=0,      # Thrust as integers (19620, 24525...)
        legend_position="top-left",
        vertical_line=(2200, "AS-23 mass"),
        vertical_line_color="#000000",
        vertical_line_width=2,
        vertical_line_dash="dash",
        vertical_line_label_position="bottom center")


#plot_xy_matplotlib(
 #   x=m,
  #  y=T_cruise_req,
   # title="Thrust Requirements vs Missile mass",
    #x_label="Mass (kg)",
    #y_label="Thrust Required (N)",
    #labels=labels,
    #line_colors=["#1f77b4", "#d62728"],
    #line_styles=["-", "--"],
    #marker_styles=["", ""],  # No markers on lines
    #font_family="Calibri",  # Will work on Windows, fallback elsewhere
    #font_size=10,
    #title_font_size=12,
    #xaxis_precision=0,      # Mass as integers
    #yaxis_precision=0,      # Thrust as integers
    #legend_position="upper right",
    #vertical_line=(2200, "AS-23 Mass"),
    #vertical_line_color="#2c7bb6",
    #vertical_line_width=2,
    #vertical_line_style="-",
    #vertical_line_label_position="bottom",
    #highlight_point=(2000, (2000 * g_0) / L_D_cruise[0]),
    #highlight_marker="*",
    #highlight_marker_size=150,
    #highlight_marker_color="darkgreen",
    #highlight_text="Min Mass (2000 kg)",
    #highlight_text_position="top",
    #width=8,
    #height=6,
    #dpi=150,
    #savefig("thrust_requirements.png", dpi=300, bbox_inches='tight')
    #)
