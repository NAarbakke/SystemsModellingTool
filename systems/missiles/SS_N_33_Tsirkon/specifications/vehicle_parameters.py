import numpy as np # type: ignore
from systems.missiles.SS_N_33_Tsirkon.specifications import stage1_parameters, stage2_parameters
from systems.missiles.SS_N_33_Tsirkon.specifications.motor_burn_profile import m_dot
from systems.missiles.SS_N_33_Tsirkon.scenarios.time_setup import t, t_start, t_end, dt

###################################### FIXED ################################################################################

d = 0.67                                                                                                #thickest
L = 8.7                                                                                                 #full length

A_ref = np.pi * (d / 2)**2                                                                              #thickest section
b_ref = d                                                                                               #can use wingspan/finspan
c_ref = L                                                                                               #can use cord

t_coasting = 2.5                                                                                        #between stage 1 and 2
t_ejection_delay = 1.25                                                                                 #stage 1 ejected 1.25 sec after burnout

m_nose = 280
m_wet = 3840

###################################### COMPUTED / PROCESSED #####################################################################

m_wet = stage1_parameters.m_wet + stage2_parameters.m_wet + m_nose                                      #should equal 3840

#Build vehicle mass array incl. stage ejection logic
m = np.arange(t_start, t_end + dt, dt)
m[0] = m_wet

for i in range(len(m) - 1):
    t[i + 1] = t[i] + dt
    m[i + 1] = m[i] - m_dot[i] * dt
    if t[i + 1] == (stage1_parameters.t_burn + t_ejection_delay):
        m[i + 1] -= stage1_parameters.m_dry


#Inertias modelled as solid cylinder, for now
Jxx = 0.5 * m_wet * (d / 2)**2
Jyy = (1 / 12) * m_wet * (3 * (d / 2)**2 + L**2)
Jzz = Jyy

#Jxx = 2000   #do CAD - make expression for how it changes with time
Jxz = 500   #do CAD - make expression for how it changes with time
#Jyy = 4000   #do CAD - make expression for how it changes with time
#Jzz = 5000   #do CAD - make expression for how it changes with time
