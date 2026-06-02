    ### Imports ###
import numpy as np
from parameters import M_c, y_air, y_exhaust, R_air, R_exhaust, T_atm, P_atm, c_p_exhaust, c_p_air, m_c, g, L_D_c, TSFC_brief, Q_R, A_core


    ### Cruise thrust (T = D and L = W) ###
W_c = m_c * g
L_c = W_c
D_c = L_c / L_D_c

T_c_total = D_c
T_c_engine = T_c_total# / 2 #or size for one engine operation


    ### Initial calcs at cruise ###
u_c = M_c * np.sqrt(y_air * R_air * T_atm)
print(u_c)





########### T-s calcs ###########

    ### Cycle parameters at cruise (chosen) ###
n_diff = 0.90 #diffuser efficiency
n_fan = 0.90 #fan (LP compressor) efficiency
n_comp = 0.90 #HP compressor efficiency
n_HP_turb = 0.93
n_LP_turb = 0.93
n_n_core = 0.97
n_n_bypass = 0.97
FPR = 1.8 #fan pressure ratio
CPR = 35 #HP compressor pressure ratio at cruise
r_c = 0.98 #combustion pressure ratio
B_c = 15 #bypass ratio
T_turb_entry = 2100 #K (by material properties)
    #higher at take-off surely, but do not want to be close to material max at cruise
    #extrapolate from graph in notes to justify



    #***** 1 *****#
T_1 = T_atm
P_1 = P_atm


    #***** 01 *****#
T_01 = T_1 * (1 + ((y_air - 1) / 2) * M_c**2)
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
P_0t_bypass = P_02
PR_check_bypass = P_0t_bypass / P_atm
M_8 = 1 #choked
T_08 = T_02
T_8 = T_08 / (1 + ((y_air - 1) / 2) * M_8**2)
T_8s = T_02 - (T_02 - T_8) / n_n_bypass
P_8s = P_02 * (T_8s / T_02)**(y_air / (y_air - 1))
P_8 = P_8s
u_8 = np.sqrt(2 * c_p_air * (T_08 - T_8))
M_8_calced = u_8 / np.sqrt(y_air * R_air * T_8)


    #***** 8 (P_exit = P_atm) *****#
#P_8s = P_atm
#P_8 = P_8s
#T_08 = T_02
#T_8s = T_02 * (P_8s / P_02)**((y_air - 1) / y_air)
#T_8 = T_02 - n_n_bypass * (T_02 - T_8s)
#u_8 = np.sqrt(2 * c_p_air * (T_08 - T_8))
#M_8_calced = u_8 / np.sqrt(y_air * R_air * T_8)



    #***** 03 *****#
P_03s = CPR * P_02
P_03 = P_03s
T_03s = T_02 * CPR**((y_air - 1) / y_air)
T_03 = T_02 + ((T_03s - T_02) / n_comp)


    #***** 04 *****#
T_04 = T_turb_entry
f_c = (c_p_exhaust * T_04 - c_p_air * T_03) / (Q_R - c_p_exhaust * T_04)
T_04s = T_04
P_04 = r_c * P_03
P_04s = P_03


    ### w_turb = w_comp + w_fan
#T_05 = T_04 - ((c_p_air * (T_03 - T_02) + (1 + B_c) * c_p_air * (T_02 - T_01)) / ((1 + f_c) * c_p_exhaust))


    #***** 05 *****#
T_05 = T_04 - ((c_p_air * (T_03 - T_02)) / ((1 + f_c) * c_p_exhaust))
T_05s = T_04 - (T_04 - T_05) / n_HP_turb
P_05s = P_04 * (T_05s / T_04)**(y_exhaust / (y_exhaust - 1))
P_05 = P_05s


    #***** 06 *****#
T_06 = T_05 - (((1 + B_c) * c_p_air * (T_02 - T_01)) / (c_p_exhaust * (1 + f_c)))
T_06s = T_05 - (T_05 - T_06) / n_LP_turb
P_06s = P_05 * (T_06s / T_05)**(y_exhaust / (y_exhaust - 1))
P_06 = P_06s

#T_06 = T_05
#P_06 = P_05


    #***** 7 (choked) *****#
