#---------------------------------------------------------------------------------------
# INIT AND CONNECT TO DATABASE
#---------------------------------------------------------------------------------------
# Import modules
from sql_functions import ModelSimulation, Plotting
import json

# Init the SeismicSimulation class
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

# Press insert key and fill the parameters you want to change the default values.
parameters = {# Remember that the Db has a max lenght from:
             #Here   :                                      to here ->,
'bs_units'          : 'kN'                                           ,
'max_bs_units'      : 'kN'                                           ,
'rel_displ_units'   : 'm'                                            ,
'max_drift_units'   : 'm'                                            ,
'abs_acc_units'     : 'm/s/s'                                        ,
'pga_units'         : 'm/s/s'                                        ,
'resp_spectrum'     : 'm/s/s'                                        ,
'sim_comments'      : 'Test FixBase'                                ,
'sm_input_comments' : 'H5DRM Input record'                           ,
'model_comments'    : 'Model of FixBase Test 1'                     ,
'bench_comments'    : 'Model w/1.25 meter spacemenet structured mesh',
'perf_comments'     : 'Model with shear,displacement & acce metrics ',
'specs_comments'    : 'Model with linear-elastic-beam-column-shells ',
'clustername'       : 'Esmeralda cluster HPC Uandes by jaabel       ',
'model_name'        : 'FixBase Test01                  '            ,
'stage'             : 'Here it goes the simulation stage            ',
'options'           : 'Here it goes the simulation options          ',
'linearity'         : 1                                              ,
'sim_type'          : 1                                              ,
'fidelity'          : 0                                              ,
'windows_os'        : True                                           ,
'time_step'         : 0.0025                                         ,
'total_time'        : 40}

DataBase = ModelSimulation(**parameters)
DataBase.loadDataFrames()
DataBase.simulation()
DataBase.Manager.close_connection()


#---------------------------------------------------------------------------------------
# QUERY THE DRIFT PER FLOOR
#---------------------------------------------------------------------------------------
DataBase = ModelSimulation(**parameters)
cursor   = DataBase.Manager.cursor
query    = "SELECT * FROM structure_max_drift_per_floor "
cursor.execute(query)
data     = cursor.fetchall() # list of tuples, where every tuple is a row, where every value is a column
cursor.close()
simulation_id = -1

# Load the data
structure_max_drift_per_floor = data[simulation_id]
max_corner_x = json.loads(str(structure_max_drift_per_floor[1]))
max_corner_y = json.loads(str(structure_max_drift_per_floor[2]))
max_center_x = json.loads(str(structure_max_drift_per_floor[3]))
max_center_y = json.loads(str(structure_max_drift_per_floor[4]))

# Plot the data
save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Drift Outputs'
plotter = Plotting(DataBase, save_path)
ax = plotter.plotModelDrift(max_corner_x, max_center_x, max_corner_y, max_center_y)
# %%
