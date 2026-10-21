"""
Every engine a frontend can show (web dashboard, CLI, TUI, PDF reports): id -> (short label, view).
"""
from interface.gui.dashboard_view import EngineView
from interface.gui.single_spool_closed_cycle_nuclear_turbofan_view import VIEW as CLOSED_CYCLE_NUCLEAR_TURBOFAN
from interface.gui.single_spool_open_cycle_liquid_fuel_turbofan_view import VIEW as CONVENTIONAL_TURBOFAN
from interface.gui.single_spool_open_cycle_liquid_fuel_turbojet_view import VIEW as CONVENTIONAL
from interface.gui.single_spool_open_cycle_nuclear_turbofan_view import VIEW as NUCLEAR_TURBOFAN
from interface.gui.single_spool_open_cycle_nuclear_turbojet_view import VIEW as NUCLEAR

ENGINES: dict[str, tuple[str, EngineView]] = {
    "conventional": ("Conventional turbojet", CONVENTIONAL),
    "nuclear": ("Nuclear turbojet", NUCLEAR),
    "conventional_turbofan": ("Conventional turbofan", CONVENTIONAL_TURBOFAN),
    "nuclear_turbofan": ("Nuclear turbofan (open cycle)", NUCLEAR_TURBOFAN),
    "closed_cycle_nuclear_turbofan": ("Nuclear turbofan (closed cycle)", CLOSED_CYCLE_NUCLEAR_TURBOFAN)}
