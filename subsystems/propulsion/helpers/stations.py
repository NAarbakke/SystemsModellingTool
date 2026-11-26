"""
Station numbering, shared by every engine (SAE ARP755): a number means the same place in every engine.

    0   freestream              (static state of the air the engine flies in)
    1   inlet lip               (highlight; x = 0 in the layouts)
    2   engine face             (first rotor: fan in a turbofan, compressor in a turbojet)
    13  fan exit, bypass stream
    25  compressor face         (turbofan core, behind the fan)
    3   compressor exit
    4   turbine entry           (combustor / reactor / heat exchanger exit)
    5   turbine exit
    9   (core) nozzle exit
    17  bypass duct exit
    19  bypass nozzle exit

Turbojets use 0-1-2-3-4-5-9; separate-flow turbofans add 13, 17, 19 (bypass) and 25 (core entry).
"""

STATION_NAMES = {
    "0": "Freestream",
    "1": "Inlet lip",
    "2": "Engine face",
    "13": "Fan exit (bypass)",
    "25": "Compressor face",
    "3": "Compressor exit",
    "4": "Turbine entry",
    "5": "Turbine exit",
    "9": "Nozzle exit",
    "17": "Bypass duct exit",
    "19": "Bypass nozzle exit"}


def stations(*keys: str) -> dict[str, str]:
    """Station -> name for the stations an engine has, in the order given"""
    return {key: STATION_NAMES[key] for key in keys}
