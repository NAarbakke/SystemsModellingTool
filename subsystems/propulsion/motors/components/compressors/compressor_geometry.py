from dataclasses import dataclass

@dataclass
class AxialCompressorGeometry:  #fixed with time and should accomodate all design geometry options
    IGV_axial_chord_length: float
    EGV_axial_chord_length: float
    IRG = 0.25 * upstream_axial_chord_length
    AR_rotor: float
    AR_stator: float
    h_rotor: float            # blade span
    h_stator: float
    c_rotor: float
    c_stator: float            # true chord 
    r_tip: float               # decide which of r_tip and hub is constant - now r_tip is      
    r_hub_inlet: float
    r_mean: float 

    # Computed
    L_stage_1: float | None = None
    L_stage_2: float | None = None
    L: float | None = None
    n_stages: int | None = None