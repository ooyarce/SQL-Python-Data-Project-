# ==================================================================================================
# ================================== INIT AND CONNECT TO DATABASE ==================================
# ==================================================================================================
# Import modules
from pyseestko.queries    import ProjectQueries            #type: ignore
from pyseestko.utilities  import get_mappings #type: ignore
from pyseestko.plotting   import Plotting                  #type: ignore

# DataBase user params
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

# Init Parameters
"""
sim_types: 1 = FB, 2 = AB, 3 = DRM
linearity: 1 = Linear, 2 = Non-Linear
magnitude: Can be '6.5', '6.7', '6.9', '7.0', 0.0 for not defined
rupture_type: Can be 1 for 'bl', 2 for 'ns' or 3 for 'sn', put 0 for for not defined
stations: Can be any number from 0 to 9, -1 for not defined
stories: For the moment, it can be 20 or 55
nsubs_lst: For the moment, it can be 2 or 4
"""
magnitude    = 6.7      # Constant
rupture_type = 1        # Constant       
linearity    = 1        # Constant
stories      = 20       # Constant      
nsubs_lst    = [4]      # 2,4
sim_types    = [3]      # 1 = FB, 2 = AB, 3 = DRM
iterations   = [1,2]#,4,5,6,7,8,9,10]      # 1,2,3,4,5,6,7,8,9,10
stations     = [0,1,2,3,4,5,6,7,8,9]
mag_map, loc_map, rup_map = get_mappings()

# Define paths to save the plots
save_drift       = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Drift Outputs'
save_spectra     = None#'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Story Spectra Output'
save_b_shear     = None#'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Base Shear Output'
structure_weight = 24531.7 # kN
zone             = 'Las Condes'
soil_category    = 'B'
importance       = 2
windows          = True # True if the OS is Windows, False if Linux
# Iterate over the subs, then over the sim_type and then over the stations so we can get all the results
for sim_type in sim_types:
    for station in stations:
        for iteration in iterations:
            for nsubs in nsubs_lst:
                # Init the classes
                plotter = Plotting(sim_type, stories,                    # The class that plots the data
                                   nsubs, magnitude,
                                   iteration, rupture_type,
                                   station)
                query   = ProjectQueries(user, password, host, database, # The class that queries the database
                                        sim_type, linearity,
                                        mag_map.get(magnitude,    'None'),
                                        rup_map.get(rupture_type, 'None'), iteration,
                                        loc_map.get(station,      'None'),
                                        stories, nsubs, plotter, windows=windows)
                query.getAllResults(save_drift, save_spectra, save_b_shear, structure_weight, zone, soil_category, importance)




