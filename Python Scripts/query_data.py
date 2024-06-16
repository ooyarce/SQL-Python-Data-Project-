#%% ================================== INIT AND CONNECT TO DATABASE ==================================
# Import modules
from pyseestko.utilities  import getMappings, load_module     #type: ignore
from pyseestko            import queries as query #type: ignore
from matplotlib           import pyplot  as plt
from pathlib              import Path
from pyseestko.utilities  import getDriftResultsDF      #type: ignore
from pyseestko.utilities  import getSpectraResultsDF    #type: ignore
from pyseestko.utilities  import getSBaseResultsDF      #type: ignore
from pyseestko.utilities  import assignZonesToStationsInDF      #type: ignore
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
    save_drift   = False,
    save_spectra = False,
    save_b_shear = False,
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


# %%
# ----------------------------------------------------------------------------------------------------
# --------------------------------------- LOAD DATA FOR ANOVA ----------------------------------------
# ----------------------------------------------------------------------------------------------------
# --------------------------------------- DRIFT ----------------------------------------
# Compute Drift Results
if all(isinstance(value, pd.DataFrame) for value in drifts_df_dict.values()):
    drift_df_x, drift_df_y = getDriftResultsDF(drifts_df_dict)
else:
    drift_df_x = pd.read_csv(project_path / 'drift_per_story_X_df.csv', index_col=0)
    drift_df_y = pd.read_csv(project_path / 'drift_per_story_Y_df.csv', index_col=0)

#%% Compute Spectra Results
# --------------------------------------- SPECTRUM ----------------------------------------
# We will have the acceleration at the period equal to mode 3 = 0.83s
if all(isinstance(value, pd.DataFrame) for value in spectra_df_dict.values()):
    spectra_df_x, spectra_df_y = getSpectraResultsDF(spectra_df_dict)

else:
    spectra_df_x = pd.read_csv(project_path / 'spectra_per_story_X_df.csv', index_col=0)
    spectra_df_y = pd.read_csv(project_path / 'spectra_per_story_Y_df.csv', index_col=0)

#%% Compute Base Shear Results
# --------------------------------------- BASE SHEAR ----------------------------------------
if all(isinstance(value, pd.DataFrame) for value in base_shear_df_dict.values()):
    base_shear_df_x, base_shear_df_y = getSBaseResultsDF(base_shear_df_dict)
else:
    base_shear_df_x = pd.read_csv(project_path / 'max_base_shear_X_df.csv', index_col=0)
    base_shear_df_y = pd.read_csv(project_path / 'max_base_shear_Y_df.csv', index_col=0)

# %% ========================================== ANOVA ==========================================

