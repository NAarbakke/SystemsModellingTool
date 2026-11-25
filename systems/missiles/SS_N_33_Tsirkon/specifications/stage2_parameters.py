import numpy as np
from systems.missiles.SS_N_33_Tsirkon.specifications.propellant_parameters import rho_grain

##################################### STAGE 2 PARAMETERS (fixed) #######################################################################################

d = 0.67                                                                                                #thickest
d_throat = 0.10                                                                                         #estimated                                                                                        
d_nozzle = 0.508                                                                                        #estimated                                                                                       

r_grain_in_0 = 0.1                                                                                      #guess

#L_nozzle = 1.089                                                                                       #estimated
L_motor = 2.742                                                                                         #estimate without nozzle 

t_liner = 0.005                                                                                         #guess
t_insulation = 0.001                                                                                    #guess
t_casing = 0.02                                                                                         #guess

m_wet = 1942.8                                                                                          #or 1980

t_burn = 27                                                                                             

n_nozzle = 0.98                                                                                         #nozzle efficiency (typical ballpark value)
n_prop = 0.98                                                                                           #propellant efficiency (lumped, typical value)

######################################### CALCULATED (STAGE 2) #############################################################################################

r_grain_out = (d / 2) - t_casing

A_throat = np.pi * (d_throat / 2)**2
A_nozzle = np.pi * (d_nozzle / 2)**2
A_cross_grain = np.pi * (r_grain_out**2 - r_grain_in_0**2)                                              #for circular grain profile

L_grain = L_motor - t_casing
V_grain = L_grain * A_cross_grain
L_D_ratio = L_grain / (2 * r_grain_out)                                                                 #print metrics like these -> this one characterises if erosive burning is an effect

m_grain = rho_grain * V_grain
m_dry = m_wet - m_grain

exp_ratio = A_nozzle / A_throat

