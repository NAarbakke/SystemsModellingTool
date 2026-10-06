from dataclasses import replace

from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.freestream_to_total import freestream_to_total
from subsystems.propulsion.motors.turbojets.single_spool_open_cycle_nuclear_turbojet_specs import SingleSpoolOpenCycleNuclearTurbojetSpecifications
from subsystems.propulsion.motors.components.inlets.subsonic_inlet import SubsonicInlet
from subsystems.propulsion.motors.components.compressors.axial_compressor import AxialCompressor
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor import FastNeutronReactor
from subsystems.propulsion.motors.components.turbines.axial_turbine import AxialTurbine
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle import ConvergentNozzle


class SingleSpoolOpenCycleNuclearTurbojet:
    def __init__(self, gas: GasModel, specs: SingleSpoolOpenCycleNuclearTurbojetSpecifications, P_atm: float):
        self.gas = gas
        self.A_noz = specs.nozzle.A_exit

        #---- Components ----#
        self.inlet = SubsonicInlet(specs.subsonic_inlet, gas, name="inlet")
        self.compressor = AxialCompressor(specs.compressor, specs.compressor_geometry, gas, name="Axial compressor")
        self.reactor = FastNeutronReactor(specs.reactor, gas, name="reactor")
        self.turbine = AxialTurbine(specs.turbine, gas, compressor=self.compressor, name="turbine")   # no fan: compressor is the only load
        self.nozzle = ConvergentNozzle(specs.nozzle, P_atm, gas, name="nozzle")
        #---------------------#

    def run_point(self, T_0: float, P_0: float, M_0: float):

        # Station 0: Freestream (static) -> Inlet entry (total)
        flow_state_0 = freestream_to_total(T_0, P_0, M_0, self.gas)

        # Station 1: Inlet -> Compressor
        flow_state_1 = self.inlet.process(flow_state_0)

        # Mass flow set by the compressor face (no fan upstream to set it)
        m_dot = flow_state_1.rho * self.compressor.A_inlet * flow_state_1.V
        flow_state_1 = replace(flow_state_1, m_dot=m_dot)

        # Station 3: Compressor -> Reactor
        flow_state_3 = self.compressor.process(flow_state_1)

        # Station 4: Reactor -> Turbine (direct heating, no HX)
        flow_state_4 = self.reactor.process(flow_state_3)

        # Station 5: Turbine -> Nozzle
        flow_state_5 = self.turbine.process(flow_state_4)

        # Station 6: Nozzle -> Atmosphere
        flow_state_6 = self.nozzle.process(flow_state_5)

        # Mass flow rate (constant through engine - no fuel addition)
        m_dot_exit = flow_state_6.m_dot
        V_exit = flow_state_6.V
        V_0 = flow_state_0.V
        P_exit = flow_state_6.P

        # Thrust
        F_total = m_dot_exit * (V_exit - V_0) + (P_exit - P_0) * self.A_noz

        Power = F_total * V_0

        # Reactor thermal power
        Q_reactor = self.reactor.last_Q_reactor

        return {
            "F_total": F_total,
            "Power": Power,
            "Q_reactor": Q_reactor,
            "power_density": self.reactor.last_power_density,
            "heat_flux": self.reactor.last_heat_flux,
            "within_limits": self.reactor.last_within_limits,
            "stations": {
                "0": flow_state_0,
                "1": flow_state_1,
                "3": flow_state_3,
                "4": flow_state_4,
                "5": flow_state_5,
                "6": flow_state_6}}
