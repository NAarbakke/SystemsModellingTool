import numpy as np 

##################################### ENVIRONMENT (fixed) ################################################################################################# put in environment

R = 8.314462618                                                                                         #universal gas constant [J/mol K]
G = 6.67430e-11

m_earth = 5.972e24
r_earth = 6.371e6                                                                                       #assuming spherical
r_earth_spherical = 6.366707e6                                                                          
r_earth_avg = 6.368e6                                                                                   #mean earth radius, check

g_0 = 9.80665
rho_atm_0 = 1.225
P_atm_0 = 101325                                                                                        #[Pa] = 1 atm = 1.01325 bar

rad2deg = 180 / np.pi


