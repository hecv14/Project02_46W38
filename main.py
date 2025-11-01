#%% imports
from turbie_mod import *
import os
import pandas as pd
import matplotlib.pyplot as plt

#%% inputs
if __name__ == '__main__':
    #%% inputs
    # skip transitory part of simulated wind speed files
    t_trans = 60 # first n seconds
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
    header = ["t", "x1", "x2", "dx1", "dx2", 'x1_rel', 'x2_rel']

    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=['ti', 'wsp_avg',
                            'x1_rel_avg', 'x1_rel_std',
                            'x2_rel_avg', 'x2_rel_std'])

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

        # do for each wind speed interval (file)
        # read wind file
        for file in files:
            # where is the file?
            path_file = os.path.join(path_files, file)
            print(f'reading {file}')
            # get wind_t and wind_wsp
            wind_t, wind_wsp = read_wind_txt(path_file, skip_first_n_secs=t_trans)
            # and ct for the avg windspeed
            wind_wsp_avg = float(wind_wsp.mean())
            ct = ct_interp_class(wind_wsp_avg)

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

            # relative blade displacements
            x1_rel = x1 - x2
            x2_rel = x2 # NOTE: could be skipped but left for completion

            # Combine results into one array
            data = np.vstack((t_sol, x1, x2, dx1, dx2, x1_rel, x2_rel)).T

            # Save in .txt
            np.savetxt(
                os.path.join(path_output, "solution_" + file),
                data,
                header="\t".join(header),  # join headers with tab
                fmt="%.4f",
                delimiter="\t",
                comments=""
            )
            
            # Add relevant stats to df
            new_row = pd.DataFrame([{
                "ti": float(folder_ti.split('_')[-1]),
                "wsp_avg": round(wind_wsp_avg, 2),
                "x1_rel_avg": x1_rel.mean(),
                "x1_rel_std": x1_rel.std(),
                "x2_rel_avg": x2_rel.mean(),
                "x2_rel_std": x2_rel.std()
                }])

            # Append to df
            df = pd.concat([df, new_row], ignore_index=True)

    # save stats
    df = df.sort_values(by=['ti', 'wsp_avg'], ascending=[True, True])
    df.to_csv('x_rel_stats.txt', index=False, sep='\t')


    # %% plot

    # NOTE: this section is very messy, refactoring would help
    # df = pd.read_csv('x_rel_stats.txt', header=0, sep='\t')
    # df = df.sort_values(by=['ti', 'wsp_avg'], ascending=[True, True])

    ti_list = df['ti'].unique()
    df_aux = pd.DataFrame()
    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'purple', 'orange']


    #%% Plot x_avg
    # Create a figure and axis for the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # Loop through the unique TI values and plot the data
    for i, ti_sim in enumerate(ti_list):
        df_aux = df[df['ti'] == ti_sim]

    # Loop through the unique TI values and plot the data
    for i, ti_sim in enumerate(ti_list):
        df_aux = df[df['ti'] == ti_sim]
        
        # Plot for Rotor
        ax1.plot(df_aux['wsp_avg'], df_aux['x1_rel_avg'],
                label=f'TI = {ti_sim}', color=colors[i])
        
        # Plot for Hub, Nacelle & Tower
        ax2.plot(df_aux['wsp_avg'], df_aux['x2_rel_avg'],
                color=colors[i])

    # Customize the plot
    ax1.set_xlabel('Wind Speed (m/s)')
    ax1.set_ylabel('Avg. Relative Displacement (m)')
    ax1.legend()
    ax1.grid(True)  # Add a grid for easier readability
    ax1.set_title("Rotor")

    ax2.set_xlabel('Wind Speed (m/s)')
    ax2.grid(True)  # Add a grid for easier readability
    ax2.set_title("Hub, Nacelle, & Tower")

    # folder to save plots
    plots_folder = os.path.join(folder_outputs, "plots")
    # make if missing
    os.makedirs(plots_folder, exist_ok=True)
    plt.savefig(os.path.join(plots_folder, 'x_rel_avg.png'), dpi=300, bbox_inches='tight')
    # Display the plot
    plt.show()


    #%% Plot x_std
    # Create a figure and axis for the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # Loop through the unique TI values and plot the data
    for i, ti_sim in enumerate(ti_list):
        df_aux = df[df['ti'] == ti_sim]

    # Loop through the unique TI values and plot the data
    for i, ti_sim in enumerate(ti_list):
        df_aux = df[df['ti'] == ti_sim]
        
        # Plot for Rotor
        ax1.plot(df_aux['wsp_avg'], df_aux['x1_rel_std'],
                label=f'TI = {ti_sim}', color=colors[i])
        
        # Plot for Hub, Nacelle & Tower
        ax2.plot(df_aux['wsp_avg'], df_aux['x2_rel_std'],
                color=colors[i])

    # Customize the plot
    ax1.set_xlabel('Wind Speed (m/s)')
    ax1.set_ylabel('Std. Deviation Rel. Displacement (m)')
    ax1.legend()
    ax1.grid(True)  # Add a grid for easier readability
    ax1.set_title("Rotor")

    ax2.set_xlabel('Wind Speed (m/s)')
    ax2.grid(True)
    ax2.set_title("Hub, Nacelle, & Tower")

    # folder to save plots
    plots_folder = os.path.join(folder_outputs, "plots")
    # make if missing
    os.makedirs(plots_folder, exist_ok=True)
    plt.savefig(os.path.join(plots_folder, 'x_rel_std.png'), dpi=300, bbox_inches='tight')
    # Display the plot
    plt.show()

    #%% Plot x_avg and x_std
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Rotor Position as f(Wsp, TI)', fontsize=16)

    for i, ti_sim in enumerate(ti_list):
        df_aux = df[df['ti'] == ti_sim]
        
    # Select the appropriate axis based on the index
        if i == 0:
            ax = ax1
        elif i == 1:
            ax = ax2
        elif i == 2:
            ax = ax3
        else:
            continue  # Skip if there are more than 3 unique TI values

        # Use errorbar to plot with y-errors
        ax.errorbar(df_aux['wsp_avg'], df_aux['x1_rel_avg'],
                    yerr=df_aux['x1_rel_std'], color=colors[i],
                    label=f'TI = {ti_sim}', fmt='o')  # fmt='o' to show data points

        # Customize each subplot
        ax.set_title(f'TI = {ti_sim}')
        ax.set_xlabel('Wind Speed (m/s)')
        ax.set_ylabel('Avg. Relative Displacement (m)')
        ax.grid(True)
        ax.legend()
        ax.set_ylim(0, 1.2)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save the plot
    plt.savefig(os.path.join(plots_folder, 'x1_rel_avg_and_std.png'), dpi=300, bbox_inches='tight')

    # Display the plot
    plt.show()

    # %% time plot
    # get wind_t and wind_wsp
    plot_this_file = r"inputs\wind_files\wind_TI_0.15\wind_9_ms_TI_0.15.txt"
    wind_t, wind_wsp = read_wind_txt(plot_this_file, skip_first_n_secs=t_trans)
    # and ct for the avg windspeed
    wind_wsp_avg = float(wind_wsp.mean())
    ct = ct_interp_class(wind_wsp_avg)

    # Solve dy
    # t_span
    t_span = (wind_t[0], wind_t[-1])
    # t_step 
    t_step=0.01
    # t_eval
    t_eval = wind_t

    # using default y0 = [0, 0, 0, 0]
    args = (M, C, K, wind_t, wind_wsp, params['Ar'], ct, params['rho'])
    t_sol, x1, x2, dx1, dx2 = simulate_turbie(t_span, t_eval, args)

    # relative blade displacements
    x1_rel = x1 - x2
    x2_rel = x2 # NOTE: could be skipped but left for completion

    # Combine results into one array
    data = np.vstack((t_sol, x1, x2, dx1, dx2, x1_rel, x2_rel)).T

    # %%
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(10,5))
    fig.suptitle(r'Position as f(Wsp=9m/s, TI=15%)', fontsize=16)

    # x vs wsp
    ax1.scatter(wind_wsp, x1, s=1, alpha=0.6, label="Rotor")
    ax1.scatter(wind_wsp, x2, s=1, alpha=0.6, label="Hub, Nacelle, & Tower")
    ax1.set_xlabel("Wind Speed (m/s)")
    ax1.set_ylabel("Displacement (m)")

    # x vs t
    ax2.plot(wind_t, x1, label="Rotor")
    ax2.plot(wind_t, x2, label="Hub, Nacelle, & Tower")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("Displacement (m)")

    # Create secondary y-axis for wind_t vs wind_wsp
    ax2b = ax2.twinx()
    ax2b.plot(wind_t, wind_wsp, color='black', label="wsp", linestyle='-.', linewidth=0.5)
    ax2b.set_ylabel("Wind Speed (m/s)")
    ax2b.set_ylim(0, 1.1*wind_wsp.max())

    # Optional: add legends
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper left")
    ax2b.legend(loc="upper right")

    plt.tight_layout()

    # Save the plot
    plt.savefig(os.path.join(plots_folder, 'x_f_t_wsp.png'), dpi=300, bbox_inches='tight')

    plt.show()
# %%
