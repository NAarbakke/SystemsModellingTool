

"""
Depending on radar detection range and object velocity, operators have a certain amount of time to shoot down the incoming object (e.g. missile).
"""


def engagement_window(d_radar_detection, v_object):
    t_engagement = d_radar_detection / v_object
    return t_engagement