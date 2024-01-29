# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
from pyseestko.db_functions import ModelSimulation                          # type: ignore
from pyseestko.utilities    import mapSimTypeID, getModelKeys, getBoxParams # type: ignore
from pathlib import Path

# ==================================================================================
# DEFINE INIT PARAMETERS
# ==================================================================================
# Init the SeismicSimulation class
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

# Define model simulation name keys parameters
project_path                      = Path(__file__)
sim_type, mag, rup, iter, station = getModelKeys(project_path)
st                                = mapSimTypeID(sim_type)
sim_keys                          = f'{sim_type}-{mag}-{rup}-{iter}-{station}'
box_comments , soil_mat_name,\
soil_ele_type, mesh_struct,\
vs30         , soil_dim           = getBoxParams(st, sim_keys)

# ==================================================================================
# DEFINE INIT PARAMETERS
# ==================================================================================
# Remember that the Db has a max lenght is 100 characters, all units are in kN/m/s
parameters = {
'sim_comments'      : f'Simulation:  {sim_keys}'                , # This value is the simulation comments
'sm_input_comments' : f'H5DRM Input: {sim_keys}'                , # This value is the input comments
'model_comments'    : f'Model:       {sim_keys}'                , # This value is the model comments
'bench_comments'    : f'1.25 mts spacing structured: {sim_keys}', # This value is the benchmark comments
'perf_comments'     : f'Performance metrics: {sim_keys}'        , # This value is the performance metrics comments
'str_specs_comments': f'Linear-elastic elements: {sim_keys}'    , # This value is the structural specs comments
'model_name'        : f'{sim_keys}'                             , # This value is the model name
'gspecs_comments'   : f'Global: {sim_keys}'                     , # This value is the global specs comments
'box_comments'      : box_comments                              , # This value is the soil box comments
'windows_os'        : True                                      , # This value is True if the OS is Windows, False if Linux
'sim_type'          : st                                        , # This value is the simulation type, 1=Fix Base, 2=Absorbing Boundaries, 3=DRM
'linearity'         : 1                                         , # This value is the linearity of the analysis, 1=Linear, 2=Nonlinear
'jump'              : 8                                         , # This value is the jumper between rows in the series, for example if a range has 10 values and jump=2, then the list will be [0,2,4,6,8]
'vs30'              : vs30                                      , # This value is the Vs30 of the soil in m/s
'soil_dim'          : soil_dim                                  , # Number of dimensions of the soil, our case is 3D
'soil_mat_name'     : soil_mat_name                             , # OpenSees Material name of the soil in the stko model
'soil_ele_type'     : soil_ele_type                             , # OpenSees Element type of the soil in the stko model
'mesh_struct'       : mesh_struct                               , # STKO Mesh element type
}

# Connect the model to the database
Model  = ModelSimulation(Path(__file__), **parameters)

# Conditions
upload_data = True
if upload_data:
    Model.simulation()

# Close the connection
Model.Manager.close_connection()
