from enum import StrEnum


class AnnulusType(StrEnum):
    """Which radius is held constant through the compressor"""
    CONSTANT_TIP = "constant_tip"
    CONSTANT_MEAN = "constant_mean"
    CONSTANT_HUB = "constant_hub"
