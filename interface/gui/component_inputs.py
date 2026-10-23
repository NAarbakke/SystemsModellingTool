"""
Dashboard inputs per component: which spec values a page can change, with the vehicle specification as defaults,
and how the chosen values go back into the specs. Engines build their sidebar from these.
"""
from dataclasses import replace

from interface.gui.dashboard_view import Input
from subsystems.propulsion.coolants.possible_coolants import FLUIDS
from subsystems.propulsion.motors.components.combustors.combustor_specs import CombustorSpecs
from subsystems.propulsion.motors.components.compressors.annulus_type import AnnulusType
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_specs import AxialCompressorSpecs
from subsystems.propulsion.motors.components.compressors.centrifugal_compressor_specs import CentrifugalCompressorSpecs
from subsystems.propulsion.motors.components.compressors.fan_specs import FanSpecs
from subsystems.propulsion.motors.components.heat_exchangers.heat_exchanger_specs import HeatExchangerSpecs
from subsystems.propulsion.motors.components.inlets.subsonic_inlet_geometry import SubsonicInletGeometry
from subsystems.propulsion.motors.components.inlets.subsonic_inlet_specs import SubsonicInletSpecs
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle_specs import ConvergentNozzleSpecs
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor_specs import FastNeutronReactorSpecs


#---- Subsonic inlet ----#
def inlet_inputs(specs: SubsonicInletSpecs, geometry: SubsonicInletGeometry) -> list[Input]:
    return [
        Input("PR_inlet", "Pressure recovery", specs.PR, 0.90, 1.00, 0.005),
        Input("r_lip", "Lip radius [m]", geometry.r_lip, 0.10, 1.00, 0.01)]


def apply_inlet(specs: SubsonicInletSpecs, geometry: SubsonicInletGeometry, values: dict):
    specs = replace(specs, PR=values["PR_inlet"])
    geometry = replace(geometry, r_lip=values["r_lip"])
    return specs, geometry
#------------------------#


#---- Fan (and the bypass ratio its exit splits at) ----#
def fan_inputs(specs: FanSpecs, bypass_ratio: float) -> list[Input]:
    return [
        Input("PR_fan", "Fan pressure ratio", specs.PR, 1.05, 2.0, 0.01),
        Input("eta_fan", "Fan polytropic efficiency", specs.eta_poly, 0.80, 0.95, 0.01),
        Input("bypass_ratio", "Bypass ratio", bypass_ratio, 0.2, 8.0, 0.1)]


def apply_fan(specs: FanSpecs, values: dict) -> FanSpecs:
    return replace(specs, PR=values["PR_fan"], eta_poly=values["eta_fan"])
#--------------------------------------------------------#


#---- Centrifugal compressor ----#
def centrifugal_compressor_inputs(specs: CentrifugalCompressorSpecs) -> list[Input]:
    return [
        Input("PR", "Pressure ratio", specs.PR, 1.2, 8.0, 0.1),
        Input("eta_poly", "Polytropic efficiency", specs.eta_poly, 0.75, 0.92, 0.01)]


def apply_centrifugal_compressor(specs: CentrifugalCompressorSpecs, values: dict) -> CentrifugalCompressorSpecs:
    return replace(specs, PR=values["PR"], eta_poly=values["eta_poly"])
#--------------------------------#


#---- Axial compressor ----#
def axial_compressor_inputs(specs: AxialCompressorSpecs, geometry: AxialCompressorGeometry) -> list[Input]:
    return [
        Input("PR", "Pressure ratio", specs.PR, 1.2, 12.0, 0.1),
        Input("eta_poly", "Polytropic efficiency", specs.eta_poly, 0.80, 0.95, 0.01),
        Input("psi", "Stage loading ψ", specs.psi, 0.20, 0.50, 0.01),
        Input("U_tip", "Tip speed [m/s]", specs.U_tip, 250.0, 500.0, 10.0),
        Input("annulus_type", "Annulus", geometry.annulus_type.name,
              options={a.name: a.name.replace("_", " ").capitalize() for a in AnnulusType})]


def apply_axial_compressor(specs: AxialCompressorSpecs, geometry: AxialCompressorGeometry, values: dict):
    specs = replace(specs, PR=values["PR"], eta_poly=values["eta_poly"], psi=values["psi"], U_tip=values["U_tip"])
    geometry = replace(geometry, annulus_type=AnnulusType[values["annulus_type"]])
    return specs, geometry
#--------------------------#


#---- Heat sources: both set the turbine entry temperature ----#
def reactor_inputs(specs: FastNeutronReactorSpecs) -> list[Input]:
    return [Input("T_tet", "Turbine entry temperature [K]", specs.T_tet, 800.0, 1800.0, 10.0)]


def apply_reactor(specs: FastNeutronReactorSpecs, values: dict) -> FastNeutronReactorSpecs:
    return replace(specs, T_tet=values["T_tet"])


def combustor_inputs(specs: CombustorSpecs) -> list[Input]:
    return [
        Input("T_tet", "Turbine entry temperature [K]", specs.T_tet, 800.0, 1800.0, 10.0),
        Input("eta_comb", "Combustion efficiency", specs.eta, 0.90, 1.00, 0.01)]


def apply_combustor(specs: CombustorSpecs, values: dict) -> CombustorSpecs:
    return replace(specs, T_tet=values["T_tet"], eta=values["eta_comb"])


def heat_exchanger_inputs(specs: HeatExchangerSpecs) -> list[Input]:
    return [
        Input("T_tet", "Turbine entry temperature [K]", specs.T_cold_out, 800.0, 1400.0, 10.0),
        Input("T_hot_in", "Coolant inlet temperature [K]", specs.T_hot_in, 1000.0, 1800.0, 10.0),
        Input("hot_fluid", "Reactor coolant", specs.hot_fluid,
              options={name: name.capitalize() for name in FLUIDS if name != "air"})]


def apply_heat_exchanger(specs: HeatExchangerSpecs, values: dict) -> HeatExchangerSpecs:
    return replace(specs, T_cold_out=values["T_tet"], T_hot_in=values["T_hot_in"], hot_fluid=values["hot_fluid"])
#--------------------------------------------------------------#


#---- Convergent nozzle: key tells a turbofan's two nozzles apart ----#
def convergent_nozzle_inputs(specs: ConvergentNozzleSpecs, key: str = "A_exit", hi: float = 0.60) -> list[Input]:
    return [Input(key, "Exit area [m²]", specs.A_exit, 0.05, hi, 0.01)]


def apply_convergent_nozzle(specs: ConvergentNozzleSpecs, values: dict, key: str = "A_exit") -> ConvergentNozzleSpecs:
    return replace(specs, A_exit=values[key])
#---------------------------------------------------------------------#
