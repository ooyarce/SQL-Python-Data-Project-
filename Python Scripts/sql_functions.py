# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
from matplotlib import pyplot as plt
from pathlib import Path
from typing import Optional

import mysql.connector
import pandas as pd
import numpy as np
import subprocess
import xlsxwriter
import datetime
import warnings
import pickle
import json

# ==================================================================================
# MAIN CLASS
# ==================================================================================
# TODO: See how to get parameters from the soil region, you know that in some of the tcl data files you can find the information
# TODO: See how to store the data such as the acceleration, displacement and reactions as pickle files, not optimized json texts
class ModelSimulation:

    # ==================================================================================
    # INIT PARAMS
    # ==================================================================================
    def __init__(self,user='omarson',password='Mackbar2112!',host='localhost',database='stkodatabase',**kwargs):

        # Define generic parameters
        bench_cluster = "Esmeralda HPC Cluster by jaabell@uandes.cl"
        model_path = Path(__file__).parents[3]
        modelname = next(model_path.glob('*.scd')).name

        # Simulation default parameters
        self._sim_comments      = kwargs.get("sim_comments", "No comments")
        self._sim_opt           = kwargs.get("sim_opt", "No options yet")
        self._sim_stage         = kwargs.get("sim_stage", "No stage yet")
        self._sim_type          = kwargs.get("sim_type", 1)
        self._sm_input_comments = kwargs.get("sm_input_comments","No comments")
        self._model_name        = kwargs.get("model_name", modelname)
        self._model_comments    = kwargs.get("model_comments", "No comments")
        self._bench_cluster     = kwargs.get("bench_cluster", bench_cluster)
        self._bench_comments    = kwargs.get("bench_comments", "No comments")
        self._perf_comments     = kwargs.get("perf_comments", "No comments")
        self._specs_comments    = kwargs.get("specs_comments", "No comments")
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
        self._jump              = kwargs.get("jump", 8) # Use this to reduce the size of the data
        self._cfactor           = kwargs.get("cfactor", 1.0)
        self._load_df_info      = kwargs.get("load_df_info", True)

        # Assert values
        assert self._linearity in [1,2], "Linearity can only be 1 (Linear) or 2 (Non-Linear)"
        assert self._sim_type in [1,2,3], "Simulation type can only be 1 (Fix Base), 2 (AbsBound) or 3(DRM)"

        # Load model info
        if self._load_df_info:
            self.loadModelInfo()
            self.loadDataFrames()

        # Connect to Dabase
        print("Attempting to establish the SSH Tunnel...")
        self._test_mode  = kwargs.get("windows_os", False)
        self.db_user     = user
        self.db_password = password
        self.db_host     = host
        self.db_database = database
        self.connect()
        print('Done!\n')

    # ==================================================================================
    # SQL FUNCTIONS
    # ==================================================================================
    def simulation(self, **kwargs):
        """
        This is the main function to export the simulation into the database.
        """
        # Initialize parameters
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

        self.simulation_sm_input()
        SM_Input = cursor.lastrowid

        # Fet date
        date = datetime.datetime.now()
        date = date.strftime("%B %d, %Y")

        # Insert data into database
        insert_query = (
            "INSERT INTO simulation("
            "idModel, idSM_Input,"
            "idType, SimStage, SimOptions, Simdate,"
            "Comments) VALUES(%s,%s,%s,%s,%s,%s,%s)")
        values = (Model, SM_Input,sim_type, sim_stage, sim_opt, date,sim_comments)
        self.Manager.insert_data(insert_query, values)

        print("simulation table updated correctly!\n")
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

        # PGA y Spectrum
        Pga = self.sm_input_pga()
        Pga = cursor.lastrowid
        Spectrum = self.sm_input_spectrum()
        Spectrum = cursor.lastrowid

        # Insert data into database
        insert_query = (
            "INSERT INTO simulation_sm_input(idPGA, idSpectrum, Magnitude,"
            "Rupture_type, Location, RealizationID, Comments)"
            " VALUES(%s,%s,%s,%s,%s,%s,%s)")
        values = (Pga,Spectrum,self.magnitude,self.rupture,self.location,self.iteration,sm_input_comments)
        cursor.execute(insert_query, values)
        print("simulation_sm_input table updated correctly!\n")

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
        self.model_specs_structure()
        SpecsStructure = cursor.lastrowid

        # Insert data into database
        insert_query = ("INSERT INTO simulation_model("
                        "idBenchmark,idStructuralPerfomance,idSpecsStructure,"
                        "ModelName,Comments) VALUES(%s,%s,%s,%s,%s)")
        values = (Benchmark,StructurePerfomance,SpecsStructure,model_name,model_comments)
        cursor.execute(insert_query, values)
        print("simulation_model table updated correctly!\n")

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
        values = (self.jobname,
                  self.simulation_time,
                  self.memory_by_results,
                  self.memory_by_model,
                  self.nodes,
                  self.threads,
                  bench_cluster,
                  comments)
        cursor.execute(insert_query, values)
        print("model_benchmark table updated correctly!\n")

    def model_specs_structure(self, **kwargs):
        """
        This function is used to export data into the model_specs_structure table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        comments = kwargs.get("specs_comments", self._specs_comments)

        # Check if the linearity parameter is correct
        if self._linearity < 1 or self._linearity > 2:
            raise TypeError(
                "The Linearity parameter can only take 1 or 2 values(int).")

        # Upload results to the database
        insert_query = (
            "INSERT INTO model_specs_structure ("
            "idLinearity, Nnodes, Nelements, Nstories, Nsubs,"
            "InterstoryHeight, Comments) VALUES (%s,%s,%s,%s,%s,%s,%s)")
        values = (self._linearity,self.nnodes,self.nelements,self.stories,self.subs,json.dumps(self.heights),comments)
        cursor.execute(insert_query, values)
        print("model_specs_structure table updated correctly!\n")

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

        # This is going to change in the future
        mta = "Not implemented yet"  # max torsion angle
        fas = "Not implemented yet"  # floor acceleration spectra

        # Upload results to the database
        insert_query = (
            "INSERT INTO model_structure_perfomance "
            "(idBaseShear,idAbsAccelerations,idRelativeDisplacements,"
            "idMaxBaseShear,idMaxDriftPerFloor,MaxTorsionAngle,"
            "FloorAccelerationSpectra,Comments)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
        values = (BaseShear,AbsAccelerations,RelativeDisplacements,MaxBaseShear,MaxDriftPerFloor,mta,fas,comments)  # mta and fas vars has to change
        cursor.execute(insert_query, values)
        print("model_structure_perfomance table updated correctly!\n")

    def structure_abs_acceleration(self, **kwargs):
        """
        This function is used to export data into the structure_abs_acceleration table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        units = kwargs.get("abs_acc_units", self._abs_acc_units)

        # Convert Data to JSON format and reduce the size of the data
        #time_series = json.dumps(self.timeseries.tolist()[::self._jump])
        #matrixes = [json.dumps(self.accel_dfs[i].iloc[::self._jump].to_dict())for i in range(3)]
        time_series = pickle.dumps(self.timeseries[::self._jump])
        matrixes = [pickle.dumps(self.accel_dfs[i].iloc[::self._jump])for i in range(3)]

        # Upload results to the database
        insert_query = ("INSERT INTO structure_abs_acceleration ("
                        "TimeSeries, AbsAccX, AbsAccY, AbsAccZ, Units) "
                        "VALUES(%s,%s,%s,%s,%s)")
        values = (time_series, matrixes[0], matrixes[1], matrixes[2], units)
        cursor.execute(insert_query, values)
        print("structure_abs_acceleration table updated correctly!\n")

    def structure_relative_displacements(self, **kwargs):
        """
        This function is used to export data into the structure_relative_displacements table database.
        """
        # Initialize parameters
        cursor = self.Manager.cursor
        units = kwargs.get("rel_displ_units", self._rel_displ_units)

        # Convert Data to JSON format and reduce the size of the data
        #time_series = json.dumps(self.timeseries.tolist()[::self._jump])
        #matrixes = [json.dumps(self.displ_dfs[i].iloc[::self._jump].to_dict())for i in range(3)]
        time_series = pickle.dumps(self.timeseries[::self._jump])
        matrixes = [pickle.dumps(self.displ_dfs[i].iloc[::self._jump])for i in range(3)]

        # Upload results to the database
        insert_query = ("INSERT INTO structure_relative_displacements ("
                        "TimeSeries, DispX, DispY, DispZ, Units) "
                        "VALUES(%s,%s,%s,%s,%s)")
        values = (time_series, matrixes[0], matrixes[1], matrixes[2], units)
        cursor.execute(insert_query, values)
        print("structure_relative_displacements table updated correctly!\n")

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
            # Inter-storey drifts
            for i in range(1,self.stories):
                story_nodes      = self.story_nodes_df.loc[i].index
                next_story_nodes = self.story_nodes_df.loc[i+1].index
                compute_drifts   = [self._computeDriftBetweenNodes(df[current_node], df[following_node], self.heights[i-1], loc)
                                    for current_node, following_node in zip(story_nodes, next_story_nodes)]
                drift_df = pd.concat(compute_drifts, axis=1)
                center   = drift_df.mean(axis=1).max()
                corner   = drift_df.max().max()
                center_drifts[loc].append(center)
                corner_drifts[loc].append(corner)

            #NOTE: THIS IS DEPRECATED, BUT MAYBE IT WILL BE USEFULL IN THE FUTURE
            """
            center_roof, corner_roof = self._computeRoofDrift(loc)
            center_drifts[loc].append(center_roof)
            corner_drifts[loc].append(corner_roof)
            """

        # Upload results to the database
        insert_query = ("INSERT INTO structure_max_drift_per_floor ("
                        "MaxDriftCornerX, MaxDriftCornerY, MaxDriftCenterX, "
                        "MaxDriftCenterY, Units) VALUES (%s,%s,%s,%s,%s)")
        values = (pickle.dumps(corner_drifts[0]),pickle.dumps(corner_drifts[1]),pickle.dumps(center_drifts[0]),pickle.dumps(center_drifts[1]),units)
        cursor.execute(insert_query, values)
        print("structure_max_drift_per_floor table updated correctly!\n")

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
        cursor.execute(insert_query, values)
        print("structure_base_shear table updated correctly!\n")

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
        cursor.execute(insert_query, values)
        print("structure_max_base_shear table updated correctly!\n")

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
        cursor.execute(insert_query, values)
        print("sm_input_pga table updated correctly!\n")

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
        Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [self.pwl(ae, wi, nu)]]

        # Spectrum North
        an = self.input_df.xs('y', level='Dir')['Acceleration'].to_list()[::16]
        Spn = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [self.pwl(an, wi, nu)]]

        # Spectrum Vertical
        az = self.input_df.xs('z', level='Dir')['Acceleration'].to_list()[::16]
        Spz = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [self.pwl(az, wi, nu)]]

        # Upload results to the database
        insert_query = ("INSERT INTO sm_input_spectrum("
                        "SpectrumX, SpectrumY, SpectrumZ, Units) "
                        "VALUES (%s,%s,%s,%s)")
        values = (pickle.dumps(Spe), pickle.dumps(Spn), pickle.dumps(Spz), units)
        cursor.execute(insert_query, values)
        print("sm_input_spectrum table updated correctly!\n")

    # ==================================================================================
    # LOAD SIMULATION INFORMATION AND DATA POST PROCESSING IN PANDAS DATAFRAMES
    # ==================================================================================
    def loadModelInfo(self, verbose=True):
        # Initialize Model Info
        self.model_info = ModelInfo(sim_type=self._sim_type,verbose=verbose)
        self.path       = Path(__file__).parent
        self.timeseries = np.arange(self._time_step, self._total_time+self._time_step, self._time_step)

        # Compute model info parameters
        if verbose: print('Computing model information...')
        self.nnodes = self.model_info.nnodes
        self.nelements = self.model_info.nelements
        self.npartitions = self.model_info.npartitions
        # Get job name, nodes, threads and logname
        with open(self.path/"run.sh") as data:
            lines = data.readlines()
            self.jobname = lines[1].split(" ")[1].split("=")[1]
            self.nodes = int(lines[2].split("=")[1])
            self.threads = int(lines[3].split("=")[1])
            self.logname = lines[4].split("=")[1].split("#")[0].strip()

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
        self.memory_by_results = sum(
            sum(file.stat().st_size
                for file in (self.path / folder).iterdir())
            for folder in folder_names) / (1024 * 1024)

        # Get model memory
        model_path = self.path.parents[2]
        model_name = next(model_path.glob("*.scd"))
        self.memory_by_model = f"{model_name.stat().st_size / (1024 * 1024):.2f} Mb"

         # Get magnitude
        magnitude = Path(__file__).parents[2].name[1:]
        self.magnitude = f"{magnitude} Mw"

        # Get rupture type
        rupture_types = {
            "bl": "Bilateral",
            "ns": "North-South",
            "sn": "South-North"}
        folder_name = Path(__file__).parents[1].name
        rup_type = folder_name.split("_")[1]
        self.rupture = rupture_types.get(rup_type)
        if not self.rupture:
            raise Warning("Folders name are not following the format rup_[bl/ns/sn]_[iteration].")

        # Get realization id
        iter_name = Path(__file__).parents[1].name
        self.iteration = (
            iter_name.split("_")[2] if len(iter_name.split("_")) == 3 else
            f"Unknown Iteration for {iter_name=}. Check folder iteration name!")

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
            9: "Far field South",}
        self.station = int((Path(__file__).parents[0].name).split("_")[1][-1])
        self.location = location_mapping.get(self.station, None)
        if self.location is None:
            warnings.warn("Location code not recognized in location_mapping.")
            self.location = "Unknown location"
        if verbose: print('Done!\n')

        # Compute structure info parameters
        if verbose: print('Computing structure information...')
        self.coordinates = self.model_info.coordinates
        self.drift_nodes = self.model_info.drift_nodes
        self.story_nodes = self.model_info.stories_nodes
        self.stories = self.model_info.stories
        self.subs = self.model_info.subs
        self.heights = self.model_info.heights
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

                    50:{'areas':{},
                        'thickness':{},
                        'masses':{}}}

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
                    for k in range(self.subs-1)},
                    50: {}}

        self.masses_series = pd.Series({**mass_sub[self.stories], **mass_base[self.stories], **mass_sup[self.stories]}).sort_index()*1.025

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
        acc_e = pd.read_csv(self.path/'acceleration_e.txt', sep=" ", header=None)
        acc_n = pd.read_csv(self.path/'acceleration_n.txt', sep=" ", header=None)
        acc_z = pd.read_csv(self.path/'acceleration_z.txt', sep=" ", header=None)

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
        # Exclude cases where the simulation is not DRM (sim_type = 2)
        if self._sim_type == 1:
            return 0,0
        # Compute Relative Displ for x
        rel_zdispl_x1 = self.base_displ_df[self.base_story_df.index[0]] - self.base_displ_df[self.base_story_df.index[2]]
        rel_zdispl_x2 = self.base_displ_df[self.base_story_df.index[1]] - self.base_displ_df[self.base_story_df.index[3]]
        rel_zdispl_x = (rel_zdispl_x1 + rel_zdispl_x2)/2

        # Compute Relative Displ for y
        rel_zdispl_y1 = self.base_displ_df[self.base_story_df.index[0]] - self.base_displ_df[self.base_story_df.index[1]]
        rel_zdispl_y2 = self.base_displ_df[self.base_story_df.index[2]] - self.base_displ_df[self.base_story_df.index[3]]
        rel_zdispl_y = (rel_zdispl_y1 + rel_zdispl_y2)/2

        # Compute distances between nodes for x and y directions
        x_dist = self.base_story_df['x'][0]-self.base_story_df['x'][2]
        y_dist = self.base_story_df['y'][0]-self.base_story_df['y'][1]

        # Compute base rotation for x and y directions
        base_rot_x = np.arctan(rel_zdispl_x/x_dist)
        base_rot_y = np.arctan(rel_zdispl_y/y_dist)
        return base_rot_x, base_rot_y

    def _computeRoofDrift(self, loc):
        """
        This function is used to compute the roof drift DataFrame.

        loc: int
            The location of the drift. 0 for x, 1 for y.
        """
        # Initialize parameters
        df = self.displ_dfs[loc]
        roof_nodes    = self.story_nodes_df.loc[self.stories]
        base_nodes    = self.story_nodes_df.loc[0]
        max_height    = self.story_nodes_df.loc[self.stories]['z'][0]
        loc_drifts = []

        # Compute drift for every timestep
        for base_node, roof_node in zip(base_nodes.index, roof_nodes.index):
            nodes_angle = np.arctan((df[roof_node] - df[base_node])/max_height)
            nodes_angle_adjusted = nodes_angle - self._computeBaseRotationDF()[loc]
            drift = pd.Series(np.tan(nodes_angle_adjusted))
            drift_abs = drift.abs()
            loc_drifts.append(drift_abs)
        drift_df = pd.concat(loc_drifts, axis=1)
        center   = drift_df.mean(axis=1).max()
        corner   = drift_df.max().max()
        return center, corner

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
        nodes_angle = np.arctan((node1_ss - node2_ss)/height)
        nodes_angle_adjusted = nodes_angle - self._computeBaseRotationDF()[loc]
        drift = pd.Series(np.tan(nodes_angle_adjusted))
        drift_abs = drift.abs()
        return drift_abs

    # ==================================================================================
    # EXTERNAL FILES GENERATIONS AND COMPLEMENTARY METHODS
    # ==================================================================================
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
            ModelSimulation.initialize_ssh_tunnel()
            time.sleep(1)
            self.Manager = DataBaseManager(self.db_user, self.db_password, self.db_host,
                                                self.db_database)
            print("Database Manager initialized correctly!")
            print(f"Connected to {self.db_database} database as {self.db_user}.")

    #DEPRECATED METHOD
    def get_sm_id(self):
        pass
        """import os
        path = os.path.dirname(os.path.abspath(__file__)).split("\\")
        path = Path(__file__).resolve().parent
        magnitude = path[-3][-3:]
        rupture = path[-2][-4:]
        station = int(path[-1][-1]) + 1
        m,r = 0,0
        if magnitude == "6.5":
            m = 0
        elif magnitude == "6.7":
            m = 90
        elif magnitude == "6.9":
            m = 180
        elif magnitude == "7.0":
            m = 270

        if rupture[0:2] == "bl":
            r = (int(rupture[-1]) - 1) * 10
        elif rupture[0:2] == "ns":
            r = (int(rupture[-1]) - 1) * 10 + 30
        elif rupture[0:2] == "sn":
            r = (int(rupture[-1]) - 1) * 10 + 60

        id = m + r + station
        return id"""

    # ==================================================================================
    # STATIC METHODS
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
    def pwl(vector_a, w, chi,step=0.04):
        """
        Use step = 0.04 for 1000 values
        Use step = 0.02 for 2000 values
        Use step = 0.01 for 4000 values
        Use step = 0.005 for 8000 values
        Use step = 0.0025 for 16000 values
        """
        # Precompute constants
        h = step
        m = 1
        w_d = w * np.sqrt(1 - chi**2)  # 1/s

        # Define functions
        sin = np.sin(w_d * h)
        cos = np.cos(w_d * h)
        e = np.exp(-chi * w * h)
        raiz = np.sqrt(1 - chi**2)
        division = 2 * chi / (w * h)

        A = e * (chi * sin / raiz + cos)
        B = e * (sin / w_d)
        C = (1 / w**2) * (division + e * (((1 - (2 * chi**2)) / (w_d * h) - chi / raiz) * sin - (1 + division) * cos))
        D = (1 / w**2) * (1 - division + e * ((2 * chi**2 - 1) * sin / (w_d * h) + division * cos))

        A1 = -e * ((w * sin) / raiz)
        B1 = e * (cos - chi * sin / raiz)
        C1 = (1 / w**2) * (-1 / h + e * ((w / raiz + chi / (h * raiz)) * sin + cos / h))
        D1 = (1 / w**2) * (1 / h - (e / h * (chi * sin / raiz + cos)))

        # Initialize vectors
        u_t = np.zeros(len(vector_a))
        up_t = np.zeros(len(vector_a))

        # Compute the first two values of the vectors
        for i in range(len(vector_a) - 1):
            pi = -vector_a[i] * m
            pi1 = -vector_a[i + 1] * m

            ui = u_t[i]
            vi = up_t[i]

            u_t[i + 1] = A * ui + B * vi + C * pi + D * pi1
            up_t[i + 1] = A1 * ui + B1 * vi + C1 * pi + D1 * pi1
        return u_t, up_t

    @staticmethod
    def initialize_ssh_tunnel():
        command = "ssh -L 3306:localhost:3307 cluster ssh -L 3307:kraken:3306 kraken"
        try:
            # Ejecutar el comando SSH en un nuevo terminal cmd, pero minimizado
            subprocess.call(["cmd.exe", "/c", "start", "/min", "cmd.exe", "/k", command])
            #print("Attempting to establish the SSH Tunnel...")
        except Exception as e:
            print(f"Error trying to open cmd:  {e}")
            return False
        return True

