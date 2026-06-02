
import numpy as np
from parameters import m_to, g, C_L_to, rho_sea, S, d_to, C_D_to, mu_r, T_sea, P_sea, y_air, y_exhaust, c_p_exhaust, c_p_air, R_air, R_exhaust, Q_R, A_core#, A_bypass
from cruise import A_bypass


    ### Take-off thrust ###
u_to = np.sqrt((2 * m_to * g) / (C_L_to * rho_sea * S))
M_to = u_to / np.sqrt(y_air * R_air * T_sea)
u_to = 1.2 * u_to #with safety factor
print(u_to)
a_avg = u_to**2 / (2 * d_to)

W_to = m_to * g
F_acc = m_to * a_avg
D_to = 0.5 * C_D_to * rho_sea * u_to**2 * S
F_rr = mu_r * W_to

T_to_req = F_acc + D_to + F_rr
#T_to_engine = T_to_req / 2 #assume it needs both engines to take off







########### T-s calcs ###########

    ### Cycle parameters at take-off (chosen) ###
n_diff = 0.90 #diffuser efficiency
n_fan = 0.90 #fan (LP compressor) efficiency
n_comp = 0.90 #HP compressor efficiency
n_HP_turb = 0.93
n_LP_turb = 0.93
n_n_core = 0.97
n_n_bypass = 0.97
FPR = 2.3 #fan pressure ratio
CPR = 30 #HP compressor pressure ratio at
r_c = 0.98 #combustion pressure ratio
B_to = 7
T_turb_entry = 2200 #K
    #higher at take-off surely, but do not want to be close to material max at cruise



    #***** 1 *****#
T_1 = T_sea
P_1 = P_sea


    #***** 01 *****#
T_01 = T_1 * (1 + ((y_air - 1) / 2) * M_to**2)
T_01s = T_1 + n_diff * (T_01 - T_1)
P_01s = P_1 * (T_01s / T_1)**(y_air / (y_air - 1))
P_01 = P_01s


    #***** 02 *****#
P_02s = FPR * P_01
P_02 = P_02s
T_02s = T_01 * FPR**((y_air - 1) / y_air)
T_02 = T_01 + ((T_02s - T_01) / n_fan)


    #***** 8 (choked) *****#
PR_choked_bypass = ((y_air + 1) / 2)**(y_air / (y_air - 1))
M_t = 1
T_0t_bypass = T_02
M_8 = M_t #choked
T_08 = T_02
T_8 = T_08 / (1 + ((y_air - 1) / 2) * M_8**2)
T_8s = T_02 - (T_02 - T_8) / n_n_bypass
P_8s = P_02 * (T_8s / T_02)**(y_air / (y_air - 1))
P_8 = P_8s
u_8 = np.sqrt(2 * c_p_air * (T_08 - T_8))
M_8_calced = u_8 / np.sqrt(y_air * R_air * T_8)

P_0t_bypass = P_02
PR_check_bypass = P_0t_bypass / P_sea


    #***** 03 *****#
P_03s = CPR * P_02
P_03 = P_03s
T_03s = T_02 * CPR**((y_air - 1) / y_air)
T_03 = T_02 + ((T_03s - T_02) / n_comp)


    #***** 04 *****#
T_04 = T_turb_entry
f_to = (c_p_air * T_03 - c_p_exhaust * T_04) / (c_p_exhaust * T_04 - Q_R)
T_04s = T_04
P_04 = r_c * P_03
P_04s = P_03


    #***** 05 *****#
T_05 = T_04 - ((c_p_air * (T_03 - T_02)) / ((1 + f_to) * c_p_exhaust))
T_05s = T_04 - (T_04 - T_05) / n_HP_turb
P_05s = P_04 * (T_05s / T_04)**(y_exhaust / (y_exhaust - 1))
P_05 = P_05s


    #***** 06 *****#
T_06 = T_05 - (((1 + B_to) * c_p_air * (T_02 - T_01)) / (c_p_exhaust * (1 + f_to)))
T_06s = T_05 - (T_05 - T_06) / n_LP_turb
P_06s = P_05 * (T_06s / T_05)**(y_exhaust / (y_exhaust - 1))
P_06 = P_06s


    #***** 7 (choked) *****#
PR_choked_core = ((y_exhaust + 1) / 2)**(y_exhaust / (y_exhaust - 1))
P_0t_core = P_06
PR_check_core = P_0t_core / P_sea
M_t = 1 #choked nozzle
T_0t_core = T_06
T_t = T_0t_core / (1 + ((y_exhaust - 1) / 2) * M_t**2)
M_7 = M_t #since convergent nozzle only
T_07 = T_0t_core
T_7 = T_t
T_7s = T_06 - (T_06 - T_7) / n_n_core
P_7s = P_06 * (T_7s / T_06)**(y_exhaust / (y_exhaust - 1))
P_7 = P_7s
u_7 = np.sqrt(2 * c_p_exhaust * (T_07 - T_7))
M_7_calced = u_7 / np.sqrt(y_exhaust * R_exhaust * T_7)


    # ***** 7 (Pe = Psea) *****#
