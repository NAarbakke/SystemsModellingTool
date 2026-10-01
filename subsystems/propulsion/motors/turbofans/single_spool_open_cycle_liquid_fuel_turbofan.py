from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.freestream_to_total import freestream_to_total
from specifications.SKYF.engine import EngineSpecifications
from subsystems.propulsion.motors.components.inlets.inlets import Inlet
from subsystems.propulsion.motors.components.compressors.axial_compressor import AxialCompressor
from subsystems.propulsion.motors.components.compressors.centrifugal_compressor import CentrifugalCompressor
from subsystems.propulsion.motors.components.compressors.fan import Fan
from subsystems.propulsion.motors.components.splitters.splitters import CoreSplitter, BypassSplitter
from subsystems.propulsion.motors.components.combustors.combustor import Combustor
from subsystems.propulsion.motors.components.turbines.turbines import AxialTurbine
from subsystems.propulsion.motors.components.ducting.ducting import Duct
from subsystems.propulsion.motors.components.nozzles.nozzles import ConvergentNozzle


class SingleSpoolOpenCycleLiquidFuelTurbofan:
    """
    Single-spool/shaft, separate-flow turbofan built from components:
        - inlet
        - fan
        - compressor
        - combustor
        - turbine (drives compressor and fan)
        - core nozzle (converging)
        - bypass duct
        - bypass nozzle (converging)

    Design parameters:
      - bypass_ratio
      - fan, compressor, burner, duct PRs and efficiencies
      - Fuel LHV and turbine entry temperature
      - fan and nozzle geometric parameters

    Station 0: inlet entry (atmosphere)
    Station 1: fan entry (inlet exit)
    Station 2: compressor (and core) entry (fan exit)
    Station 3: combustor entry (compressor exit)
    Station 4: turbine entry (combustor exit)
    Station 5: core nozzle entry (turbine exit)
    Station 6: core nozzle exit (throat (and ambient if ideally expanded))
    Station 7: bypass duct entry (same as core entry but different mass flow rate)
    Station 8: bypass nozzle entry (bypass duct exit)
    Station 9: bypass nozzle exit (throat (and ambient if ideally expanded))
    """

    def __init__(self, gas: GasModel, specs: EngineSpecifications, P_atm: float):
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
        self.combustor = Combustor(specs.combustor, gas, name="combustor")
        self.turbine = AxialTurbine(specs.turbine, gas, self.fan, self.compressor, name="turbine")
        self.core_nozzle = ConvergentNozzle(specs.core_nozzle, P_atm, gas, name="core nozzle")
        self.bypass_duct = Duct(specs.bypass_duct, gas, name="bypass duct")
        self.bypass_nozzle = ConvergentNozzle(specs.bypass_nozzle, P_atm, gas, name="bypass nozzle")
        #---------------------#

    def run_point(self, T_0: float, P_0: float, M_0: float):

        # Station 0: Freestream (static) → Inlet entry (total)
        flow_state_0 = freestream_to_total(T_0, P_0, M_0, self.gas)

        # Staion 1: Inlet → Fan
        flow_state_1 = self.inlet.process(flow_state_0)

        # Staion 2: Fan → Core splitter/Bypass splitter
        flow_state_2 = self.fan.process(flow_state_1)

        # Station 25a: Core splitter → Compressor
        flow_state_25a = self.core_splitter.process(flow_state_2)

        # Station 25b: Bypass splitter → Bypass duct
        flow_state_25b = self.bypass_splitter.process(flow_state_2)

        # Staion 3: Compressor → Combustor
        flow_state_3 = self.compressor.process(flow_state_25a)

        # Staion 4: Combustor → Turbine
        flow_state_4 = self.combustor.process(flow_state_3)

        # Staion 5: Turbine → Core nozzle
        flow_state_5 = self.turbine.process(flow_state_4)

        # Staion 6: Core nozzle → Atmosphere
        flow_state_6 = self.core_nozzle.process(flow_state_5)

        # Staion 7: Bypass duct → Bypass nozzle
        flow_state_7 = self.bypass_duct.process(flow_state_25b)

        # Staion 8: Bypass nozzle → Atmosphere
        flow_state_8 = self.bypass_nozzle.process(flow_state_7)

        # Mass flow rates
        #beta = self.bypass_ratio
        #A_fan = np.pi * (self.r_fan_tip**2 - self.r_fan_hub**2)
        #A_fan = np.pi * self.r_fan_tip**2 * (1 - self.epsilon)
        #m_dot_total = flow_state_1.rho * A_fan * flow_state_1.V
        #m_dot_total = flow_state_1.m_dot
        #m_dot_bypass = beta * m_dot_total / (1 + beta)
        m_dot_bypass = flow_state_8.m_dot
        #m_dot_core = m_dot_bypass / beta
        m_dot_core = flow_state_6.m_dot
        V_exit_core = flow_state_6.V
        V_exit_bypass = flow_state_8.V
        V_0 = flow_state_0.V
        P_exit_core = flow_state_6.P
        P_exit_bypass = flow_state_8.P

        #lambda = (1 + np.cos(nozzle_half_angle) / 2)
        # add in front of momentum thrust part of thrust eqs.
        # for deLaval, lambda approaches 1, maybe 0.99

        # Thrust contributions
        F_core = m_dot_core * (V_exit_core - V_0) + (P_exit_core - P_0) * self.area_noz_core
        F_bypass = m_dot_bypass * (V_exit_bypass - V_0) + (P_exit_bypass - P_0) * self.area_noz_bypass
        F_total = F_core + F_bypass

        Power = F_total * V_0   #compare to turbine power? should they be equal?

        m_dot_fuel = self.combustor.last_fuel_flow
        TSFC = m_dot_fuel / F_total

        return {
            "F_total": F_total,
            "F_core": F_core,
            "F_bypass": F_bypass,
            "Power": Power,
            "TSFC": TSFC,
            "m_dot_fuel": m_dot_fuel,
            "stations": {
                "0": flow_state_0,
                "1": flow_state_1,
                "2": flow_state_2,
                "3": flow_state_3,
                "4": flow_state_4,
                "5": flow_state_5,
                "6": flow_state_6,
                "7": flow_state_7,
                "8": flow_state_8}}
