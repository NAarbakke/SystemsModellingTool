from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.static_to_total import static_to_total
from systems.shared.flight_condition import FlightCondition
from subsystems.propulsion.motors.turbojets.single_spool_open_cycle_nuclear_turbojet_specs import SingleSpoolOpenCycleNuclearTurbojetSpecs
from subsystems.propulsion.motors.components.inlets.subsonic_inlet import SubsonicInlet
from subsystems.propulsion.motors.components.compressors.axial_compressor import AxialCompressor
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor import FastNeutronReactor
from subsystems.propulsion.motors.components.turbines.axial_turbine import AxialTurbine
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle import ConvergentNozzle


class SingleSpoolOpenCycleNuclearTurbojet:
    """
    Single-spool turbojet with a directly heated reactor: inlet -> axial compressor -> reactor -> turbine -> convergent
    nozzle. Stations 0-1-2-3-4-5-9 (SAE ARP755, see helpers/stations.py); m_dot is constant through the engine.
    """

    def __init__(self, gas: GasModel, specs: SingleSpoolOpenCycleNuclearTurbojetSpecs):
        self.gas = gas
        self.A_nozzle = specs.nozzle.A_exit

        #---- Components ----#
        self.inlet = SubsonicInlet(specs.subsonic_inlet, specs.subsonic_inlet_geometry, gas, name="inlet")
        self.compressor = AxialCompressor(specs.compressor, specs.compressor_geometry, gas, name="Axial compressor")
        self.reactor = FastNeutronReactor(specs.reactor, gas, name="reactor")
        self.turbine = AxialTurbine(specs.turbine, gas, compressor=self.compressor, name="turbine")   # no fan: compressor is the only load
        self.nozzle = ConvergentNozzle(specs.nozzle, gas, name="nozzle")
        #---------------------#

    def run_point(self, flight: FlightCondition):
        P_atm = flight.atmosphere.P

        # Station 0: Freestream (static -> total)
        flow_state_0 = static_to_total(flight.atmosphere, flight.M, self.gas)

        # Station 2: Inlet diffuser -> Compressor face (the compressor sets the face velocity, and so m_dot)
        flow_state_2 = self.compressor.face(self.inlet.process(flow_state_0))

        # Station 1: Inlet lip, back-filled from the m_dot the face swallows
        flow_state_1 = self.inlet.lip(flow_state_0, flow_state_2.m_dot)

        # Station 3: Compressor -> Reactor
        flow_state_3 = self.compressor.process(flow_state_2)

        # Station 4: Reactor -> Turbine (direct heating, no HX)
        flow_state_4 = self.reactor.process(flow_state_3)

        # Station 5: Turbine -> Nozzle
        flow_state_5 = self.turbine.process(flow_state_4)

        # Station 9: Nozzle -> Atmosphere
        flow_state_9 = self.nozzle.process(flow_state_5, P_atm)

        # Mass flow rate (constant through engine - no fuel addition)
        m_dot_exit = flow_state_9.m_dot
        V_exit = flow_state_9.V
        V_0 = flow_state_0.V
        P_exit = flow_state_9.P

        # Thrust
        F_thrust = m_dot_exit * (V_exit - V_0) + (P_exit - P_atm) * self.A_nozzle

        Power = F_thrust * V_0

        # Reactor thermal power
        Q_reactor = self.reactor.last_Q_reactor

        return {
            "Thrust": F_thrust,
            "Power": Power,
            "Q_reactor": Q_reactor,
            "power_density": self.reactor.last_power_density,
            "heat_flux": self.reactor.last_heat_flux,
            "within_limits": self.reactor.last_within_limits,
            "stations": {
                "0": flow_state_0,
                "1": flow_state_1,
                "2": flow_state_2,
                "3": flow_state_3,
                "4": flow_state_4,
                "5": flow_state_5,
                "9": flow_state_9}}
