

class Guidance:
    def __init__(self, state_vector: StateVector) -> None:
        self.state_vector = state_vector

    def command_guidance(self) -> float:    #one command at certain point
        command = None
        alt = self.state_vector[7] #fex
        if alt < 1000:
            command = 10

        return command
