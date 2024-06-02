# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
from pyseestko.db_manager import DataBaseManager        #type: ignore
from pyseestko.plotting   import Plotting               #type: ignore
from pyseestko.utilities  import NCh433_2012            #type: ignore
from pyseestko.utilities  import initialize_ssh_tunnel  #type: ignore
from pyseestko.utilities  import checkMainQueryInput  #type: ignore
from pathlib              import Path
from typing               import List, Dict, Tuple 
import pandas as pd
import pickle
import time

# ==================================================================================================
# MAIN FUNCTION
# ==================================================================================================

def executeMainQuery(
    # Params
    sim_types   : List[int], 
    stations    : List[int], 
    iterations  : List[int], 
    nsubs_lst   : List[int], 
    mag_map     : Dict[float, str], 
    loc_map     : Dict[int, str], 
    rup_map     : Dict[int, str], 
    user        : str, 
    password    : str, 
    host        : str, 
    database    : str,
    
    # Optional params
    linearity   : int  = 1, 
    stories     : int  = 20, 
    magnitude   : int  = 6.7, 
    rupture_type: int  = 1, 
    save_drift  : str  = None, 
    save_spectra: str  = None, 
    save_b_shear: str  = None, 
    windows     : bool = True
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, List[pd.DataFrame]], Dict[str, pd.DataFrame]]:
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
   
    # Map the sim_types
    checkMainQueryInput(sim_types, nsubs_lst, iterations, stations)
    sim_type_map = {1: 'FixBase', 2: 'AbsBound', 3: 'DRM'}
    
    # Iterative params
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
                                    station)
                    query   = ProjectQueries(user, password, host, database, # The class that queries the database
                                            sim_type, linearity,
                                            mag_map.get(magnitude,    'None'),
                                            rup_map.get(rupture_type, 'None'), iteration,
                                            loc_map.get(station,      'None'),
                                            stories, nsubs, plotter, windows=windows)
                    
                    # Get the results for zone = 'Las Condes', soil_category = 'B' and importance = 2
                    drift, spectra, base_shear = query.getAllResults(save_drift, 
                                                                    save_spectra, 
                                                                    save_b_shear, 
                                                                    structure_weight)
                    # Append the results to the dicts
                    sim_type_name = sim_type_map[sim_type]
                    sim_name = f'{sim_type_name}_20f{nsubs}s_rup_bl_{iteration}_s{station}'
                    drifts_df_dict[sim_name]     = drift
                    spectra_df_dict[sim_name]    = spectra
                    base_shear_df_dict[sim_name] = base_shear
    print('Done!')
    return drifts_df_dict, spectra_df_dict, base_shear_df_dict

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

def getSpectraDfs(spectra_df_lst:List[pd.DataFrame]):
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
        windows     :bool=True):

        # Save attributes
        self.values  = (sim_type, linearity, magnitude, rupture_type, iteration, location, stories, subs)
        self.plotter = plotter

        # Connect the model to the database
        if windows:
            initialize_ssh_tunnel()
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
        save_drift       :str|None,
        save_spectra     :str|None,
        save_b_shear     :str|None,
        structure_weight :float,
        zone             :str = 'Las Condes',
        soil_category    :str = 'B',
        importance       :int = 2
                      ):
        # Init params
        start_time = time.time()
        drift_results_df      = None
        spectra_results_df    = None
        base_shear_results_df = None
        
        # ===================================================================================================
        # ==================================== QUERY THE DRIFT PER FLOOR ====================================
        # ===================================================================================================
        if save_drift is not None:
            # Init the query
            max_center_x, max_center_y, max_corner_x, max_corner_y = self.story_drift()

            # Plot the data
            self.plotter.save_path = Path(save_drift)
            ax                = self.plotter.plotModelDrift(max_corner_x, max_center_x, max_corner_y, max_center_y)
            drift_results_df  = pd.DataFrame({'CM x': max_center_x, 
                                              'CM y': max_center_y, 
                                              'Max x': max_corner_x, 
                                              'Max y': max_corner_y}, 
                                             index=range(1, len(max_corner_x)+1)).rename_axis('Story')
            

        # ===================================================================================================
        # ===================================== QUERY THE STORY SPECTRUM ====================================
        # ===================================================================================================
        if save_spectra is not None:
            # Init the query
            accel_df, story_nodes_df = self.stories_spectra()

            # Plot the data
            self.plotter.save_path = Path(save_spectra)
            stories_lst = [1,5,10,15,20]
            ax, spa_x_df = self.plotter.plotLocalStoriesSpectrums(accel_df, story_nodes_df, 'x', stories_lst, soften=True)
            ax, spa_y_df = self.plotter.plotLocalStoriesSpectrums(accel_df, story_nodes_df, 'y', stories_lst, soften=True)
            
            # Convert to df where the index is the period
            spectra_results_df = [spa_x_df, spa_y_df]

        # ===================================================================================================
        # ======================================= QUERY THE BASE SHEAR ======================================
        # ===================================================================================================
        if save_b_shear is not None:
            # Init the query
            time_series, shear_x, shear_y, shear_z = self.base_shear()

            # Init plot params
            nch  = NCh433_2012(zone, soil_category, importance)
            Qmin = nch.computeMinBaseShear_c6_3_7_1(structure_weight)
            Qmax = nch.computeMaxBaseShear_c6_3_7_2(structure_weight)

            # Plot the data
            self.plotter.save_path = Path(save_b_shear)
            ax = self.plotter.plotShearBaseOverTime(time_series, shear_x, Qmin, Qmax, 'x')
            ax = self.plotter.plotShearBaseOverTime(time_series, shear_y, Qmin, Qmax, 'y')
            base_shear_results_df = pd.DataFrame({'Shear X': shear_x, 
                                                  'Shear Y': shear_y, 
                                                  'Shear Z': shear_z}, 
                                                 index=time_series).rename_axis('Time Step')

        # ===================================================================================================
        # =========================================== END QUERIES ===========================================
        # ===================================================================================================
        end_time = time.time()
        self.close_connection()
        print(f'Elapsed time: {end_time - start_time} seconds.')
        return drift_results_df, spectra_results_df, base_shear_results_df
        



