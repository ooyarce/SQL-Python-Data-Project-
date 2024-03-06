# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
from pyseestko.db_manager import DataBaseManager        #type: ignore
from pyseestko.plotting   import Plotting               #type: ignore
from pyseestko.utilities  import NCh433_2012            #type: ignore
from pyseestko.utilities  import initialize_ssh_tunnel  #type: ignore
from pathlib              import Path
import time
import pickle

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
        structure_max_drift_per_floor = data[0]
        max_corner_x = pickle.loads(structure_max_drift_per_floor[1]) # type: ignore
        max_corner_y = pickle.loads(structure_max_drift_per_floor[2]) # type: ignore
        max_center_x = pickle.loads(structure_max_drift_per_floor[3]) # type: ignore
        max_center_y = pickle.loads(structure_max_drift_per_floor[4]) # type: ignore

        return max_corner_x, max_corner_y, max_center_x, max_center_y

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
        structure_perfomance = data[0]
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
        base_shear_over_time = data[0]
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
        zone             :str,
        soil_category    :str,
        importance       :int
                      ):
        # ===================================================================================================
        # ==================================== QUERY THE DRIFT PER FLOOR ====================================
        # ===================================================================================================
        if save_drift is not None:
            # Init the query
            start_time = time.time()
            max_corner_x, max_corner_y,\
            max_center_x, max_center_y = self.story_drift()

            # Plot the data
            self.plotter.save_path = Path(save_drift)
            ax                = self.plotter.plotModelDrift(max_corner_x, max_center_x, max_corner_y, max_center_y)


        # ===================================================================================================
        # ===================================== QUERY THE STORY SPECTRUM ====================================
        # ===================================================================================================
        if save_spectra is not None:
            # Init the query
            accel_df, story_nodes_df = self.stories_spectra()

            # Plot the data
            self.plotter.save_path = Path(save_spectra)
            stories_lst = [1,5,10,15,20]
            ax = self.plotter.plotLocalStoriesSpectrums(accel_df, story_nodes_df, 'x', stories_lst, soften=True)
            ax = self.plotter.plotLocalStoriesSpectrums(accel_df, story_nodes_df, 'y', stories_lst, soften=True)


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

        # ===================================================================================================
        # =========================================== END QUERIES ===========================================
        # ===================================================================================================
        end_time = time.time()
        self.close_connection()
        print(f'Elapsed time: {end_time - start_time} seconds.')

