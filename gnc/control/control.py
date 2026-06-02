
class Control:
    def __init__(self, trim_state: TrimState) -> None:
        self.trim_state = trim_state

    def PID_controller(self) -> np.ndarray: #signals of some sort
