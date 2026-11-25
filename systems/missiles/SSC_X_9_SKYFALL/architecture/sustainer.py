


class Sustainer:
    def __init__(self, ):
        
        #-----Subsystems-----
        #self.airframe = Airframe()     #aero model and mass props here?
        self.propulsion = SingleSpoolOpenCycleInlineNuclearTurbojet()
        self.actuators = [Rudder(), ]   #?
        self.gnc = GNC()
        
        
        #-----Specifications-----