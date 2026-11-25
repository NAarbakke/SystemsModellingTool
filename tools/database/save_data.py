import h5py
import numpy as np


def save_data(filename, simulation_data):
    with h5py.File(filename, 'w') as f:
        # Store main data
        f.create_dataset('time', data=simulation_data['t'])
        f.create_dataset('state_vector', data=simulation_data['state_vector'])
        f.create_dataset('force_vector', data=simulation_data['force_vector'])
        
        # Store metadata
        f.attrs['vehicle_name'] = simulation_data.get('vehicle_name', 'unknown')
        f.attrs['timestamp'] = simulation_data.get('timestamp', '')
        f.attrs['dt'] = simulation_data.get('dt', 0.0)
