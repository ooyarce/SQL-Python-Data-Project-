from pathlib import Path
from pyseestko import utilities as pyutl # type: ignore

# Define the path to the main_sql.py file
new_main_sql_path = Path("C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/Python Scripts/main_sql.py")

# DEfube los tipos de simulación, estructuras, iteraciones de ruptura y estaciones
sim_types        = ['FixBase', 'AbsBound', 'DRM']         # Options are 'FixBase', 'AbsBound', 'DRM' and 'Validations 
structure_types  = ['20f2s', '20f4s']                     # Options are '20f2s', '20f4s' 
rupture_iters    = [i for i in range(1, 4) ]              # Options are 'bl', 'ns', 'sn' and iter in range(11)
stations         = [f'station_s{i}' for i in range(0,9)]  # Generate a list of stations from 'station_s0' to 'station_s8'

# Directorio raíz donde se encuentran los tipos de simulación
root_path = Path(__file__).parent
files_to_delete =['analysis_steps.tcl','elements.tcl', 'main.tcl', 'materials.tcl', 'nodes.tcl', 'sections.tcl',
                  '*.mpco'            ,'*.mpco.cdata',
                  'import_h5py.py'    ,'input.h5drm']
# Iterate over the simulation types
pyutl.run_main_sql_simulations(
    root_path         = root_path,
    new_main_sql_path = new_main_sql_path,
    sim_types         = sim_types,
    structure_types   = structure_types,
    rupture_iters     = rupture_iters,
    stations          = stations,
    files_to_delete   = files_to_delete)