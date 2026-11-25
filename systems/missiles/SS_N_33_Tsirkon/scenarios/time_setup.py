import numpy as np

##################################### SIMULATION SETUP #################################################################################################### makeone for each system

t_start = 0                                           # start time                  delete cause one for each system anyway
t_end = 6                                             # end time
dt = 0.1                                              # time step

#Create time array
t = np.arange(t_start, t_end + dt, dt)                # time array: [0, 0.1, 0.2, ... 5.9, 6.0]         just keep in main script in class
n_t = t.size                                          # size of time array (60 now)

