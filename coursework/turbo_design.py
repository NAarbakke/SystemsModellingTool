import numpy as np
from parameters import y_exhaust, c_p_exhaust, R_exhaust, g
from cruise import T_04, T_05, P_05, P_04, m_dot_core_c

print(" ")
print(" ")
print(" ")
print(" ")
print("************ Turbo design **************")


    ### HP Turbine calcs ###
r_tip = 0.5 #m
#r_hub =  #???
#r_m = (r_tip - r_hub) / 2
RPM = 13000
omega = RPM * ((2 * np.pi) / 60) #rad/s



rho_4 = P_04 / (R_exhaust * T_04)
rho_5 = P_05 / (R_exhaust * T_05) #or T_5 using V_x?? no i dont think so
w_HP_turb = c_p_exhaust * (T_04 - T_05)




Ø = 0.5 #choose - Ø = V_x / U
U = omega * r_tip
psy = w_HP_turb / U**2
R = (2 - psy) / 2 # a_0 = 0
V_x = Ø * U





r_hub_5 = np.sqrt(r_tip**2 - (m_dot_core_c / (rho_5 * np.pi * V_x)))
b = r_tip - r_hub_5

r_hub_4 = np.sqrt(r_tip**2 - (m_dot_core_c / (rho_4 * np.pi * V_x)))


#check massflow in?
m_dot_check_out = rho_5 * np.pi * (r_tip**2 - r_hub_5**2) * V_x #will V_x be the same going out as in? surely not

#what turbine architecture is used by meangen and stagen
#why is mass flow produced by program so much lower than my input massflow



print(" ")
print(f"P_04: {P_04 / 10**5} bar")
print(f"T_04: {T_04} K")
print(" ")
print(f"P_05: {P_05 / 10**5} bar")
print(f"T_05: {T_05} K")
print(" ")
print(f"Turbine work: {w_HP_turb / 1000} kJ/kg")
print(f"Core mass flow rate: {m_dot_core_c} kg/s")
print(f"Check mass flow rate out: {m_dot_check_out} kg/s")
print(" ")
print(f"U: {U} m/s")
print(f"Flow coefficient (Ø): {Ø}")
print(f"Stage loading coefficient (psy): {psy}")
print(f"Reaction (R): {R}")
print(f"Axial velocity (V_x): {V_x} m/s")
print(" ")
print(f"r_tip: {r_tip} m")
print(f"r_hub_5: {r_hub_5} m")
print(f"b: {b * 100} cm")
print(f"r_hub_4: {r_hub_4} m")

#n_HP_t_calc =

#R = 1 - stage_loading?






GE90_85B = 15.4 * 3600 * g * 10**(-6)
Trent_XWB = 13.5 * 3600 * g * 10**(-6)
Trent_7000 = 14.3 * 3600 * g * 10**(-6)

#print(Trent_7000)
#print(Trent_XWB)
#print(GE90_85B)
