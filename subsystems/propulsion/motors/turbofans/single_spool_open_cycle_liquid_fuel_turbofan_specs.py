from dataclasses import dataclass
from subsystems.propulsion.motors.components.inlets.subsonic_inlet_specs import SubsonicInletSpecs
from subsystems.propulsion.motors.components.compressors.fan_specs import FanSpecs
from subsystems.propulsion.motors.components.compressors.centrifugal_compressor_specs import CentrifugalCompressorSpecs
from subsystems.propulsion.motors.components.combustors.combustor_specs import CombustorSpecs
from subsystems.propulsion.motors.components.turbines.axial_turbine_specs import AxialTurbineSpecs
from subsystems.propulsion.motors.components.nozzles.convergent_nozzle_specs import ConvergentNozzleSpecs
from subsystems.propulsion.motors.components.ducting.duct_specs import DuctSpecs


@dataclass
class SingleSpoolOpenCycleLiquidFuelTurbofanSpecifications:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    bypass_ratio: float                     # [-]
    subsonic_inlet: SubsonicInletSpecs
    fan: FanSpecs
    compressor: CentrifugalCompressorSpecs
    combustor: CombustorSpecs
    turbine: AxialTurbineSpecs
    core_nozzle: ConvergentNozzleSpecs
    bypass_duct: DuctSpecs
    bypass_nozzle: ConvergentNozzleSpecs
