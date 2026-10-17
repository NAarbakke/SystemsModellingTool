"""
Dashboard inputs per component: which spec values a page can change, with the vehicle specification as defaults,
and how the chosen values go back into the specs. Engines build their sidebar from these.
"""
from dataclasses import replace

from interface.gui.dashboard_view import Input
from subsystems.propulsion.motors.components.combustors.combustor_specs import CombustorSpecs
from subsystems.propulsion.motors.components.compressors.annulus_type import AnnulusType
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.compressors.axial_compressor_specs import AxialCompressorSpecs
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle_specs import ConvergentNozzleSpecs
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor_specs import FastNeutronReactorSpecs


#---- Axial compressor ----#
def axial_compressor_inputs(specs: AxialCompressorSpecs, geometry: AxialCompressorGeometry) -> list[Input]:
    return [
        Input("PR", "Pressure ratio", specs.PR, 1.2, 12.0, 0.1),
        Input("eta_poly", "Polytropic efficiency", specs.eta_poly, 0.80, 0.95, 0.01),
        Input("psi", "Stage loading ψ", specs.psi, 0.20, 0.50, 0.01),
        Input("U_tip", "Tip speed [m/s]", specs.U_tip, 250.0, 500.0, 10.0),
        Input("r_tip", "Inlet tip radius [m]", geometry.r_tip, 0.15, 0.60, 0.01),
        Input("hub_to_tip", "Inlet hub-to-tip ratio", geometry.hub_to_tip, 0.30, 0.80, 0.01),
        Input("annulus_type", "Annulus", geometry.annulus_type.name,
              options={a.name: a.name.replace("_", " ").capitalize() for a in AnnulusType})]


def apply_axial_compressor(specs: AxialCompressorSpecs, geometry: AxialCompressorGeometry, values: dict):
    specs = replace(specs, PR=values["PR"], eta_poly=values["eta_poly"], psi=values["psi"], U_tip=values["U_tip"])
    geometry = replace(
        geometry, r_tip=values["r_tip"], r_hub=values["hub_to_tip"] * values["r_tip"],
        annulus_type=AnnulusType[values["annulus_type"]])
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
#--------------------------------------------------------------#


#---- Convergent nozzle ----#
def convergent_nozzle_inputs(specs: ConvergentNozzleSpecs) -> list[Input]:
    return [Input("A_exit", "Exit area [m²]", specs.A_exit, 0.05, 0.60, 0.01)]


def apply_convergent_nozzle(specs: ConvergentNozzleSpecs, values: dict) -> ConvergentNozzleSpecs:
    return replace(specs, A_exit=values["A_exit"])
#---------------------------#
