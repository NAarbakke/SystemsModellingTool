from dataclasses import dataclass
from subsystems.propulsion.motors.components.inlets.subsonic_inlet_specs import SubsonicInletSpecs
from subsystems.propulsion.motors.components.compressors.axial_compressor_specs import AxialCompressorSpecs
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor_specs import FastNeutronReactorSpecs
from subsystems.propulsion.motors.components.turbines.axial_turbine_specs import AxialTurbineSpecs
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle_specs import ConvergentNozzleSpecs


@dataclass
class SingleSpoolOpenCycleNuclearTurbojetSpecifications:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    subsonic_inlet: SubsonicInletSpecs
    compressor: AxialCompressorSpecs
    compressor_geometry: AxialCompressorGeometry
    reactor: FastNeutronReactorSpecs
    turbine: AxialTurbineSpecs
    nozzle: ConvergentNozzleSpecs
