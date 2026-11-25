from dataclasses import dataclass, field
from typing import Final
import numpy as np
import pandas as pd 
import os
import re

from systems.missiles.SSC_X_9_SKYFALL.specifications.all_specs_from_excel import all_specs_from_excel_instance



@dataclass#(frozen=True)  # ← makes it immutable
class MissileSpecifications:                            #or PhysicalProperties? think specs
    length: float                   # [m]
    width: float                    # [m]
    height: float                   # [m]

    mass: float                     # [kg]
    #moment of inertias

    span_wing: float                # [m]
    span_tail: float                # [m]
    A_wing: float                   # [m2]
    A_tail: float                   # [m2]
    x_wing: float                   # [m] distance from CoG to airfoil neutral point
    x_tail: float                   # [m] distance from CoG to airfoil neutral point
    MAC_wing: float
    #MAC_tail: float

    u_cruise: float                 # [m/s]

    @property
    def fuselage_cross_sectional_area(self) -> float:
        area = self.width * self.height
        return area
    




missile_specifications = MissileSpecifications(
    length=all_specs_from_excel_instance.stage_3_length,
    width=all_specs_from_excel_instance.stage_3_width,
    height=all_specs_from_excel_instance.stage_3_height,
    mass=all_specs_from_excel_instance.stage_3_mass,
    span_wing=all_specs_from_excel_instance.stage_3_wing_span,
    span_tail=all_specs_from_excel_instance.stage_3_tail_span,
    A_wing=all_specs_from_excel_instance.stage_3_wing_area,
    A_tail=all_specs_from_excel_instance.stage_3_tail_area,
    x_wing=all_specs_from_excel_instance.stage_3_distance_from_cog_to_wing_neutral_point,
    x_tail=all_specs_from_excel_instance.stage_3_distance_from_cog_to_tail_neutral_point,
    MAC_wing=all_specs_from_excel_instance.stage_3_wing_mean_aerodynamic_chord,
    u_cruise=all_specs_from_excel_instance.cruise_velocity
    #etc.
)




#def clean_spec_name(name: str) -> str:
 #   #Example: "Stage 1 length [m]" → "stage_1_length"
  #  name = re.sub(r'\s*\[.*?\]\s*', '', name)  #Remove [m], [kg], etc.
   # name = re.sub(r'[^a-zA-Z0-9]', '_', name)  #Replace non-alphanumeric with _
    #name = name.lower().strip('_')
    #return name

