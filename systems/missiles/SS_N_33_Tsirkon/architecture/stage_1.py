



class Stage_1: 
    def __init__(self):
        self.airframe = Airframe()
        self.propulsion = SolidRocket()
        self.geometry = Geometry()
        self.mass_properties = MassProperties()
        self.actuators = Fins()