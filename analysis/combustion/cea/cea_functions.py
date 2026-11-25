import numpy as np
import cea

#P_c = 6.895e6
#MR = 5
#exp_ratio = 5.6

#fuel = 'H2(L)'
#oxidizer = 'O2(L)'
#T_fuel = 20.27
#T_oxidizer = 90.17

#frozen_condition = False
#frozen_throat_condition = False


def get_combustion_product_conditions_from_CEA(P_chamber, MR, eps, fuel, oxidizer, T_fuel, T_oxidizer, frozen_condition, frozen_throat_condition):

    print("The function get_combustion_product_conditions_from_CEA is being called")

    if frozen_condition is False:
        n_frz = None                            #equilibrium
    elif frozen_throat_condition is False:
        n_frz = 1                               #frozen in chamber
    else:
        n_frz = 2                               #frozen at throat

    reactant_names = [fuel, oxidizer]           #NASA CEA thermo database names, e.g. 'H2(L)', 'O2(L)'
    reactants = cea.Mixture(reactant_names)
    products = cea.Mixture(reactant_names, products_from_reactants=True)
    solver = cea.RocketSolver(products, reactants=reactants)
    solution = cea.RocketSolution(solver)

    weights = reactants.of_ratio_to_weights(np.array([0.0, 1.0]), np.array([1.0, 0.0]), MR)
    h_chamber = reactants.calc_property(cea.ENTHALPY, weights, np.array([T_fuel, T_oxidizer])) / cea.R

    solver.solve(solution, weights, P_chamber * 1e-5, supar=[eps], n_frz=n_frz, hc=h_chamber)      #[Pa] -> [bar], infinite area combustor
    if not solution.converged:
        raise RuntimeError(f"CEA did not converge (P_chamber={P_chamber} Pa, MR={MR}, eps={eps})")

    T_chamber, T_throat, T_exit = solution.T                                                           #[K] points: chamber, throat, exit
    M_w_chamber, M_w_throat, M_w_exit = solution.M * (1 / 1000)                                         #[g/mol] -> [kg/mol]
    gamma_chamber, gamma_throat, gamma_exit = solution.gamma_s
    M_exit = solution.Mach[2]
    c_star_theoretical = solution.c_star[0]                                                            #[m/s]

    return T_chamber, T_throat, T_exit, M_w_chamber, M_w_throat, M_w_exit, gamma_chamber, gamma_throat, gamma_exit, M_exit, c_star_theoretical





#T_c, T_t, T_e, M_w_c, M_w_t, M_w_e, gamma_c, gamma_t, gamma_e, M_e, c_star = get_combustion_product_conditions_from_CEA(P_c, MR, exp_ratio, fuel, oxidizer, T_fuel, T_oxidizer, frozen_condition, frozen_throat_condition)

#print(f"Chamber T: {T_c} K")
#print(f"Throat T: {T_t} K")
#print(f"Exit T: {T_e} K")

#print(f"Chamber M_w: {M_w_c} kg/mol")
#print(f"Throat M_w: {M_w_t} kg/mol")
#print(f"Exit M_w: {M_w_e} kg/mol")

#print(f"Chamber gamma: {gamma_c}")
#print(f"Throat gamma: {gamma_t}")
#print(f"Exit gamma: {gamma_e}")

#print(f"Exit Mach: {M_e}")

#print(f"c_star: {c_star} m/s")
