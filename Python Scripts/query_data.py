#%% ================================== INIT AND CONNECT TO DATABASE ==================================
# Import modules
from pyseestko.utilities  import getMappings, load_module     #type: ignore
from pyseestko            import queries as query #type: ignore
from matplotlib           import pyplot  as plt
from pathlib              import Path
from pyseestko.utilities  import getDriftResultsDF      #type: ignore
from pyseestko.utilities  import getSpectraResultsDF    #type: ignore
from pyseestko.utilities  import getSBaseResultsDF      #type: ignore
from pyseestko.utilities  import assignZonesToStationsInDF      #type: ignore
# Temp imports
import pandas as pd
import winsound


# DataBase user params
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

# Debugging
path_to_queries = Path("C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/Python Scripts/PySeesTKO/pyseestko/queries.py")
#query = load_module('query', path_to_queries)

#%% ========================================== INPUT PARAMS ==========================================
# Define paths to save the plots
project_path = Path('C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs')

# Define the parameters
sim_types  = [i for i in range(1,4)]   # 1 = FB, 2 = AB, 3 = DRM
nsubs_lst  = [2,4]                     # Can be: 2,4
iterations = [i for i in range(1,6)]   # Can be: {1,2,3,4,5,6,7,8,9,10}
stations   = [i for i in range(1,10)]  # Can be: {0,1,2,3,4,5,6,7,8,9}

# Some extra parameters
windows    = True  # True if the OS is Windows, False if Linux
save_csvs  = False # True if you want to save the results, False if not
show_plots = False # True if you want to show the plots, False if not
mag_map, loc_map, rup_map = getMappings()


#%% =========================================== QUERY DATA ===========================================
# Get the drifts, spectra and base shear dataframes for the selected simulation types, nsubs,
# iterations and stations
# -------------------------------------- Execyte the main query --------------------------------------
drifts_df_dict, spectra_df_dict, base_shear_df_dict = query.executeMainQuery(
    # Main params
    sim_types    = sim_types,
    nsubs_lst    = nsubs_lst,
    iterations   = iterations,
    stations     = stations,
    mag_map      = mag_map,
    loc_map      = loc_map,
    rup_map      = rup_map,
    # DataBase params
    user         = user,
    password     = password,
    host         = host,
    database     = database,
    # Save params
    save_drift   = False,
    save_spectra = False,
    save_b_shear = True,
    save_results = save_csvs,
    # Plot params
    show_plots   = show_plots,
    xlim_sup     = 0.003, #0.025 NOTE: see how to put it as a tuple for x,y
    grid         = True,
    fig_size     = (8.25, 11),
    dpi          = 150,
    file_type    = 'pdf',
    # Extra params
    project_path = project_path,
    verbose      = False,
    )

winsound.Beep(1000, 500)


# %%
# ----------------------------------------------------------------------------------------------------
# --------------------------------------- LOAD DATA FOR ANOVA ----------------------------------------
# ----------------------------------------------------------------------------------------------------
# --------------------------------------- DRIFT ----------------------------------------
# Compute Drift Results
if all(isinstance(value, pd.DataFrame) for value in drifts_df_dict.values()):
    sim_type_lst  = [key.split('_')[0] for key in drifts_df_dict.keys()]
    nsubs_lst     = [key.split('_')[1] for key in drifts_df_dict.keys()]
    iteration_lst = [key.split('_')[4] for key in drifts_df_dict.keys()]
    station_lst   = [key.split('_')[5] for key in drifts_df_dict.keys()]

    drift_df = pd.DataFrame({
                    'Sim_Type'  : sim_type_lst,
                    'Nsubs'     : nsubs_lst,
                    'Iteration' : iteration_lst,
                    'Station'   : station_lst})

    dfx = pd.DataFrame([df['CM x'] for df in drifts_df_dict.values()])
    dfy = pd.DataFrame([df['CM y'] for df in drifts_df_dict.values()])
    dfy = dfy.reset_index()
    dfx = dfx.reset_index()
    dfy = dfy.iloc[:,1:]
    dfx = dfx.iloc[:,1:]
    drift_df_x = pd.concat([drift_df, dfx], axis=1)
    drift_df_y = pd.concat([drift_df, dfy], axis=1)
    rename_dict = {
        1  : 's1',
        2  : 's2',
        3  : 's3',
        4  : 's4',
        5  : 's5',
        6  : 's6',
        7  : 's7',
        8  : 's8',
        9  : 's9',
        10 : 's10',
        11 : 's11',
        12 : 's12',
        13 : 's13',
        14 : 's14',
        15 : 's15',
        16 : 's16',
        17 : 's17',
        18 : 's18',
        19 : 's19',
        20 : 's20',
    }
    drift_df_x = drift_df_x.rename(columns=rename_dict).copy()[['Sim_Type', 'Nsubs', 'Iteration', 'Station', 's1','s5','s10','s15','s20']]
    drift_df_y = drift_df_y.rename(columns=rename_dict).copy()[['Sim_Type', 'Nsubs', 'Iteration', 'Station', 's1','s5','s10','s15','s20']]
