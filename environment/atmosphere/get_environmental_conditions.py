import numpy as np # type: ignore
#from pyatmos import expo                                                                                #explore model limitations
import ussa1976 # type: ignore

_atmosphere = ussa1976.compute()
_altitude_list = _atmosphere["z"].values              #[m]
_rho_atm_list = _atmosphere["rho"].values             #[kg/m3]
_P_atm_list = _atmosphere["p"].values                 #[Pa]
_sound_speed_list = _atmosphere["cs"].values          #[m/s]

def get_environmental_conditions(altitude):
    rho_atm = np.interp(altitude, _altitude_list, _rho_atm_list)
    P_atm = np.interp(altitude, _altitude_list, _P_atm_list)
    sound_speed = np.interp(altitude, _altitude_list, _sound_speed_list)
    g = ussa1976.core.compute_gravity(altitude)
    
    return rho_atm, P_atm, sound_speed, g



# T_atm
# heat capacity of air parameters

#alt = 10000
#rho_atm, P_atm, sound_speed, g = get_environmental_conditions(alt)
#print(f"rho atm: {rho_atm} kg/m3")
#print(f"P atm: {P_atm} Pa")
#print(f"g: {g} m/s2")



#def get_g(G, m_earth, r_earth, z_inertial):                                                             #how is the method formulated when in a class, also what symbol for z       assumed spherical earth, uniform density, small relative height         z_inertial must be altitude from eartch surface, so maybe use another name, since earth surface is not inertial
 #   g = (G * m_earth) / (r_earth + z_inertial)**2
  #  return g

#def get_P_atm(z_inertial):
    #P_atm = expo.P(z_inertial)
 #   P_atm = 0
  #  return P_atm

#def get_rho_atm(z_inertial):
    #rho_atm = expo(z_inertial)
 #   return rho_atm




#how do i use these in other scripts??