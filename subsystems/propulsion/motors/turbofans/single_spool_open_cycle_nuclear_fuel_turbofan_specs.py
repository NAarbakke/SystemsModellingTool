from dataclasses import dataclass
from subsystems.propulsion.motors.components.inlets.inlet_specs import InletSpecs
from subsystems.propulsion.motors.components.compressors.fan_specs import FanSpecs
from subsystems.propulsion.motors.components.compressors.axial_compressor_specs import AxialCompressorSpecs
from subsystems.propulsion.motors.components.compressors.axial_compressor_geometry import AxialCompressorGeometry
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor_specs import FastNeutronReactorSpecs
from subsystems.propulsion.motors.components.turbines.axial_turbine_specs import AxialTurbineSpecs
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle_specs import ConvergentNozzleSpecs
from subsystems.propulsion.motors.components.ducting.duct_specs import DuctSpecs


@dataclass
class SingleSpoolOpenCycleNuclearTurbofanSpecifications:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    bypass_ratio: float                     # [-]
    inlet: InletSpecs
    fan: FanSpecs
    compressor: AxialCompressorSpecs
    compressor_geometry: AxialCompressorGeometry
    reactor: FastNeutronReactorSpecs
    turbine: AxialTurbineSpecs
    core_nozzle: ConvergentNozzleSpecs
    bypass_duct: DuctSpecs
    bypass_nozzle: ConvergentNozzleSpecs
