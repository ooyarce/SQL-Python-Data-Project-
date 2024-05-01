# ==================================================================================================
# ================================== INIT AND CONNECT TO DATABASE ==================================
# ==================================================================================================
# Import modules
from pyseestko.utilities  import get_mappings              #type: ignore
from pyseestko.queries    import executeMainQuery          #type: ignore

# DataBase user params
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'


# ==================================================================================================
# ========================================== INPUT PARAMS ==========================================
# ==================================================================================================
"""
sim_types: 1 = FB, 2 = AB, 3 = DRM
linearity: 1 = Linear, 2 = Non-Linear
magnitude: Can be '6.5', '6.7', '6.9', '7.0', 0.0 for not defined
rupture_type: Can be 1 for 'bl', 2 for 'ns' or 3 for 'sn', put 0 for for not defined
stations: Can be any number from 0 to 9, -1 for not defined
stories: For the moment, it can be 20 or 55
nsubs_lst: For the moment, it can be 2 or 4
"""
# Define the parameters
sim_types    = [i for i in range(3,4)]  # 1 = FB, 2 = AB, 3 = DRM
nsubs_lst    = [i for i in range(4,5)]  # Can be: 2,4
iterations   = [i for i in range(1,11)] # Can be: {1,2,3,4,5,6,7,8,9,10}
stations     = [i for i in range(0,1)]  # Can be: {0,1,2,3,4,5,6,7,8,9 }

# Define paths to save the plots
save_drift       = None #'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Drift Outputs'
save_spectra     = None #'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Story Spectra Output'
save_b_shear     = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Base Shear Output'
windows          = True # True if the OS is Windows, False if Linux
mag_map, loc_map, rup_map = get_mappings()


# ==================================================================================================
# =========================================== QUERY DATA ===========================================
# ==================================================================================================
drifts_df_lst, spectra_df_lst, base_shear_df_lst = executeMainQuery(
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



