#%% ================================== INIT AND CONNECT TO DATABASE ==================================
# Import modules
from pyseestko.utilities import perfomDriftAnova #type: ignore
from pathlib             import Path

# Temp imports
import statsmodels.api as sm
from matplotlib import pyplot as plt
import pandas as pd

project_path = Path('C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/')
drift_df_x   = pd.read_csv(project_path / 'DataBase-Outputs' / 'Anova Output'/ 'drift_df_x.csv', index_col=0)
drift_df_y   = pd.read_csv(project_path / 'DataBase-Outputs' / 'Anova Output'/ 'drift_df_y.csv', index_col=0)

#%%  ------------------------------------------ Perfom analysis ------------------------------------------
sim_case  = 'FixBase'
anova_res = {}
dict_anova = {'1':['s1','s2','s3'],
              '2':['s4','s5','s6'],
              '3':['s7','s8','s9']}
print(f'----------------- {sim_case} --------------------')
for num_subs in ['20f2s', '20f4s']:
    print(f'----------------- {num_subs} --------------------')
    for zone, stats in dict_anova.items():
        for dir in ['X', 'Y']:
            # Filter the df
            if dir == 'X':
                drift_df = drift_df_x
            else:
                drift_df = drift_df_y

            # Perform the ANOVA
            print(f'{sim_case}-{num_subs} - Zone {zone} - Direction {dir}')
            model, anova = perfomDriftAnova(drift_df, sim_case, num_subs, stats, zone=zone, direction=dir)
            anova_res[f'{sim_case}-{num_subs}-{zone}-{dir}'] = [model, anova]

            print('-------------------------------------------------\n')



























