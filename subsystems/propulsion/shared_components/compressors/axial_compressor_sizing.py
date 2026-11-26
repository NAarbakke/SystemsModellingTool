from dataclasses import dataclass


@dataclass
class AxialCompressorSizing:
    """
    Results of sizing an axial compressor - computed by AxialCompressor.compute_geometry().
    """
    n_stages: int           # [-]
    L_stage: list[float]    # [m]   per stage: rotor + stator + inter-row gaps, front to back
    r_hub_stage: list[float]    # [m]   per stage: hub radius at stage entry
    r_tip_stage: list[float]    # [m]   per stage: tip radius at stage entry
    L: float                # [m]   total length incl. IGV and EGV
