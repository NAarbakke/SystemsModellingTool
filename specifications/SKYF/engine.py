from dataclasses import dataclass, field


@dataclass
class InletSpecs:
    PR: float = 0.9


@dataclass
class FanSpecs:
    PR: float = 1.2
    eta_poly: float = 0.88
    r_tip: float = 0.5
    r_hub: float = 0.1


@dataclass
class CompressorSpecs:
    PR: float = 2.0
    eta_poly: float = 0.90


@dataclass
class CombustorSpecs:
    PR_loss: float = 0.98
    eta: float = 0.97
    LHV: float = 43e6
    T_tet: float = 1200.0  # [K]


@dataclass
class HeatExchangerSpecs:
    T_cold_out: float = 1200.0  # [K]  target HX cold-side outlet temperature
    hot_fluid: str = "helium"
    T_hot_in: float = 1500.0  # [K]  reactor coolant inlet temperature
    P_hot: float = 7e6  # [Pa] reactor coolant loop pressure
    mdot_hot: float = 100.0  # [kg/s] reactor coolant mass flow rate
    wall_material: str = "inconel_617"
    t_wall: float = 0.001  # [m]  wall thickness
    n_channels_cold: int = 150000
    n_channels_hot: int = 70000
    D_h_cold: float = 0.005  # [m]  hydraulic diameter, cold channels
    D_h_hot: float = 0.005  # [m]  hydraulic diameter, hot channels
    n_segments: int = 50


@dataclass
class TurbineSpecs:
    eta_poly: float = 0.88
    eta_mech: float = 0.95


@dataclass
class CoreNozzleSpecs:
    eta_isen: float = 0.98
    area: float = 0.3
    C_discharge: float = 0.95


@dataclass
class DuctSpecs:
    PR_loss: float = 0.95


@dataclass
class BypassNozzleSpecs:
    eta_isen: float = 0.98
    area: float = 0.7
    C_discharge: float = 0.98


@dataclass
class ReactorSpecs:
    T_tet: float = 1200.0              # [K]  target turbine entry temperature (air heated to this)
    PR_loss: float = 0.97              # total pressure loss factor through core (Pt_out / Pt_in)
    fuel_material: str = "UC"          # fuel: "UC" (uranium carbide), "UN" (nitride), "U-metal"
    n_fuel_rods: int = 2000            # number of fuel rods in core
    fuel_rod_length: float = 1.0       # [m]  active fuel rod length
    fuel_rod_diameter: float = 0.008   # [m]  fuel rod outer diameter
    max_fuel_T: float = 2500.0         # [K]  fuel centreline temperature limit
    power_density_limit: float = 2e9   # [W/m^3] max core power density (fast reactor ~1-3 GW/m^3)


@dataclass
class SingleSpoolClosedCycleNuclearTurbofanSpecifications:
    bypass_ratio: float = 2.0
    inlet: InletSpecs = field(default_factory=InletSpecs)
    fan: FanSpecs = field(default_factory=FanSpecs)
    compressor: CompressorSpecs = field(default_factory=CompressorSpecs)
    combustor: CombustorSpecs = field(default_factory=CombustorSpecs)
    hx: HeatExchangerSpecs = field(default_factory=HeatExchangerSpecs)
    turbine: TurbineSpecs = field(default_factory=TurbineSpecs)
    core_nozzle: CoreNozzleSpecs = field(default_factory=CoreNozzleSpecs)
    bypass_duct: DuctSpecs = field(default_factory=DuctSpecs)
    bypass_nozzle: BypassNozzleSpecs = field(default_factory=BypassNozzleSpecs)


@dataclass
class SingleSpoolOpenCycleNuclearTurbofanSpecifications:
    bypass_ratio: float = 2.0
    inlet: InletSpecs = field(default_factory=InletSpecs)
    fan: FanSpecs = field(default_factory=FanSpecs)
    compressor: CompressorSpecs = field(default_factory=CompressorSpecs)
    reactor: ReactorSpecs = field(default_factory=ReactorSpecs)
    turbine: TurbineSpecs = field(default_factory=TurbineSpecs)
    core_nozzle: CoreNozzleSpecs = field(default_factory=CoreNozzleSpecs)
    bypass_duct: DuctSpecs = field(default_factory=DuctSpecs)
    bypass_nozzle: BypassNozzleSpecs = field(default_factory=BypassNozzleSpecs)


specs_open_cycle = SingleSpoolClosedCycleNuclearTurbofanSpecifications()
