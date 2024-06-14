#%% ================================== INIT AND CONNECT TO DATABASE ==================================
# Import modules
from pyseestko.utilities  import getMappings, load_module     #type: ignore
from pyseestko            import queries as query #type: ignore
from matplotlib           import pyplot  as plt
from pathlib              import Path
from pyseestko.utilities  import getDriftResultsDF      #type: ignore
from pyseestko.utilities  import getSpectraResultsDF    #type: ignore
from pyseestko.utilities  import getSBaseResultsDF      #type: ignore
# Temp imports
import pandas as pd
import winsound


# DataBase user params
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

# Debugging
path_to_queries = Path("C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/Python Scripts/PySeesTKO/pyseestko/queries.py")
#query = load_module('query', path_to_queries)

#%% ========================================== INPUT PARAMS ==========================================
# Define paths to save the plots
project_path = Path('C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs')

# Define the parameters
sim_types  = [i for i in range(1,4)]   # 1 = FB, 2 = AB, 3 = DRM
nsubs_lst  = [2,4]                     # Can be: 2,4
iterations = [i for i in range(1,6)]   # Can be: {1,2,3,4,5,6,7,8,9,10}
stations   = [i for i in range(1,10)]  # Can be: {0,1,2,3,4,5,6,7,8,9}

# Some extra parameters
windows    = True  # True if the OS is Windows, False if Linux
save_csvs  = False # True if you want to save the results, False if not
show_plots = False # True if you want to show the plots, False if not
mag_map, loc_map, rup_map = getMappings()


#%% =========================================== QUERY DATA ===========================================
# Get the drifts, spectra and base shear dataframes for the selected simulation types, nsubs,
# iterations and stations
# -------------------------------------- Execyte the main query --------------------------------------
drifts_df_dict, spectra_df_dict, base_shear_df_dict = query.executeMainQuery(
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
    save_spectra = True,
    save_b_shear = True,
    save_results = save_csvs,
    # Plot params
    show_plots   = show_plots,
    xlim_sup     = 0.003, #0.025 NOTE: see how to put it as a tuple for x,y
    grid         = True,
    fig_size     = (8.25, 11),
    dpi          = 150,
    file_type    = 'pdf',
    # Extra params
    project_path = project_path,
    verbose      = False,
    )

winsound.Beep(1000, 500)
# --------------------------------------- LOAD DATA FOR ANOVA ----------------------------------------
# Spectra results:
max_spectra_lst_x = [(df.iloc[:,:5]).mean().max() for df in spectra_df_dict.values()]
max_spectra_lst_y = [(df.iloc[:,5:]).mean().max() for df in spectra_df_dict.values()]

## Base shear results:
#mean_base_shear_lst_x = [abs(df['Shear X'].mean()) for df in base_shear_df_dict.values()]
#mean_base_shear_lst_y = [abs(df['Shear Y'].mean()) for df in base_shear_df_dict.values()]


# %%
# Compute Drift Results
sim_type_lst  = [key.split('_')[0] for key in drifts_df_dict.keys()]
nsubs_lst     = [key.split('_')[1] for key in drifts_df_dict.keys()]
iteration_lst = [key.split('_')[4] for key in drifts_df_dict.keys()]
station_lst   = [key.split('_')[5] for key in drifts_df_dict.keys()]
drift_df_max_x  = getDriftResultsDF(sim_type_lst, nsubs_lst, iteration_lst, station_lst,
                                    [df['Max x'].max()  for df in drifts_df_dict.values()])
drift_df_max_y  = getDriftResultsDF(sim_type_lst, nsubs_lst, iteration_lst, station_lst,
                                    [df['Max y'].max()  for df in drifts_df_dict.values()])
drift_df_mean_x = getDriftResultsDF(sim_type_lst, nsubs_lst, iteration_lst, station_lst,
                                    [df['Max x'].mean() for df in drifts_df_dict.values()])
drift_df_mean_y = getDriftResultsDF(sim_type_lst, nsubs_lst, iteration_lst, station_lst,
                                    [df['Max y'].mean() for df in drifts_df_dict.values()])
drift_tple = (drifts_df_dict, drift_df_max_x, drift_df_max_y, drift_df_mean_x, drift_df_mean_y)

# Compute Spectra Results
sim_type_lst  = [key.split('_')[0] for key in spectra_df_dict.keys()]
nsubs_lst     = [key.split('_')[1] for key in spectra_df_dict.keys()]
iteration_lst = [key.split('_')[4] for key in spectra_df_dict.keys()]
station_lst   = [key.split('_')[5] for key in spectra_df_dict.keys()]
spectra_df    = getSpectraResultsDF(sim_type_lst, nsubs_lst, iteration_lst, station_lst,
                                    spectra_df_dict)

# Compute Base Shear Results
sim_type_lst  = [key.split('_')[0] for key in base_shear_df_dict.keys()]
nsubs_lst     = [key.split('_')[1] for key in base_shear_df_dict.keys()]
iteration_lst = [key.split('_')[4] for key in base_shear_df_dict.keys()]
station_lst   = [key.split('_')[5] for key in base_shear_df_dict.keys()]
base_shear_df = getSBaseResultsDF(sim_type_lst, nsubs_lst, iteration_lst, station_lst,
                                    base_shear_df_dict)

