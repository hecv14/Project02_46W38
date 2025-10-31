#%% imports
from turbie_mod import *
import os
import matplotlib.pyplot as plt


#%% inputs
# file paths
filepath_params = r"inputs\turbie_inputs\turbie_parameters.txt"
filepath_ct     = r"inputs\turbie_inputs\CT.txt"
filepath_wind   = r"inputs\wind_files\wind_TI_0.05\wind_4_ms_TI_0.05.txt"
# folder paths
folder_wind     = r"inputs\wind_files"
folder_outputs  = "outputs"


#%% prepare to solve_ivp
# get turbie_params
params = get_turbie_params(filepath_params)

# build M, C, K matrices
M, C, K = get_MCK(params)

# get ct interpolation class
ct_interp_class = get_ct(wsp=None, filepath_ct=filepath_ct)

#%% loop preparation

# how many TIs? make a list with TI folders
folders_ti = [entry.name for entry in os.scandir(folder_wind) if entry.is_dir()]
# NOTE: the list comprehension above can be understood as:
# folders_ti = []  # initialize empty list
# for entry in os.scandir(folder_wind):
#     if entry.is_dir():
#         folders_ti.append(entry.name)

# result headers
header = ["t", "x1", "x2", "dx1", "dx2"]

#%% prepare to solve_ivp

# Do for each TI class
for folder_ti in folders_ti:
    # path of the TI folder
    path_files = os.path.join(folder_wind, folder_ti)
    # how many wsp files for that TI? make a list of the files
    files = [entry.name for entry in os.scandir(path_files) if entry.is_file()]

    # Create folder for results for this TI
    path_output = os.path.join(folder_outputs, "solution_files", folder_ti)
    # Create directory if it does not exist
    os.makedirs(path_output, exist_ok=True)

    # lists to store results
    avg_wsps = []

    # do for each wind speed interval (file)
    # read wind file
    for file in files:
        # where is the file?
        path_file = os.path.join(path_files, file)
        print(f'reading {file}')
        # get wind_t and wind_wsp
        wind_t, wind_wsp = read_wind_txt(path_file)
        # and ct for the avg windspeed
        avg_wsp = float(wind_wsp.mean())
        ct = ct_interp_class(avg_wsp)
        # store average wind speed
        avg_wsps.append(round(avg_wsp,2))  

        # Solve dy
        # t_span
        t_span = (wind_t[0], wind_t[-1])
        # t_step 
        t_step=0.01
        # t_eval
        # t_eval = wind_t
        t_eval = np.arange(t_span[0], t_span[1] + t_step, t_step)

        # using default y0 = [0, 0, 0, 0]
        args = (M, C, K, wind_t, wind_wsp, params['Ar'], ct, params['rho'])
        t_sol, x1, x2, dx1, dx2 = simulate_turbie(t_span, t_eval, args)

        # Combine results into one array
        data = np.vstack((t_sol, x1, x2, dx1, dx2)).T
        
        # Save in .txt
        np.savetxt(
            os.path.join(path_output, "sol_" + file),
            data,
            header="\t".join(header),  # join headers with tab
            fmt="%.4f",
            delimiter="\t",
            comments=""
        )

        # plot t-series

        # relative blade displacements
        # x1_rel = x1 - x2
        # x2_rel = x2

        # %%