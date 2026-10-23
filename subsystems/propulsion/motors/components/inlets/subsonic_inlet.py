from subsystems.propulsion.motors.components.base_component import Component
from subsystems.propulsion.motors.helpers.flow_state import FlowState
from subsystems.propulsion.motors.helpers.gas_model import GasModel
from subsystems.propulsion.motors.helpers.total_to_static import static_from_mass_flow
from subsystems.propulsion.motors.components.inlets.subsonic_inlet_specs import SubsonicInletSpecs
from subsystems.propulsion.motors.components.inlets.subsonic_inlet_geometry import SubsonicInletGeometry


class SubsonicInlet(Component):
    """
    Simple inlet: preserves Tt, drops Pt by a pressure recovery factor PR_inlet in the diffuser (lip 1 -> face 2).
    Passes totals only: the face velocity (and so the statics and m_dot) is set by the compressor or fan downstream.
    """

    def __init__(self, specs: SubsonicInletSpecs, geometry: SubsonicInletGeometry, gas_model: GasModel, name: str = "inlet"):
        super().__init__(gas_model, name, specs, geometry)
        self.PR_inlet = specs.PR

    def process(self, flow: FlowState) -> FlowState:
        Tt_in = flow.Tt
        Pt_in = flow.Pt

        Tt_out = Tt_in
        Pt_out = self.PR_inlet * Pt_in

        out = FlowState(
            Tt=Tt_out,
            Pt=Pt_out)

        return out

    def lip(self, freestream: FlowState, m_dot: float) -> FlowState:
        """
        State at the lip (station 1), back-filled once the engine face has set m_dot.
        Ahead of the lip the stream tube is loss-free, so the totals are the freestream's (recovery is lost in the
        diffuser); continuity through the lip area gives the lip Mach. Works static: the engine sucks the air in.
        """
        totals = FlowState(
            Tt=freestream.Tt,
            Pt=freestream.Pt)

        out = static_from_mass_flow(totals, m_dot, self.geometry.A_lip, self.gas)

        return out