#P_7s = P_sea
#P_7 = P_7s
#T_07 = T_0t_core
#T_7s = T_06 * (P_7s / P_06)**((y_exhaust - 1) / y_exhaust)
#T_7 = T_06 - n_n_core * (T_06 - T_7s)
#u_7 = np.sqrt(2 * c_p_air * (T_07 - T_7))
#M_7_calced = u_7 / np.sqrt(y_exhaust * R_exhaust * T_7)



    ### Calc mass flow rates ###
rho_7 = P_7 / (R_exhaust * T_7)
rho_8 = P_8 / (R_air * T_8)

m_dot_core_to = rho_7 * A_core * u_7
m_dot_bypass_to = rho_8 * A_bypass * u_8
m_dot_bypass_to_check = B_to * m_dot_core_to
#print(m_dot_bypass_to_check)

B_to_check = m_dot_bypass_to / m_dot_core_to
print(f"BP ratio check: {B_to_check}")

m_dot_total_to = m_dot_bypass_to + m_dot_core_to

u_e_bypass = u_8
u_e_core = u_7

#m_dot_core_to = T_to_engine / ((((1 + f_to) * u_e_core) - u_to) + B * (u_e_bypass - u_to))
    #assume Pressure thrust is negilgible
#m_dot_total_to = m_dot_core_to * (1 + B)
#m_dot_bypass_to = B * m_dot_core_to
m_dot_f_to = m_dot_core_to * f_to

#m_dot_total_c = m_dot_f_c_engine / f_c
#m_dot_core_c = m_dot_total_c / (1 + B)

#alternative
#m_dot_core_c_2 = (1 / (1 + f_c)) * ((P_7 * u_7 * A_e_core) / (R_exhaust * T_7))


    ### Thrust produced ###
T_core = m_dot_core_to * ((1 + f_to) * u_7 - u_to) + (P_7 - P_sea) * A_core
print(f"Core thrust: {T_core / 1000}")
T_bypass = m_dot_bypass_to * (u_8 - u_to) + (P_8 - P_sea) * A_bypass
print(f"Bypass thrust: {T_bypass / 1000}")
T_to = T_core + T_bypass
print(f"Total thrust: {T_to / 1000}")



T_e_core = T_7
P_e_core = P_7
T_e_bypass = T_8
P_e_bypass = P_8


    ### TSFC ###
TSFC_to = (m_dot_f_to / T_to) * 3600 * g



    #### Print values ####
print(" ")
print("**************** TAKE-OFF ****************")
print(f"Thrust at take-off needed (per engine): {T_to_req / 1000} kN")
print(" ")
print(f"f (take-off): {f_to}")
print(" ")

print(f"Bypass PR required for choked flow: {PR_choked_bypass}")
print(f"Bypass PR check: {PR_check_bypass}")
if PR_check_bypass > PR_choked_bypass:
    print("Flow is choked")
else:
    print("Not choked!")
print(" ")
print(f"Core PR required for choked flow: {PR_choked_core}")
print(f"Core PR check: {PR_check_core}")
if PR_check_core > PR_choked_core:
    print("Flow is choked")
else:
    print("Not choked!")

print(" ")
print(" ")
print(f"Total mass flow rate: {m_dot_total_to}")
print(f"Bypass mass flow rate: {m_dot_bypass_to}")
print(f"Core mass flow rate: {m_dot_core_to}")
print(f"Fuel mass flow rate: {m_dot_f_to}")
print(" ")
print(f"Exit velocity core: {u_e_core}, M_7: {M_7_calced}")
print(f"Exit velocity bypass: {u_e_bypass}, M_8: {M_8_calced}")
print(" ")
#print(f"Exit area core nozzle: {A_core} m2")
#print(f"Exit area bypass nozzle: {A_bypass} m2")
#print(" ")
print(f"TSFC at take-off: {TSFC_to}")
print(" ")
print(" ")

print("Pressures and Temperatures")
print(f"P_1: {P_1} Pa, P_sea: {P_sea}")
print(f"T_1: {T_1} K")
print(" ")
print(f"P_01: {P_01} Pa")
print(f"T_01: {T_01} K")
print(" ")
print(f"P_02: {P_02} Pa")
print(f"T_02: {T_02} K")
print(" ")
print(f"P_03: {P_03} Pa")
print(f"T_03: {T_03} K")
print(" ")
print(f"P_04: {P_04} Pa")
print(f"T_04: {T_04} K")
print(" ")
print(f"P_05: {P_05} Pa")
print(f"T_05: {T_05} K")
print(" ")
print(f"P_06: {P_06} Pa")
print(f"T_06: {T_06} K")
print(" ")
print(f"P_7: {P_7} Pa")
print(f"T_7: {T_7} K")
print(" ")
print(f"P_8: {P_8} Pa")
print(f"T_8: {T_8} K")
print(" ")
print(f"Temp. ratio: {T_turb_entry / T_02}")