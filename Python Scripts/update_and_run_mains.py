#%% ================================================================================
# IMPORT MODULES
# ==================================================================================
from pathlib import Path
from pyseestko import utilities as pyutl # type: ignore

#%% ================================================================================
# DEFINE INIT PARAMETERS
# ==================================================================================
# Define new_main_sql_path

# Define the simulation types, structure types, rupture iterations and stations
sim_types        = ['DRM']         # Options are 'FixBase', 'AbsBound', 'DRM' and 'Validations 
structure_types  = ['20f4s']                     # Options are '20f2s', '20f4s' 
rupture_iters    = [i for i in range(10, 11) ]              # Options are 'bl', 'ns', 'sn' and iter in range(11)
stations         = [f'station_s{i}' for i in range(0,9)]  # Generate a list of stations from 'station_s0' to 'station_s8'
Validate         = True

# Define the root path and the files to delete
if Validate:
    new_main_sql_path = "D:/Universidad/Tesis/FondeCyT-DataBase/Results_Analysis/Validations/DRM/20f4s/m6.7/rup_bl_1/station_s0/main_sql.py"
    root_path = Path(__file__).parent / 'Validations'
else:
    new_main_sql_path = "C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/Python Scripts/main_sql.py"
    root_path = Path(__file__).parent 

# Define the files to delete
files_to_delete =['analysis_steps.tcl','elements.tcl', 'main.tcl', 'materials.tcl', 'nodes.tcl', 'sections.tcl',
                  '*.mpco'            ,'*.mpco.cdata',
                  'import_h5py.py'    ,'input.h5drm']

#%% ================================================================================
# RUN ALL MAINS
# ==================================================================================
# Iterate over the simulation types
pyutl.run_main_sql_simulations(
    root_path         = root_path,
    new_main_sql_path = new_main_sql_path,
    sim_types         = sim_types,
    structure_types   = structure_types,
    rupture_iters     = rupture_iters,
    stations          = stations,
    files_to_delete   = files_to_delete)
# %%
