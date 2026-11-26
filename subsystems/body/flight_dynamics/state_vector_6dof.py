from dataclasses import dataclass
from typing import ClassVar

import numpy as np


@dataclass(slots=True)
class StateVector3DoF:
    t: float = 0.0
    lat: float = 0.0
    lon: float = 0.0
    alt_m: float = 0.0
    V: float = 0.0
    gamma: float = 0.0
    chi: float = 0.0
    mass: float = 1.0

    NAMES: ClassVar = ("lat", "lon", "alt_m", "V", "gamma", "chi", "mass")

    def to_array(self):
        return np.array([self.lat, self.lon, self.alt_m,
                         self.V, self.gamma, self.chi, self.mass])

    @classmethod
    def from_array(cls, t, y):
        return cls(t, *(float(x) for x in y))



@dataclass(slots=True)
class StateVector3oOFCartesian:
    t: float = 0.0
    lat: float = 0.0
    lon: float = 0.0
    alt_m: float = 0.0
    vn: float = 0.0
    ve: float = 0.0
    vd: float = 0.0
    mass: float = 1.0

    NAMES: ClassVar = ("lat", "lon", "alt_m", "vn", "ve", "vd", "mass")

    def to_array(self):
        return np.array([self.lat, self.lon, self.alt_m,
                         self.vn, self.ve, self.vd, self.mass])

    @classmethod
    def from_array(cls, t, y):
        return cls(t, *(float(x) for x in y))


        
@dataclass(slots=True)
class StateVector6DoF:
    t: float = 0.0
    lat: float = 0.0
    lon: float = 0.0
    alt_m: float = 0.0
    u: float = 0.0
    v: float = 0.0
    w: float = 0.0
    phi: float = 0.0
    theta: float = 0.0
    psi: float = 0.0
    p: float = 0.0
    q: float = 0.0
    r: float = 0.0
    mass: float = 1.0

    NAMES: ClassVar = ("lat", "lon", "alt_m", "u", "v", "w",
                       "phi", "theta", "psi", "p", "q", "r", "mass")

    def to_array(self):
        return np.array([self.lat, self.lon, self.alt_m,
                         self.u, self.v, self.w,
                         self.phi, self.theta, self.psi,
                         self.p, self.q, self.r, self.mass])

    @classmethod
    def from_array(cls, t, y):
        return cls(t, *(float(x) for x in y))
