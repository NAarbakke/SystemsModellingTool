from tools.calculations.conversion_factors import in2m
from properties.propellants.solid_propellant_compounds_data import rho_AP, rho_Al_powder, rho_HTPB_R45HTLO

##################################### PROPELLANT TYPE DEPENDENT (play around with) ####################################################################################

a_coeff = 0.0135 * in2m * 0.3  #to increase burn time                                                                                 #[m/s] burn rate coefficient (grain composition dependent)                                                apply Monte Carlo as no exact value can be found theoretically (find rough vals from tried and tested formulations)
n_coeff = 0.4                                                                                           #[-] pressure exponent (grain composition dependent) -> 0.3 - 0.5 for most composite propellants          apply Monte Carlo as no exact value can be found theoretically (find rough vals from tried and tested formulations)

fuel = 'H2(L)'                                                                                          #NASA CEA thermo database name
oxidizer = 'O2(L)'                                                                                      #NASA CEA thermo database name
T_fuel = 20.27                                                                                          #[K] reactant temperature
T_oxidizer = 90.17                                                                                      #[K] reactant temperature


#compute density based on grain composition, which can be varied

f_oxidizer = 0.70                                                                                       #by mass
f_fuel = 0.15                                                                                           #by mass
f_binder = 0.15                                                                                         #by mass

MR = 5      #for now



def calc_grain_density(rho_oxidizer, rho_fuel, rho_binder, f_oxidizer, f_fuel, f_binder):
    rho_grain = 1 / ((f_oxidizer / rho_oxidizer) + (f_fuel / rho_fuel) + (f_binder / rho_binder))               #evt. flere drivstoffskomponenter                                                                   #from CEA, or compute myself?
    return rho_grain


rho_grain = calc_grain_density(rho_AP, rho_Al_powder, rho_HTPB_R45HTLO, f_oxidizer, f_fuel, f_binder)

#or just define oxidizer, fuel, binder characteristics in a json file or something

#function that computes reaction product composition based on propellant formulation (chemical formula, mass fractions)     CEA for this?? think so

#move to stage 1 and 2 params

