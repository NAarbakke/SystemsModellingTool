from propulsion.motors.helpers.gas_model import GasModel
from propulsion.motors.helpers.freestream_to_total import freestream_to_total
from system_specifications.SKYF.engine import (
    SingleSpoolClosedCycleNuclearTurbofanSpecifications,
    SingleSpoolOpenCycleNuclearTurbofanSpecifications)  #or import specs_open_cycle
from propulsion.motors.components.inlets import Inlet
from propulsion.motors.components.compressors import CentrifugalCompressor, AxialCompressor, Fan
from propulsion.motors.components.splitters import CoreSplitter, BypassSplitter
from propulsion.motors.components.heat_exchangers import HeatExchangerComponent
from propulsion.motors.components.reactors import FastNeutronReactor
from propulsion.motors.components.turbines import AxialTurbine
from propulsion.motors.components.ducting import Duct
from propulsion.motors.components.nozzles import ConvergentNozzle


class SingleSpoolClosedCycleNuclearTurbofan:
    """
    Single-spool/shaft, separate-flow nuclear turbofan built from components:
        - inlet
        - fan
        - compressor
        - heat exchanger (replaces combustor — heated by reactor coolant loop)
        - turbine (drives compressor and fan)
        - core nozzle (converging)
        - bypass duct
        - bypass nozzle (converging)

    Key difference from liquid-fuel version:
        No combustion — heat is added via a counterflow heat exchanger
        between the reactor coolant (hot side) and compressed air (cold side).
        Air mass flow is constant through the core (no fuel addition).

    Station 0:  inlet entry (atmosphere)
    Station 1:  fan entry (inlet exit)
    Station 2:  compressor (and core) entry (fan exit)
    Station 25a: core splitter exit → compressor
    Station 25b: bypass splitter exit → bypass duct
    Station 3:  heat exchanger entry (compressor exit)
    Station 4:  turbine entry (heat exchanger exit)
    Station 5:  core nozzle entry (turbine exit)
    Station 6:  core nozzle exit
    Station 7:  bypass nozzle entry (bypass duct exit)
    Station 8:  bypass nozzle exit
    """

    def __init__(self, gas: GasModel, specs: SingleSpoolClosedCycleNuclearTurbofanSpecifications, P_atm: float):
        self.gas = gas
        self.bypass_ratio = specs.bypass_ratio
        self.r_fan_tip = specs.fan.r_tip
        self.r_fan_hub = specs.fan.r_hub
        self.area_noz_core = specs.core_nozzle.area
        self.area_noz_bypass = specs.bypass_nozzle.area

        #---- Components ----#
        self.inlet = Inlet(specs.inlet, gas, name="inlet")
        self.fan = Fan(specs.fan, gas, name="fan")
        self.core_splitter = CoreSplitter(specs.bypass_ratio, gas, name="core_splitter")
        self.bypass_splitter = BypassSplitter(specs.bypass_ratio, gas, name="bypass_splitter")
        self.compressor = CentrifugalCompressor(specs.compressor, gas, name="compressor")
        self.heat_exchanger = HeatExchangerComponent(specs.hx, gas, name="heat_exchanger")
        self.turbine = AxialTurbine(specs.turbine, gas, self.fan, self.compressor, name="turbine")
        self.core_nozzle = ConvergentNozzle(specs.core_nozzle, P_atm, gas, name="core nozzle")
        self.bypass_duct = Duct(specs.bypass_duct, gas, name="bypass duct")
        self.bypass_nozzle = ConvergentNozzle(specs.bypass_nozzle, P_atm, gas, name="bypass nozzle")
        #---------------------#

    def run_point(self, T_0: float, P_0: float, M_0: float):

        # Station 0: Freestream (static) → Inlet entry (total)
        flow_state_0 = freestream_to_total(T_0, P_0, M_0, self.gas)

        # Station 1: Inlet → Fan
        flow_state_1 = self.inlet.process(flow_state_0)

        # Station 2: Fan → Core splitter/Bypass splitter
        flow_state_2 = self.fan.process(flow_state_1)

        # Station 25a: Core splitter → Compressor
        flow_state_25a = self.core_splitter.process(flow_state_2)

        # Station 25b: Bypass splitter → Bypass duct
        flow_state_25b = self.bypass_splitter.process(flow_state_2)

        # Station 3: Compressor → Heat exchanger
        flow_state_3 = self.compressor.process(flow_state_25a)

        # Station 4: Heat exchanger → Turbine
        flow_state_4 = self.heat_exchanger.process(flow_state_3)

        # Station 5: Turbine → Core nozzle
        flow_state_5 = self.turbine.process(flow_state_4)

        # Station 6: Core nozzle → Atmosphere
        flow_state_6 = self.core_nozzle.process(flow_state_5)

        # Station 7: Bypass duct → Bypass nozzle
        flow_state_7 = self.bypass_duct.process(flow_state_25b)

        # Station 8: Bypass nozzle → Atmosphere
        flow_state_8 = self.bypass_nozzle.process(flow_state_7)

        # Mass flow rates (constant through core — no fuel addition)
        m_dot_bypass = flow_state_8.m_dot
        m_dot_core = flow_state_6.m_dot
        V_exit_core = flow_state_6.V
        V_exit_bypass = flow_state_8.V
        V_0 = flow_state_0.V
        P_exit_core = flow_state_6.P
        P_exit_bypass = flow_state_8.P

        # Thrust contributions
        F_core = m_dot_core * (V_exit_core - V_0) + (P_exit_core - P_0) * self.area_noz_core
        F_bypass = m_dot_bypass * (V_exit_bypass - V_0) + (P_exit_bypass - P_0) * self.area_noz_bypass
        F_total = F_core + F_bypass

        Power = F_total * V_0

        # Reactor thermal power from HX sizing
        hx_result = self.heat_exchanger.last_hx_result
        Q_reactor = hx_result.Q

        return {
            "F_total": F_total,
            "F_core": F_core,
            "F_bypass": F_bypass,
            "Power": Power,
            "Q_reactor": Q_reactor,
            "hx_result": hx_result,
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


class SingleSpoolOpenCycleNuclearTurbofan:
    """
    Single-spool/shaft, separate-flow open-cycle nuclear turbofan built from components:
        - inlet
        - fan
        - compressor
        - fast neutron reactor (direct heating of airstream)
        - turbine (drives compressor and fan)
        - core nozzle (converging)
        - bypass duct
        - bypass nozzle (converging)

    Key difference from closed cycle:
        Air passes DIRECTLY through the reactor core - no intermediate
        coolant loop, no heat exchanger. The compressed air is itself
        the reactor coolant, heated by direct contact with the fuel rods.
        Mass flow is constant through the core (no fuel addition).

        Trade-off: thermodynamically simpler and lighter (no HX, no
        secondary loop) and avoids the cold-side / hot-side temperature
        pinch of the closed cycle, but the exhaust stream is
        radioactively contaminated.

    Station 0:  inlet entry (atmosphere)
    Station 1:  fan entry (inlet exit)
    Station 2:  compressor (and core) entry (fan exit)
    Station 25a: core splitter exit -> compressor
    Station 25b: bypass splitter exit -> bypass duct
    Station 3:  reactor entry (compressor exit)
    Station 4:  turbine entry (reactor exit)
    Station 5:  core nozzle entry (turbine exit)
    Station 6:  core nozzle exit
    Station 7:  bypass nozzle entry (bypass duct exit)
    Station 8:  bypass nozzle exit
    """

    def __init__(self, gas: GasModel, specs: SingleSpoolOpenCycleNuclearTurbofanSpecifications, P_atm: float):
        self.gas = gas
        self.bypass_ratio = specs.bypass_ratio
        self.r_fan_tip = specs.fan.r_tip
        self.r_fan_hub = specs.fan.r_hub
        self.area_noz_core = specs.core_nozzle.area
        self.area_noz_bypass = specs.bypass_nozzle.area

        #---- Components ----#
        self.inlet = Inlet(specs.inlet, gas, name="inlet")
        self.fan = Fan(specs.fan, gas, name="fan")
        self.core_splitter = CoreSplitter(specs.bypass_ratio, gas, name="core_splitter")
        self.bypass_splitter = BypassSplitter(specs.bypass_ratio, gas, name="bypass_splitter")
        self.compressor = CentrifugalCompressor(specs.compressor, gas, name="compressor")
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
        F_core = m_dot_core * (V_exit_core - V_0) + (P_exit_core - P_0) * self.area_noz_core
        F_bypass = m_dot_bypass * (V_exit_bypass - V_0) + (P_exit_bypass - P_0) * self.area_noz_bypass
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
