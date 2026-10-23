from environment.atmosphere.international_standard_atmosphere import InternationalStandardAtmosphere
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from systems.shared.flight_condition import FlightCondition


#---- Cruise ----#
h_cruise = 100.0        # [m]   geopotential altitude
V_cruise = 260.0        # [m/s] true airspeed

cruise = FlightCondition.from_altitude(h=h_cruise, V=V_cruise, isa=InternationalStandardAtmosphere(), gas=GasModel())
#----------------#
