
    ### Constants (fixed) ###
g = 9.81
rho_sea = 1.225
P_sea = 1.01325 * 10**5
T_sea = 288.15
c_p_air = 1.005 * 1000
c_p_exhaust = 1.10 * 1000
y_air = 1.40
y_exhaust = 1.33
R_air = 287 #J/kg/K
R_exhaust = c_p_exhaust * (1 - (1 / y_exhaust))
#R_exhaust = 287


    ### Constants (given) ###
TSFC_brief = 0.50 #kg/h/kg (at static, sea-level conditions?)
L_D_c = 21.6 #cruise assumed
M_c = 0.78 #local assumed
R1 = 3000 #nm
R1 = R1 * 1852 #m
S = 304 #m2
m_pl = 40200 #kg (max) paylaod
m_to = 176000 #kg (max) take-off
m_e = 100000 #empty
m_f_R1 = 27800 #kg
m_f_R1_per_dist = m_f_R1 / R1 #kg/m in cruise assumed
m_f = m_to - m_pl - m_e #fuel mass
m_c = m_to - 0.10 * m_f #assuming 10% fuel spent in climb


    ### Constants (chosen) ###
T_atm = 220.0 #K (10500m alt)
#T_atm = 216.65
rho_atm = 0.3172 * rho_sea
P_atm = 0.2454 * 10**5 #Pa
#P_atm = 18800

C_L_to = 1.5
L_D_to = 9
C_D_to = C_L_to / L_D_to #assuming LD ratio maintained (probably not valid!!) include C_D, C_L graphs
C_D = 0.2 #??
mu_r = 0.02
d_to = 3000 #min. take-off distance (m)

Q_R = 44000 * 1000 #J/kg

#A_bypass = 2
A_core = 0.55