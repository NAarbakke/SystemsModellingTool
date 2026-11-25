import numpy as np
from graphics.plots.plotting_functions import plot_two_quantities
from subsystems.propulsion.motors.solid_rocket.solid_rocket import compute_motor_characteristics
from environment.constants import R, G, m_earth, r_earth, rho_atm_0, P_atm_0, g_0
from systems.missiles.SS_N_33_Tsirkon.specifications.propellant_parameters import a_coeff, n_coeff, rho_grain
from systems.missiles.SS_N_33_Tsirkon.specifications.stage1_parameters import d, d_throat, d_nozzle, r_grain_in_0, L_motor, t_casing, m_wet, m_dry, m_grain, t_burn, n_nozzle, n_prop, L_grain, r_grain_out, A_throat, A_nozzle, exp_ratio
from systems.missiles.SS_N_33_Tsirkon.specifications.vehicle_parameters import A_ref


#############################################################################################################################################################

#estimate thrust -> then find possible engine I_sp and compositions
#work in vectors ? and define them 
#zircon CM eller BM? rotere gravity component
#from burn time and motor volume/grain mass find burn rate required?
#compute C_D by using velocity and altitude data from track after booster cutoff
#use burn rate calcs etc. to determine realistic grain geometry (size, cutout shape)
#use metric acc. data to find exact thrust profile of the Tsirkon? is this possible? Yes, with trial and tuning of a simulator framework to match the data, given accurate gravity and drag models are incubated. 

#############################################################################################################################################################

theta_avg = np.radians(30)                                                                             #guess

delta_u_gravity = g_0 * np.sin(theta_avg) * t_burn                                                     #integrate
#delta_u_drag = (D_avg / m) * t_burn                                                                   #integrate, add when good model is found, or neglect initially
delta_u_drag = 0
delta_u_achieved = 1000                                                                                #find value, this too high i think

I_sp_achieved = (delta_u_achieved + delta_u_gravity + delta_u_drag) / (g_0 * np.log(m_wet / m_dry))                                                     #WHEN I GET ACC. DATA -> TRY THIS TO ESTIMATE I_SP      also break down into the first thrust phase and the second after reorientation
print(f"I_sp achieved: {I_sp_achieved} s")                                                                                                              #consider this number against how I_sp is typically quoted, i.e is the dry mass only motor hardware or also rest of the rocket -> this will significantly impact the I_sp figure here. Does it even make sense to compute a "achieved" I_sp

#F_thrust_avg = I_sp * m_dot                                                                           #I_sp in m/s
#I_sp = I_tot / (m_grain * g_0)                                                                        #in seconds
#I_sp = u_e / g_0                                                                                      #in seconds                         #play with I_sp value to get appropriate u_e for correct thrust?

