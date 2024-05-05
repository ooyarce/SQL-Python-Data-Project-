#%% ==================================================================================================
# ================================== INIT AND CONNECT TO DATABASE ==================================
# ==================================================================================================
# Import modules   
from pyseestko.utilities  import getMappings, getCSVNames, save_df_to_csv_paths  #type: ignore
from pyseestko import queries as query                     #type: ignore
from pathlib import Path

# DataBase user params
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'


#%% ==================================================================================================
# ========================================== INPUT PARAMS ==========================================
# ==================================================================================================
# Define paths to save the plots
project_path     = Path('C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/')
save_drift       = project_path / 'DataBase-Outputs' / 'Drift Outputs'
save_spectra     = project_path / 'DataBase-Outputs' / 'Story Spectra Output'
save_b_shear     = project_path / 'DataBase-Outputs' / 'Base Shear Output'
save_csv_drift   = project_path / 'DataBase-Outputs' / 'Analysis Output' / 'CSV' / 'Drift'
save_csv_spectra = project_path / 'DataBase-Outputs' / 'Analysis Output' / 'CSV' / 'Spectra'
save_csv_b_shear = project_path / 'DataBase-Outputs' / 'Analysis Output' / 'CSV' / 'Base Shear'

# Define the parameters
sim_types    = [i for i in range(1,4)]  # 1 = FB, 2 = AB, 3 = DRM
nsubs_lst    = [2, 4]                   # Can be: 2,4  
iterations   = [i for i in range(1,3)]  # Can be: {1,2,3,4,5,6,7,8,9,10}
stations     = [i for i in range(0,10)] # Can be: {0,1,2,3,4,5,6,7,8,9 }

# Some extra parameters
windows      = True  # True if the OS is Windows, False if Linux
save_results = False # True if you want to save the results, False if not
mag_map, loc_map, rup_map = getMappings()
sim_csv_names_lst         = getCSVNames(sim_types, nsubs_lst, iterations, stations)


#%% ==================================================================================================
# =========================================== QUERY DATA ===========================================
# ==================================================================================================
drifts_df_lst, spectra_df_lst, base_shear_df_lst = query.executeMainQuery(
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
    save_drift   = save_drift, 
    save_spectra = save_spectra, 
    save_b_shear = save_b_shear)

# Backup the dataframes of drifts, spectra and base shear into folders and csv
if save_results:
    save_df_to_csv_paths(
        drifts_df_lst     = drifts_df_lst, 
        spectra_df_lst    = spectra_df_lst, 
        base_shear_df_lst = base_shear_df_lst, 
        csv_names_lst     = sim_csv_names_lst,
        save_csv_drift    = save_csv_drift,
        save_csv_spectra  = save_csv_spectra,
        save_csv_b_shear  = save_csv_b_shear)
