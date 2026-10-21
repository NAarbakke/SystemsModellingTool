from environment.atmosphere.international_standard_atmosphere import InternationalStandardAtmosphere
from specifications.SKYF.flight_state.cruise import h_cruise


#---- Atmosphere ----#
isa = InternationalStandardAtmosphere()

cruise = isa.conditions(h_cruise)
#--------------------#
