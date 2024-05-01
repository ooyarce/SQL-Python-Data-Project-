# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
from pyseestko.db_manager import DataBaseManager        #type: ignore
from pyseestko.plotting   import Plotting               #type: ignore
from pyseestko.utilities  import NCh433_2012            #type: ignore
from pyseestko.utilities  import initialize_ssh_tunnel  #type: ignore
from pathlib              import Path
from typing               import List, Dict, Tuple 
import pandas as pd
import pickle
import time

# ==================================================================================================
# MAIN FUNCTION
# ==================================================================================================
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
def executeMainQuery(
    # Params
    sim_types   : List[int], 
    stations    : List[int], 
    iterations  : List[int], 
    nsubs_lst   : List[int], 
    mag_map     : Dict[int, str], 
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
    windows     : bool = True):
    
    # Iterative params
    drifts_df_lst     = []
    spectra_df_lst    = []
    base_shear_df_lst = []

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
                    # Append the results to the lists
                    drifts_df_lst.append(drift)
                    spectra_df_lst.append(spectra)
                    base_shear_df_lst.append(base_shear)
    print('Done!')
    return drifts_df_lst, spectra_df_lst, base_shear_df_lst

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
            ax, T, Spx = self.plotter.plotLocalStoriesSpectrums(accel_df, story_nodes_df, 'x', stories_lst, soften=True)
            ax, _, Spy = self.plotter.plotLocalStoriesSpectrums(accel_df, story_nodes_df, 'y', stories_lst, soften=True)
            spectra_results_df = pd.DataFrame({'Spectrum X': Spx, 
                                               'Spectrum Y': Spy}, 
                                              index=T).rename_axis('Period [T]')


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
        


