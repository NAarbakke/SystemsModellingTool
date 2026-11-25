from systems.missiles.SSC_X_9_SKYFALL.specifications.missile_specifications import missile_specifications
from systems.missiles.SSC_X_9_SKYFALL.specifications.aerodynamic_model import aerodynamic_model


def aerodynamic_centre(specifications: missile_specifications, aerodynamic_model: aerodynamic_model):
    """
    Inputs
        C_L_wing_alpha:                     derivative of wing lift coefficient wrt. alpha (pitch angle) -> dC_L_wing / da 
        A_wing:                             wing reference area (projected?)
        x_wing:                             distance between CoG and point on wing through which lift acts

        C_L_tail_alpha:                     derivative of tail lift coefficient wrt. alpha (pitch angle) -> dC_L_tail / da
        A_tail:                             tail reference area (projected?)
        x_tail:                             distance between CoG and point on tail through which lift acts

    Returns
        x_np:                               aerodynamic centre / missile neutral point (same as neutral point for an aerofoil - the point about which the pitching moment is independent of incidence)
    """

    A_wing = specifications.A_wing
    x_wing = specifications.x_wing
    A_tail = specifications.A_tail
    x_tail = specifications.x_tail

    C_L_wing_alpha = aerodynamic_model.C_L_wing_alpha
    C_L_tail_alpha = aerodynamic_model.C_L_tail_alpha
    
    x_np = (C_L_wing_alpha * A_wing * x_wing + C_L_tail_alpha * A_tail * x_tail) / (C_L_wing_alpha * A_wing + C_L_tail_alpha * A_tail)

    return x_np
