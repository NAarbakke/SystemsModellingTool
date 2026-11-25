import numpy as np 
import math as m
from systems.missiles.SS_N_33_Tsirkon.specifications import stage1_parameters, stage2_parameters, propellant_parameters
from subsystems.propulsion.motors.solid_rocket.solid_rocket import compute_motor_characteristics
from environment.constants import R
from systems.missiles.SS_N_33_Tsirkon.scenarios.time_setup import t, dt
#from system_specifications.SS_N_33_Zircon.vehicle_parameters import t_coasting

t_coasting = 2.5   #to avoid circular import, for now. how solve this? create mass list through EOM-function

#Get all stage 1 burn parameters
#print("Making stage 1 burn profile")
stage1_burn_profile = compute_motor_characteristics(dt, R, stage1_parameters, propellant_parameters)

#Get all stage 2 burn parameters
#print("Making stage 2 burn profile")
stage2_burn_profile = compute_motor_characteristics(dt, R, stage2_parameters, propellant_parameters)

#Make list for coasting phase between stages
list_length_coasting = int(t_coasting / dt)
list_length_stage1_burn = m.ceil(stage1_burn_profile[1] / dt)
list_length_stage2_burn = m.ceil(stage2_burn_profile[1] / dt)
coasting_list = np.zeros(list_length_coasting)

#Make stage 1 lists
#print("Making stage 1 m_dot, u_e, P_e lists")
m_dot_stage1_list = stage1_burn_profile[2]
u_e_stage1_list = stage1_burn_profile[3]
P_e_stage1_list = stage1_burn_profile[4]
A_nozzle_stage1_list = [stage1_parameters.A_nozzle] * list_length_stage1_burn
#print(A_nozzle_stage1_list)
#print(f"Burn time (stage 1): {stage1_burn_profile[1]} s")

#Make stage 2 lists
#print("Making stage 2 m_dot, u_e, P_e lists")
m_dot_stage2_list = stage2_burn_profile[2]
u_e_stage2_list = stage2_burn_profile[3]
P_e_stage2_list = stage2_burn_profile[4]
A_nozzle_stage2_list = [stage2_parameters.A_nozzle] * list_length_stage2_burn
#print(A_nozzle_stage2_list)
#print(f"Burn time (stage 2): {stage2_burn_profile[1]} s")

#Remove first entry as it is zero, but now t is not 0
m_dot_stage2_list.remove(m_dot_stage2_list[0])                                                          
u_e_stage2_list.remove(u_e_stage2_list[0])
P_e_stage2_list.remove(P_e_stage2_list[0])
#A_nozzle_stage2_list.remove(A_nozzle_stage2_list[0])                                                       #this line needed? think not

#Make list for after burnout
list_length_after_burnout = t.size - len(m_dot_stage1_list) - coasting_list.size - len(m_dot_stage2_list) 
after_burnout_list = np.zeros(list_length_after_burnout)

#Compile complete lists over entire simulation time
m_dot = np.concatenate((m_dot_stage1_list, coasting_list, m_dot_stage2_list, after_burnout_list))
u_e = np.concatenate((u_e_stage1_list, coasting_list, u_e_stage2_list, after_burnout_list))
P_e = np.concatenate((P_e_stage1_list, coasting_list, P_e_stage2_list, after_burnout_list))
A_nozzle = np.concatenate((A_nozzle_stage1_list, coasting_list, A_nozzle_stage2_list, after_burnout_list))

#print(f"Size of m_dot array: {m_dot.size}")
#print(f"Size of A_nozzle array: {A_nozzle.size}")
