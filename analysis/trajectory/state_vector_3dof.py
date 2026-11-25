from dataclasses import dataclass


@dataclass
class StateVector3DoF:
    u_body: float
    v_body: float
    w_body: float
    x_ned: float 
    y_ned: float
    z_ned: float
    m: float
    