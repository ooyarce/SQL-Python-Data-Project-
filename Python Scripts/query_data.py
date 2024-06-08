#%% ================================== INIT AND CONNECT TO DATABASE ==================================
# Import modules
from pyseestko.utilities import getMappings      #type: ignore
from pyseestko           import queries as query #type: ignore
from matplotlib          import pyplot  as plt
from pathlib             import Path

# Temp imports
import pandas as pd

# DataBase user params
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'


#%% ========================================== INPUT PARAMS ==========================================
# Define paths to save the plots
project_path     = Path('C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/')

# Define the parameters
sim_types  = [i for i in range(1,4)]   # 1 = FB, 2 = AB, 3 = DRM
nsubs_lst  = [2,4]                       # Can be: 2,4
iterations = [i for i in range(1,6)]   # Can be: {1,2,3,4,5,6,7,8,9,10}
stations   = [i for i in range(1,10)]  # Can be: {0,1,2,3,4,5,6,7,8,9}

# Some extra parameters
windows      = True  # True if the OS is Windows, False if Linux
save_results = False # True if you want to save the results, False if not
show_plots   = False # True if you want to show the plots, False if not
mag_map, loc_map, rup_map = getMappings()


#%% =========================================== QUERY DATA ===========================================
# Get the drifts, spectra and base shear dataframes for the selected simulation types, nsubs,
# iterations and stations
# -------------------------------------- Execyte the main query --------------------------------------
drift_tple, spectra_df_dict, base_shear_df_dict = query.executeMainQuery(
    # Main params
    sim_types    = sim_types,
    nsubs_lst    = nsubs_lst,
    iterations   = iterations,
    stations     = stations,
    mag_map      = mag_map,
    loc_map      = loc_map,
    rup_map      = rup_map,
    # DataBase params
    user         = user,
    password     = password,
    host         = host,
    database     = database,
    # Save params
    save_drift   = True,
    save_spectra = False,
    save_b_shear = False,
    xlim_sup     = 0.025,
    # Extra params
    show_plots   = show_plots,
    save_results = save_results,
    project_path = project_path,
    )
drift_df_max_x, drift_df_max_y, drift_df_mean_x, drift_df_mean_y = drift_tple

# --------------------------------------- LOAD DATA FOR ANOVA ----------------------------------------
# Spectra results:
#max_spectra_lst_x = [df[0].max().max() for df in spectra_df_dict.values()]
#max_spectra_lst_y = [df[1].max().max() for df in spectra_df_dict.values()]

## Base shear results:
#mean_base_shear_lst = [abs(df['Shear X'].mean()) for df in base_shear_df_dict.values()]
#mean_base_shear_lst = [abs(df['Shear Y'].mean()) for df in base_shear_df_dict.values()]


# %%