# ==================================================================================
# SECONDARY CLASSES
# ==================================================================================
class DataBaseManager:
    """
    This class is used to manage the connection to the database.
    """

    def __init__(self, user: str, password: str, host: str, database: str):
        self.cnx = mysql.connector.connect(user=user,
                                           password=password,
                                           host=host,
                                           database=database)
        self.cursor = self.cnx.cursor()

    def insert_data(self, query: str, values: tuple):
        self.cursor.execute(query, values)
        self.cnx.commit()

    def close_connection(self):
        self.cursor.close()
        self.cnx.close()

class ModelInfo:
    """
    This class is used to check the model info and extract specific data from the model.
    This data is used in the class SeismicSimulation to perform the analysis and upload
    the results to the database.

    Attributes
    ----------
    path : str
        Path to the 'PartitionsInfo' subfolder.
    folder_accel : str
        Path to the 'PartitionsInfo/accel' subfolder.
    folder_coords : str
        Path to the 'PartitionsInfo/coords' subfolder.
    folder_disp : str
        Path to the 'PartitionsInfo/disp' subfolder.
    folder_info : str
        Path to the 'PartitionsInfo/info' subfolder.
    folder_reaction : str
        Path to the 'PartitionsInfo/reaction' subfolder.

    Methods
    -------
    give_accelerations()
        Returns the accelerations of the model.
    give_coords_info()
        Returns the coordinates of the model.
    give_displacements()
        Returns the displacements of the model.
    give_model_info()
        Returns the info of the model.
    give_reactions()
        Returns the reactions of the model.
    """

    def __init__(self, sim_type:int = 1, verbose:bool=True):
        # Set the path to the 'PartitionsInfo' subfolder
        self.verbose = verbose
        current_path = Path(__file__).parent
        self.path = Path(__file__).parent / "PartitionsInfo"
        # Check if the 'PartitionsInfo' subfolder exists
        if not self.path.exists():
            raise Exception("The PartitionsInfo folder does not exist!\n"
                            "Current path = {}".format(current_path))
        if self.verbose:
            # Call the methods to initialize the data
            print("---------------------------------------------|")
            print("------- CHECKING NODES IN PARTITIONS --------|")
            print("---------------------------------------------|")
        self.accelerations, self.acce_nodes  = self.give_accelerations()
        self.displacements, self.displ_nodes = self.give_displacements()

        if self.verbose:
            print('\n---------------------------------------------|')
            print('------------- INITIALIZING DATA -------------|')
            print('---------------------------------------------|')
        self.reactions, self.reaction_nodes = self.give_reactions() if sim_type==1 else (None, None)
        self.nnodes, self.nelements, self.npartitions = self.give_model_info()

        self.coordinates,\
        self.drift_nodes,\
        self.stories_nodes,\
        self.stories,\
        self.subs,\
        self.heights = self.give_coords_info()

    def give_accelerations(self):
        # check nodes
        folder_name = "accel"
        files_accel = self.path / folder_name
        files = [open(file, "r") for file in files_accel.iterdir() if file.is_file()]

        # create dictionary
        accelerations = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")]
                     for line in files[file]]
            file_id = (str(files[file]).split("/")[-1].split("-")[1].split(" ")
                       [0].split(".")[0])
            accelerations[f"Partition {file_id}"] = {}
            for nodei in range(len(nodes)):
                accelerations[f"Partition {file_id}"][f"Node {nodei}"] = nodes[
                    nodei][0]

        # create list with nodes sorted
        acce_nodes = []
        for values in accelerations.values():
            for node in values.values():
                acce_nodes.append(int(node))
        acce_nodes.sort()
        listed = set(acce_nodes)

        if len(acce_nodes) == len(listed):
            if self.verbose:
                print("Accelerations: No nodes repeated")
        else:
            raise Exception("WARNING: NODES REPEATED")
        return accelerations, acce_nodes

    def give_displacements(self):
        # check nodes
        folder_name = "disp"
        files_disp = self.path / folder_name
        files = [open(file, "r") for file in files_disp.iterdir() if file.is_file()]

        # create dictionary
        displacements = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")]
                     for line in files[file]]
            file_id = (str(files[file]).split("/")[-1].split("-")[1].split(" ")
                       [0].split(".")[0])
            displacements[f"Partition {file_id}"] = {}
            for nodei in range(len(nodes)):
                displacements[f"Partition {file_id}"][f"Node {nodei}"] = nodes[nodei][0]

        # create list with nodes sorted
        displ_nodes = []

        for values in displacements.values():
            for node in values.values():
                displ_nodes.append(int(node))
        displ_nodes.sort()
        listed = set(displ_nodes)

        if len(displ_nodes) == len(listed):
            if self.verbose:
                print("Displacements: No nodes repeated")
        else:
            raise Exception("WARNING: NODES REPEATED")

        return displacements, displ_nodes

    def give_reactions(self):
        # check nodes
        folder_name = "reaction"
        files_reaction = self.path / folder_name
        files = [open(file, "r") for file in files_reaction.iterdir() if file.is_file()]

        # create dictionary
        reactions = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")]
                     for line in files[file]]
            file_id = (str(files[file]).split("/")[-1].split("-")[1].split(" ")
                       [0].split(".")[0])
            reactions[f"Partition {file_id}"] = {}
            for nodei in range(len(nodes)):
                reactions[f"Partition {file_id}"][f"Node {nodei}"] = nodes[nodei][0]

        # create list with nodes sorted
        reaction_nodes = []
        for values in reactions.values():
            for node in values.values():
                reaction_nodes.append(int(node))

        reaction_nodes.sort()
        listed = set(reaction_nodes)
        if len(reaction_nodes) == len(listed):
            if self.verbose:
                print("Reactions:     No nodes repeated ")
        else:
            raise Exception("WARNING: NODES REPEATED")
        return reactions, reaction_nodes

    def give_coords_info(self):
        # check nodes
        folder_name = "coords"
        files_coords = self.path / folder_name
        files = [open(file, "r") for file in files_coords.iterdir()if file.is_file()]

        # create dictionary
        coordinates = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")] for line in files[file]]

            for nodei in range(1, len(nodes)):
                node_id = nodes[nodei][0].split(" ")[0]
                coord_x = round(float(nodes[nodei][0].split(" ")[1]), 1)
                coord_y = round(float(nodes[nodei][0].split(" ")[2]), 1)
                coord_z = round(float(nodes[nodei][0].split(" ")[3]), 1)
                coordinates[f"Node {node_id}"] = {}
                coordinates[f"Node {node_id}"] = {}
                coordinates[f"Node {node_id}"] = {}
                coordinates[f"Node {node_id}"]["coord x"] = float(f"{coord_x:.1f}")
                coordinates[f"Node {node_id}"]["coord y"] = float(f"{coord_y:.1f}")
                coordinates[f"Node {node_id}"]["coord z"] = float(f"{coord_z:.1f}")

        # sort every node per level
        sorted_nodes = sorted(coordinates.items(), key=lambda x: (x[1]["coord x"], x[1]["coord y"], x[1]["coord z"]))
        # create dictionary with specific nodes per corner to calculate directly the drift
        drift_nodes = {"corner1": [],"corner2": [],"corner3": [],"corner4": []}

        # calculate subs, stories, and fill drift nodes with heights
        height = 0
        id_corner = 1
        subs = []
        stories = 0
        for tuple_i in sorted_nodes:
            z = tuple_i[1]["coord z"]
            # print(z)
            node = tuple_i[0]
            if z < 0 and z != height:
                subs.append(z)
                continue
            elif z == height and z < 0:
                continue
            elif z == height and z >= 0:
                continue
            elif z > height:
                height = z
                drift_nodes[f"corner{id_corner}"].append(f"{node}|{z}")
                stories += 1
                continue
            height = 0.0
            id_corner += 1

        subs = sorted(set(subs))
        subs = len(subs)
        stories = int(stories / 4)
        # list of heigths
        heights = []
        for data in range(len(drift_nodes["corner1"]) - 1):
            current_height = float(
                drift_nodes["corner1"][data + 1].split("|")[1]) - float(
                    drift_nodes["corner1"][data].split("|")[1])
            heights.append(current_height)

        # create dict with nodes per story
        sort_by_story = sorted(coordinates.items() ,key=lambda x: (x[1]["coord z"], x[1]["coord x"], x[1]["coord y"]))
        stories_nodes = {}
        counter = 0
        for i in range(stories + subs + 1):
            i -= subs
            if i < 0:
                counter += 4
                continue
            stories_nodes[f"Level {i}"] = {}
            node1 = sort_by_story[counter][0]
            node2 = sort_by_story[counter + 1][0]
            node3 = sort_by_story[counter + 2][0]
            node4 = sort_by_story[counter + 3][0]
            # print(node1,node2,node3,node4)
            stories_nodes[f"Level {i}"][node1] = sort_by_story[counter][1]
            stories_nodes[f"Level {i}"][node2] = sort_by_story[counter + 1][1]
            stories_nodes[f"Level {i}"][node3] = sort_by_story[counter + 2][1]
            stories_nodes[f"Level {i}"][node4] = sort_by_story[counter + 3][1]
            counter += 4
        heights.insert(0, (coordinates[list(stories_nodes["Level 1"])[0]]["coord z"] - coordinates[list(stories_nodes["Level 0"])[0]]["coord z"]))
        return coordinates, drift_nodes, stories_nodes, stories, subs, heights

    def give_model_info(self):
        # read file
        folder_name = "info"
        files_coords = self.path / folder_name
        file = open(files_coords / 'model_info.csv', "r")
        # get number of nodes and number of elements
        info = [[row for row in line.split(" ")] for line in file]
        nnodes = int(info[0][4])
        nelements = int(info[1][4])
        npartitions = int(info[2][4])
        file.close()
        return nnodes, nelements, npartitions