"""

sim_case = 'FixBase'
# ==================================================================================================
# ============================== 20 stories, 2 subterrains, Fix Base ===============================
# ==================================================================================================
num_subs = '20f2s'
# Filter the df zone 1
stats     = ['s1','s2','s3']
anova_1_x = perfomDriftAnova(drift_df_x, sim_case, num_subs, stats, zone='1', direction='X')
anova_1_y = perfomDriftAnova(drift_df_y, sim_case, num_subs, stats, zone='1', direction='Y')

# Filter the df zone 2
stats     = ['s4','s5','s6']
anova_2_x = perfomDriftAnova(drift_df_x, sim_case, num_subs, stats, zone='2', direction='X')
anova_2_y = perfomDriftAnova(drift_df_y, sim_case, num_subs, stats, zone='2', direction='Y')

# Filter the df zone 3
stats     = ['s7','s8','s9']
anova_3_x = perfomDriftAnova(drift_df_x, sim_case, num_subs, stats, zone='3', direction='X')
anova_3_y = perfomDriftAnova(drift_df_y, sim_case, num_subs, stats, zone='3', direction='Y')

# ==================================================================================================
# ============================== 20 stories, 4 subterrains, Fix Base ===============================
# ==================================================================================================
num_subs = '20f4s'

# Filter the df zone 1
stats    = ['s1','s2','s3']
anova_1_x = perfomDriftAnova(drift_df_x, sim_case, num_subs, stats, zone='1', direction='X')
anova_1_y = perfomDriftAnova(drift_df_y, sim_case, num_subs, stats, zone='1', direction='Y')

# Filter the df zone 2
stats    = ['s4','s5','s6']
anova_2_x = perfomDriftAnova(drift_df_x, sim_case, num_subs, stats, zone='2', direction='X')
anova_2_y = perfomDriftAnova(drift_df_y, sim_case, num_subs, stats, zone='2', direction='Y')

# Filter the df zone 3
stats    = ['s7','s8','s9']
anova_3_x = perfomDriftAnova(drift_df_x, sim_case, num_subs, stats, zone='3', direction='X')
anova_3_y = perfomDriftAnova(drift_df_y, sim_case, num_subs, stats, zone='3', direction='Y')















# --------------------------------- SPECTRA ANOVA ----------------------------------
# Get the mean and max base shear structured dfs for each simulation type for the anova
max_drift_lst  = [df['Max x'].max()  for df in spectra_df_dict.values()]
mean_drift_lst = [df['Max x'].mean() for df in spectra_df_dict.values()]

# Build DF, apply iteration modification, apply zone mapping columns and select specific columns avoiding NaN
spectra_df = pd.DataFrame({
                'Sim_Type': sim_type_lst,
                'Nsubs'     : nsubs_lst,
                'Iteration' : iteration_lst,
                'Station'   : station_lst,
                'Max_Drift' : max_drift_lst
                          })
spectra_df['Zone'] = spectra_df['Station'].apply(assign_zones)
sim_case           = 'DRM'
num_subs           = '20f4s'
stats              = ['s7','s8','s9']

#Filter the df
spectra_df = spectra_df[(spectra_df['Sim_Type'] == sim_case) & (spectra_df['Nsubs'] == num_subs) & (spectra_df['Station'].isin(stats))]

# Realizamos el ANOVA de modelos lineales
model_lm       = ols('Mean_Drift ~ C(Iteration)', data=spectra_df).fit()
anova_table_lm = sm.stats.anova_lm(model_lm, typ=2)
print("ANOVA de Modelos Lineales")
print(anova_table_lm)

# --------------------------------------------------------------------------------
# BASE SHEAR DF STRUCTURATION
# --------------------------------------------------------------------------------
# Get df columns
sim_type_lst  = [key.split('_')[0] for key in base_shear_df_dict.keys()]
nsubs_lst     = [key.split('_')[1] for key in base_shear_df_dict.keys()]
iteration_lst = [key.split('_')[4] for key in base_shear_df_dict.keys()]
station_lst   = [key.split('_')[5] for key in base_shear_df_dict.keys()]

# Get the mean and max base shear structured dfs for each simulation type for the anova
max_shear_base_lst  = [df['Shear X'].abs().max() for df in base_shear_df_dict.values()]
mean_shear_base_lst = [df['Shear X'].abs().std() for df in base_shear_df_dict.values()]

# --------------------------------------------------------------------------------
# SHEAR BASE ANOVA
# --------------------------------------------------------------------------------
# Build DF, apply iteration modification, apply zone mapping columns and select specific columns avoiding NaN
shear_base_df              = pd.DataFrame({'Sim_Type': sim_type_lst, 'Nsubs': nsubs_lst, 'Iteration': iteration_lst, 'Station': station_lst, 'Shear_Base': max_shear_base_lst})
shear_base_df['Iteration'] = shear_base_df.apply(assign_zones)

#NOTE: TEMP DF
sim_case = 'AbsBound'
num_subs = '20f2s'
stats    = ['s1','s2','s3']

#Filter the df
shear_base_df = shear_base_df[(shear_base_df['Sim_Type'] == sim_case) & (shear_base_df['Nsubs'] == num_subs) & (shear_base_df['Station'].isin(stats))]

# Apply OLS model
model = ols('Shear_Base  ~ C(Station)', data=shear_base_df).fit()
anova_results = sm.stats.anova_lm(model, typ=2)
print(anova_results)

# --------------------------------------------------------------------------------
# BASE SHEAR DF STRUCTURATION
# --------------------------------------------------------------------------------
# Structure the data for the ANOVA
def mod_iteration_row(row):
    replica_map = {
                's1': '1', 's2': '2', 's3': '3',
                's4': '1', 's5': '2', 's6': '3',
                's7': '1', 's8': '2', 's9': '3'}
    if row['Station'] == 's0':
        return row['Iteration']
    else:
        value = int(replica_map[row['Station']])/10
        new_value = int(row['Iteration']) + value
        return float(new_value)

# Get df columns
sim_type_lst   = [key.split('_')[0] for key in drifts_df_dict.keys()]
nsubs_lst      = [key.split('_')[1] for key in drifts_df_dict.keys()]
iteration_lst  = [key.split('_')[4] for key in drifts_df_dict.keys()]
station_lst    = [key.split('_')[5] for key in drifts_df_dict.keys()]

# Get the mean and max base shear structured dfs for each simulation type for the anova
max_shear_base_lst  = [df['Shear X'].abs().max() for df in base_shear_df_dict.values()]
mean_shear_base_lst = [df['Shear X'].abs().std() for df in base_shear_df_dict.values()]


# --------------------------------------------------------------------------------
# SHEAR BASE ANOVA
# --------------------------------------------------------------------------------
# Build DF, apply iteration modification, apply zone mapping columns and select specific columns avoiding NaN
shear_base_df              = pd.DataFrame({'Sim_Type': sim_type_lst, 'Nsubs': nsubs_lst, 'Iteration': iteration_lst, 'Station': station_lst, 'Shear_Base': max_shear_base_lst})
shear_base_df['Iteration'] = shear_base_df.apply(mod_iteration_row, axis=1)

#NOTE: TEMP DF
sim_case = 'AbsBound'
num_subs = '20f2s'
stats    = ['s1','s2','s3']

#Filter the df
shear_base_df = shear_base_df[(shear_base_df['Sim_Type'] == sim_case) & (shear_base_df['Nsubs'] == num_subs) & (shear_base_df['Station'].isin(stats))]

# Apply OLS model
model = ols('Shear_Base  ~ C(Station)', data=shear_base_df).fit()
anova_results = sm.stats.anova_lm(model, typ=2)
print(anova_results)

"""
# %%
