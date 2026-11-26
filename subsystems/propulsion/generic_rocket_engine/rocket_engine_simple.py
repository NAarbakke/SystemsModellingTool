"""
Simple rocket engine model that takes burn time from collection, specific impulse from propellant assumptions,
initial mass from open sources and mass ratio as iterating parameter to compute a constant thrust level
"""

class RocketEngineSimple:
    def __init__(self, performance_characteristics: PerformanceCharacteristics, physical_properties: PhysicalProperties, collection_data: CollectionData, constants: Constants):
        self.I_sp = performance_characteristics.I_sp
        self.MR = physical_properties.MR
        self.m_wet = physical_properties.m_wet
        self.t_burn = collection_data.t_burn
        self.g_0 = constants.g_0
        
        
    def dry_mass(self) -> float:
        m_dry = self.m_wet / self.MR
        return m_dry
        
        
    def propellant_mass(self) -> float:
        m_dry = self.dry_mass()
        m_prop = self.m_wet - m_dry
        return m_prop
        
        
    def mass_flow_rate(self) -> float:
        m_prop = self.propellant_mass()
        m_dot = m_prop / self.t_burn
        return m_dot
        
        
    def effective_exhaust_velocity(self) -> float:
        c = self.I_sp * self.g_0
        return c
        
        
    def thrust(self) -> float:
        m_dot = self.mass_flow_rate()
        c = self.effective_exhaust_velocity()
        F_T = m_dot * c
        return F_T