class Plotting:
    """
    This class is used to perform the seismic analysis of the structure.
    It's used to analyse quiclky the structure and get the results of the analysis.
    You use it in the main after the results are uploaded to the database.
    """
    def __init__(self, database: ModelSimulation, path:str):
        database.loadModelInfo(verbose=False)
        self.path = database.path
        self.stories = database.stories
        self.station = database.station
        self.rup_type = database.rupture
        self.mag = database.magnitude
        self.save_path = Path(path)
        if database._sim_type == 1:
            self.sim_type = 'FB'
        elif database._sim_type == 2:
            self.sim_type = 'AB'
        elif database._sim_type == 3:
            self.sim_type = 'DRM'
        if database.rupture == 'Bilateral':
            self.rup_type = 'BL'
        self.file_name           = f'{self.sim_type}_{self.mag[:3]}_{self.rup_type}_s{self.station}'
        self.drift_title         = f'Drift per story plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'
        self.input_title         = f'Input Accelerations Response Spectra Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'
        self.sprectums_title     = f'Story PSa Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'
        self.base_spectrum_title = f'Base Accelerations Spectrum Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'
        self.base_shear_ss_title = f'Base Shear Plot | {self.sim_type} |  {self.mag[:3]} | {self.rup_type} | Station {self.station}'

    def plotConfig(self, title:str, x = 19.2, y = 10.8, dpi = 100):
        fig = plt.figure(num=1, figsize=(x, y), dpi=dpi)
        ax = fig.add_subplot(1, 1, 1)
        y = None
        ax.grid(True)
        ax.set_title(title)
        return fig, ax, y

    def plotSave(self, fig, file_type = 'png'):
        self.save_path.mkdir(parents=True, exist_ok=True)
        full_save_path = self.save_path / f'{self.file_name}.{file_type}'
        fig.savefig(full_save_path, dpi=100)
        plt.show()

    def plotModelDrift(self, max_corner_x: list, max_center_x: list, max_corner_y: list, max_center_y:list, xlim_inf:float = 0.0, xlim_sup:float = 0.008 ):
        # Input params
        fig, ax, y = self.plotConfig(self.drift_title)
        ax.set_yticks(range(1, self.stories))
        ax.set_xlabel('Interstory Drift Ratio (Drift/Story Height)')
        ax.set_ylabel('Story')
        ax.set_xlim(xlim_inf, xlim_sup)

        # Plot corner drift
        y = [i for i in range(1, self.stories)]
        ax.plot(max_corner_x, y, label='max_corner_x')
        ax.plot(max_center_x, y, label='max_center_x',linestyle='--')

        # Plot center drift
        ax.plot(max_corner_y, y, label='max_corner_y')
        ax.plot(max_center_y, y, label='max_center_y',linestyle='--')

        # Plot NCH433 limits
        ax.axvline(x=0.002, color='r', linestyle='--', label='NCh433 - 5.9.2 = 0.002')
        ax.axvline(x=0.002+(0.001), color='r', linestyle='--', label=f'NCh433 - 5.9.3 = {0.002+(0.001)}')
        ax.legend()
        self.plotSave(fig)
        return ax

    def plotModelSpectrum(self, spectrum_x:list[float], spectrum_y:list[float], spectrum_z:list[float], plotNCh433:bool = True):
        # Input params
        fig, ax, y = self.plotConfig(self.input_title)
        ax.set_xlabel('T (s)')
        ax.set_ylabel('Acceleration (m/s/s)')

        # Plot Spectrums
        if plotNCh433:
            ax = self.NCh433Spectrum(ax)
        x = np.linspace(0.003, 2, 1000)
        ax.plot(x, spectrum_x, label='Spectrum X')
        ax.plot(x, spectrum_y, label='Spectrum Y')
        ax.plot(x, spectrum_z, label='Spectrum Z')
        ax.legend()
        self.plotSave(fig)
        return ax

    @staticmethod
    def NCh433Spectrum(ax, S = 1, To = 0.3, p = 1.5, Ao = 0.3 *9.81 , Io = 1.2, R = 5):
        # Input params
        T = np.linspace(0,2.,1000)
        Sah = np.zeros(1000)
        Sav = np.zeros(1000)

        # Compute spectrum
        for i in range(1000):
            tn = T[i]
            alpha = (1 + 4.5*(tn/To)**p)/(1 +(tn/To)**3)
            Sah[i] = S*Ao*alpha/(R/Io)
            Sav[i] = 2/3 * S*Ao*alpha/(R/Io)

        # Plot spectrum
        ax.plot(T, Sah, linestyle='--', label='NCh433 Horizontal')
        ax.plot(T, Sav, linestyle='--', label='NCh433 Vertical')
        return ax

    def plotStoriesSpectrums(self, ModelSimulation: ModelSimulation, dir_:str, accel_df:pd.DataFrame, stories_df:pd.DataFrame,
                             stories_lst:list[int], T:np.ndarray, plot:bool=True, ax:Optional[plt.Axes]=None,
                             method:str='Fix Base', linestyle:str='--'):
        # Input params
        self.file_name = f'{self.sim_type}_{self.mag}_{self.rup_type}_s{self.station}_{dir_.upper()}'
        assert dir_ in ['x', 'y', 'z'], f'dir must be x, y or z! Current: {dir}'
        if ax is None:
            fig, ax, _ = self.plotConfig(self.sprectums_title)
        else:
            self.sprectums_title = f'{method} {self.sprectums_title}'
            fig = ax.figure
        ax.set_xlabel('T (s)')
        ax.set_ylabel(f'Acceleration in {dir_.upper()} (m/s/s)')
        nu = 0.05
        w  = 2 * np.pi / np.array(T)

        # Plot Spectrum
        for i in stories_lst:
            df = accel_df[stories_df.loc[i].index].copy()
            df.loc[:,'Average'] = df.mean(axis=1)
            adir = df.xs(dir_, level='Dir')['Average'][::16]
            Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [ModelSimulation.pwl(adir.values, wi, nu)]]
            ax.plot(T, Spe, label=f'{method}: Story {i}', linestyle=linestyle)
        ax.legend()
        if plot:
            self.plotSave(fig)
        return ax

    def plotBaseSpectrum(self, ModelSimulation: ModelSimulation, accel_df:pd.DataFrame, stories_df:pd.DataFrame,
                         T:np.ndarray, spectrum_modes:list[float], plot_z:bool=True):
        # Input params
        fig, ax, _ = self.plotConfig(self.base_spectrum_title)
        ax.set_xlabel('T (s)')
        ax.set_ylabel('Acceleration (m/s/s)')
        nu = 0.05
        w  = 2 * np.pi / np.array(T)
        df = accel_df[stories_df.loc[0].index].copy()
        df.loc[:,'Average'] = df.mean(axis=1)

        # Compute and plot spectrum
        ae = df.xs('x', level='Dir')['Average'][::16]
        an = df.xs('y', level='Dir')['Average'][::16]
        Spe = [max(max(u_x), abs(min(u_x))) * wi**2 for wi in w for u_x, _ in [ModelSimulation.pwl(ae.values, wi, nu)]]
        Spn = [max(max(u_y), abs(min(u_y))) * wi**2 for wi in w for u_y, _ in [ModelSimulation.pwl(an.values, wi, nu)]]
        ax.plot(T, Spe, label='Dir X')
        ax.plot(T, Spn, label='Dir Y')

        # Plot z if desired
        if plot_z:
            az = df.xs('z', level='Dir')['Average'][::16]
            Spz = [max(max(u_z), abs(min(u_z))) * wi**2 for wi in w for u_z, _ in [ModelSimulation.pwl(az.values, wi, nu)]]
            ax.plot(T, Spz, label='Dir Z')

        # Plot the modes in vertical lines with squares or crosses
        for i, mode in enumerate(spectrum_modes):
            ax.axvline(x=mode, linestyle='--', label=f'Mode{i} = {mode}',color='red')

        ax.legend()
        self.plotSave(fig)
        return ax

    def plotShearBaseOverTime(self, time:np.ndarray, time_shear_fma:list[float], time_shear_react:pd.Series, dir_:str):
        # Input params
        self.file_name = f'{self.sim_type}_{self.mag}_{self.rup_type}_s{self.station}_{dir_.upper()}'
        assert dir_ in ['x','X','y','Y','e','E','n','N'], f'dir must be x, y, e or n! Current: {dir}'
        fig, ax, _ = self.plotConfig(self.base_shear_ss_title)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel(f'Shear in {dir_.upper()} direction (kN)')
        ax.plot(time, time_shear_fma, label='Method: F=ma')
        ax.plot(time, time_shear_react,linestyle='--', label='Method: Node reactions')
        ax.legend()
        self.plotSave(fig)