else:
    drift_df_x = pd.read_csv(project_path / 'drift_per_story_X_df.csv', index_col=0)
    drift_df_y = pd.read_csv(project_path / 'drift_per_story_Y_df.csv', index_col=0)

#%% Compute Spectra Results
# --------------------------------------- SPECTRUM ----------------------------------------
# We will have the acceleration at the period equal to mode 3 = 0.83s
if all(isinstance(value, pd.DataFrame) for value in spectra_df_dict.values()):
    sim_type_lst  = [key.split('_')[0] for key in spectra_df_dict.keys()]
    nsubs_lst     = [key.split('_')[1] for key in spectra_df_dict.keys()]
    iteration_lst = [key.split('_')[4] for key in spectra_df_dict.keys()]
    station_lst   = [key.split('_')[5] for key in spectra_df_dict.keys()]
    spectra_df = pd.DataFrame({
                    'Sim_Type'  : sim_type_lst,
                    'Nsubs'     : nsubs_lst,
                    'Iteration' : iteration_lst,
                    'Station'   : station_lst,})
    spectra_df['Zone']  = spectra_df['Station'].apply(assignZonesToStationsInDF)
    columns_x = ['Story 1 x', 'Story 5 x', 'Story 10 x', 'Story 15 x', 'Story 20 x']
    columns_y = ['Story 1 y', 'Story 5 y', 'Story 10 y', 'Story 15 y', 'Story 20 y']

    dfx = pd.DataFrame([df[columns_x].iloc[416] for df in spectra_df_dict.values()])
    dfy = pd.DataFrame([df[columns_y].iloc[416] for df in spectra_df_dict.values()])
    dfy = dfy.reset_index()
    dfx = dfx.reset_index()
    dfy = dfy.iloc[:,1:]
    dfx = dfx.iloc[:,1:]
    spectra_df_x = pd.concat([spectra_df, dfx], axis=1)
    spectra_df_y = pd.concat([spectra_df, dfy], axis=1)
    rename_dict = {
        'Story 1 x'  : 's1',
        'Story 5 x'  : 's5',
        'Story 10 x' : 's10',
        'Story 15 x' : 's15',
        'Story 20 x' : 's20',
    }
    spectra_df_x = spectra_df_x.rename(columns=rename_dict)
    rename_dict = {
        'Story 1 y'  : 's1',
        'Story 5 y'  : 's5',
        'Story 10 y' : 's10',
        'Story 15 y' : 's15',
        'Story 20 y' : 's20',
    }
    spectra_df_y = spectra_df_y.rename(columns=rename_dict)

else:
    spectra_df_x = pd.read_csv(project_path / 'spectra_per_story_X_df.csv', index_col=0)
    spectra_df_y = pd.read_csv(project_path / 'spectra_per_story_Y_df.csv', index_col=0)

#%% Compute Base Shear Results
# --------------------------------------- BASE SHEAR ----------------------------------------
if all(isinstance(value, pd.DataFrame) for value in base_shear_df_dict.values()):
    sim_type_lst  = [key.split('_')[0] for key in base_shear_df_dict.keys()]
    nsubs_lst     = [key.split('_')[1] for key in base_shear_df_dict.keys()]
    iteration_lst = [key.split('_')[4] for key in base_shear_df_dict.keys()]
    station_lst   = [key.split('_')[5] for key in base_shear_df_dict.keys()]
    base_shear_df = pd.DataFrame({
                    'Sim_Type'  : sim_type_lst,
                    'Nsubs'     : nsubs_lst,
                    'Iteration' : iteration_lst,
                    'Station'   : station_lst,})
    dfx = pd.DataFrame([df['Shear X'].abs().max() for df in base_shear_df_dict.values()], columns=['MaxShearX'])
    dfy = pd.DataFrame([df['Shear Y'].abs().max() for df in base_shear_df_dict.values()], columns=['MaxShearY'])
    dfy = dfy.reset_index()
    dfx = dfx.reset_index()
    dfy = dfy.iloc[:,1:]
    dfx = dfx.iloc[:,1:]
    base_shear_df_x = pd.concat([base_shear_df, dfx], axis=1)
    base_shear_df_y = pd.concat([base_shear_df, dfy], axis=1)
else:
    base_shear_df_x = pd.read_csv(project_path / 'max_base_shear_X_df.csv', index_col=0)
    base_shear_df_y = pd.read_csv(project_path / 'max_base_shear_Y_df.csv', index_col=0)

# %%
