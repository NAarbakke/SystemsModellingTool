from analysis.detection.line_of_sight import los_distance

"""
Radio waves (radar) actually bend slightly downward as they travel through the Earth's atmosphere due to variations in air density and refractive index. 
This refraction effectively allows the radar to "see" about 15% further over the horizon than pure light-of-sight geometry allows.
This figure comes from the 4/3 Earth Radius Model in a standard atmosphere. 
It does not (yet) take into account the capabilities and limitations of the specific radar in use. 
"""


def radar_detection_range(r_earth, h_observer, h_object):
    d_los = los_distance(r_earth, h_observer, h_object)
    d_radar_detection = 1.15 * d_los
    return d_radar_detection