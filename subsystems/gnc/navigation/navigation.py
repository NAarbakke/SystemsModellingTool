

class Navigation:
    def __init__(self, state_vector: StateVector) -> None:
        self.state_vector = state_vector

    def coordinates_from_state_vector(self) -> np.ndarray:
        lat = self.state_vector[4]  #fex
        long =
        alt =
        coordinates = np.array([lat, long, alt])
        return coordinates
