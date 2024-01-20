# ==================================================================================================
# ================================== INIT AND CONNECT TO DATABASE ==================================
# ==================================================================================================
"""
THE DEFAULT INPUT PARAMETERS FOR THE CURRENT MODEL SIMULATION ARE THE FOLLOWING:

        # Simulation default parameters
        "sim_comments"     : "No comments"
        "sim_opt"          : "No options yet"
        "sim_stage"        : "No stage yet"
        "sm_input_comments": "No comments"
        "model_comments"   : "No comments"
        "bench_comments"   : "No comments"
        "perf_comments"    : "No comments"
        "specs_comments"   : "No comments"
        "box_comments"     : "No comments"
        "gspecs_comments"  : "No comments"
        "pga_units"        : "m/s/s"
        "resp_spectrum"    : "m/s/s"
        "abs_acc_units"    : "m/s/s"
        "rel_displ_units"  : "m"
        "max_drift_units"  : "m"
        "max_bs_units"     : "kN"
        "bs_units"         : "kN"
        "linearity"        : 1      # This value is the linearity of the analysis, 1=Linear, 2=Nonlinear
        "time_step"        : 0.0025 # This value is the time step of the analysis
        "total_time"       : 40     # This value is the total time of the analysis
        "jump"             : 8      # This value is the jumper between rows in the series, for example if a range has 10 values and jump=2, then the list will be [0,2,4,6,8]
        "cfactor"          : 1.0    # Value to increase the input acceleration; usefull when change in units is needed
        "load_df_info"     : True
        'soil_dim'         : 'Dimentions'
        'soil_mat_name     : 'Material
        "soil_ele_type     : 'Element type'
        'vs30'             : '750' # This value is the Vs30 of the soil in m/s
        'mesh_struct'      : 'Structured mesh'
"""

# Import modules
from sql_functions import ModelSimulation, mapSimTypeID, getModelKeys
from pathlib import Path

# Init the SeismicSimulation class
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

# Define model simulation name keys parameters
project_path = Path(__file__)
sim_type, mag, rup, iter, station = getModelKeys(project_path)
st = mapSimTypeID(sim_type)

# Remember that the Db has a max lenght is 100 characters, all units are in kN/m/s
sim_keys = f'{sim_type}-{mag}-{rup}-{iter}-{station}'
parameters = {
'sim_comments'      : f'Simulation:  {sim_keys}'                , # This value is the simulation comments
'sm_input_comments' : f'H5DRM Input: {sim_keys}'                , # This value is the input comments
'model_comments'    : f'Model:       {sim_keys}'                , # This value is the model comments
'bench_comments'    : f'1.25 mts spacing structured: {sim_keys}', # This value is the benchmark comments
'perf_comments'     : f'Performance metrics: {sim_keys}'        , # This value is the performance metrics comments
'str_specs_comments': f'Linear-elastic elements: {sim_keys}'    , # This value is the structural specs comments
'model_name'        : f'{sim_keys}'                             , # This value is the model name
'box_comments'      : f'Box: {sim_keys}'                        , # This value is the box comments
'gspecs_comments'   : f'Global: {sim_keys}'                     , # This value is the ground motion specs comments
'windows_os'        : True                                      , # This value is True if the OS is Windows, False if Linux
'sim_type'          : 1                                         , # This value is the simulation type, 1=Fix Base, 2=Absorbing Boundaries, 3=DRM
'linearity'         : 1                                         , # This value is the linearity of the analysis, 1=Linear, 2=Nonlinear
'jump'              : 8                                         , # This value is the jumper between rows in the series, for example if a range has 10 values and jump=2, then the list will be [0,2,4,6,8]
'vs30'              : 750                                       , # This value is the Vs30 of the soil in m/s
'soil_dim'          : 3                                         , # Number of dimensions of the soil, our case is 3D
'soil_mat_name'     : 'Elastoisotropic'                         , # OpenSees Material name of the soil in the stko model
'soil_ele_type'     : 'SSPBrick Element'                        , # OpenSees Element type of the soil in the stko model
'mesh_struct'       : 'Structured Quad Elem by 1.25 meters'     , # STKO Mesh element type
}

# Connect the model to the database
Model  = ModelSimulation(**parameters)

# Upload the data to the database, for the first time or not
upload_data      = True

# Conditions
if upload_data:
    Model.simulation()



