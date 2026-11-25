import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import json

from systems.missiles.SS_N_33_Tsirkon.scenarios.time_setup import dt, t, n_t
from environment.constants import g_0, rad2deg
from integrators.forward_euler import forward_euler
from integrators.runge_kutta_4 import runge_kutta_4
from subsystems.body.flight_dynamics.flat_earth_6dof_eom import flat_earth_6dof_eom
from subsystems.body.flight_dynamics.flat_earth_3dof_eom import flat_earth_3dof_eom
from environment.atmosphere.get_environmental_conditions import get_environmental_conditions
from graphics.plots.plotting_functions import plot_state_vector, plot_3_quantities, plot_force_vector, plot_n_nr_of_quantities_in_2D, plot_moment_vector
from systems.missiles.SS_N_33_Tsirkon.specifications import motor_burn_profile, aerodynamic_model, vehicle_parameters, stage1_parameters, stage2_parameters, initial_conditions

with open('data/missiles/SS_N_33_Tsirkon/simulation_setup/SS_N_33_Tsirkon_setup.json', 'r') as file:
    simulation_setup = json.load(file)


if simulation_setup['governing_equations'] == "flat_earth_6dof_eom":

    #Create state vector array
    state_vector = np.zeros((initial_conditions.state_vector_0.size, t.size), dtype=np.float64)         #need to make suitable for 3dof - use skyfall sim as test case to develop class based code
    force_vector = np.zeros((initial_conditions.force_vector_0.size, t.size), dtype=np.float64)

    #Insert initial state (t = 0)
    state_vector[:, 0] = initial_conditions.state_vector_0
    force_vector[:, 0] = initial_conditions.force_vector_0

    #Run simulation
    t, state_vector, force_vector = runge_kutta_4(flat_earth_6dof_eom, t, state_vector, force_vector, dt, vehicle_parameters, aerodynamic_model, motor_burn_profile)
    #t, state_vector, force_vector = runge_kutta_4(flat_earth_3dof_eom, t, state_vector, force_vector, dt, vehicle_parameters, aerodynamic_model, motor_burn_profile)

    #divide into stage 1 and 2 sims, using vehicle classes, alternatively an object for Stage1 and Stage2?


#Data post-processing
pos_north = np.zeros((n_t, 1))
pos_east = np.zeros((n_t, 1))
altitude = np.zeros((n_t, 1))

true_airspeed = np.zeros((n_t, 1))
rho_atm = np.zeros((n_t, 1))
P_atm = np.zeros((n_t, 1))
sound_speed = np.zeros((n_t, 1))
g = np.zeros((n_t, 1))

Mach_nr = np.zeros((n_t, 1))
alpha = np.zeros((n_t, 1))
beta = np.zeros((n_t, 1))

for i, element in enumerate(t):
    pos_north[i, 0] = state_vector[9, i]
    pos_east[i, 0] = state_vector[10, i]
    altitude[i, 0] = -state_vector[11, i]                                                                   #why minus
    true_airspeed[i, 0] = np.sqrt(state_vector[0, i]**2 + state_vector[1, i]**2 + state_vector[2, i]**2)
    rho_atm[i, 0], P_atm[i, 0], sound_speed[i, 0], g[i, 0] = get_environmental_conditions(altitude[i, 0])
    Mach_nr[i, 0] = true_airspeed[i, 0] / sound_speed[i, 0]

    if state_vector[0, i] == 0 and state_vector[2, i] == 0:
        w_over_u = 0
    else:
        w_over_u = state_vector[2, i] / state_vector[0, i]

    alpha[i, 0] = np.atan(w_over_u)

    if state_vector[1, i] == 0 and true_airspeed[i, 0] == 0:
        v_over_VT = 0
    else:
        v_over_VT = state_vector[1, i] / true_airspeed[i, 0]

    beta[i, 0] = np.asin(v_over_VT)


I_tot = sum(force_vector[3]) * dt         #thik its correct now                              #decompose into stage 1 and 2
I_sp_simulated = I_tot / (g_0 * stage1_parameters.m_grain)              #simulate burn in vacuum or at sealevel for I_sp calc? considering P_atm changes in flight
print(f"I_sp from simulation: {I_sp_simulated} s")



#Plotting - move to plotting folder - read from stored state vector data
state_vector_over_time_plot = plot_state_vector(t, state_vector)        #add inertia plots
force_vector_over_time_plot = plot_force_vector(t, force_vector[0:5, :])
moment_vector_over_tme_plot = plot_moment_vector(t, force_vector[5:8, :])
spatial_plot = plot_3_quantities(pos_north, -pos_east, altitude)                #east pos sign reversed
flight_data_plots = plot_n_nr_of_quantities_in_2D(t, 3, [alpha * rad2deg, beta * rad2deg, Mach_nr], ['Alpha [deg]', 'Beta [deg]', 'Mach nr [-]'])
#air_data_plots = plot_n_nr_of_quantities_in_2D(t, 4, [rho_atm, P_atm, sound_speed, g], ['Atmospheric density [kg/m3]', 'Atmospheric pressure [Pa]', 'Speed of sound [m/s]', 'Gravitational acceleration [m/s2]'])


####store t and state vector to do quick plots and analysis without rerunning sim


