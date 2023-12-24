#%% INIT AND CONNECT TO DATABASE ==================================================================
# INIT AND CONNECT TO DATABASE
#==================================================================================================
# Import modules
from sql_functions import ModelSimulation, Plotting
import numpy as np
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
'sim_comments'      : 'Test FixBase'                                 ,
'sm_input_comments' : 'H5DRM Input record'                           ,
'model_comments'    : 'Model of FixBase Test 1'                      ,
'bench_comments'    : 'Model w/1.25 meter spacemenet structured mesh',
'perf_comments'     : 'Model with shear,displacement & acce metrics ',
'specs_comments'    : 'Model with linear-elastic-beam-column-shells ',
'clustername'       : 'Esmeralda cluster HPC Uandes by jaabel       ',
'model_name'        : 'FixBase Test01                  '             ,
'stage'             : 'Here it goes the simulation stage            ',
'options'           : 'Here it goes the simulation options          ',
'linearity'         : 1                                              ,
'sim_type'          : 1                                              ,
'windows_os'        : True                                           ,
'time_step'         : 0.0025                                         ,
'total_time'        : 40
}

# Connect the model to the database
DataBase = ModelSimulation(**parameters)

# Upload the data to the database, for the first time or not
first_time       = False
upload_data      = True

# Query the data from the database
query_drift         = True
query_input_spectra = True
query_story_spectra = True
query_base_spectra  = True
query_time_shear    = True

# Conditions
if first_time:
    DataBase.model_linearity()
    DataBase.simulation_type()
if upload_data:
    DataBase.simulation()
    DataBase.Manager.close_connection()

#%% QUERY THE DRIFT PER FLOOR =====================================================================
# QUERY THE DRIFT PER FLOOR
#==================================================================================================
DataBase = ModelSimulation(**parameters)
if query_drift:
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


#%% QUERY THE INPUT SPECTRUM ========================================================================
# QUERY THE INPUT SPECTRUM
#==================================================================================================
DataBase = ModelSimulation(**parameters)
if query_input_spectra:
    cursor   = DataBase.Manager.cursor
    query    = "SELECT * FROM sm_input_spectrum "
    cursor.execute(query)
    data     = cursor.fetchall() # list of tuples, where every tuple is a row, where every value is a column
    cursor.close()
    simulation_id = -1

    # Load the data
    sm_input_spectrum = data[simulation_id]
    spectrum_x = json.loads(str(sm_input_spectrum[1]))
    spectrum_y = json.loads(str(sm_input_spectrum[2]))
    spectrum_z = json.loads(str(sm_input_spectrum[3]))


    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Input Spectrums'
    plotter = Plotting(DataBase, save_path)
    ax = plotter.plotModelSpectrum(spectrum_x, spectrum_y, spectrum_z, plotNCh433=False)


#%% QUERY STRUCTURE SPECTRUM ========================================================================
# QUERY STRUCTURE SPECTRUM
#====================================================================================================
DataBase = ModelSimulation(**parameters)
stories_df = DataBase.story_nodes_df.iloc[8:] # Get df with nodes from story 0 to roof
accel_df   = DataBase.accel_mdf
T = np.linspace(0.003, 2.5, 1000)
spectrum_modes = [2.16, 1.44, 0.83, 0.46, 0.36, 0.29]
if query_story_spectra:
    # Input data
    stories_lst = [5,10,20]
    dirs_lst    = ['x', 'y', 'z']

    # Plotting story spectrums
    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Story Spectrums'
    for dir_ in dirs_lst:
        plotter = Plotting(DataBase, save_path)
        plotter.plotStoriesSpectrums(DataBase, dir_, accel_df, stories_df, stories_lst, T)

if query_base_spectra:
    # Plotting the base spectrum
    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Base Spectrums'
    plotter = Plotting(DataBase, save_path)
    plotter.plotBaseSpectrum(DataBase, accel_df, stories_df, T, spectrum_modes, plot_z=False)

    # Create a dataframe with: index= modes 1,...6


#%% QUERY THE TIME-SERIES SHEAR BASE ================================================================
# QUERY THE TIME-SERIES SHEAR BASE
#====================================================================================================
if query_time_shear:
    # Data for plots
    save_path = 'C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs/Base Shear Over Time'
    time_shear_x_fma = DataBase._computeBaseShearByAccelerations()[0][0]
    time_shear_y_fma = DataBase._computeBaseShearByAccelerations()[0][1]

    reactions_df = DataBase.react_mdf.sum(axis=1)
    matrixes     = [reactions_df.xs(dir, level='Dir') for dir in ['x', 'y']]
    time_shear_x_react = matrixes[0]
    time_shear_y_react = matrixes[1]
    time = DataBase.timeseries

    # Plot X
    plotter = Plotting(DataBase, save_path)
    ax      = plotter.plotShearBaseOverTime(time, time_shear_x_fma, time_shear_x_react, 'x')

    # Plot Y
    plotter = Plotting(DataBase, save_path)
    ax      = plotter.plotShearBaseOverTime(time, time_shear_y_fma, time_shear_y_react, 'y')


#%% ADITIONAL NOTATIONS ===========================================================================
# ADITIONAL NOTATIONS
#==================================================================================================
#TODO: PLOTEAR ESPECTRO MÁXIMO, ESPECTRO MÍNIMO PROMEDIO DE TODOS LOS PISOS
#TODO: ENVIAR EL GRAFICO CON LOS 3 PRIMEROS MODOS, ENVIAR TABLAS DE MASAS, OJO CON LOS TRES PRIMEROS MODOS
#TODO: Me hace ruido que tengamos muy altos drift con mucha masa traslacional con los primeros 3 modos moviendo el 55% en cada eje
#TODO:
