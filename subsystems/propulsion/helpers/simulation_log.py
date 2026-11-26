from dataclasses import dataclass, field
from typing import List

from subsystems.propulsion.shared.flow_state import FlowState


@dataclass
class SimulationLog:
    """
    Time history of any station-based flow state.

    Generic container: the logged records can be FlowState (a single station
    over time) or any compound dataclass grouping FlowStates (e.g. MotorState).
    """
    states: List[FlowState] = field(default_factory=list)

    def append(self, state: FlowState) -> None:
        self.states.append(state)

    def __getitem__(self, index) -> FlowState:
        return self.states[index]

    def __len__(self) -> int:
        return len(self.states)
