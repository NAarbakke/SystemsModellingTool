import h5py
import numpy as np



def load_data(filename):
    with h5py.File(filename, 'r') as f:
        data = {
            't': f['time'][:],
            'state_vector': f['state_vector'][:],
            'force_vector': f['force_vector'][:],
            'metadata': dict(f.attrs)
        }
    return data

