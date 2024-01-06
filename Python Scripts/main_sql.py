#!/usr/bin/env python3
#TODO: FIND HOW TO AUTOMATIZE THE GENERATION OF THE PARAMETERS DICT
#TODO: THE IDEA BEHIND IS TO MAKE A MAIN WHERE YOU CAN GIVE SHELL PARAMS AND A CERTAIN JSON DICT TO LOAD
#TODO: (THE JSON DICT IS THE ONE THAT CONTAINS THE PARAMETERS OF THE MODEL SUCH AS FOLLOWING).
#TODO: SO, YOU WILL HAVE 3 TYPES OF JSON DICTS, ONE FOR THE FIX BASE, ANOTHER FOR THE ABS BOUND AND ANOTHER FOR THE DRM
#TODO: THE UNIQUE PARAMS OF THE DICT FOREACH TYPE OF JSON DICT, ARE model_name, SO THEN YOU CAN QUERY THE DATA FROM THE DB
#TODO: BASED ON THE model_name VALUE.
#TODO: SEE HOW TO SEPARATE THE MAIN FROM THE SQL QUERIES, SO YOU CAN USE THE SQL QUERIES IN OTHER MAINS.

#TODO: SEE HOW TO RECONECT TO THE DATABASE AFTER UPLOADING THE RESULTS, MAYBE YOU DONT HAVE TO DISCONECT FROM DATABASE
# ==================================================================================================
# ================================== INIT AND CONNECT TO DATABASE ==================================
# ==================================================================================================
# Import modules
from sql_functions import ModelSimulation, Plotting
import numpy as np
import pickle

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
'sim_comments'      : 'Test AbsBound'                                ,
'sm_input_comments' : 'H5DRM Input record'                           ,
'model_comments'    : 'Model of AbsBound Test 1'                     ,
'bench_comments'    : 'Model w/1.25 meter spacemenet structured mesh',
'perf_comments'     : 'Model with shear,displacement & acce metrics ',
'specs_comments'    : 'Model with linear-elastic-beam-column-shells ',
'clustername'       : 'Esmeralda cluster HPC Uandes by jaabel       ',
'model_name'        : 'AbsBound Test01                  '            ,
'stage'             : 'Here it goes the simulation stage            ',
'options'           : 'Here it goes the simulation options          ',
'linearity'         : 1                                              , # This value is the linearity of the analysis, 1=Linear, 2=Nonlinear
'jump'              : 8                                              , # This value is the jumper between rows in the series, for example if a list has 10 values and jump=2, then the list will be [0,2,4,6,8]
'sim_type'          : 1                                              , # This value is the simulation type, 1=Fix Base, 2=Absorbing Boundaries, 3=DRM
'windows_os'        : True                                           , # This value is True if the OS is Windows, False if Linux
'time_step'         : 0.0025                                         , # This value is the time step of the analysis
'total_time'        : 40                                               # This value is the total time of the analysis
}

# Connect the model to the database
Model = ModelSimulation(**parameters)

# Upload the data to the database, for the first time or not
first_time       = False
upload_data      = True

# Query the data from the database
query_drift         = False
query_input_spectra = False
query_story_spectra = False
query_base_spectra  = False
query_time_shear    = True

# Conditions
if first_time:
    Model.model_linearity()
    Model.simulation_type()
if upload_data:
    Model.simulation()


cursor   = Model.Manager.cursor
# ===================================================================================================
# ==================================== QUERY THE DRIFT PER FLOOR ====================================
# ====================================================================================================
if query_drift:
    query    = "SELECT * FROM structure_max_drift_per_floor "
    cursor.execute(query)
    data     = cursor.fetchall() # list of tuples, where every tuple is a row, where every value is a column
    simulation_id = -1

    # Load the data
    structure_max_drift_per_floor = data[simulation_id]
    max_corner_x = pickle.loads(structure_max_drift_per_floor[1]) # type: ignore
    max_corner_y = pickle.loads(structure_max_drift_per_floor[2]) # type: ignore
    max_center_x = pickle.loads(structure_max_drift_per_floor[3]) # type: ignore
    max_center_y = pickle.loads(structure_max_drift_per_floor[4]) # type: ignore

    # Plot the data
    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Drift Outputs'
    plotter = Plotting(Model, save_path)
    ax = plotter.plotModelDrift(max_corner_x, max_center_x, max_corner_y, max_center_y)


