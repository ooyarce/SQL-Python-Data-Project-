# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
# Objects
from mysql.connector.errors import DatabaseError
from concurrent.futures     import ThreadPoolExecutor
from pathlib                import Path
from pyseestko.errors       import SQLFunctionError, DataBaseError
from pyseestko.db_manager   import DataBaseManager
from pyseestko.model_info   import ModelInfo
from pyseestko              import utilities as utl

# Packages
import pandas as pd
import numpy  as np
import subprocess
import xlsxwriter 
import datetime
import warnings
import pickle
import json
import time
import re




# ==================================================================================
# MAIN CLASS
# ==================================================================================
class ModelSimulation:
    """
    This class is used to manage the connection to the database.
    It's used to upload the results of the analysis to the database.
    It works with the ModelInfo class to get the data from the model.
    The main function is simulation, which uploads the results to the database.
    The other functions are used to upload the results to the database.
    The algorithm is the following:
        1. Connect to the database
        2. Get the data from the model
        3. Upload the data to the database
    The parameters are the following:
    
    Parameters
    ----------
    main_path : Path
        Path to the main file of the model.
    user : str, optional
        User of the database. The default is 'omarson'.
    password : str, optional
    host : str, optional
        Host of the database. The default is 'localhost'.
    database : str, optional
        Database name. The default is 'stkodatabase'.
    kwargs : dict, optional
        Dictionary with the parameters of the simulation. There are a lot of parameters, so it's better to see the code.
    """
    
    
    
    # ==================================================================================
    # INIT PARAMS
    # ==================================================================================
    def __init__(self, main_path:Path, user='omarson', password='Mackbar2112!', host='localhost', database='stkodatabase', **kwargs):
        print('=============================================')
        # Define generic parameters
        bench_cluster = "Esmeralda HPC Cluster by jaabell@uandes.cl"
        try:
            self.model_path = main_path.parents[3]
            self.stko_model_name = next(self.model_path.glob('*.scd')).name
        except StopIteration:
            try:
                self.model_path = main_path.parent
                self.stko_model_name = next(self.model_path.glob('*.scd')).name
            except StopIteration:
                self.model_path = main_path.parent
                self.stko_model_name = 'No model name found'
        # Simulation default parameters
        self._sim_comments      = kwargs.get("sim_comments", "No comments")
        self._sim_opt           = kwargs.get("sim_opt", "No options yet")
        self._sim_stage         = kwargs.get("sim_stage", "No stage yet")
        self._sim_type          = kwargs.get("sim_type", 1)
        self._sm_input_comments = kwargs.get("sm_input_comments","No comments")
        self._model_name        = kwargs.get("model_name", 'Testing Model')
        self._model_comments    = kwargs.get("model_comments", "No comments")
        self._bench_cluster     = kwargs.get("bench_cluster", bench_cluster)
        self._bench_comments    = kwargs.get("bench_comments", "No comments")
        self._perf_comments     = kwargs.get("perf_comments", "No comments")
        self._specs_comments    = kwargs.get("str_specs_comments", "No comments")
        self._box_comments      = kwargs.get("box_comments", "No comments")
        self._gspecs_comments   = kwargs.get("gspecs_comments", "No comments")
        self._pga_units         = kwargs.get("pga_units", "m/s/s")
        self._resp_spectrum     = kwargs.get("resp_spectrum", "m/s/s")
        self._abs_acc_units     = kwargs.get("abs_acc_units", "m/s/s")
        self._rel_displ_units   = kwargs.get("rel_displ_units", "m")
        self._max_drift_units   = kwargs.get("max_drift_units", "m")
        self._max_bs_units      = kwargs.get("max_bs_units", "kN")
        self._bs_units          = kwargs.get("bs_units", "kN")
        self._linearity         = kwargs.get("linearity", 1)
        self._time_step         = kwargs.get("time_step", 0.0025)
        self._total_time        = kwargs.get("total_time", 40)
        self._jump              = kwargs.get("jump", 8)
        self._cfactor           = kwargs.get("cfactor", 1.0)
        self._load_df_info      = kwargs.get("load_df_info", True)
        self._vs30              = kwargs.get("vs30", 750) #ms
        self._dimentions        = kwargs.get("soil_dim", "3D")
        self._material          = kwargs.get("soil_mat_name", "Elastoisotropic")
        self._soil_ele_type     = kwargs.get("soil_ele_type", "SSPBrick Element")
        self._mesh_struct       = kwargs.get("mesh_struct", "Structured")
        print(f'=========== {self._model_name} =============')
        print('=============================================')

        # Assert values
        if self._linearity not in [1,2]:
            raise AttributeError("Linearity can only be 1 (Linear) or 2 (Non-Linear)")
        if self._sim_type not in [1,2,3]:
            raise AttributeError("Simulation type can only be 1 (Fix Base), 2 (AbsBound) or 3(DRM)")

        # Connect to Dabase
        self._test_mode  = kwargs.get("windows_os", False)
        self.db_user     = user
        self.db_password = password
        self.db_host     = host
        self.db_database = database
        self.connect()
        print('=============================================')

        # Load model info
        if self._load_df_info:
            self.loadModelInfo(main_path)
            self.loadDataFrames()

        # Init database tables in case they are not created
        try:
            self.model_linearity()
            self.simulation_type()
        except DatabaseError as e:
            pass




    # ==================================================================================
    # SQL FUNCTIONS
    # ==================================================================================
    def simulation(self, **kwargs):
        """
        This is the main function to export the simulation into the database.
        """
        # Initialize parameters
        init_time    = time.time()
        cursor       = self.Manager.cursor
        sim_comments = kwargs.get("sim_comments", self._sim_comments)
        sim_opt      = kwargs.get("sim_opt", self._sim_opt)
        sim_stage    = kwargs.get("sim_stage", self._sim_stage)
        sim_type     = kwargs.get("sim_type", self._sim_type)

        print("---------------------------------------------|")
        print("----------EXPORTING INTO DATABASE------------|")
        print("---------------------------------------------|")

        # Fills simulation and simulation_sm_input tables
        self.simulation_model()
        Model = cursor.lastrowid
        self.model_specs_box(Model)
        self.model_specs_global(Model)

        SM_Input = self.simulation_sm_input()

        # Fet date
        date = datetime.datetime.now()
        date = date.strftime("%B %d, %Y")

        # Insert data into database
        insert_query = (
            "INSERT INTO simulation("
            "idModel, idSM_Input,"
            "idType, SimStage, SimOptions, Simdate,"
            "Comments) VALUES(%s,%s,%s,%s,%s,%s,%s)")
        values = (Model, SM_Input,sim_type, sim_stage, sim_opt, date, sim_comments)
        try:
            self.Manager.insert_data(insert_query, values)
        except Exception as e:
            raise SQLFunctionError("Error while updating simulation table") from e
        end_time = time.time()
        print("simulation table updated correctly!\n")
        print(f"Time elapsed: {end_time-init_time:.2f} seconds")
        print("---------------------------------------------|")
        print("---------------------------------------------|")
        print("---------------------------------------------|\n")

    def simulation_sm_input(self, **kwargs):
        """
        This function is used to export the simulation sm input into the database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        sm_input_comments = kwargs.get("sm_input_comments", self._sm_input_comments)

        # Define the values for the columns that must be unique together
        unique_values = (self.magnitude, self.rupture, self.location, self.iteration)

        # Check if an entry already exists with these unique values
        existing_entry = self.Manager.check_if_sm_input(unique_values)
        if existing_entry:
            # An entry with the same values already exists, so reuse its idSM_Input
            sm_input_id = existing_entry[0]
            print(f"Reusing existing simulation_sm_input with id: {sm_input_id}")

        else:
            # PGA y Spectrum
            Pga = self.sm_input_pga()
            Pga = cursor.lastrowid
            Spectrum = self.sm_input_spectrum()
            Spectrum = cursor.lastrowid

            # Insert data into database
            insert_query = (
                "INSERT INTO simulation_sm_input(idPGA, idSpectrum, Magnitude, "
                "Rupture_type, Location, RealizationID, Comments) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s)")
            values = (Pga,Spectrum,self.magnitude,self.rupture,self.location,self.iteration,sm_input_comments)
            try:
                cursor.execute(insert_query, values)
                print('simulation_sm_input table updated correctly!\n')
                sm_input_id = cursor.lastrowid  # Get the new idSM_Input
                print(f"Inserted new simulation_sm_input with id: {sm_input_id}")
            except Exception as e:
                raise SQLFunctionError("Error while updating simulation_sm_input table") from e
        return sm_input_id

    def simulation_model(self, **kwargs):
        """
        This function is used to export data into the simulation_model table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        model_name = kwargs.get("model_name", self._model_name)
        model_comments = kwargs.get("model_comments", self._model_comments)

        # Fills benchmark, structure perfomance and specs structure tables
        self.model_benchmark()
        Benchmark = cursor.lastrowid
        self.model_structure_perfomance()
        StructurePerfomance = cursor.lastrowid
        SpecsStructure = self.model_specs_structure()

        # Insert data into database
        insert_query = ("INSERT INTO simulation_model("
                        "idBenchmark,idStructuralPerfomance,idSpecsStructure,"
                        "ModelName,Comments) VALUES(%s,%s,%s,%s,%s)")
        values = (Benchmark,StructurePerfomance,SpecsStructure,model_name,model_comments)
        try:
            cursor.execute(insert_query, values) # type: ignore
            print("simulation_model table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating simulation_model table") from e

    def model_benchmark(self, **kwargs):
        # ------------------------------------------------------------------------------------------------------------------------------------
        # Get calculus time from log file, nodes, threads and comments
        # ------------------------------------------------------------------------------------------------------------------------------------
        # Initialize parameters
        cursor = self.Manager.cursor
        bench_cluster = kwargs.get("bench_cluster", self._bench_cluster)
        comments = kwargs.get("bench_comments", self._bench_comments)

        # Insert data into database
        insert_query = (
            "INSERT INTO model_benchmark (JobName,SimulationTime,"
            "MemoryResults,MemoryModel,ClusterNodes,CpuPerNodes,ClusterName,"
            "Comments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")


        simulation_time = self.convert_and_store_time(self.simulation_time)
        values = (self.jobname,
                  simulation_time,
                  self.memory_by_results,
                  self.memory_by_model,
                  self.cluster_nodes,
                  self.threads,
                  bench_cluster,
                  comments)
        try:
            cursor.execute(insert_query, values)
            print("model_benchmark table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating model_benchmark table") from e

    def model_specs_structure(self, **kwargs):
        """
        This function is used to export data into the model_specs_structure table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        comments = kwargs.get("specs_comments", self._specs_comments)
        nnodes    = self.str_nnodes
        nelements = self.str_nelements

        # Define the values for the columns that must be unique together
        unique_values = (self._linearity,nnodes,nelements,self.stories,self.subs,json.dumps(self.heights),comments)

        # Check if an entry already exists with these unique values
        existing_entry = self.Manager.check_if_specs_structure(unique_values)
        if existing_entry:
            # An entry with the same values already exists, so reuse its idSM_Input
            model_specs_structure_id = existing_entry[0]
            print(f"Reusing existing model_specs_structure with id: {model_specs_structure_id}")
        else:
            # Upload results to the database
            insert_query = (
                "INSERT INTO model_specs_structure ("
                "idLinearity, Nnodes, Nelements, Nstories, Nsubs, InterstoryHeight, Comments) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)")
            values = (self._linearity,nnodes,nelements,self.stories,self.subs,json.dumps(self.heights),comments)
            try:
                cursor.execute(insert_query, values) # type: ignore
                model_specs_structure_id = cursor.lastrowid  # Get the new idSM_Input
                print(f"Inserted new model_specs_structure with id: {model_specs_structure_id}")
            except Exception as e:
                raise SQLFunctionError("Error while updating model_specs_structure table") from e
        print("model_specs_structure table updated correctly!\n")
        return model_specs_structure_id

    def model_specs_box(self, idModel, **kwargs):
        """
        This function is used to export data into the model_specs_box table database.
        """
        cursor = self.Manager.cursor
        comments = kwargs.get("box_comments", self._box_comments)

        # Upload results to the database
        insert_query = (
            "INSERT INTO model_specs_box ("
            "idModel, idLinearity, Vs30, Nnodes, Nelements, Dimentions, Material, ElementType, Comments) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        values = (idModel, self._linearity, self._vs30, self.soil_nnodes, self.soil_nelements, self._dimentions, self._material, self._soil_ele_type, comments)
        try:
            cursor.execute(insert_query, values)
            print("model_specs_box table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating model_specs_box table") from e

    def model_specs_global(self, idModel, **kwargs):
        cursor = self.Manager.cursor
        comments = kwargs.get("gspecs_comments", self._gspecs_comments)

        # Upload results to the database
        insert_query = (
            "INSERT INTO model_specs_global ("
            "idModel, Nnodes, Nelements, Npartitions, MeshStructuration, Comments)"
            "VALUES (%s,%s,%s,%s,%s,%s)")
        values = (idModel, self.glob_nnodes, self.glob_nelements, self.npartitions, self._mesh_struct, comments)
        try:
            cursor.execute(insert_query, values)
            print("model_specs_global table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating model_specs_global table") from e

    def model_structure_perfomance(self, **kwargs):
        """
        This function is used to export data into the model_structure_perfomance table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        comments = kwargs.get("perf_comments", self._perf_comments)

        # Fills base shear
        self.structure_base_shear()
        BaseShear = cursor.lastrowid

        # Fills max base shear
        self.structure_max_base_shear()
        MaxBaseShear = cursor.lastrowid

        # Fills absolute accelerations
        self.structure_abs_acceleration()
        AbsAccelerations = cursor.lastrowid

        # Fills relative displacements
        self.structure_relative_displacements()
        RelativeDisplacements = cursor.lastrowid

        # Fills max drift per floor
        self.structure_max_drift_per_floor()
        MaxDriftPerFloor = cursor.lastrowid

        # Fills the story accelerations
        dump_data = self.paralelize_serialization([self.accel_mdf[::self._jump], self.story_nodes_df.iloc[8:]])
        #StoryAccelerations = pickle.dumps(self.accel_mdf[::self._jump])
        StoryAccelerations = dump_data[0]

        # Fills the nodes id of the stories
        #StoryNodesDataFrame = pickle.dumps(self.story_nodes_df.iloc[8:])
        StoryNodesDataFrame = dump_data[1]

        # Upload results to the database
        insert_query = (
            "INSERT INTO model_structure_perfomance ("
            "idBaseShear,idAbsAccelerations,idRelativeDisplacements,idMaxBaseShear,idMaxDriftPerFloor,"
            "StoryAccelerations,StoryNodesDataFrame,Comments) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
        values = (BaseShear,AbsAccelerations,RelativeDisplacements,MaxBaseShear,MaxDriftPerFloor,
                  StoryAccelerations, StoryNodesDataFrame, comments)
        try:
            cursor.execute(insert_query, values) # type: ignore
            print("model_structure_perfomance table updated correctly!\n")
        except Exception as e:
            raise SQLFunctionError("Error while updating model_structure_perfomance table") from e

    def structure_abs_acceleration(self, **kwargs):
        """
        This function is used to export data into the structure_abs_acceleration table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        units = kwargs.get("abs_acc_units", self._abs_acc_units)

        # Convert Data to JSON format and reduce the size of the data
        time_series = pickle.dumps(self.timeseries[::self._jump])
        matrixes    = [pickle.dumps(self.accel_dfs[i].iloc[::self._jump])for i in range(3)]

        # Upload results to the database
        insert_query = ("INSERT INTO structure_abs_acceleration ("
                        "TimeSeries, AbsAccX, AbsAccY, AbsAccZ, Units) "
                        "VALUES(%s,%s,%s,%s,%s)")
        values = (time_series, matrixes[0], matrixes[1], matrixes[2], units)
        try:
            cursor.execute(insert_query, values)
            print("structure_abs_acceleration table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating structure_abs_acceleration table") from e

    def structure_relative_displacements(self, **kwargs):
        """
        This function is used to export data into the structure_relative_displacements table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        units = kwargs.get("rel_displ_units", self._rel_displ_units)

        # Convert Data to JSON format and reduce the size of the data
        time_series = pickle.dumps(self.timeseries[::self._jump])
        matrixes = [pickle.dumps(self.displ_dfs[i].iloc[::self._jump])for i in range(3)]

        # Upload results to the database
        insert_query = ("INSERT INTO structure_relative_displacements ("
                        "TimeSeries, DispX, DispY, DispZ, Units) "
                        "VALUES(%s,%s,%s,%s,%s)")
        values = (time_series, matrixes[0], matrixes[1], matrixes[2], units)
        try:
            cursor.execute(insert_query, values)
            print("structure_relative_displacements table updated correctly!\n")
        except Exception as e:
            raise SQLFunctionError("Error while updating structure_relative_displacements table") from e

    def structure_max_drift_per_floor(self, **kwargs):
        """
        This function is used to export data into the structure_max_drift_per_floor table database.

        loc: 0 -> X direction
        loc: 1 -> Y direction

        """
        # Initialize parameters
        cursor = self.Manager.cursor
        units = kwargs.get("max_drift_units", self._max_drift_units)
        displacements = self.displ_dfs
        center_drifts = [[], []]
        corner_drifts = [[], []]

        # Compute Inter-Storey Drifts
        for loc, df in enumerate(displacements[:2]):
            # Inter-storey drifts between the i-esim and (i-1)-esim storeys
            for i in range(self.stories, 0, -1):
                story_nodes      = self.story_nodes_df.loc[i].index
                lowwer_story_nodes = self.story_nodes_df.loc[i-1].index
                compute_drifts   = [self._computeDriftBetweenNodes(df[current_node], df[following_node], self.heights[i-1], loc)
                                    for current_node, following_node in zip(story_nodes, lowwer_story_nodes)]
                drift_df = pd.concat(compute_drifts, axis=1)
                center   = drift_df.mean(axis=1).max()
                corner   = drift_df.max().max()
                center_drifts[loc].append(center)
                corner_drifts[loc].append(corner)
            center_drifts[loc].reverse()
            corner_drifts[loc].reverse()
        # Upload results to the database
        insert_query = ("INSERT INTO structure_max_drift_per_floor ("
                        "MaxDriftCornerX, MaxDriftCornerY, MaxDriftCenterX, "
                        "MaxDriftCenterY, Units) VALUES (%s,%s,%s,%s,%s)")
        values = (pickle.dumps(corner_drifts[0]),pickle.dumps(corner_drifts[1]),pickle.dumps(center_drifts[0]),pickle.dumps(center_drifts[1]),units)
        try:
            cursor.execute(insert_query, values)
            print("structure_max_drift_per_floor table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating structure_max_drift_per_floor table") from e

    def structure_base_shear(self, **kwargs):
        """
        This function is used to export data into the structure_base_shear table database using
        the reactions obtained in the simulation.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        units = kwargs.get("bs_units", self._bs_units)

        # Convert Data to JSON format and reduce the size of the data
        timeseries = pickle.dumps(self.timeseries[::self._jump])

        if self._sim_type == 1:
            df = self.react_mdf.sum(axis=1)
            matrixes = [df.xs(dir, level='Dir') for dir in ['x', 'y', 'z']]
            matrixes = [pickle.dumps(matrix.iloc[::self._jump]) for matrix in matrixes]

        else:
            matrixes = self._computeBaseShearByAccelerations()[0]
            matrixes = [pickle.dumps(matrix[::self._jump]) for matrix in matrixes]

        # Upload results to the database
        insert_query = "INSERT INTO structure_base_shear (TimeSeries, ShearX, ShearY, ShearZ, Units) VALUES (%s,%s,%s,%s,%s)"
        values = (timeseries, matrixes[0], matrixes[1], matrixes[2],units)
        try:
            cursor.execute(insert_query, values)
            print("structure_base_shear table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating structure_base_shear table") from e

    def structure_max_base_shear(self, **kwargs):
        """
        This function is used to export data into the structure_max_base_shear table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        units = kwargs.get("max_bs_units", self._max_bs_units)

        # Get max base shear
        if self._sim_type == 1:
            df = self.react_mdf.sum(axis=1)
            shear_x_ss = df.xs('x', level='Dir').abs().max()
            shear_y_ss = df.xs('y', level='Dir').abs().max()
            shear_z_ss = df.xs('z', level='Dir').abs().max()
        else:
            shear_x_ss = self._computeBaseShearByAccelerations()[1][0]
            shear_y_ss = self._computeBaseShearByAccelerations()[1][1]
            shear_z_ss = self._computeBaseShearByAccelerations()[1][2]

        # Upload results to the database
        insert_query = ("INSERT INTO structure_max_base_shear ("
                        "MaxX, MaxY, MaxZ, Units) VALUES (%s,%s,%s,%s)")

        values = (f'{shear_x_ss:.2f}', f'{shear_y_ss:.2f}', f'{shear_z_ss:.2f}', units)
        try:
            cursor.execute(insert_query, values)
            print("structure_max_base_shear table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating structure_max_base_shear table") from e

    def sm_input_pga(self, **kwargs):
        """
        This function is used to export data into the sm_input_pga table database.
        """
        # Initialize parameters
        cursor   = self.Manager.cursor
        units    = kwargs.get("pga_units", self._pga_units)
        input_df = self._computeInputAccelerationsDF()

        az = input_df.xs('z', level='Dir').to_numpy()
        ae = input_df.xs('x', level='Dir').to_numpy()
        an = input_df.xs('y', level='Dir').to_numpy()

        PGA_max_z = az.argmax()
        PGA_max_e = ae.argmax()
        PGA_max_n = an.argmax()
        PGA_min_n = an.argmin()
        PGA_min_z = az.argmin()
        PGA_min_e = ae.argmin()

        PGA_max_e_rounded = round(ae[PGA_max_e].item(), 2)
        PGA_min_e_rounded = round(ae[PGA_min_e].item(), 2)
        PGA_max_n_rounded = round(an[PGA_max_n].item(), 2)
        PGA_min_n_rounded = round(an[PGA_min_n].item(), 2)
        PGA_max_z_rounded = round(az[PGA_max_z].item(), 2)
        PGA_min_z_rounded = round(az[PGA_min_z].item(), 2)


        PGAx = json.dumps({"max": PGA_max_e_rounded,"min": PGA_min_e_rounded})
        PGAy = json.dumps({"max": PGA_max_n_rounded,"min": PGA_min_n_rounded})
        PGAz = json.dumps({"max": PGA_max_z_rounded,"min": PGA_min_z_rounded})

        # Upload results to the database
        insert_query = ("INSERT INTO sm_input_pga ("
                        "PGA_X, PGA_Y, PGA_Z, Units) VALUES(%s,%s,%s,%s)")
        values = (PGAx, PGAy, PGAz, units)
        try:
            cursor.execute(insert_query, values)
            print("sm_input_pga table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating sm_input_pga table") from e

    def sm_input_spectrum(self, **kwargs):
        """
        This function is used to export data into the sm_input_spectrum table database.
        """
        # Initialize parameters
        cursor   = self.Manager.cursor
        units    = kwargs.get("resp_spectrum", self._resp_spectrum)
        dt       = np.linspace(0.003, 2, 1000)
        nu       = 0.05
        w        = 2 * np.pi / np.array(dt)

        # Spectrum East
        ae = self.input_df.xs('x', level='Dir')['Acceleration'].to_list()[::16]
        Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [utl.pwl(ae, wi, nu)]]

        # Spectrum North
        an = self.input_df.xs('y', level='Dir')['Acceleration'].to_list()[::16]
        Spn = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [utl.pwl(an, wi, nu)]]

        # Spectrum Vertical
        az = self.input_df.xs('z', level='Dir')['Acceleration'].to_list()[::16]
        Spz = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [utl.pwl(az, wi, nu)]]

        # Upload results to the database
        insert_query = ("INSERT INTO sm_input_spectrum("
                        "SpectrumX, SpectrumY, SpectrumZ, Units) "
                        "VALUES (%s,%s,%s,%s)")
        values = (pickle.dumps(Spe), pickle.dumps(Spn), pickle.dumps(Spz), units)
        try:
            cursor.execute(insert_query, values)
            print("sm_input_spectrum table updated correctly!\n")
        except Exception as e:
                raise SQLFunctionError("Error while updating sm_input_spectrum table") from e




    # ==================================================================================
    # LOAD SIMULATION INFORMATION AND DATA POST PROCESSING IN PANDAS DATAFRAMES
    # ==================================================================================
    def loadModelInfo(self, main_path,verbose=True):
        # Initialize Model Info
        self.model_info = ModelInfo(main_path, sim_type=self._sim_type,verbose=verbose)
        self.path       = main_path.parent
        self.timeseries = np.arange(self._time_step, self._total_time+self._time_step, self._time_step)

        # Compute structure  information
        if verbose: print('Computing structure information...')

        # ================================================
        # Get job name, nodes, threads and logname
        # ================================================
        with open(self.path/"run.sh") as data:
            lines = data.readlines()
            self.jobname = lines[1].split(" ")[1].split("=")[1]
            self.cluster_nodes = int(lines[2].split("=")[1])
            self.threads = int(lines[3].split("=")[1])
            self.logname = lines[4].split("=")[1].split("#")[0].strip()

        # ================================================
        # Get simulation time and memory results
        # ================================================
        # Get simulation time
        with open(self.path/self.logname) as log:
            self.simulation_time = ""
            for row in log:
                if "Elapsed:" in row:
                    value = row.split(" ")[1]
                    self.simulation_time = f"{value} seconds"  # first value of query
                    break

        # Get memort by results
        folder_names = ["Accelerations", "Displacements", "PartitionsInfo"]
        if self._sim_type == 1:
            folder_names.append("Reactions")

        # Calcular el tamaño en paralelo
        with ThreadPoolExecutor() as executor:
            tamanos = list(executor.map(utl.folder_size, [self.path] * len(folder_names), folder_names))

        # Sumar los tamaños y convertir a MB
        self.memory_by_results = sum(tamanos) / (1024 * 1024)
        self.memory_by_results = f"{self.memory_by_results:.2f} Mb"

        # Get model memory
        model_name = next(self.model_path.glob("*.scd"))
        self.memory_by_model = f"{model_name.stat().st_size / (1024 * 1024):.2f} Mb"
        
        # ================================================
        # Get model unique params
        # ================================================
        # Get magnitude
        magnitude = main_path.parents[2].name[1:]
        self.magnitude = f"{magnitude} Mw"
        if self.magnitude not in ['6.5 Mw', '6.7 Mw', '6.9 Mw', '7.0 Mw']:
            self.magnitude = "Not defined"

        # Get rupture type
        ruptures_mapping = {
            "bl": "Bilateral",
            "ns": "North-South",
            "sn": "South-North"}
        folder_name = main_path.parents[1].name
        try:
            rup_type = folder_name.split("_")[1]
            self.rupture = ruptures_mapping.get(rup_type)
            if not self.rupture:
                warnings.warn("Folders name are not following the format rup_[bl/ns/sn]_[iteration].")
        except IndexError:
            self.rupture = "Not defined"
            warnings.warn("Folders name are not following the format rup_[bl/ns/sn]_[iteration].")
        # Get realization id
        iter_name = main_path.parents[1].name
        if len(iter_name.split("_")) == 3:
            self.iteration = iter_name.split("_")[2]
        else:
            warnings.warn(f"Unknown Iteration for {iter_name=}. Check folder iteration name!")
            self.iteration = "0"

        # Get location
        location_mapping = {
            0: "UAndes Campus",
            1: "Near field North",
            2: "Near field Center",
            3: "Near field South",
            4: "Intermediate field North",
            5: "Intermediate field Center",
            6: "Intermediate field South",
            7: "Far field North",
            8: "Far field Center",
            9: "Far field South"}
        try:
            self.station = int((main_path.parents[0].name).split("_")[1][-1])
            self.location = location_mapping.get(self.station, None)
            if self.location is None:
                warnings.warn("Location code not recognized in location_mapping.")
                self.location = "Unknown location"
            if verbose: print('Done!\n')

        except IndexError:
            self.station  = 0
            self.location = "Unknown location"
            warnings.warn("Folders name are not following the format rup_[bl/ns/sn]_[iteration].")

        # ================================================
        # Final structure info properties
        # ================================================
        # Final structure info properties
        self.coordinates = self.model_info.coordinates
        self.drift_nodes = self.model_info.drift_nodes
        self.story_nodes = self.model_info.stories_nodes
        self.stories = self.model_info.stories
        self.subs = self.model_info.subs
        self.heights = self.model_info.heights


        # Compute model info parameters
        if verbose: print('Computing model information...')
        self.npartitions    = self.model_info.npartitions
        self.glob_nnodes    = self.model_info.glob_nnodes
        self.glob_nelements = self.model_info.glob_nelements
        self.str_nnodes,\
        self.str_nelements,\
        self.soil_nnodes,\
        self.soil_nelements = self.Manager.get_nodes_and_elements(self.glob_nnodes,
                                                                  self.glob_nelements,
                                                                  self.stories,
                                                                  self.subs,
                                                                  self._sim_type)
        if verbose: print('Done!\n')

    def loadDataFrames(self):
    # Compute DataFrames
        print('Computing DataFrames...')
        self.accel_mdf, self.accel_dfs = self._computeAbsAccelerationsDF()
        self.displ_mdf, self.displ_dfs = self._computeRelativeDisplacementsDF()
        self.react_mdf, self.react_dfs = self._computeReactionForcesDF()
        self.coords_df                 = self._computeCoordsDF()
        self.story_nodes_df            = self._computeStoryNodesDF()
        self.story_mean_accel_df       = self._computeStoryMeanAccelerationsDF()
        self.base_story_df             = self._computeBaseDF()[0]
        self.base_displ_df             = self._computeBaseDF()[1]
        self.input_df                  = self._computeInputAccelerationsDF()
        print('Done!\n')

    def model_linearity(self):
        """
        This function is used to create the model_linearity table database.
        """
        # initialize parameters
        cursor = self.Manager.cursor
        cnx = self.Manager.cnx

        # create table
        insert_query = "INSERT INTO model_linearity(Type) VALUES (%s)"
        values = ("Linear", )
        cursor.execute(insert_query, values)
        insert_query = "INSERT INTO model_linearity(Type) VALUES (%s)"
        values = ("Non Linear", )
        cursor.execute(insert_query, values)
        cnx.commit()
        print("model_linearity created correctly!\n")

    def simulation_type(self):
        """
        This function is used to create the simulation_type table database.
        """
        # initialize parameters
        cursor = self.Manager.cursor
        cnx = self.Manager.cnx

        # create table
        insert_query = "INSERT INTO simulation_type(Type) VALUES (%s)"
        values = ("Fix Base Model", )
        cursor.execute(insert_query, values)
        insert_query = "INSERT INTO simulation_type(Type) VALUES (%s)"
        values = ("Absorbing Boundaries Model", )
        cursor.execute(insert_query, values)
        insert_query = "INSERT INTO simulation_type(Type) VALUES (%s)"
        values = ("DRM Model", )
        cursor.execute(insert_query, values)
        cnx.commit()
        print("simulation_type created correctly!\n")

    def connect(self):
        """
        This function is used to connect to the database.
        """
        import time
        if self._test_mode:
            print('Connecting to the database...')
            ModelSimulation.initialize_ssh_tunnel()
            time.sleep(1)
            self.Manager = DataBaseManager(self.db_user, self.db_password, self.db_host,
                                                self.db_database)
            print(f"Succesfully connected to '{self.db_database}' database as '{self.db_user}'.")
        print('Done!\n')




    # ==================================================================================
    # COMPUTE DATAFRAMES FOR ACCELERATIONS AND DISPLACEMENTS
    # ==================================================================================
    def _computeBaseShearByAccelerations(self):
        """
        This function is used to export data into the structure_base_shear table database using
        the accelerations obtained in the simulation for every story.

        Compute shear by story and direction, and then the base shear.
        Story shear is computed as:
          -> The mean of the acceleration in the 4 nodes of the story dot mass of the story
          -> Story mass: Area * Thickness * Density + Core Area * Core Thickness * Density
        Then, summ all the story shears to get the base shear
        """
        # Initialize parameters
        density  = 2.4 # Megagramos/m3
        density1 = 4.1
        density2 = 5.45
        model_dic = {20:{
                        'areas':{
                            "slabs_area"     : 704.0  , #m2
                            "sub_slabs_area" : 1408.0 , #m2
                            "external_core"  : 28.0   , #m2
                            "internal_core_x": 112.0  , #m2
                            "internal_core_y": 94.5   , #m2
                            'perimetral_wall': 912    , #m2
                            'columns_sup'    : 3.5*10 , #m (10 columns of height 3.5)
                            'columns_sub'    : 3.0*10}, #m
                        'thickness':{
                            "slabs_sup"      :np.array([0.15] * self.stories)                            ,
                            "slabs_sub"      :np.array([0.15] * self.subs)                               ,
                            "external_core"  :np.array([0.40] * 4 + [0.30] * 6 + [0.20] * 5 + [0.15] * 5),
                            "internal_core_x":np.array([0.25] * 4 + [0.15] * 6 + [0.15] * 5 + [0.15] * 5),
                            "internal_core_y":np.array([0.35] * 4 + [0.25] * 6 + [0.15] * 5 + [0.15] * 5),
                            'perimetral_wall':np.array([0.45] * self.subs)                               ,
                            "columns_sup"    :np.array([0.8**2]*6 + [0.7**2]*5 + [0.6**2]*3 + [0.5**2]*3 + [0.4**2]*3),
                            "columns_sub"    :np.array([0.9**2]*self.subs)}}, # this is not a thickness is the area of the columns}
                    }

        # Compute Story Mases in a dict
        mass_sup = {20: {k+1:
                      model_dic[20]['areas']["slabs_area"]      *  model_dic[20]['thickness']["slabs_sup"][k]         * density2
                    # Add bottom mass
                    + model_dic[20]['areas']["external_core"]   *  model_dic[20]['thickness']["external_core"][k]     * density/2
                    + model_dic[20]['areas']["internal_core_x"] *  model_dic[20]['thickness']["internal_core_x"][k]   * density/2
                    + model_dic[20]['areas']["internal_core_y"] *  model_dic[20]['thickness']["internal_core_y"][k]   * density/2
                    + model_dic[20]['areas']['columns_sup']     *  model_dic[20]['thickness']['columns_sup'][k]       * density/2
                    # Add top mass
                    + (0 if k == self.stories-1 else
                    + model_dic[20]['areas']["external_core"]   *  model_dic[20]['thickness']["external_core"]  [k+1] * density/2
                    + model_dic[20]['areas']["internal_core_x"] *  model_dic[20]['thickness']["internal_core_x"][k+1] * density/2
                    + model_dic[20]['areas']["internal_core_y"] *  model_dic[20]['thickness']["internal_core_y"][k+1] * density/2
                    + model_dic[20]['areas']['columns_sup']     *  model_dic[20]['thickness']['columns_sup']    [k+1] * density/2)
                    for k in range(self.stories)},
                    50:{}}
        mass_base = {20:{
                        0:
                        model_dic[20]['areas']["sub_slabs_area"]  *  model_dic[20]['thickness']["slabs_sub"][1]         * density1   +
                        # Add bottom mass
                        model_dic[20]['areas']["perimetral_wall"] *  model_dic[20]['thickness']["perimetral_wall"][1]   * density/2 +
                        model_dic[20]['areas']['columns_sub']     *  model_dic[20]['thickness']['columns_sub'][1]       * density/2 +
                        # Add top mass
                        model_dic[20]['areas']["external_core"]   *  model_dic[20]['thickness']["external_core"][2]   * density/2 +
                        model_dic[20]['areas']["internal_core_x"] *  model_dic[20]['thickness']["internal_core_x"][2] * density/2 +
                        model_dic[20]['areas']["internal_core_y"] *  model_dic[20]['thickness']["internal_core_y"][2] * density/2 +
                        model_dic[20]['areas']['columns_sup']     *  model_dic[20]['thickness']['columns_sup'][2]     * density/2},
                     50:{}}
        mass_sub = {20: {k-1:
                        model_dic[20]['areas']["sub_slabs_area"]  *  model_dic[20]['thickness']["slabs_sub"][k]       * density1 +
                        model_dic[20]['areas']["perimetral_wall"] *  model_dic[20]['thickness']["perimetral_wall"][k] * density1 +
                        model_dic[20]['areas']['columns_sub']     *  model_dic[20]['thickness']['columns_sub'][k]     * density1
                    for k in range(0, -(self.subs-1), -1)},
                    }
        factor = {20:{2:1.025, 4:1.025}} # Factor of 4 subs may change cause it's not studied yet
        self.masses_series = pd.Series({**mass_sub[self.stories], **mass_base[self.stories], **mass_sup[self.stories]}).sort_index()*factor[self.stories][self.subs]

        # For each story, compute the mean acceleration in the 4 nodes of the story
        mean_accel_df = self.story_mean_accel_df[self.story_mean_accel_df.columns[1:]]

        # Compute the shear for every story and direction (X,Y,Z) and every timestep
        self.masses_series.index = mean_accel_df.columns
        stories_shear_df = mean_accel_df.mul(self.masses_series, axis=1)
        stories_shear_df['Shear Base'] = stories_shear_df.sum(axis=1)

        # Return the base shear for every direction in the same format as the function
        # structure_base_shear
        shear_x = stories_shear_df.xs('x',level='Dir')['Shear Base'].tolist()
        shear_y = stories_shear_df.xs('y',level='Dir')['Shear Base'].tolist()
        shear_z = stories_shear_df.xs('z',level='Dir')['Shear Base'].tolist()

        max_shear_x = stories_shear_df.xs('x',level='Dir')['Shear Base'].abs().max()
        max_shear_y = stories_shear_df.xs('y',level='Dir')['Shear Base'].abs().max()
        max_shear_z = stories_shear_df.xs('z',level='Dir')['Shear Base'].abs().max()

        return [shear_x, shear_y, shear_z], [max_shear_x, max_shear_y, max_shear_z]

    def _computeReactionForcesDF(self):
        """
        This function is used to compute the nodes accelerations DataFrame.
        """
        # Initialize parameters
        if self._sim_type !=1:
            multi_index = pd.MultiIndex.from_product([self.timeseries,  ['x', 'y', 'z']], names=['Time Step', 'Dir'])
            nodes_react_df = pd.DataFrame([], index=multi_index)
            nodes_react_df = nodes_react_df.round(2)
            react_df_x = nodes_react_df.xs('x', level='Dir')
            react_df_y = nodes_react_df.xs('y', level='Dir')
            react_df_z = nodes_react_df.xs('z', level='Dir')
            return nodes_react_df, [react_df_x, react_df_y, react_df_z]
        files = [file.name for file in (self.path/'Reactions').iterdir() if file.is_file()]
        directions = ['x', 'y', 'z']
        data_dict = {}

        # Extract node names and sort it
        node_numbers = [int(file_name.split("_")[1].split("-")[0]) for file_name in files]
        node_numbers.sort()
        num_rows = 0

        # Read data from each node and store it in a dictionary
        for node_number in node_numbers:
            # Find the file corresponding to the node number
            file_name = next(file for file in files if f"_{node_number}-" in file)
            node = f"Node {node_number}"
            file_path = f"{self.path}/Reactions/{file_name}"

            # Read data with space separator
            data = pd.read_csv(file_path, sep=' ', header=None).values.flatten()

            # Add vector of results to the dictionary, key = node, values = file data
            data_dict[node] = data[:48000]
            num_rows = len(data)

        # Create DataFrame with MultiIndex and data
        time_steps = self.timeseries[:int(num_rows/3)]
        multi_index = pd.MultiIndex.from_product([time_steps, directions], names=['Time Step', 'Dir'])
        nodes_react_df = pd.DataFrame(data_dict, index=multi_index)
        nodes_react_df = nodes_react_df.round(2)
        react_df_x = nodes_react_df.xs('x', level='Dir')
        react_df_y = nodes_react_df.xs('y', level='Dir')
        react_df_z = nodes_react_df.xs('z', level='Dir')
        return nodes_react_df, [react_df_x, react_df_y, react_df_z]

    def _computeCoordsDF(self):
        """
        This function is used to get the coordinates of the model.
        """
        df = pd.DataFrame(self.coordinates)
        df = df.transpose()
        df = df.sort_values('coord z')
        return df

    def _computeStoryNodesDF(self):
        """
        This function is used to get the nodes of each story of the model.
        """
        sort_by_story = sorted(self.coordinates.items(), key=lambda x: (x[1]["coord z"], x[1]["coord x"], x[1]["coord y"]))
        stories_nodes = {f"Level {i - self.subs}": {} for i in range(self.stories + self.subs + 1)}

        # Get dictionary with the nodes of each story including the subterrain
        counter = 0
        for level in stories_nodes.keys():
            stories_nodes[level] = dict(sort_by_story[counter:counter + 4])
            counter += 4
        flattened_data = [(int(level.split()[1]), (node), coords['coord x'], coords['coord y'], coords['coord z'])
                          for level, nodes in stories_nodes.items() for node, coords in nodes.items()]

        # Create a MultiIndex DataFrame with the data
        multi_index_df = pd.DataFrame(flattened_data,columns=['Story', 'Node', 'x', 'y', 'z']).set_index(['Story', 'Node'])
        return multi_index_df

    def _computeStoryMeanAccelerationsDF(self):
        """
        This function is used to compute the mean accelerations of each story.
        """
        story_mean_acceleration_df = pd.DataFrame(index=self.accel_mdf.index)
        level_lst = [i for i in range(-self.subs, self.stories + 1)]
        for story in level_lst:
            story_nodes_lst = self.story_nodes_df.xs(story, level='Story').index
            story_acce_df = self.accel_mdf[story_nodes_lst].copy()
            story_acce_df.loc[:,'Average'] = story_acce_df.mean(axis=1)
            story_mean_acceleration_df[f'Story {story}'] = story_acce_df['Average']
        story_mean_acceleration_df.round(4)
        return story_mean_acceleration_df

    def _computeRelativeDisplacementsDF(self):
        """
        This function is used to compute the nodes accelerations DataFrame.
        """
        files = [file.name for file in (self.path/'Displacements').iterdir() if file.is_file()]
        directions = ['x', 'y', 'z']
        data_dict = {}

        # Extract node names and sort it
        node_numbers = [int(file_name.split("_")[1].split("-")[0]) for file_name in files]
        node_numbers.sort()
        num_rows = 0

         # Read data from each node and store it in a dictionary
        for node_number in node_numbers:
            # Find the file corresponding to the node number
            file_name = next(file for file in files if f"_{node_number}-" in file)
            node = f"Node {node_number}"
            file_path = f"{self.path}/Displacements/{file_name}"

            # Read data with space separator
            data = pd.read_csv(file_path, sep=' ', header=None).values.flatten()

            # Add vector of results to the dictionary, key = node, values = file data
            data_dict[node] = data[:48000]
            num_rows = len(data)

        time_steps = self.timeseries[:int(num_rows/3)]
        multi_index = pd.MultiIndex.from_product([time_steps, directions], names=['Time Step', 'Dir'])
        nodes_displ_df = pd.DataFrame(data_dict, index=multi_index)
        nodes_displ_df = nodes_displ_df.round(4)
        displ_x_df = nodes_displ_df.xs('x', level='Dir')
        displ_y_df = nodes_displ_df.xs('y', level='Dir')
        displ_z_df = nodes_displ_df.xs('z', level='Dir')
        return nodes_displ_df, [displ_x_df, displ_y_df, displ_z_df]

    def _computeAbsAccelerationsDF(self):
        """
        This function is used to compute the absolute accelerations DataFrame.
        """
        nodes_df = self._computeNodesAccelerationsDF()
        input_df = self._computeInputAccelerationsDF()
        accel_df = nodes_df.add(input_df['Acceleration'][:len(nodes_df)], axis='index')
        accel_df = accel_df.round(4)
        accel_df_x = accel_df.xs('x', level='Dir')
        accel_df_y = accel_df.xs('y', level='Dir')
        accel_df_z = accel_df.xs('z', level='Dir')

        return accel_df, [accel_df_x, accel_df_y, accel_df_z]

    def _computeInputAccelerationsDF(self):
        """
        This function is used to compute the input accelerations DataFrame.
        """
        # Read each file with soil accelerations
        acc_e = pd.read_csv(self.path/'acceleration_e.txt', sep=" ", header=None)[:len(self.timeseries)]
        acc_n = pd.read_csv(self.path/'acceleration_n.txt', sep=" ", header=None)[:len(self.timeseries)]
        acc_z = pd.read_csv(self.path/'acceleration_z.txt', sep=" ", header=None)[:len(self.timeseries)]

        # Create a time step series with the same length as the accelerations
        time_steps = self.timeseries

        # Create the multiindex for everystep, every direction
        directions = ['x', 'y', 'z']
        multi_index = pd.MultiIndex.from_product([time_steps, directions], names=['Time Step', 'Dir'])

        # Concatenate and asociate the data to the multiindex
        acc_data = np.stack((acc_e, acc_n, acc_z)).flatten('F')
        input_acce_df = pd.DataFrame(acc_data, index=multi_index, columns=['Acceleration'])*self._cfactor

        return input_acce_df

    def _computeNodesAccelerationsDF(self):
        """
        This function is used to compute the nodes accelerations DataFrame.
        """
        # Initialize parameters
        files = [file.name for file in (self.path/'Accelerations').iterdir() if file.is_file()]
        directions = ['x', 'y', 'z']
        data_dict = {}

        # Extract node names and sort it
        node_numbers = [int(file_name.split("_")[1].split("-")[0]) for file_name in files]
        node_numbers.sort()
        num_rows = 0

        # Read data from each node and store it in a dictionary
        for node_number in node_numbers:
            # Find the file corresponding to the node number
            file_name = next(file for file in files if f"_{node_number}-" in file)
            node = f"Node {node_number}"
            file_path = f"{self.path}/Accelerations/{file_name}"

            # Read data with space separator
            data = pd.read_csv(file_path, sep=' ', header=None).values.flatten()

            # Add vector of results to the dictionary, key = node, values = file data
            data_dict[node] = data[:48000]
            num_rows = len(data)

        # Create DataFrame with MultiIndex and data
        time_steps = self.timeseries[:int(num_rows/3)]
        multi_index = pd.MultiIndex.from_product([time_steps, directions], names=['Time Step', 'Dir'])
        nodes_acce_df = pd.DataFrame(data_dict, index=multi_index)
        return nodes_acce_df

    def _computeBaseDF(self):
        base_story_df  = self.story_nodes_df.xs(0, level='Story')
        base_displ_df  = self.displ_mdf[base_story_df.index].xs('z',level='Dir')
        return base_story_df, base_displ_df

    def _computeBaseRotationDF(self):
        """
        This function is used to compute the base rotation DataFrame.
        """
        # Exclude cases where the simulation is not DRM nor AB (sim_type = 2, 3)
        if self._sim_type == 1:
            return 0,0

        # Compute Relative Displ for x
        rel_zdispl_x1 = self.base_displ_df[self.base_story_df.index[0]] - \
                        self.base_displ_df[self.base_story_df.index[2]]
        rel_zdispl_x2 = self.base_displ_df[self.base_story_df.index[1]] - \
                        self.base_displ_df[self.base_story_df.index[3]]
        rel_zdispl_x = (rel_zdispl_x1 + rel_zdispl_x2) / 2

        # Compute Relative Displ for y
        rel_zdispl_y1 = self.base_displ_df[self.base_story_df.index[0]] - \
                        self.base_displ_df[self.base_story_df.index[1]]
        rel_zdispl_y2 = self.base_displ_df[self.base_story_df.index[2]] - \
                        self.base_displ_df[self.base_story_df.index[3]]
        rel_zdispl_y = (rel_zdispl_y1 + rel_zdispl_y2) / 2

        # Compute distances between nodes for x and y directions
        x_dist = self.base_story_df['x'].iloc[0] - self.base_story_df['x'].iloc[2]
        y_dist = self.base_story_df['y'].iloc[0] - self.base_story_df['y'].iloc[1]

        # Compute base rotation for x and y directions
        base_rot_x = np.arctan2(rel_zdispl_x, x_dist)
        base_rot_y = np.arctan2(rel_zdispl_y, y_dist)

        return base_rot_x, base_rot_y

    def _computeDriftBetweenNodes(self, node1_ss:pd.Series, node2_ss:pd.Series, height:float, loc:int) -> pd.Series:
        """
        This functions computes the drift between two nodes in a given direction.
        The drift is computed as the tangent of the angle between the two nodes in the given direction less
        the base rotation in the given direction.

        Parameters
        ----------
        node1_ss : pd.Series
            The node 1 displacements series. 1 value for each timestep.
        node2_ss : pd.Series
            The node 2 displacements series. 1 value for each timestep.
        height : float
            The height of the nodes.
        loc : int
            The direction of the nodes. 0 for x, 1 for y.

        Returns
        -------
        pd.Series
            The absolute drift between the two nodes in the given direction.
        """
        nodes_angle = np.arctan2((node1_ss - node2_ss), height)
        nodes_angle_adjusted = nodes_angle - self._computeBaseRotationDF()[loc]
        drift = pd.Series(np.tan(nodes_angle_adjusted))
        drift_abs = drift.abs()
        return drift_abs




    # ==================================================================================
    # EXTERNAL FILES GENERATIONS AND COMPLEMENTARY METHODS
    # ==================================================================================
    def create_reaction_xlsx(self):
        import os

        #create nodes sorted list
        nodes = []
        path = os.getcwd()
        results = os.listdir(f'{path}/Reactions/')

        #sorting nodes
        for result in results:
            node = (int(result.split('-')[1].split('_')[1]))
            nodes.append(node)
        nodes.sort()

        #sorting files in list
        results_sorted = []
        for node in nodes:
            nodeid = f'_{node}-'
            for result in results:
                if nodeid in result:
                    results_sorted.append(result)

        #define format
        workbook = xlsxwriter.Workbook('reactions.xlsx')
        main_format = workbook.add_format({'bold':True})
        main_format.set_align('center')
        second_format = workbook.add_format({'font_color': 'black'})
        second_format.set_align('center')


        #open book and start writing in shells
        x_sheet = workbook.add_worksheet('Reaction East')
        y_sheet = workbook.add_worksheet('Reaction North')
        z_sheet = workbook.add_worksheet('Reaction Vertical')
        x_sheet.write(0,0,'Timestep/NodeID',main_format)
        y_sheet.write(0,0,'Timestep/NodeID',main_format)
        z_sheet.write(0,0,'Timestep/NodeID',main_format)
        x_sheet.set_column(0,0,17,main_format)
        y_sheet.set_column(0,0,17,main_format)
        z_sheet.set_column(0,0,17,main_format)


        #fill rows names
        row = 1
        column = 0
        time_step = 0.0
        while time_step < self._total_time:
            x_sheet.write(row,column,f'{time_step:.3f}',main_format)
            y_sheet.write(row,column,f'{time_step:.3f}',main_format)
            z_sheet.write(row,column,f'{time_step:.3f}',main_format)
            time_step += self._time_step
            row +=1

        #fill columns names
        row = 0
        column = 1
        files = []
        for node in (range(len(nodes))):
            x_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            y_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            z_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            column+=1

        #fill matrix in correct values, here the file is the column and it's results are the rows
        files = [open(f'Reactions/{file}','r') for file in results_sorted]
        column = 1
        for file in range(len(files)):
            nodal_result = [[(num) for num in line.split('\n')] for line in files[file]]
            row = 1
            for row_val in nodal_result:
                reaction_X = float(row_val[0].split(' ')[0])
                reaction_Y = float(row_val[0].split(' ')[1])
                reaction_Z = float(row_val[0].split(' ')[2])
                x_sheet.write(row,column,reaction_X,second_format)
                y_sheet.write(row,column,reaction_Y,second_format)
                z_sheet.write(row,column,reaction_Z,second_format)
                row += 1

            column += 1

        workbook.close()

    @staticmethod
    def create_displacement_xlsx():

        import os

        #create nodes sorted list
        nodes = []
        path = os.getcwd()
        results = os.listdir(f'{path}/Displacements/')

        #sorting nodes
        for result in results:
            node = (int(result.split('-')[1].split('_')[1]))
            nodes.append(node)
        nodes.sort()

        #sorting files in list
        results_sorted = []
        for node in nodes:
            nodeid = f'_{node}-'
            for result in results:
                if nodeid in result:
                    results_sorted.append(result)

        #define format
        workbook = xlsxwriter.Workbook('displacements.xlsx')
        main_format = workbook.add_format({'bold':True})
        main_format.set_align('center')
        second_format = workbook.add_format({'font_color': 'black'})
        second_format.set_align('center')

        #open book and start writing in shells
        x_sheet = workbook.add_worksheet('Displacements East')
        y_sheet = workbook.add_worksheet('Displacements North')
        z_sheet = workbook.add_worksheet('Displacements Vertical')
        x_sheet.write(0,0,'Timestep/NodeID',main_format)
        y_sheet.write(0,0,'Timestep/NodeID',main_format)
        z_sheet.write(0,0,'Timestep/NodeID',main_format)

        x_sheet.set_column(0,0,17,main_format)
        y_sheet.set_column(0,0,17,main_format)
        z_sheet.set_column(0,0,17,main_format)

        #fill rows names
        row = 1
        column = 0
        time_step = 0.0
        while time_step < 50:
            x_sheet.write(row,column,time_step,main_format)
            y_sheet.write(row,column,time_step,main_format)
            z_sheet.write(row,column,time_step,main_format)

            time_step += 0.025
            row +=1

        #fill columns names
        row = 0
        column = 1
        files = []
        for node in (range(len(nodes))):
            x_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            y_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            z_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            column+=1

        #fill matrix in correct values, here the file is the column and it's results are the rows
        files = [open(f'Displacements/{file}','r') for file in results_sorted]
        column = 1
        for file in range(len(files)):

            nodal_result = [[(num) for num in line.split('\n')] for line in files[file]]
            row = 1
            for row_val in nodal_result:
                acceleration_X = float(row_val[0].split(' ')[0])
                acceleration_Y = float(row_val[0].split(' ')[1])
                acceleration_Z = float(row_val[0].split(' ')[2])
                x_sheet.write(row,column,acceleration_X,second_format)
                y_sheet.write(row,column,acceleration_Y,second_format)
                z_sheet.write(row,column,acceleration_Z,second_format)
                row += 1

            column += 1

        workbook.close()

    @staticmethod
    def create_accelerations_xlsx():

        import os

        #create nodes sorted list
        nodes = []
        path = os.getcwd()
        results = os.listdir(f'{path}/Accelerations/')

        #sorting nodes
        for result in results:
            node = (int(result.split('-')[1].split('_')[1]))
            nodes.append(node)
        nodes.sort()

        #sorting files in list
        results_sorted = []
        for node in nodes:
            nodeid = f'_{node}-'
            for result in results:
                if nodeid in result:
                    results_sorted.append(result)

        #define format
        workbook = xlsxwriter.Workbook('accelerations.xlsx')
        main_format = workbook.add_format({'bold':True})
        main_format.set_align('center')
        second_format = workbook.add_format({'font_color': 'black'})
        second_format.set_align('center')

        #open book and start writing in shells
        x_sheet = workbook.add_worksheet('Accelerations East')
        y_sheet = workbook.add_worksheet('Accelerations North')
        z_sheet = workbook.add_worksheet('Accelerations Vertical')
        x_sheet.write(0,0,'Timestep/NodeID',main_format)
        y_sheet.write(0,0,'Timestep/NodeID',main_format)
        z_sheet.write(0,0,'Timestep/NodeID',main_format)

        x_sheet.set_column(0,0,17,main_format)
        y_sheet.set_column(0,0,17,main_format)
        z_sheet.set_column(0,0,17,main_format)

        #fill rows names
        row = 1
        column = 0
        time_step = 0.0
        while time_step < 50:
            x_sheet.write(row,column,time_step,main_format)
            y_sheet.write(row,column,time_step,main_format)
            z_sheet.write(row,column,time_step,main_format)

            time_step += 0.025
            row +=1

        #fill columns names
        row = 0
        column = 1
        files = []
        for node in (range(len(nodes))):
            x_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            y_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            z_sheet.write(row,column,f'Node {nodes[node]}',main_format)
            column+=1

        #fill matrix in correct values, here the file is the column and it's results are the rows
        files = [open(f'Accelerations/{file}','r') for file in results_sorted]
        column = 1
        for file in range(len(files)):

            nodal_result = [[(num) for num in line.split('\n')] for line in files[file]]
            row = 1
            for row_val in nodal_result:
                acceleration_X = float(row_val[0].split(' ')[0])
                acceleration_Y = float(row_val[0].split(' ')[1])
                acceleration_Z = float(row_val[0].split(' ')[2])
                x_sheet.write(row,column,acceleration_X,second_format)
                y_sheet.write(row,column,acceleration_Y,second_format)
                z_sheet.write(row,column,acceleration_Z,second_format)
                row += 1

            column += 1

        workbook.close()

    @staticmethod
    def initialize_ssh_tunnel(server_alive_interval=60):
        local_port = "3306"
        try:
            # Ejecutar netstat y capturar la salida con una codificación adecuada
            netstat_output = subprocess.check_output(['netstat', '-ano'], text=True, encoding='cp1252')

            # Buscar el puerto local en la salida de netstat
            if re.search(rf'\b{local_port}\b', netstat_output):
                print("SSH tunnel already established and operational...")

                # Verificar si el proceso SSH está activo usando tasklist
                tasklist_output = subprocess.check_output(['tasklist'], text=True, encoding='cp1252')
                if "ssh.exe" in tasklist_output:
                    print("SSH process is running.")
                else:
                    print("SSH process not running. Closing all existing SSH processes and attempting to restart...")
                    # Cerrar todos los procesos SSH
                    subprocess.call(["taskkill", "/F", "/IM", "ssh.exe"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    # Cerrar el túnel existente y abrir uno nuevo
                    command = f"ssh -o ServerAliveInterval={server_alive_interval} -L 3306:localhost:3307 cluster ssh -L 3307:kraken:3306 kraken"
                    subprocess.call(["cmd.exe", "/c", "start", "/min", "cmd.exe", "/k", command])

            else:
                # Si el puerto local no está en uso, abrir el túnel
                print("Attempting to establish the SSH Tunnel...")
                command = f"ssh -o ServerAliveInterval={server_alive_interval} -L 3306:localhost:3307 cluster ssh -L 3307:kraken:3306 kraken"
                subprocess.call(["cmd.exe", "/c", "start", "/min", "cmd.exe", "/k", command])

        except subprocess.CalledProcessError as e:
            raise DataBaseError(f"Error executing a system command: {e}")
        except Exception as e:
            raise DataBaseError(f"Error trying to open cmd: {e}")

    @staticmethod
    def convert_and_store_time(time_string):
        # Extraer el número de segundos de la cadena y convertir a entero
        total_seconds = int(time_string.split()[0])

        # Calcular días, horas, minutos y segundos
        days, remainder  = divmod(total_seconds, 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Construir la cadena de salida
        readable_format = f"{days} day{'s' if days != 1 else ''}, {hours}hrs, {minutes}mins, {seconds} secs"

        return str(readable_format)

    @staticmethod
    def paralelize_serialization(data_frames):
        # Función para serializar un único DataFrame
        def serializar_df(df):
            return pickle.dumps(df)

        # Usando ThreadPoolExecutor para serializar en paralelo
        with ThreadPoolExecutor(max_workers=6) as executor:  # Ajustado para Ryzen 5 5600X
            resultados_serializados = list(executor.map(serializar_df, data_frames))

        return resultados_serializados
