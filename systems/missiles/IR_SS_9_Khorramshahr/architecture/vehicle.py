from subsystems.body.aerodynamics.constant_model import constant_model

from systems.missiles.IR_SS_9_Khorramshahr.specifications.physical_properties import physical_properties
from systems.missiles.IR_SS_9_Khorramshahr.specifications.performance_characteristics import performance_characteristics
from systems.missiles.IR_SS_9_Khorramshahr.specifications.collection_data import collection_data



class Khorramshahr_1:
    def __init__(self):
       # Stages
       self.booster = Booster_with_GNC()
       self.rv = ReentryVehicle

       # Properties
       self.aerodynamics = constant_model
       
    def eject?