# ===================================================================================================
# ==================================== QUERY THE INPUT SPECTRUM =====================================
# ====================================================================================================
if query_input_spectra:
    #cursor   = Model.Manager.cursor
    query    = "SELECT * FROM sm_input_spectrum "
    cursor.execute(query)
    data     = cursor.fetchall() # list of tuples, where every tuple is a row, where every value is a column
    simulation_id = -1

    # Load the data
    sm_input_spectrum = data[simulation_id]
    spectrum_x = pickle.loads(sm_input_spectrum[1]) # type: ignore
    spectrum_y = pickle.loads(sm_input_spectrum[2]) # type: ignore
    spectrum_z = pickle.loads(sm_input_spectrum[3]) # type: ignore


    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Input Spectrums'
    plotter = Plotting(Model, save_path)
    ax = plotter.plotModelSpectrum(spectrum_x, spectrum_y, spectrum_z, plotNCh433=False)

#FIXME: THIS IS MADE BY LOCAL MODEL DATA, YOU SHOULD DO THIS VIA A QUERY(abs_accelerations table)
# ===================================================================================================
# ===================================== LOCAL STRUCTURE SPECTRUM ====================================
# ===================================================================================================
stories_df = Model.story_nodes_df.iloc[8:] # Get df with nodes from story 0 to roof
accel_df   = Model.accel_mdf
T = np.linspace(0.003, 2.5, 1000)
spectrum_modes = [2.16, 1.44, 0.83, 0.46, 0.36, 0.29]
if query_story_spectra:
    # Input data
    stories_lst = [5,10,20]
    dirs_lst    = ['x', 'y', 'z']

    # Plotting story spectrums
    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Story Spectrums'
    for dir_ in dirs_lst:
        plotter = Plotting(Model, save_path)
        plotter.plotLocalStoriesSpectrums(Model, dir_, accel_df, stories_df, stories_lst, T)

if query_base_spectra:
    # Plotting the base spectrum
    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Base Spectrums'
    plotter = Plotting(Model, save_path)
    plotter.plotLocalBaseSpectrum(Model, accel_df, stories_df, T, spectrum_modes, plot_z=False)

# ===================================================================================================
# ===================================== QUERY STRUCTURE SPECTRUM ====================================
# ===================================================================================================




#FIXME: THIS IS MADE BY LOCAL MODEL DATA, YOU SHOULD DO THIS VIA A QUERY(shear base table)
# ====================================================================================================
# ================================= QUERY THE TIME-SERIES SHEAR BASE =================================
# =====================================================================================================
if query_time_shear:
    # Data for plots
    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Base Shear Over Time'
    time_shear_x_fma = Model._computeBaseShearByAccelerations()[0][0]
    time_shear_y_fma = Model._computeBaseShearByAccelerations()[0][1]

    reactions_df = Model.react_mdf.sum(axis=1)
    matrixes     = [reactions_df.xs(dir, level='Dir') for dir in ['x', 'y']]
    time_shear_x_react = matrixes[0]
    time_shear_y_react = matrixes[1]
    time = Model.timeseries

    # Plot X
    plotter = Plotting(Model, save_path)
    ax      = plotter.plotLocalShearBaseOverTime(time, time_shear_x_fma, time_shear_x_react, 'x')

    # Plot Y
    plotter = Plotting(Model, save_path)
    ax      = plotter.plotLocalShearBaseOverTime(time, time_shear_y_fma, time_shear_y_react, 'y')


