from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.freestream_to_total import freestream_to_total
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_nuclear_fuel_turbofan_specs import SingleSpoolOpenCycleNuclearTurbofanSpecifications
from subsystems.propulsion.motors.components.inlets.subsonic_inlet import SubsonicInlet
from subsystems.propulsion.motors.components.compressors.axial_compressor import AxialCompressor
from subsystems.propulsion.motors.components.compressors.fan import Fan
from subsystems.propulsion.motors.components.splitters.splitters import CoreSplitter, BypassSplitter
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor import FastNeutronReactor
from subsystems.propulsion.motors.components.turbines.axial_turbine import AxialTurbine
from subsystems.propulsion.motors.components.ducting.ducting import Duct
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle import ConvergentNozzle


class SingleSpoolOpenCycleNuclearTurbofan:
    def __init__(self, gas: GasModel, specs: SingleSpoolOpenCycleNuclearTurbofanSpecifications, P_atm: float):
        self.gas = gas
        self.bypass_ratio = specs.bypass_ratio
        self.r_fan_tip = specs.fan.r_tip
        self.r_fan_hub = specs.fan.r_hub
        self.A_noz_core = specs.core_nozzle.A_exit
        self.A_noz_bypass = specs.bypass_nozzle.A_exit

        #---- Components ----#
        self.inlet = SubsonicInlet(specs.subsonic_inlet, gas, name="inlet")
        self.fan = Fan(specs.fan, gas, name="fan")
        self.core_splitter = CoreSplitter(specs.bypass_ratio, gas, name="core_splitter")
        self.bypass_splitter = BypassSplitter(specs.bypass_ratio, gas, name="bypass_splitter")
        self.compressor = AxialCompressor(specs.compressor, specs.compressor_geometry, gas, name="Axial compressor")
        self.reactor = FastNeutronReactor(specs.reactor, gas, name="reactor")
        self.turbine = AxialTurbine(specs.turbine, gas, self.fan, self.compressor, name="turbine")
        self.core_nozzle = ConvergentNozzle(specs.core_nozzle, P_atm, gas, name="core nozzle")
        self.bypass_duct = Duct(specs.bypass_duct, gas, name="bypass duct")
        self.bypass_nozzle = ConvergentNozzle(specs.bypass_nozzle, P_atm, gas, name="bypass nozzle")
        #---------------------#

    def run_point(self, T_0: float, P_0: float, M_0: float):

        # Station 0: Freestream (static) -> Inlet entry (total)
        flow_state_0 = freestream_to_total(T_0, P_0, M_0, self.gas)

        # Station 1: Inlet -> Fan
        flow_state_1 = self.inlet.process(flow_state_0)

        # Station 2: Fan -> Core splitter/Bypass splitter
        flow_state_2 = self.fan.process(flow_state_1)

        # Station 25a: Core splitter -> Compressor
        flow_state_25a = self.core_splitter.process(flow_state_2)

        # Station 25b: Bypass splitter -> Bypass duct
        flow_state_25b = self.bypass_splitter.process(flow_state_2)

        # Station 3: Compressor -> Reactor
        flow_state_3 = self.compressor.process(flow_state_25a)

        # Station 4: Reactor -> Turbine (direct heating, no HX)
        flow_state_4 = self.reactor.process(flow_state_3)

        # Station 5: Turbine -> Core nozzle
        flow_state_5 = self.turbine.process(flow_state_4)

        # Station 6: Core nozzle -> Atmosphere
        flow_state_6 = self.core_nozzle.process(flow_state_5)

        # Station 7: Bypass duct -> Bypass nozzle
        flow_state_7 = self.bypass_duct.process(flow_state_25b)

        # Station 8: Bypass nozzle -> Atmosphere
        flow_state_8 = self.bypass_nozzle.process(flow_state_7)

        # Mass flow rates (constant through core - no fuel addition)
        m_dot_bypass = flow_state_8.m_dot
        m_dot_core = flow_state_6.m_dot
        V_exit_core = flow_state_6.V
        V_exit_bypass = flow_state_8.V
        V_0 = flow_state_0.V
        P_exit_core = flow_state_6.P
        P_exit_bypass = flow_state_8.P

        # Thrust contributions
        F_core = m_dot_core * (V_exit_core - V_0) + (P_exit_core - P_0) * self.A_noz_core
        F_bypass = m_dot_bypass * (V_exit_bypass - V_0) + (P_exit_bypass - P_0) * self.A_noz_bypass
        F_total = F_core + F_bypass

        Power = F_total * V_0

        # Reactor thermal power
        Q_reactor = self.reactor.last_Q_reactor

        return {
            "F_total": F_total,
            "F_core": F_core,
            "F_bypass": F_bypass,
            "Power": Power,
            "Q_reactor": Q_reactor,
            "power_density": self.reactor.last_power_density,
            "heat_flux": self.reactor.last_heat_flux,
            "within_limits": self.reactor.last_within_limits,
            "stations": {
                "0": flow_state_0,
                "1": flow_state_1,
                "2": flow_state_2,
                "25a": flow_state_25a,
                "25b": flow_state_25b,
                "3": flow_state_3,
                "4": flow_state_4,
                "5": flow_state_5,
                "6": flow_state_6,
                "7": flow_state_7,
                "8": flow_state_8}}
