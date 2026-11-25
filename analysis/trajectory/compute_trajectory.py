
def compute_trajectory() -> np.array:
    
with open('data/missiles/SS_N_33_Tsirkon/simulation_setup/SS_N_33_Tsirkon_setup.json', 'r') as file:
    simulation_setup = json.load(file)


if simulation_setup['governing_equations'] == "flat_earth_6dof_eom":

    #Create state vector array
    state_vector = np.zeros((initial_conditions.state_vector_0.size, t.size), dtype=np.float64)         #need to make suitable for 3dof - use skyfall sim as test case to develop class based code
    force_vector = np.zeros((initial_conditions.force_vector_0.size, t.size), dtype=np.float64)

    #Insert initial state (t = 0)
    state_vector[:, 0] = initial_conditions.state_vector_0
    force_vector[:, 0] = initial_conditions.force_vector_0

    #Run simulation
    t, state_vector, force_vector = runge_kutta_4(flat_earth_6dof_eom, t, state_vector, force_vector, dt, vehicle_parameters, aerodynamic_model, motor_burn_profile)
    #t, state_vector, force_vector = runge_kutta_4(flat_earth_3dof_eom, t, state_vector, force_vector, dt, vehicle_parameters, aerodynamic_model, motor_burn_profile)

    #divide into stage 1 and 2 sims, using vehicle classes, alternatively an object for Stage1 and Stage2?



class Trajectory:
    def __init__(self):
        self.