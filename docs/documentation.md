    ## Mass flow rate
  How do deal with:
    1) compute from fan - m_dot_total
      - m_dot_bypass = beta * m_dot_core
      - m_dot_total = m_dot_core + m_dot_bypass = m_dot_core * (1 + beta)
      - m_dot_core = m_dot_total / (1 + beta)
        --> size core from mass flow rate through it
      
    2) compute from nozzle - m_dot_core
      - then get the others from bypass ratio
    
  

# Design inputs
  - atmospheric conditions at given altitude (T, P, rho, cp, gamma, a (sound speed))
  - cruise velocity (u) -> get M (Mach nr)
  - bypass ratio
  - fan tip radius (r_tip) - check typical tip to hub ratio to get flow area
  - turbine entry temperature (T_tet)



# documentation/features noe som forklarer hva koden gjør og kan gjøre


# todo
calcs/cycle analysis of microreactors of various cycle architectures for various prop systems and vehicles