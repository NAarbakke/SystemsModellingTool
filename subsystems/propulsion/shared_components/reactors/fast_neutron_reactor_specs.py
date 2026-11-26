from dataclasses import dataclass


@dataclass
class FastNeutronReactorSpecs:
    """
    No defaults: values come from a vehicle specification (e.g. specifications/SKYF/engine.py).
    """
    T_tet: float                # [K]     target turbine entry temperature (air heated to this)
    PR_loss: float              # [-]     total pressure loss factor through core (Pt_out / Pt_in)
    fuel_material: str          # [-]     "UC" (uranium carbide), "UN" (nitride), "U-metal"
    n_fuel_rods: int            # [-]     number of fuel rods in core
    fuel_rod_length: float      # [m]     active fuel rod length
    fuel_rod_diameter: float    # [m]     fuel rod outer diameter
    max_fuel_T: float           # [K]     fuel centreline temperature limit
    power_density_limit: float  # [W/m^3] max core power density (fast reactor ~1-3 GW/m^3)
