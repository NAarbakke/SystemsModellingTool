import numpy as np # type: ignore
from tools.calculations.conversion_factors import kmh2ms
from systems.propulsion.turbofans.TRDD_50A import T_max_kgf

m = 2200                                                        # 2200 - 2400 kg
D = 0.51                                                        # somewhat uncertain
A = np.pi * (D / 2)**2                                          # ish
L = 7.45
wingspan = 4.05
                                            
T_max = T_max_kgf * 9.81                                        

u_max_kmh = 970
u_max_mach = 0.79                                               # @ sea level

u_max = u_max_kmh * kmh2ms                                      # [m/s]