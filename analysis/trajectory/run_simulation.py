import json
from datetime import datetime

from tools.database.save_data import save_data
from systems.missiles.SSC_X_9_SKYFALL.architecture.SSC_X_9_SKYFALL import SSC_X_9_SKYFALL



with open('data/missiles/SSC_X_9_SKYFALL/simulation_setup_GENERIC/SSC_X_9_SKYFALL_setup.json', 'r') as file:
    simulation_setup = json.load(file)



t, state_vector, force_vector = SSC_X_9_SKYFALL.simulate_stage_3(simulation_setup)      







simulation_result = {
    't': t,
    'state_vector': state_vector,
    'force_vector': force_vector,
    'vehicle_name': 'SSC-X-9 SKYFALL',
    'dt': dt,
    'timestamp': str(datetime.now())
}

filename = 'simulation_run.h5' 

save_data(filename, simulation_result)



#in plotting script
#simulation_data = load_data(filename)

#plot