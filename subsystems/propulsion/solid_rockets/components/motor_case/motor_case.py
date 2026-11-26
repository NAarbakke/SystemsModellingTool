from dataclasses import dataclass


@dataclass(frozen=True)
class MotorCase:
    d: float                    # [m] outer diameter
    L: float                    # [m] length, without nozzle
    t_casing: float             # [m] casing wall thickness
    t_liner: float              # [m]
    t_insulation: float         # [m]

    # Derived - computed from the inputs above so they can never disagree
    @property
    def d_inner(self) -> float:
        """[m] bore inside casing + insulation + liner = outer diameter of a case-bonded grain."""
        return self.d - 2 * (self.t_casing + self.t_insulation + self.t_liner)
