# ==================================================================================================
# ================================== INIT AND CONNECT TO DATABASE ==================================
# ==================================================================================================
# Import modules
from pyseestko.db_manager import DataBaseManager                     #type: ignore
from pyseestko.utilities  import NCh433_2012, initialize_ssh_tunnel, get_mappings #type: ignore
from pyseestko.plotting   import Plotting                            #type: ignore
from pathlib              import Path

import time
import pickle

# Init the SeismicSimulation class
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

# Connect the model to the database
initialize_ssh_tunnel()
time.sleep(1)
DataBase = DataBaseManager(user, password, host, database)
cursor   = DataBase.cursor
magnitude_mapping, location_mapping, ruptures_mapping = get_mappings()

linearity    = 1    # 1 = Linear, 2 = Non-Linear
sim_type     = 2    # 1 = FB,     2 = AB, 3 = DRM
magnitude    = 6.7  # Can be '6.5', '6.7', '6.9', '7.0', 0.0 for not defined
rupture_type = 1    # Can be 1 for 'bl', 2 for 'ns' or 3 for 'sn', put 0 for for not defined
station      = 0    # Can be any number from 0 to 9, -1 for not defined
stories      = 20   # For the moment, it can be 20 or 55
subs         = 4    # For the moment, it can be 2 or 4
plotter      = Plotting(sim_type, stories, magnitude, rupture_type, station)




# ===================================================================================================
# ==================================== QUERY THE DRIFT PER FLOOR ====================================
# ===================================================================================================
# Init the query
query = """
        SELECT drift.*
        FROM simulation sim
        JOIN simulation_sm_input           sminput  ON sim.idSM_Input            = sminput.IDSM_Input
        JOIN simulation_model              sm       ON sim.idModel 	         = sm.IDModel
        JOIN model_specs_structure         mss      ON sm.idSpecsStructure       = mss.IDSpecsStructure
        JOIN model_structure_perfomance    msp      ON sm.idStructuralPerfomance = msp.IDStructuralPerfomance
        JOIN structure_max_drift_per_floor drift    ON msp.idMaxDriftPerFloor    = drift.IDMaxDriftPerFloor
        WHERE sim.idType      = %s AND mss.idLinearity      = %s
        AND sminput.Magnitude = %s AND sminput.Rupture_Type = %s AND sminput.Location = %s AND mss.Nstories = %s
        AND mss.Nsubs = %s;
        """
cursor.execute(query, (sim_type, linearity, magnitude_mapping.get(magnitude), ruptures_mapping.get(rupture_type), location_mapping.get(station), stories, subs))
data = cursor.fetchall()

# Load the data
structure_max_drift_per_floor = data[0]
max_corner_x = pickle.loads(structure_max_drift_per_floor[1]) # type: ignore
max_corner_y = pickle.loads(structure_max_drift_per_floor[2]) # type: ignore
max_center_x = pickle.loads(structure_max_drift_per_floor[3]) # type: ignore
max_center_y = pickle.loads(structure_max_drift_per_floor[4]) # type: ignore

# Plot the data
save_path         = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Drift Outputs'
plotter.save_path = Path(save_path)
ax                = plotter.plotModelDrift(max_corner_x, max_center_x, max_corner_y, max_center_y)




# ===================================================================================================
# ===================================== QUERY THE STORY SPECTRUM ====================================
# ===================================================================================================
# Init the query
query = """
        SELECT msp.*
        FROM simulation sim
        JOIN simulation_sm_input           sminput 	ON sim.idSM_Input            = sminput.IDSM_Input
        JOIN simulation_model              sm           ON sim.idModel 	             = sm.IDModel
        JOIN model_specs_structure         mss          ON sm.idSpecsStructure       = mss.IDSpecsStructure
        JOIN model_structure_perfomance    msp 		ON sm.idStructuralPerfomance = msp.IDStructuralPerfomance
        WHERE sim.idType      = %s AND mss.idLinearity      = %s
        AND sminput.Magnitude = %s AND sminput.Rupture_Type = %s AND sminput.Location = %s AND mss.Nstories = %s;
        """
cursor.execute(query, (sim_type, linearity, magnitude_mapping.get(magnitude), ruptures_mapping.get(rupture_type), location_mapping.get(station), stories))
data = cursor.fetchall() # list of tuples, where every tuple is a row, where every value is a column

# Load the data
structure_perfomance = data[0]
accel_df       = pickle.loads(structure_perfomance[6]) # type: ignore
story_nodes_df = pickle.loads(structure_perfomance[7]) # type: ignore

# Plot the data
stories_lst       = [1,5,10,15,20]
save_path         = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Input Spectrums'
plotter.save_path = Path(save_path)
ax                = plotter.plotLocalStoriesSpectrums(accel_df, story_nodes_df, 'x', stories_lst, soften=True)




# ===================================================================================================
# ======================================= QUERY THE BASE SHEAR ======================================
# ===================================================================================================
query = """
        SELECT sbs.*
        FROM simulation sim
        JOIN simulation_sm_input        sminput ON sim.idSM_Input 	     = sminput.IDSM_Input
        JOIN simulation_model           sm      ON sim.idModel 		     = sm.IDModel
        JOIN model_specs_structure      mss     ON sm.idSpecsStructure       = mss.IDSpecsStructure
        JOIN model_structure_perfomance msp 	ON sm.idStructuralPerfomance = msp.IDStructuralPerfomance
        JOIN structure_base_shear       sbs     ON msp.idBaseShear           = sbs.IDBaseShear
        WHERE sim.idType      = %s AND mss.idLinearity      = %s
        AND sminput.Magnitude = %s AND sminput.Rupture_Type = %s AND sminput.Location = %s AND mss.Nstories = %s;
        """
cursor.execute(query, (sim_type, linearity, magnitude_mapping.get(magnitude), ruptures_mapping.get(rupture_type), location_mapping.get(station), stories))
data = cursor.fetchall() # list of tuples, where every tuple is a row, where every value is a column

# Load the data
base_shear_over_time = data[0]
time_series = pickle.loads(base_shear_over_time[1]) # type: ignore
shear_x     = pickle.loads(base_shear_over_time[2]) # type: ignore
shear_y     = pickle.loads(base_shear_over_time[3]) # type: ignore
shear_z     = pickle.loads(base_shear_over_time[4]) # type: ignore

# Plot the data
zone             = 'Las Condes'
direction        = 'x'
soil_category    = 'B'
importance       = 2
structure_weight = 37134.5 # kN
nch              = NCh433_2012(zone, soil_category, importance)
Qmin             = nch.computeMinBaseShear_c6_3_7_1(structure_weight)
Qmax             = nch.computeMaxBaseShear_c6_3_7_2(structure_weight)

save_path         = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Base Shear Over Time'
plotter.save_path = Path(save_path)
ax = plotter.plotShearBaseOverTime(time_series, shear_x, Qmin, Qmax, 'x')




# ===================================================================================================
# =========================================== END QUERIES ===========================================
# ===================================================================================================
DataBase.close_connection()
