from dataclasses import dataclass


@dataclass
class AxialCompressorSizing:
    """
    Results of sizing an axial compressor - computed by AxialCompressor.compute_geometry().
    """
    n_stages: int           # [-]
    L_stage: list[float]    # [m]   per stage: rotor + stator + inter-row gaps, front to back
    L: float                # [m]   total length incl. IGV and EGV
