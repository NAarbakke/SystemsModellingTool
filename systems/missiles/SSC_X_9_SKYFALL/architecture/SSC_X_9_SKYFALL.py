import numpy as np
from systems.missiles.SSC_X_9_SKYFALL.initial_conditions.initial_conditions import initial_conditions_3dof
from systems.missiles.SSC_X_9_SKYFALL.specifications.launch_booster_specifications import launch_booster_specifications
from systems.missiles.SSC_X_9_SKYFALL.specifications.side_booster_specifications import side_booster_specifications
from systems.missiles.SSC_X_9_SKYFALL.specifications.missile_specifications import missile_specifications


class SSC_X_9_SKYFALL:      # serve the purpose of declaring missile structure only, or also implementing analysis functions, like now?????
    def __init__(self, initial_conditions_3dof):
        #-----Initial conditions-----
        self.initial_conditions_3dof = initial_conditions_3dof                     # do not specify WHICH dof, as could be either 3 or 6DOF --- ikke hensiktsmessig å simulere kryssermissil i 3dof!
        self.initial_considtions_6dof = InitialConditions6DoF()
        
        #-----Stages-----
        self.launch_booster = LaunchBooster()
        self.side_boosters = [SideBooster(), ]
        self.sustainer = Sustainer()
        
        self.aerodynamic_model = 
        
        
       
        
        
        
    #def simulate_stage_2(self, ...):
     
     #   updated_initial_cond = InitialConditions(...)   
     #   self.initial_conditions_3dof = updated_initial_conditions_after_stage_2_sim
     


    def compute_trajectory(self, simulation_setup) -> np.ndarray:             # keep in flight_trajectory folder instead so i dont have to repeat for every system? its GENERIC
        analysis.compute_trajectory()
        
        # move to analysis dir
        integrator = simulation_setup['integrator']
        flight_dynamics = simulation_setup['governing_equations']           # should do flight_dynamics = flat_earth_3dof_eom, now it does "flat_earth_3dof_eom", right?
        
        #initial conditions (state_vector_0) insert
        
        if integrator == "runge_kutta_4th":     
            t, state_vector, force_vector = runge_kutta_4(flat_earth_3dof_eom, t, state_vector, force_vector, dt, vehicle_parameters, aerodynamic_model, motor_burn_profile)    #how to solve this difference in input parameters - make into class?
            
            
    #def simulate_stage_3_with_propulsion_in_the_loop()
                    
    #def combine_simulation_data(self, sim_data):
    









    #### or break it up into more specific specs, like below:


    #physical_properties, propulsion, etc.

    #other properties? like separation times, delays

    #or do missile = Missile, where Missile consists of physcial_dims = MissilePhysicalDims, propulsion = MissilePropulsion, etc. ?
    
    
    
    #### ALSO NEED TO WRITE ACTUAL CLASS DECLARATION, like done in flight_trajectory folder - do it here i think
    
    SSC_X_9_SKYFALL = SSC_X_9_SKYFALL()
    