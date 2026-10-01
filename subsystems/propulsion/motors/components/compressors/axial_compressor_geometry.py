from dataclasses import dataclass
from subsystems.propulsion.motors.components.compressors.annulus_type import AnnulusType


@dataclass
class AxialCompressorGeometry:
    """
    Physical dimensions of an axial compressor.
    Inputs only - sized results (n_stages, length) live in AxialCompressorSizing.
    No defaults for vehicle values: they come from a vehicle specification.
    """
    annulus_type: AnnulusType       # [-] which radius is held constant through the compressor
    r_tip: float                    # [m] inlet tip radius
    r_hub: float                    # [m] inlet hub radius
    AR_rotor: float                 # [-] rotor blade aspect ratio = h / c
    AR_stator: float                # [-] stator blade aspect ratio = h / c
    IGV_axial_chord_length: float   # [m] inlet guide vane axial chord
    EGV_axial_chord_length: float   # [m] exit guide vane axial chord
    IRG_to_chord: float = 0.25      # [-] inter-row gap as a fraction of the upstream axial chord

    # Derived - computed from the inputs above so they can never disagree
    @property
    def r_mean(self) -> float:
        return (self.r_tip + self.r_hub) / 2

    @property
    def hub_to_tip(self) -> float:
        return self.r_hub / self.r_tip    # 0.4 - 0.6 at front stage ish

    @property
    def h(self) -> float:
        """Blade span at inlet [m]"""
        return self.r_tip - self.r_hub

    @property
    def c_rotor(self) -> float:
        """Rotor chord [m], treated as axial chord (stagger not modelled yet)"""
        return self.h / self.AR_rotor

    @property
    def c_stator(self) -> float:
        """Stator chord [m], treated as axial chord (stagger not modelled yet)"""
        return self.h / self.AR_stator
