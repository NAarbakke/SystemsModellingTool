from systems.missiles.AS_23_KODIAK.specifications.specifications import m, A, u_max, T_max
from environment.constants import rho_atm_0, g_0

print("-----AS-23 KODIAK parameter estimations-----")
print(" ")

#----------------------------------------------------

C_L_max_vel = (2 * m * g_0) / (rho_atm_0 * A * u_max**2)
C_D_max_vel = (2 * T_max)  / (rho_atm_0 * A * u_max**2)

print(f"C_L @ max velocity: {C_L_max_vel}")
print(f"C_D @ max velocity: {C_D_max_vel}")

#----------------------------------------------------

L_D_from_coeffs_max_vel = C_L_max_vel / C_D_max_vel

#print(f"L/D @ max velocity: {L_D_from_coeffs_max_vel}")



#----------IDENTICAL TO ABOVE APPROACH---------------

L_D_max_vel = (m * g_0) / T_max
print(f"L/D @ max velocity: {L_D_max_vel}")



#simulate to check range, given fuel conumption, speed, tank size and C_D found
    #have one nr for fuel mass - maybe max vel is 450 kgf @ almost empty tank, i.e 1250 kg lighter missile