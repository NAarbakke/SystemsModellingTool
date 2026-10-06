from subsystems.propulsion.motors.components.inlets.subsonic_inlet_specs import SubsonicInletSpecs
from subsystems.propulsion.motors.components.compressors.fan_specs import FanSpecs
from subsystems.propulsion.motors.components.compressors.centrifugal_compressor_specs import CentrifugalCompressorSpecs
from subsystems.propulsion.motors.components.compressors.axial_compressor_specs import AxialCompressorSpecs
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.annulus_type import AnnulusType
from subsystems.propulsion.motors.components.combustors.combustor_specs import CombustorSpecs
from subsystems.propulsion.motors.components.heat_exchangers.heat_exchanger_specs import HeatExchangerSpecs
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor_specs import FastNeutronReactorSpecs
from subsystems.propulsion.motors.components.turbines.axial_turbine_specs import AxialTurbineSpecs
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle_specs import ConvergentNozzleSpecs
from subsystems.propulsion.motors.components.ducting.duct_specs import DuctSpecs
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_liquid_fuel_turbofan_specs import SingleSpoolOpenCycleLiquidFuelTurbofanSpecifications
from subsystems.propulsion.motors.turbofans.single_spool_closed_cycle_nuclear_fuel_turbofan_specs import SingleSpoolClosedCycleNuclearTurbofanSpecifications
from subsystems.propulsion.motors.turbofans.single_spool_open_cycle_nuclear_fuel_turbofan_specs import SingleSpoolOpenCycleNuclearTurbofanSpecifications
from subsystems.propulsion.motors.turbojets.single_spool_open_cycle_nuclear_turbojet_specs import SingleSpoolOpenCycleNuclearTurbojetSpecifications


#---- Components ----#
subsonic_inlet = SubsonicInletSpecs(
    PR=0.9)

fan = FanSpecs(
    PR=1.2,
    eta_poly=0.88,
    r_tip=0.5,          # [m]
    r_hub=0.1)          # [m]

centrifugal_compressor = CentrifugalCompressorSpecs(
    PR=2.0,
    eta_poly=0.90)

axial_compressor = AxialCompressorSpecs(
    PR=2.0,
    eta_poly=0.90,
    phi=0.35,
    U_tip=350.0)        # [m/s]

axial_compressor_geometry = AxialCompressorGeometry(   # placeholder values
    annulus_type=AnnulusType.CONSTANT_TIP,  #minimises compressor length
    r_tip=0.30,                     # [m]
    r_hub=0.15,                     # [m]
    AR_rotor=2.0,
    AR_stator=2.5,
    IGV_axial_chord_length=0.04,    # [m]
    EGV_axial_chord_length=0.04)    # [m]

combustor = CombustorSpecs(
    PR_loss=0.98,
    eta=0.97,
    LHV=43e6,           # [J/kg]
    T_tet=1200.0)       # [K]

heat_exchanger = HeatExchangerSpecs(
    T_cold_out=1200.0,              # [K]  target HX cold-side outlet temperature
    hot_fluid="helium",
    T_hot_in=1500.0,                # [K]  reactor coolant inlet temperature
    P_hot=7e6,                      # [Pa] reactor coolant loop pressure
    mdot_hot=100.0,                 # [kg/s] reactor coolant mass flow rate
    wall_material="inconel_617",
    t_wall=0.001,                   # [m]
    n_channels_cold=150000,
    n_channels_hot=70000,
    D_h_cold=0.005,                 # [m]
    D_h_hot=0.005,                  # [m]
    n_segments=50)

reactor = FastNeutronReactorSpecs(
    T_tet=1200.0,                   # [K]
    PR_loss=0.97,
    fuel_material="UC",
    n_fuel_rods=2000,
    fuel_rod_length=1.0,            # [m]
    fuel_rod_diameter=0.008,        # [m]
    max_fuel_T=2500.0,              # [K]
    power_density_limit=2e9)        # [W/m^3]

turbine = AxialTurbineSpecs(
    eta_poly=0.88,
    eta_mech=0.95)

core_nozzle = ConvergentNozzleSpecs(
    eta_isen=0.98,
    A_exit=0.3,          # [m^2]
    C_discharge=0.95)

bypass_duct = DuctSpecs(
    PR_loss=0.95)

bypass_nozzle = ConvergentNozzleSpecs(
    eta_isen=0.98,
    A_exit=0.7,          # [m^2]
    C_discharge=0.98)
#--------------------#


#---- Engines ----#
specs = SingleSpoolOpenCycleLiquidFuelTurbofanSpecifications(
    bypass_ratio=2.0,
    subsonic_inlet=subsonic_inlet,
    fan=fan,
    compressor=centrifugal_compressor,
    combustor=combustor,
    turbine=turbine,
    core_nozzle=core_nozzle,
    bypass_duct=bypass_duct,
    bypass_nozzle=bypass_nozzle)

specs_closed_cycle_nuclear = SingleSpoolClosedCycleNuclearTurbofanSpecifications(
    bypass_ratio=2.0,
    subsonic_inlet=subsonic_inlet,
    fan=fan,
    compressor=centrifugal_compressor,
    combustor=combustor,
    hx=heat_exchanger,
    turbine=turbine,
    core_nozzle=core_nozzle,
    bypass_duct=bypass_duct,
    bypass_nozzle=bypass_nozzle)

specs_open_cycle_nuclear = SingleSpoolOpenCycleNuclearTurbofanSpecifications(
    bypass_ratio=2.0,
    subsonic_inlet=subsonic_inlet,
    fan=fan,
    compressor=axial_compressor,
    compressor_geometry=axial_compressor_geometry,
    reactor=reactor,
    turbine=turbine,
    core_nozzle=core_nozzle,
    bypass_duct=bypass_duct,
    bypass_nozzle=bypass_nozzle)

specs_open_cycle_nuclear_turbojet = SingleSpoolOpenCycleNuclearTurbojetSpecifications(
    subsonic_inlet=subsonic_inlet,
    compressor=axial_compressor,
    compressor_geometry=axial_compressor_geometry,
    reactor=reactor,
    turbine=turbine,
    nozzle=core_nozzle)
#-----------------#
