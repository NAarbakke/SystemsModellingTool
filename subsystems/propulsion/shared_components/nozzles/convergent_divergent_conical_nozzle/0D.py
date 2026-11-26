

class ZeroDimensionalModel:
    def __init__(self, nozzle_geometry: NozzleGeometry):
        self.geometry = nozzle_geometry
        
    def expand_flow(self) -> FlowState:
        