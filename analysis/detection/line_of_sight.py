import numpy as np

"""
Line of sight to object in air due to the curvature of earth

Inputs:
    h_object
    h_observer
    r_earth
    
Returns:
    d_los
"""


def los_distance(r_earth, h_observer, h_object):
    d_los = np.sqrt((r_earth + h_observer)**2 - r_earth**2) + np.sqrt((r_earth + h_object)**2 - r_earth**2)
    return d_los