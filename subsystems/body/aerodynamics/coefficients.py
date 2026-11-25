
#def C_x(alpha, beta, Mach, Re, aerodynamic_model): #what else
 #   C_x = C_x_0 + C_x_alpha * alpha + C_x_q * ((q * c) / (2 * V))   #simple model only dependent on alpha and q
  #  return C_x

#this is the aerodynamic model!! so rename...

def C_D(alpha, aerodynamic_model):
    C_D = aerodynamic_model.C_D_0 + aerodynamic_model.C_D_alpha * alpha     #simple model only dependent on alpha. actually also beta dependent(++?)
    return C_D

def C_S(beta, aerodynamic_model):
    C_S = aerodynamic_model.C_S_0 + aerodynamic_model.C_S_beta * beta 
    return C_S

def C_L(alpha, aerodynamic_model):
    C_L = aerodynamic_model.C_L_0 + aerodynamic_model.C_L_alpha * alpha 
    return C_L


#what should these models really be like

def C_l(alpha, aerodynamic_model):  #roll moment coeff
    C_l = aerodynamic_model.C_l_0 + aerodynamic_model.C_l_alpha * alpha #gamma
    return C_l

def C_m(alpha, aerodynamic_model, q_body, c_ref, true_airspeed):  #pitch moment coeff
    C_m = aerodynamic_model.C_m_0 + aerodynamic_model.C_m_alpha * alpha + aerodynamic_model.C_m_q * ((q_body * c_ref) / (2 * true_airspeed)) # + C_m_de * de (elevator angle)
    return C_m

def C_n(beta, aerodynamic_model):  #yaw moment coeff
    C_n = aerodynamic_model.C_n_0 + aerodynamic_model.C_n_beta * beta 
    return C_n

