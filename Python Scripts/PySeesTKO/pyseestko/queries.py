# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
from pyseestko.db_manager import DataBaseManager        #type: ignore
from pyseestko.plotting   import Plotting               #type: ignore
from pyseestko.utilities  import NCh433_2012            #type: ignore
from pyseestko.utilities  import initialize_ssh_tunnel  #type: ignore
from pyseestko.utilities  import checkMainQueryInput    #type: ignore
from pyseestko.utilities  import save_df_to_csv_paths   #type: ignore
from pathlib              import Path
from typing               import List, Dict, Tuple
from tqdm                 import tqdm
from matplotlib           import pyplot as plt

import numpy  as np
import pandas as pd
import pickle
import time
# ==================================================================================================
# MAIN FUNCTION
# ==================================================================================================
git_path     = Path('C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/DataBase-Outputs')
def executeMainQuery(
    # Params
    sim_types   : List[int],
    stations    : List[int],
    iterations  : List[int],
    nsubs_lst   : List[int],
    mag_map     : Dict[float, str],
    loc_map     : Dict[int, str],
    rup_map     : Dict[int, str],
    # DataBase params
    user        : str,
    password    : str,
    host        : str,
    database    : str,
    # Save params
    save_drift  : bool = True,
    save_spectra: bool = True,
    save_b_shear: bool = True,
    save_results: bool = False,
    # Plot params
    show_plots  : bool = True,
    xlim_sup    : float = 0.008,
    grid        : bool = False,
    fig_size    : Tuple[float, float] = (19.2, 10.8),
    dpi         : int = 300,
    file_type   : str = 'png',
    # Optional params
    linearity   : int  = 1,
    stories     : int  = 20,
    magnitude   : int  = 6.7,
    rupture_type: int  = 1,
    # Logic params
    windows     : bool = True,
    project_path: Path = git_path/ 'DataBase-Outputs',
    verbose     : bool = True,
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """
    This function will execute the main query to get the results from the database
    The logic is the following:
    1. Iterate over the simulation types
    2. Iterate over the stations
    3. Iterate over the iterations
    4. Iterate over the number of substructures
    5. Query the database
    6. Append the results to the lists
    7. Return the lists

    Params:
    - sim_types: List of simulation types
    - stations: List of stations
    - iterations: List of iterations
    - nsubs_lst: List of number of substructures
    - mag_map: Dictionary with the mapping of the magnitudes
    - loc_map: Dictionary with the mapping of the locations
    - rup_map: Dictionary with the mapping of the rupture types
    - user: User of the database
    - password: Password of the database
    - host: Host of the database
    - database: Name of the database

    Optional params:
    - linearity: Linearity of the model, always 1 for linear, 2 for non-linear, default is 1
    - stories: Number of stories, default is 20
    - magnitude: Magnitude of the earthquake, default is 6.7
    - rupture_type: Type of rupture, default is 1
    - save_drift: Path to save the drift plots if None, it will not save the plots nor the data
    - save_spectra: Path to save the spectra plots, if None, it will not save the plots nor the data
    - save_b_shear: Path to save the base shear plots, if None, it will not save the plots nor the data
    - windows: True if the OS is Windows, False if Linux

    Returns:
    - drifts_df_lst: List of drift dataframes
    - spectra_df_lst: List of spectra dataframes
    - base_shear_df_lst: List of base shear dataframes

    Note:
    This is mean to be used for statistical analysis, so this is the main fuction to access to the specific data
    and then analyze it with diverse statistical methods such as ANOVA, POWER ANALYSIS OR MANOVA.
    """

    # -------------------------------------- INITIALIZATION -----------------------------------------
    # Check the input
    checkMainQueryInput(sim_types, nsubs_lst, iterations, stations, save_drift, save_spectra, save_b_shear, grid)

    # Iterate over the subs, then over the sim_type and then over the stations so we can get all the results
    total_iterations = len(sim_types) * len(stations) * len(iterations) * len(nsubs_lst)
    pbar = tqdm(total=total_iterations, desc='Processing')

    # -------------------------------------- EXECUTE THE MAIN QUERY ---------------------------------
    # Iterate over the simulation types
    drifts_df_dict, spectra_df_dict, base_shear_df_dict = queryMetricsInGridPlots(
        sim_types, stations, iterations, nsubs_lst, mag_map, loc_map, rup_map, project_path, pbar,
        user, password, host, database,
        save_drift, save_spectra, save_b_shear, show_plots, fig_size, xlim_sup, dpi, file_type,
        linearity, stories, magnitude, rupture_type,
        windows, verbose)
    pbar.close()
    print('Done!')

    # -------------------------------------- SAVE THE RESULTS ---------------------------------------
    save_csv_drift   = project_path / 'Analysis Output' / 'CSV' / 'Drift'
    save_csv_spectra = project_path / 'Analysis Output' / 'CSV' / 'Spectra'
    save_csv_b_shear = project_path / 'Analysis Output' / 'CSV' / 'Base Shear'
    if save_results:
        save_df_to_csv_paths(drifts_df_dict, spectra_df_dict,base_shear_df_dict,
                             save_csv_drift, save_csv_spectra, save_csv_b_shear)

    return drifts_df_dict, spectra_df_dict, base_shear_df_dict

def queryMetricsInSinglePlots(
    # Params
    sim_types   : List[int],
    stations    : List[int],
    iterations  : List[int],
    nsubs_lst   : List[int],
    mag_map     : Dict[float, str],
    loc_map     : Dict[int, str],
    rup_map     : Dict[int, str],
    project_path: Path,
    pbar        : tqdm,
    # DataBase params
    user        : str,
    password    : str,
    host        : str,
    database    : str,
    # Plot params
    save_drift  : bool  = True,
    save_spectra: bool  = True,
    save_b_shear: bool  = True,
    show_plots  : bool  = True,
    xlim_sup    : float = 0.008,
    dpi         : int   = 100,
    file_type   : str   = 'png',
    # Sim params
    linearity   : int  = 1,
    stories     : int  = 20,
    magnitude   : int  = 6.7,
    rupture_type: int  = 1,
    # Optional params
    windows     : bool = True,
    verbose     : bool = True,
    )-> Tuple[Dict[str, pd.DataFrame], Dict[str, List[pd.DataFrame]], Dict[str, pd.DataFrame]]:
    """
    This function will execute the main query to get the results from the database in single plots
    """
    # Iterative params
    save_drift   = project_path / 'Drift Output'         if save_drift   else None
    save_spectra = project_path / 'Story Spectra Output' if save_spectra else None
    save_b_shear = project_path / 'Base Shear Output'    if save_b_shear else None
    sim_type_map       = {1: 'FixBase', 2: 'AbsBound', 3: 'DRM'}
    drifts_df_dict     = {}
    spectra_df_dict    = {}
    base_shear_df_dict = {}

    # Iterate over the subs, then over the sim_type and then over the stations so we can get all the results
    for sim_type in sim_types:
        for station in stations:
            for iteration in iterations:
                for nsubs in nsubs_lst:
                    structure_weight = 22241.3 if nsubs == 4 else 18032.3
                    # Init the classes
                    plotter = Plotting(sim_type, stories,                    # The class that plots the data
                                    nsubs, magnitude,
                                    iteration, rupture_type,
                                    station, show_plots=show_plots, dpi=dpi, file_type=file_type)
                    query   = ProjectQueries(user, password, host, database, # The class that queries the database
                                            sim_type, linearity,
                                            mag_map.get(magnitude,    'None'),
                                            rup_map.get(rupture_type, 'None'), iteration,
                                            loc_map.get(station,      'None'),
                                            stories, nsubs, plotter, windows=windows, verbose=verbose)

                    # Get the results for zone = 'Las Condes', soil_category = 'B' and importance = 2
                    drift, spectra, base_shear, _ = query.getAllResults(save_drift,
                                                                    save_spectra,
                                                                    save_b_shear,
                                                                    structure_weight,
                                                                    xlim_sup = xlim_sup, verbose=verbose)

                    # Append the results to the dicts
                    sim_type_name = sim_type_map[sim_type]
                    sim_name      = f'{sim_type_name}_20f{nsubs}s_rup_bl_{iteration}_s{station}'
                    drifts_df_dict[sim_name]     = drift
                    spectra_df_dict[sim_name]    = spectra
                    base_shear_df_dict[sim_name] = base_shear

                    # Update tqdm
                    pbar.update(1)
    return drifts_df_dict, spectra_df_dict, base_shear_df_dict

def queryMetricsInGridPlots(
    # Params
    sim_types   : List[int],
    stations    : List[int],
    iterations  : List[int],
    nsubs_lst   : List[int],
    mag_map     : Dict[float, str],
    loc_map     : Dict[int, str],
    rup_map     : Dict[int, str],
    project_path: Path,
    pbar        : tqdm,
    # DataBase params
    user        : str,
    password    : str,
    host        : str,
    database    : str,
    # Plot params
    save_drift  : bool  = True,
    save_spectra: bool  = True,
    save_b_shear: bool  = True,
    show_plots  : bool  = True,
    fig_size    : Tuple[float, float] = (19.2, 10.8),
    xlim_sup    : float = 0.008,
    dpi         : int   = 100,
    file_type   : str   = 'png',
    # Sim params
    linearity   : int  = 1,
    stories     : int  = 20,
    magnitude   : int  = 6.7,
    rupture_type: int  = 1,
    # Optional params
    windows     : bool = True,
    verbose     : bool = True,
    )-> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """
    This function will execute the main query to get the results from the database in grid plots
    The grid is going to be a 3x3 grid with the drifts, spectra and base shear.
    """
    # Init params
    sim_type_map       = {1: 'FixBase', 2: 'AbsBound', 3: 'DRM'}
    drifts_df_dict     = {}
    spectra_df_dict    = {}
    base_shear_df_dict = {}

    # Save path params
    save_drift   = project_path / 'Drift Output'         if save_drift   else None
    save_spectra = project_path / 'Story Spectra Output' if save_spectra else None
    save_b_shear = project_path / 'Base Shear Output'    if save_b_shear else None
    nch  = NCh433_2012('Las Condes', 'B', 2)
    # Iterate over the subs, then over the sim_type and then over the stations so we can get all the results
    for sim_type in sim_types:
        for nsubs in nsubs_lst:
            structure_weight = 22241.3 if nsubs == 4 else 18032.3
            Qmax = nch.computeMaxBaseShear_c6_3_7_2(structure_weight)

            # Drift params
            drift_axes      = [np.full((3, 3), None), np.full((3, 3), None)]
            spectra_axes    = [np.full((3, 3), None), np.full((3, 3), None)]
            base_shear_axes = [np.full((3, 3), None), np.full((3, 3), None)]
            print(f'Processing: {sim_type_map[sim_type]}, {nsubs} subs')
            for station in stations:
                for iteration in iterations:
                    if not all([save_drift==None, save_spectra==None, save_b_shear==None]):
                        # -------------------------------------- INITIALIZATION -----------------------------------------
                        # Init the classes
                        save_fig = True if station == stations[-1] and iteration == iterations[-1] else False
                        plotter = Plotting(sim_type, stories,                    # The class that plots the data
                                        nsubs, magnitude,
                                        iteration, rupture_type,
                                        station, show_plots=show_plots, grid=True, dpi=dpi, file_type=file_type)
                        query   = ProjectQueries(user, password, host, database, sim_type, linearity,
                                                mag_map.get(magnitude,    'None'),
                                                rup_map.get(rupture_type, 'None'),
                                                iteration,
                                                loc_map.get(station,      'None'),
                                                stories, nsubs, plotter, windows=windows, verbose=verbose)

                        # -------------------------------------- EXECUTE THE MAIN QUERY ---------------------------------
                        # Get the results for zone = 'Las Condes', soil_category = 'B' and importance = 2
                        drift, spectra, base_shear, axes = query.getAllResults(save_drift, save_spectra, save_b_shear,
                                                                    structure_weight, xlim_sup=xlim_sup, verbose=verbose,
                                                                    drift_axes=drift_axes, spectra_axes=spectra_axes, base_shear_axes=base_shear_axes,
                                                                    save_fig=False, fig_size=fig_size)
                        drift_axes, spectra_axes, base_shear_axes = axes # update the axes

                        # Fill dictionaries
                        sim_type_name                = sim_type_map[sim_type]
                        sim_name                     = f'{sim_type_name}_20f{nsubs}s_rup_bl_{iteration}_s{station}'
                        drifts_df_dict[sim_name]     = drift
                        spectra_df_dict[sim_name]    = spectra
                        base_shear_df_dict[sim_name] = base_shear

                        # -------------------------------------- PLOT THE RESULTS ---------------------------------
                        # Add plot of mean drifts
                        if iteration == iterations[-1]:
                            # Plot mean drift
                            _plotMeanDriftColor(drifts_df_dict, plotter, xlim_sup, drift_axes, save_fig, fig_size) if save_drift else None

                            # Plot mean spectra
                            _plotMeanSpectraColor(spectra_df_dict, plotter, spectra_axes, save_fig, fig_size) if save_spectra else None

                            # Plot mean base shear
                            _plotMeanBaseShearColor(base_shear_df_dict, plotter, base_shear_axes, save_fig, fig_size, Qmax) if save_b_shear else None

                        # Update tqdm
                        pbar.update(1)
                    else:
                        pbar.update(1)
                        sim_type_name                = sim_type_map[sim_type]
                        sim_name                     = f'{sim_type_name}_20f{nsubs}s_rup_bl_{iteration}_s{station}'
                        drifts_df_dict[sim_name]     = None
                        spectra_df_dict[sim_name]    = None
                        base_shear_df_dict[sim_name] = None
                        continue
    return drifts_df_dict, spectra_df_dict, base_shear_df_dict


def _plotMeanDriftColor(drifts_df_dict: Dict[str, pd.DataFrame], plotter: Plotting, xlim_sup:float, drift_axes:plt.Axes, save_fig:bool, fig_size:bool):
    mean_drifts_x = pd.concat([df['CM x'] for df in list(drifts_df_dict.values())[-5:]], axis=1).mean(axis=1).values
    mean_drifts_y = pd.concat([df['CM y'] for df in list(drifts_df_dict.values())[-5:]], axis=1).mean(axis=1).values
    plotter.setup_direction(x_direction=True)
    plotter.plotModelDrift([], mean_drifts_x, [], [],
                            xlim_sup = xlim_sup,
                            axes     = drift_axes[0],
                            legend   = True,
                            save_fig = save_fig,
                            fig_size = fig_size,
                            line_color = 'red')
    plotter.setup_direction(x_direction=False)
    plotter.plotModelDrift([], [], [], mean_drifts_y,
                            xlim_sup = xlim_sup,
                            axes     = drift_axes[1],
                            legend   = True,
                            save_fig = save_fig,
                            fig_size = fig_size,
                            line_color = 'blue')

def _plotMeanSpectraColor(spectra_df_dict: Dict[str, pd.DataFrame], plotter: Plotting, spectra_axes:plt.Axes, save_fig:bool, fig_size:bool):
    columns_x = [f'Story {story} x' for story in [1,5,10,15,20]]
    columns_y = [f'Story {story} y' for story in [1,5,10,15,20]]
    mean_spectras_x = pd.concat([df[columns_x] for df in list(spectra_df_dict.values())[-5:]], axis=1)
    mean_spectras_y = pd.concat([df[columns_y] for df in list(spectra_df_dict.values())[-5:]], axis=1)
    plotter.setup_direction(x_direction=True)
    plotter.plotMeanStoriesSpectrums(mean_spectras_x, 'x', [1,5,10,15,20], save_fig, spectra_axes[0], fig_size)
    plotter.setup_direction(x_direction=False)
    plotter.plotMeanStoriesSpectrums(mean_spectras_y, 'y', [1,5,10,15,20], save_fig, spectra_axes[1], fig_size)

def _plotMeanBaseShearColor(base_shear_df_dict: Dict[str, pd.DataFrame], plotter: Plotting, base_shear_axes:plt.Axes, save_fig:bool, fig_size:bool, Qmax:float):
    mean_base_shear_x = pd.concat([df['Shear X'] for df in list(base_shear_df_dict.values())[-5:]], axis=1).mean(axis=1)
    mean_base_shear_y = pd.concat([df['Shear Y'] for df in list(base_shear_df_dict.values())[-5:]], axis=1).mean(axis=1)
    plotter.setup_direction(x_direction=True)
    plotter.plotShearBaseOverTime(
                time           = mean_base_shear_x.index,
                time_shear_fma = mean_base_shear_x.values,
                Qmax           = Qmax,
                dir_           = 'x',
                axes           = base_shear_axes[0],
                save_fig       = save_fig,
                fig_size       = fig_size,
                leyend         = True,
                mean           = True)
    plotter.setup_direction(x_direction=False)
    plotter.plotShearBaseOverTime(
                time           = mean_base_shear_y.index,
                time_shear_fma = mean_base_shear_y.values,
                Qmax           = Qmax,
                dir_           = 'y',
                axes           = base_shear_axes[1],
                save_fig       = save_fig,
                fig_size       = fig_size,
                leyend         = True,
                mean           = True)

def getDriftDFs(drifts_df_lst:List[pd.DataFrame]):
    """
    This function will get the drifts dataframes of the x and y directions
    and return the drifts dataframe of the x direction, the drifts dataframe of the y direction
    and the concatenation of both dataframes.
    It's input is a list of drifts dataframes and it will return the global drifts dataframes based
    on the maximum drifts of the x and y directions.
    of the x and y directions.
    It's supposed to be used after the main query is executed.

    Parameters
    ----------
    drifts_df_lst : List[pd.DataFrame]
        List of drifts dataframes.

    Returns
    -------
    df1 : pd.DataFrame
        Drifts dataframe of the x direction.
    df2 : pd.DataFrame
        Drifts dataframe of the y direction.
    drift_df : pd.DataFrame
        Concatenation of df1 and df2.
    """
    #X Direction
    max_drifts_lst_X = [dfx[['CM x']] for dfx in drifts_df_lst]
    df1 = pd.concat(max_drifts_lst_X, axis=1)
    df1 = df1.set_index(pd.Index(['drift'] * len(df1), name='Metric'), append=True)
    df1 = df1.set_index(pd.Index(['x'] * len(df1), name='Dir'), append=True)
    df1.columns = pd.Index([f'rep_{i+1}' for i in range(len(max_drifts_lst_X))])

    #Y Direction
    max_drifts_lst_Y = [dfy[['CM y']] for dfy in drifts_df_lst]
    df2 = pd.concat(max_drifts_lst_Y, axis=1)
    df2 = df2.set_index(pd.Index(['drift'] * len(df2), name='Metric'), append=True)
    df2 = df2.set_index(pd.Index(['y'] * len(df2), name='Dir'), append=True)
    df2.columns = pd.Index([f'rep_{i+1}' for i in range(len(max_drifts_lst_Y))])

    # Concatenate X and Y
    drift_df = pd.concat([df1, df2], axis=0)

    return df1, df2, drift_df

def getReplicaCummStatisticDriftDFs(drifts_df_lst:List[pd.DataFrame], statistic:str='mean'):
    """
    This function will get the cummultive mean drifts dataframes of the x and y directions, for each story as index,
    based on the max value for each replica, given a certain type of simulation,
    certain type of structure and certain location. That means, the first column gives the mean given 1 replica,
    the second column gives the mean given 2 replicas and so on.

    Parameters
    ----------
    drifts_df_lst : List[pd.DataFrame]
        List of drifts dataframes.

    Returns
    -------
    df1 : pd.DataFrame
        Mean drifts dataframe of the x direction.
    df2 : pd.DataFrame
        Mean drifts dataframe of the y direction.
    drift_df : pd.DataFrame
        Concatenation of df1 and df2.
    """
    # Check input
    if statistic not in ['mean', 'std']:
        raise ValueError(f'Statistic must be mean or std, current: {statistic}')

    # Init params
    drift_x_df, drift_y_df, drift_df = getDriftDFs(drifts_df_lst)

    #X Direction
    stories_statistic_lst = []
    for i, column in enumerate(drift_x_df.columns):
        if statistic == 'mean':
            stories_statistic_lst.append(drift_x_df[drift_x_df.columns[:i+1]].mean(axis=1).loc[[1,5,10,15,20]])
        elif statistic == 'std':
            stories_statistic_lst.append(drift_x_df[drift_x_df.columns[:i+1]].std(axis=1).loc[[1,5,10,15,20]])
    df1 = pd.concat(stories_statistic_lst, axis=1)
    df1 = df1.droplevel((1,2))

    #Y Direction
    stories_statistic_lst = []
    for i, column in enumerate(drift_y_df.columns):
        if statistic == 'mean':
            stories_statistic_lst.append(drift_y_df[drift_y_df.columns[:i+1]].mean(axis=1).loc[[1,5,10,15,20]])
        elif statistic == 'std':
            stories_statistic_lst.append(drift_y_df[drift_y_df.columns[:i+1]].std(axis=1).loc[[1,5,10,15,20]])
    df2 = pd.concat(stories_statistic_lst, axis=1)
    df2 = df2.droplevel((1,2))

    # Concatenate X and Y
    drift_df = pd.concat([df1, df2], axis=0)

    return df1, df2, drift_df

def DEPgetSpectraDfs(spectra_df_lst:List[pd.DataFrame]):
    """
    This function will get the mean spectra dataframes of the x and y directions}
    and return the spectra dataframe of the x direction, the spectra dataframe of the y direction
    and the concatenation of both dataframes.
    It's input is a list of spectra dataframes and it will return the mean spectra dataframes
    of the x and y directions.
    It's supposed to be used after the main query is executed.

    Parameters
    ----------
    spectra_df_lst : List[pd.DataFrame]
        List of spectra dataframes.

    Returns
    -------
    df1 : pd.DataFrame
        Spectra dataframe of the x direction.
    df2 : pd.DataFrame
        Spectra dataframe of the y direction.
    spectra_df : pd.DataFrame
        Concatenation of df1 and df2.
    """
    # X Direction
    max_spectra_lst_X = [(dfx[0][['Story 1', 'Story 5', 'Story 10', 'Story 15', 'Story 20']].T.set_index(pd.Index([1, 5, 10, 15, 20], name='Story')).max(axis=1))
                        for dfx in spectra_df_lst]
    df1 = pd.concat(max_spectra_lst_X, axis=1)
    df1.columns = pd.Index([f'rep_{i+1}' for i in range(len(max_spectra_lst_X))])
    df1 = df1.set_index(pd.Index(['spectrum'] * len(df1), name='Metric'), append=True)
    df1 = df1.set_index(pd.Index(['x'] * len(df1), name='Dir'), append=True)

    #Y Direction
    max_spectra_lst_Y = [(dfy[0][['Story 1', 'Story 5', 'Story 10', 'Story 15', 'Story 20']].T.set_index(pd.Index([1, 5, 10, 15, 20], name='Story')).max(axis=1))
                        for dfy in spectra_df_lst]
    df2 = pd.concat(max_spectra_lst_Y, axis=1)
    df2.columns = pd.Index([f'rep_{i+1}' for i in range(len(max_spectra_lst_Y))])
    df2 = df2.set_index(pd.Index(['spectrum'] * len(df2), name='Metric'), append=True)
    df2 = df2.set_index(pd.Index(['y'] * len(df2), name='Dir'), append=True)
    spectra_df = pd.concat([df1, df2], axis=0)

    return df1, df2, spectra_df

def getCummStatisticSpectraDFs(spectra_df_lst:List[pd.DataFrame], statistic:str='mean'):
    """
    This function will get the cummultive mean spectra dataframes of the x and y directions, for each story as index,
    based on the max value for each replica, given a certain type of simulation,
    certain type of structure and certain location. That means, the first column gives the mean given 1 replica,
    the second column gives the mean given 2 replicas and so on.

    Parameters
    ----------
    spectra_df_lst : List[pd.DataFrame]
        List of spectra dataframes.

    Returns
    -------
    df1 : pd.DataFrame
        Mean spectra dataframe of the x direction.
    df2 : pd.DataFrame
        Mean spectra dataframe of the y direction.
    spectra_df : pd.DataFrame
        Concatenation of df1 and df2.
    """
    # Check input
    if statistic not in ['mean', 'std']:
        raise ValueError(f'Statistic must be mean or std, current: {statistic}')

    # Init params
    spectra_x_df, spectra_y_df, spectra_df = getSpectraDfs(spectra_df_lst)

    #X Direction
    stories_statistic_lst = []
    for i, column in enumerate(spectra_x_df.columns):
        if statistic == 'mean':
            stories_statistic_lst.append(spectra_x_df[spectra_x_df.columns[:i+1]].mean(axis=1))
        elif statistic == 'std':
            stories_statistic_lst.append(spectra_x_df[spectra_x_df.columns[:i+1]].std(axis=1))
    df1 = pd.concat(stories_statistic_lst, axis=1)
    df1 = df1.droplevel((1,2))

    #Y Direction
    stories_statistic_lst = []
    for i, column in enumerate(spectra_y_df.columns):
        if statistic == 'mean':
            stories_statistic_lst.append(spectra_y_df[spectra_y_df.columns[:i+1]].mean(axis=1))
        elif statistic == 'std':
            stories_statistic_lst.append(spectra_y_df[spectra_y_df.columns[:i+1]].std(axis=1))
    df2 = pd.concat(stories_statistic_lst, axis=1)
    df2 = df2.droplevel((1,2))

    # Concatenate X and Y
    spectra_df = pd.concat([df1, df2], axis=0)

    return df1, df2, spectra_df

def getReplicaCummStatisticBaseShearDFs(base_shear_df_lst:List[pd.DataFrame], statistic:str='mean'):
    # Check input
    if statistic not in ['mean', 'std']:
        raise ValueError(f'Statistic must be mean or std, current: {statistic}')

    # Init params
    spectra_x_lst = [df['Shear X'].max() for df in base_shear_df_lst]
    spectra_y_lst = [df['Shear Y'].max() for df in base_shear_df_lst]

    # Create a one row DataFrame, with index name equal to "Base Shear"
    max_shear_x_df = pd.DataFrame([spectra_x_lst], index=['Base Shear'], columns=[f'rep_{i}' for i in range(1,11)])
    max_shear_y_df = pd.DataFrame([spectra_y_lst], index=['Base Shear'], columns=[f'rep_{i}' for i in range(1,11)])

    # Concatenate X and Y
    max_shear_df = pd.concat([max_shear_x_df, max_shear_y_df], axis=0)

    return max_shear_x_df, max_shear_y_df, max_shear_df


# ==================================================================================================
# CLASS TO QUERY THE DATABASE
# ==================================================================================================
class ProjectQueries:
    def __init__(
        self,
        user        :str,
        password    :str,
        host        :str,
        database    :str,
        sim_type    :int,
        linearity   :int,
        magnitude   :str,
        rupture_type:str,
        iteration   :int,
        location    :str,
        stories     :int,
        subs        :int,
        plotter     :Plotting,
        windows     :bool=True,
        verbose     :bool=True):

        # Save attributes
        self.values  = (sim_type, linearity, magnitude, rupture_type, iteration, location, stories, subs)
        self.plotter = plotter

        # Connect the model to the database
        if windows:
            initialize_ssh_tunnel(verbose=verbose)
            time.sleep(1)
        self.DataBase = DataBaseManager(user, password, host, database)
        self.cursor = self.DataBase.cursor

    def _execute_query(self, query, parameters):
        self.cursor.execute(query, parameters)
        return self.cursor.fetchall()

    def story_drift(self):
        # Init the query
        query = """
        SELECT drift.*
        FROM simulation sim
        JOIN simulation_sm_input           sminput  ON sim.idSM_Input            = sminput.IDSM_Input
        JOIN simulation_model              sm       ON sim.idModel 	         = sm.IDModel
        JOIN model_specs_structure         mss      ON sm.idSpecsStructure       = mss.IDSpecsStructure
        JOIN model_structure_perfomance    msp      ON sm.idStructuralPerfomance = msp.IDStructuralPerfomance
        JOIN structure_max_drift_per_floor drift    ON msp.idMaxDriftPerFloor    = drift.IDMaxDriftPerFloor
        WHERE sim.idType          = %s AND mss.idLinearity      = %s
        AND sminput.Magnitude     = %s AND sminput.Rupture_Type = %s
        AND sminput.RealizationID = %s AND sminput.Location     = %s
        AND mss.Nstories          = %s AND mss.Nsubs            = %s;
        """
        data = self._execute_query(query, self.values)

        # Load the data
        structure_max_drift_per_floor = data[-1]
        max_corner_x = pickle.loads(structure_max_drift_per_floor[1]) # type: ignore
        max_corner_y = pickle.loads(structure_max_drift_per_floor[2]) # type: ignore
        max_center_x = pickle.loads(structure_max_drift_per_floor[3]) # type: ignore
        max_center_y = pickle.loads(structure_max_drift_per_floor[4]) # type: ignore

        return max_center_x, max_center_y, max_corner_x, max_corner_y

    def stories_spectra(self):
        query = """
        SELECT msp.*
        FROM simulation sim
        JOIN simulation_sm_input           sminput 	ON sim.idSM_Input            = sminput.IDSM_Input
        JOIN simulation_model              sm           ON sim.idModel 	             = sm.IDModel
        JOIN model_specs_structure         mss          ON sm.idSpecsStructure       = mss.IDSpecsStructure
        JOIN model_structure_perfomance    msp 		ON sm.idStructuralPerfomance = msp.IDStructuralPerfomance
        WHERE sim.idType          = %s AND mss.idLinearity      = %s
        AND sminput.Magnitude     = %s AND sminput.Rupture_Type = %s
        AND sminput.RealizationID = %s AND sminput.Location     = %s
        AND mss.Nstories          = %s AND mss.Nsubs            = %s;
        """
        data = self._execute_query(query, self.values)

        # Load the data
        structure_perfomance = data[-1]
        accel_df       = pickle.loads(structure_perfomance[6]) # type: ignore
        story_nodes_df = pickle.loads(structure_perfomance[7]) # type: ignore

        return accel_df, story_nodes_df

    def base_shear(self):
        query = """
        SELECT sbs.*
        FROM simulation sim
        JOIN simulation_sm_input        sminput ON sim.idSM_Input 	     = sminput.IDSM_Input
        JOIN simulation_model           sm      ON sim.idModel 		     = sm.IDModel
        JOIN model_specs_structure      mss     ON sm.idSpecsStructure       = mss.IDSpecsStructure
        JOIN model_structure_perfomance msp 	ON sm.idStructuralPerfomance = msp.IDStructuralPerfomance
        JOIN structure_base_shear       sbs     ON msp.idBaseShear           = sbs.IDBaseShear
        WHERE sim.idType          = %s AND mss.idLinearity      = %s
        AND sminput.Magnitude     = %s AND sminput.Rupture_Type = %s
        AND sminput.RealizationID = %s AND sminput.Location     = %s
        AND mss.Nstories          = %s AND mss.Nsubs            = %s;
        """
        data = self._execute_query(query, self.values)

        # Load the data
        base_shear_over_time = data[-1]
        time_series = pickle.loads(base_shear_over_time[1]) # type: ignore
        shear_x     = pickle.loads(base_shear_over_time[2]) # type: ignore
        shear_y     = pickle.loads(base_shear_over_time[3]) # type: ignore
        shear_z     = pickle.loads(base_shear_over_time[4]) # type: ignore

        return time_series, shear_x, shear_y, shear_z

    def close_connection(self):
        self.DataBase.close_connection()

    # ===================================================================================================
    # ==================================== GET ALL THE RESULTS ==========================================
    # ===================================================================================================
    def getAllResults(self,
        # Path to save figs
        save_drift       :str|None,
        save_spectra     :str|None,
        save_b_shear     :str|None,
        # Sim params
        structure_weight :float,
        zone             :str   = 'Las Condes',
        soil_category    :str   = 'B',
        importance       :int   = 2,
        # Plot params
        xlim_sup         :float = 0.008,
        drift_axes       :plt.Axes = None,
        spectra_axes     :plt.Axes = None,
        base_shear_axes  :plt.Axes = None,
        save_fig         :bool     = True,
        fig_size         :Tuple[float, float] = (19.2, 10.8),
        # Optional params
        verbose          :bool  = False,
                      )->Tuple[pd.DataFrame, List[pd.DataFrame], pd.DataFrame]:
        """
        This function will execute all the queries to get the results from the database
        """

        # Init params
        start_time            = time.time()
        drift_results_df      = None
        spectra_results_df    = None
        base_shear_results_df = None
        xlim_sup              = 0.0001

        # ===================================================================================================
        # ==================================== QUERY THE DRIFT PER FLOOR ====================================
        # ===================================================================================================
        if save_drift is not None:
            # Init the query
            max_center_x, max_center_y, max_corner_x, max_corner_y = self.story_drift()
            self.plotter.save_path = Path(save_drift)

            # Generate drift direction X plot
            self.plotter.setup_direction(x_direction=True)
            drift_axes_x = self.plotter.plotModelDrift(max_corner_x, max_center_x, max_corner_y, max_center_y,
                                                     xlim_sup = xlim_sup,
                                                     axes     = drift_axes[0],
                                                     legend   = False,
                                                     save_fig = save_fig,
                                                     fig_size = fig_size)

            # Generate drift direction Y plot
            self.plotter.setup_direction(x_direction=False)
            drift_axes_y = self.plotter.plotModelDrift(max_corner_x, max_center_x, max_corner_y, max_center_y,
                                                     xlim_sup = xlim_sup,
                                                     axes     = drift_axes[1],
                                                     legend   = False,
                                                     save_fig = save_fig,
                                                     fig_size = fig_size)
            drift_results_df  = pd.DataFrame({'CM x': max_center_x,
                                              'CM y': max_center_y,
                                              'Max x': max_corner_x,
                                              'Max y': max_corner_y},
                                             index=range(1, len(max_corner_x)+1)).rename_axis('Story')
            drift_axes = (drift_axes_x, drift_axes_y)

        # ===================================================================================================
        # ===================================== QUERY THE STORY SPECTRUM ====================================
        # ===================================================================================================
        if save_spectra is not None:
            # Init the query
            accel_df, story_nodes_df = self.stories_spectra()

            # Plot the data
            self.plotter.save_path = Path(save_spectra)
            stories_lst = [1,5,10,15,20]
            # Generate spectra direction X plot
            self.plotter.setup_direction(x_direction=True)
            spectra_axes_x, spa_x_df = self.plotter.plotLocalStoriesSpectrums(
                                            accel_df, story_nodes_df, 'x', stories_lst,
                                            axes= spectra_axes[0],
                                            save_fig = save_fig,
                                            fig_size = fig_size)

            # Generate spectra direction Y plot
            self.plotter.setup_direction(x_direction=False)
            spectra_axes_y, spa_y_df = self.plotter.plotLocalStoriesSpectrums(
                                            accel_df, story_nodes_df, 'y', stories_lst,
                                            axes = spectra_axes[1],
                                            save_fig = save_fig,
                                            fig_size = fig_size)
            # Convert to df where the index is the period
            spectra_axes = (spectra_axes_x, spectra_axes_y)
            spectra_results_df = pd.concat([spa_x_df, spa_y_df], axis=1)

        # ===================================================================================================
        # ======================================= QUERY THE BASE SHEAR ======================================
        # ===================================================================================================
        if save_b_shear is not None:
            # Init the query
            time_series, shear_x, shear_y, shear_z = self.base_shear()
            shear_x = list(np.array(shear_x) / 2.6)
            shear_y = list(np.array(shear_y) / 2.8)

            # Init plot params
            nch  = NCh433_2012(zone, soil_category, importance)
            Qmax = nch.computeMaxBaseShear_c6_3_7_2(structure_weight)

            # Plot the data
            self.plotter.save_path = Path(save_b_shear)
            self.plotter.setup_direction(x_direction=True)
            shear_axes_x = self.plotter.plotShearBaseOverTime(
                                        time           = time_series,
                                        time_shear_fma = shear_x,
                                        Qmax           = Qmax,
                                        dir_           = 'x',
                                        axes           = base_shear_axes[0],
                                        save_fig       = save_fig,
                                        fig_size       = fig_size,
                                        mean           = False
                                        )
            self.plotter.setup_direction(x_direction=False)
            shear_axes_y = self.plotter.plotShearBaseOverTime(
                                        time           = time_series,
                                        time_shear_fma = shear_y,
                                        Qmax           = Qmax,
                                        dir_           = 'y',
                                        axes           = base_shear_axes[1],
                                        save_fig       = save_fig,
                                        fig_size       = fig_size,
                                        mean           = False
                                        )
            base_shear_results_df = pd.DataFrame({'Shear X': shear_x,
                                                  'Shear Y': shear_y,
                                                  'Shear Z': shear_z},
                                                 index=time_series).rename_axis('Time Step')
            base_shear_axes = (shear_axes_x, shear_axes_y)
        # ===================================================================================================
        # =========================================== END QUERIES ===========================================
        # ===================================================================================================
        axes = drift_axes, spectra_axes, base_shear_axes
        end_time = time.time()
        self.close_connection()
        if verbose:
            print(f'Elapsed time: {round(end_time - start_time)} seconds.')
        return drift_results_df, spectra_results_df, base_shear_results_df, axes




