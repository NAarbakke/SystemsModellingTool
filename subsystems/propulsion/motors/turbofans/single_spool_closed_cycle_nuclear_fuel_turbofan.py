from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.static_to_total import static_to_total
from systems.shared.flight_condition import FlightCondition
from subsystems.propulsion.motors.turbofans.single_spool_closed_cycle_nuclear_fuel_turbofan_specs import SingleSpoolClosedCycleNuclearTurbofanSpecs
from subsystems.propulsion.motors.components.inlets.subsonic_inlet import SubsonicInlet
from subsystems.propulsion.motors.components.compressors.axial_compressor import AxialCompressor
from subsystems.propulsion.motors.components.compressors.fan import Fan
from subsystems.propulsion.motors.components.splitters.splitters import CoreSplitter, BypassSplitter
from subsystems.propulsion.motors.components.heat_exchangers.heat_exchangers import HeatExchangerComponent
from subsystems.propulsion.motors.components.turbines.axial_turbine import AxialTurbine
from subsystems.propulsion.motors.components.ducting.ducting import Duct
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle import ConvergentNozzle


class SingleSpoolClosedCycleNuclearTurbofan:
    """
    Single-spool separate-flow turbofan; a reactor coolant loop heats the core air through a heat exchanger.
    Stations 0-1-2-25-3-4-5-9 (core) and 13-17-19 (bypass), SAE ARP755: see helpers/stations.py.
    """

    def __init__(self, gas: GasModel, specs: SingleSpoolClosedCycleNuclearTurbofanSpecs):
        self.gas = gas
        self.bypass_ratio = specs.bypass_ratio
        self.r_fan_tip = specs.fan.r_tip
        self.r_fan_hub = specs.fan.r_hub
        self.A_noz_core = specs.core_nozzle.A_exit
        self.A_noz_bypass = specs.bypass_nozzle.A_exit

        #---- Components ----#
        self.inlet = SubsonicInlet(specs.subsonic_inlet, specs.subsonic_inlet_geometry, gas, name="inlet")
        self.fan = Fan(specs.fan, gas, name="fan")
        self.core_splitter = CoreSplitter(specs.bypass_ratio, gas, name="core_splitter")
        self.bypass_splitter = BypassSplitter(specs.bypass_ratio, gas, name="bypass_splitter")
        self.compressor = AxialCompressor(specs.compressor, specs.compressor_geometry, gas, name="Axial compressor")
        self.heat_exchanger = HeatExchangerComponent(specs.hx, gas, name="heat_exchanger")
        self.turbine = AxialTurbine(specs.turbine, gas, self.fan, self.compressor, name="turbine")
        self.core_nozzle = ConvergentNozzle(specs.core_nozzle, gas, name="core nozzle")
        self.bypass_duct = Duct(specs.bypass_duct, gas, name="bypass duct")
        self.bypass_nozzle = ConvergentNozzle(specs.bypass_nozzle, gas, name="bypass nozzle")
        #---------------------#

    def run_point(self, flight: FlightCondition):
        P_atm = flight.atmosphere.P

        # Station 0: Freestream (static → total)
        flow_state_0 = static_to_total(flight.atmosphere, flight.M, self.gas)

        # Station 2: Inlet diffuser → Fan face (the fan sets the face Mach, and so m_dot)
        flow_state_2 = self.fan.face(self.inlet.process(flow_state_0))

        # Station 1: Inlet lip, back-filled from the m_dot the fan swallows
        flow_state_1 = self.inlet.lip(flow_state_0, flow_state_2.m_dot)

        # Fan → Core splitter/Bypass splitter (the fan exit totals are shared by stations 25 and 13)
        fan_exit = self.fan.process(flow_state_2)

        # Station 25: Core splitter → Compressor face (core m_dot from the split; face Mach from continuity)
        flow_state_25 = self.compressor.face(self.core_splitter.process(fan_exit))

        # Station 13: Bypass splitter → Bypass duct
        flow_state_13 = self.bypass_splitter.process(fan_exit)

        # Station 3: Compressor → Heat exchanger
        flow_state_3 = self.compressor.process(flow_state_25)

        # Station 4: Heat exchanger → Turbine
        flow_state_4 = self.heat_exchanger.process(flow_state_3)

        # Station 5: Turbine → Core nozzle
        flow_state_5 = self.turbine.process(flow_state_4)

        # Station 9: Core nozzle → Atmosphere
        flow_state_9 = self.core_nozzle.process(flow_state_5, P_atm)

        # Station 17: Bypass duct → Bypass nozzle
        flow_state_17 = self.bypass_duct.process(flow_state_13)

        # Station 19: Bypass nozzle → Atmosphere
        flow_state_19 = self.bypass_nozzle.process(flow_state_17, P_atm)

        # Mass flow rates (constant through core — no fuel addition)
        m_dot_bypass = flow_state_19.m_dot
        m_dot_core = flow_state_9.m_dot
        V_exit_core = flow_state_9.V
        V_exit_bypass = flow_state_19.V
        V_0 = flow_state_0.V
        P_exit_core = flow_state_9.P
        P_exit_bypass = flow_state_19.P

        # Thrust contributions
        F_core = m_dot_core * (V_exit_core - V_0) + (P_exit_core - P_atm) * self.A_noz_core
        F_bypass = m_dot_bypass * (V_exit_bypass - V_0) + (P_exit_bypass - P_atm) * self.A_noz_bypass
        F_thrust = F_core + F_bypass

        Power = F_thrust * V_0

        # Reactor thermal power from HX sizing
        hx_result = self.heat_exchanger.last_hx_result
        Q_reactor = hx_result.Q

        return {
            "Thrust": F_thrust,
            "F_core": F_core,
            "F_bypass": F_bypass,
            "Power": Power,
            "Q_reactor": Q_reactor,
            "hx_result": hx_result,
            "stations": {
                "0": flow_state_0,
                "1": flow_state_1,
                "2": flow_state_2,
                "25": flow_state_25,
                "3": flow_state_3,
                "4": flow_state_4,
                "5": flow_state_5,
                "9": flow_state_9,
                "13": flow_state_13,
                "17": flow_state_17,
                "19": flow_state_19}}

