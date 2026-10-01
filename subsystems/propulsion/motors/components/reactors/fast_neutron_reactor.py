import numpy as np

from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.components.reactors.fast_neutron_reactor_specs import FastNeutronReactorSpecs


class FastNeutronReactor(Component):
    """
    Open-cycle fast neutron reactor: air passes directly through the
    reactor core and is heated by contact with the fuel rods.

    Fast spectrum (no moderator) - typical for compact, high power
    density aerospace reactors. Metallic / ceramic fuel (UC, UN, U-metal)
    arranged as a bundle of parallel fuel rods; cooling air flows in
    the gaps between rods.

    Thermodynamic model (1-D, lumped):
        - Air is heated from Tt_in to T_tet at the core exit.
        - Total pressure drops by PR_loss across the core (friction +
          form losses in the rod bundle).
        - Mass flow is unchanged (no mass addition; air IS the coolant).
        - Required thermal power:  Q = m_dot * cp_avg * (T_tet - Tt_in)

    Sizing checks performed each call:
        - Volumetric power density vs. limit
        - (room for fuel centreline temperature check later)
    """

    def __init__(self, specs: FastNeutronReactorSpecs, gas_model: GasModel, name: str = "reactor"):
        super().__init__(gas_model, name)
        self.T_tet = specs.T_tet
        self.PR_loss = specs.PR_loss
        self.fuel_material = specs.fuel_material
        self.n_fuel_rods = specs.n_fuel_rods
        self.fuel_rod_length = specs.fuel_rod_length
        self.fuel_rod_diameter = specs.fuel_rod_diameter
        self.max_fuel_T = specs.max_fuel_T
        self.power_density_limit = specs.power_density_limit

        # Pre-compute core geometry
        self.V_fuel = (
            self.n_fuel_rods
            * np.pi * (self.fuel_rod_diameter / 2.0)**2
            * self.fuel_rod_length)
        self.A_fuel_surface = (
            self.n_fuel_rods
            * np.pi * self.fuel_rod_diameter
            * self.fuel_rod_length)

        # Results from last process() call
        self.last_Q_reactor: float = 0.0
        self.last_power_density: float = 0.0
        self.last_heat_flux: float = 0.0
        self.last_within_limits: bool = True

    def process(self, flow: FlowState) -> FlowState:
        self.last_inlet = flow
        
        Tt_in = flow.Tt
        Pt_in = flow.Pt

        # Heat addition (constant-cp approximation at mean temperature)
        cp_avg = self.gas.cp(0.5 * (Tt_in + self.T_tet))
        Q = flow.m_dot * cp_avg * (self.T_tet - Tt_in)

        # Core power density and surface heat flux
        q_vol = Q / self.V_fuel if self.V_fuel > 0 else 0.0
        q_surf = Q / self.A_fuel_surface if self.A_fuel_surface > 0 else 0.0

        self.last_Q_reactor = Q
        self.last_power_density = q_vol
        self.last_heat_flux = q_surf
        self.last_within_limits = q_vol <= self.power_density_limit

        # Total pressure loss across core
        Pt_out = self.PR_loss * Pt_in

        out = FlowState(
            Tt=self.T_tet,
            Pt=Pt_out,
            m_dot=flow.m_dot)

        self.last_exit = out
        return out
