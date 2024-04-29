# ==================================================================================================
# ================================== INIT AND CONNECT TO DATABASE ==================================
# ==================================================================================================
# Import modules
from pyseestko.db_manager import DataBaseManager
from pyseestko.plotting   import Plotting                  #type: ignore
import numpy as np
import pickle

# Init the SeismicSimulation class
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

Model = DataBaseManager
# Connect the model to the database
cursor   = Model.Manager.cursor

# Query the data from the database
query_drift         = True
query_input_spectra = False
query_story_spectra = False
query_base_spectra  = False
query_time_shear    = False

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