PR_choked_core = ((y_exhaust + 1) / 2)**(y_exhaust / (y_exhaust - 1))
P_0t_core = P_06
PR_check_core = P_0t_core / P_atm
M_t = 1 #choked nozzle
T_0t = T_06
T_t = T_0t / (1 + ((y_exhaust - 1) / 2) * M_t**2)
M_7 = M_t #since convergent nozzle only
T_07 = T_0t
T_7 = T_t
T_7s = T_06 - (T_06 - T_7) / n_n_core
P_7s = P_06 * (T_7s / T_06)**(y_exhaust / (y_exhaust - 1))
P_7 = P_7s
u_7 = np.sqrt(2 * c_p_exhaust * (T_07 - T_7))
M_7_calced = u_7 / np.sqrt(y_exhaust * R_exhaust * T_7)

    #***** 7 (P_exit = P_atm) *****#
#P_7s = P_atm
#P_7 = P_7s
#T_07 = T_0t
#T_7s = T_06 * (P_7s / P_06)**((y_exhaust - 1) / y_exhaust)
#T_7 = T_06 - n_n_core * (T_06 - T_7s)
#u_7 = np.sqrt(2 * c_p_air * (T_07 - T_7))
#M_7_calced = u_7 / np.sqrt(y_exhaust * R_exhaust * T_7)




    ### Calc mass flow rates ###
rho_7 = P_7 / (R_exhaust * T_7)
rho_8 = P_8 / (R_air * T_8)

A_bypass = (B_c * rho_7 * A_core * u_7) / (rho_8 * u_8)


m_dot_core_c = rho_7 * A_core * u_7
m_dot_bypass_c = rho_8 * A_bypass * u_8
m_dot_total_c = m_dot_bypass_c + m_dot_core_c
m_dot_f_c = m_dot_core_c * f_c


    ### Calc radii ###
r_inner = 0 #m2
r_outer = np.sqrt((A_core / np.pi) + r_inner**2)
r_outer_bypass = np.sqrt((A_bypass / np.pi) + r_outer**2)



#alternative
#m_dot_core_c_2 = (1 / (1 + f_c)) * ((P_7 * u_7 * A_e_core) / (R_exhaust * T_7))




    ### Thrust produced ###
T_core = m_dot_core_c * ((1 + f_c) * u_7 - u_c) + (P_7 - P_atm) * A_core
print(f"Core thrust: {T_core / 1000}")
T_bypass = m_dot_bypass_c * (u_8 - u_c) + (P_8 - P_atm) * A_bypass
print(f"Bypass thrust: {T_bypass / 1000}")
T_c = T_core + T_bypass
print(f"Total thrust: {T_c / 1000}")

print(f"Checking bypass: {m_dot_bypass_c / m_dot_core_c}")



    ### Evaluate TSFC at cruise ###
TSFC_c = (m_dot_f_c / T_c) * 3600 * g


#u_e_bypass = u_8
#u_e_core = u_7
#T_e_core = T_7
#P_e_core = P_7
#T_e_bypass = T_8
#P_e_bypass = P_8



    #### Print values ####
print(" ")
print("**************** CRUISE ****************")
print(f"Thrust at cruise nedded (per engine): {T_c_engine / 1000} kN")
print(" ")
print(f"f (cruise): {f_c}")
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
print(f"Total mass flow rate: {m_dot_total_c}")
print(f"Bypass mass flow rate: {m_dot_bypass_c}")
print(f"Core mass flow rate: {m_dot_core_c}")
print(f"Fuel mass flow rate: {m_dot_f_c}")
print(" ")
print(f"TSFC (from brief): {TSFC_brief}")
print(f"TSFC (from calculated values): {TSFC_c}")
print(" ")
print(f"Exit velocity core: {u_7}, M_7: {M_7_calced}")
print(f"Exit velocity bypass: {u_8}, M_8: {M_8_calced}")
print(" ")
print(f"Area bypass: {A_bypass}")
print(f"Area core: {A_core}")
print(" ")
print(f"Core inner radius: {r_inner} m2")
print(f"Core outer radius / bypass inner radius: {r_outer} m2")
print(f"Bypass outer radius: {r_outer_bypass} m2")
print(" ")
print(" ")
print(" ")
print("Pressures and Temperatures")
print(f"P_1: {P_1} Pa, P_atm: {P_atm}")
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


