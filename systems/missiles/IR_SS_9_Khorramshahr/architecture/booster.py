


class Booster_with_GNC(Stage):
    def __init__(self):
        self.propulsion = RocketEngineSimple(..)
        self.guidance = PitchProgram(..)

        self.physical_properties = PhysicalProperties(..)
        #self.aerodynamics = AeroConstModel     #for splashdown estimation