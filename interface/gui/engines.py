"""
Every engine a frontend can show (web dashboard, PDF reports): id -> (short label, view).
"""
from interface.gui.dashboard_view import EngineView
from interface.gui.single_spool_open_cycle_liquid_fuel_turbojet_view import VIEW as CONVENTIONAL
from interface.gui.single_spool_open_cycle_nuclear_turbojet_view import VIEW as NUCLEAR

ENGINES: dict[str, tuple[str, EngineView]] = {
    "conventional": ("Conventional", CONVENTIONAL),
    "nuclear": ("Nuclear", NUCLEAR)}
