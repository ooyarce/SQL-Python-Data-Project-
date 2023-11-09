from matplotlib import pyplot as plt
from pathlib import Path
import mysql.connector
import pandas as pd
import numpy as np
import datetime
import warnings
import glob
import json


# ==================================================================================
# MAIN CLASS
# ==================================================================================
class ModelSimulation:
    """
    This class is used to export the simulation into the database.

    Methods
    -------
    simulation(**kwargs)
        This is the main function to export the simulation into the database.
    simulation_sm_input(**kwargs)
        This function is used to export the simulation sm input into the database.
    simulation_model(**kwargs)
        This function is used to export data into the simulation_model table database.
    model_benchmark(**kwargs)
        This function is used to export data into the model_benchmark table database.
    model_specs_structure(**kwargs)
        This function is used to export data into the model_specs_structure table
        database.
    model_structure_perfomance(**kwargs)
        This function is used to export data into the model_structure_perfomance table
        database.
    structure_base_shear(**kwargs)
        This function is used to export data into the structure_base_shear table
        database.
    structure_max_base_shear(**kwargs)
        This function is used to export data into the structure_max_base_shear table
        database.
    structure_abs_acceleration(**kwargs)
        This function is used to export data into the structure_abs_acceleration table
        database.
    structure_relative_displacements(**kwargs)
        This function is used to export data into the structure_relative_displacements
        table database.
    structure_max_drift_per_floor(**kwargs)
        This function is used to export data into the structure_max_drift_per_floor
        table database.
    sm_input_pga(**kwargs)
        This function is used to export data into the sm_input_pga table database.
    sm_input_spectrum(**kwargs)
        This function is used to export data into the sm_input_spectrum table database.
    """

    # ==================================================================================
    # INIT PARAMS
    # ==================================================================================
    def __init__(
        self, db_user: str, db_password: str, db_host: str, db_database: str, **kwargs
    ):
        """
        This method is used to initialize the parameters.
        """
        # Define generic parameters
        bench_cluster = "Esmeralda HPC Cluster by jaabell@uandes.cl"
        modelname = glob.glob("*.scd")[0]

        # Define default parameters
        self._sim_comments: str = kwargs.get("sim_comments", "No comments")
        self._sim_opt: str = kwargs.get("sim_opt", "No options yet")
        self._sim_stage: str = kwargs.get("sim_stage", "No stage yet")
        self._sim_type: int = kwargs.get("sim_type", 1)
        self._sm_input_comments: str = kwargs.get("sm_input_comments", "No comments")
        self._model_name: str = kwargs.get("model_name", modelname)
        self._model_comments: str = kwargs.get("model_comments", "No comments")
        self._bench_cluster: str = kwargs.get("bench_cluster", bench_cluster)
        self._bench_comments: str = kwargs.get("bench_comments", "No comments")
        self._perf_comments: str = kwargs.get("perf_comments", "No comments")
        self._specs_comments: str = kwargs.get("specs_comments", "No comments")
        self._pga_units: str = kwargs.get("pga_units", "m/s/s")
        self._resp_spectrum: str = kwargs.get("resp_spectrum", "m/s/s")
        self._abs_acc_units: str = kwargs.get("abs_acc_units", "m/s/s")
        self._rel_displ_units: str = kwargs.get("rel_displ_units", "m")
        self._max_drift_units: str = kwargs.get("max_drift_units", "m")
        self._max_bs_units: str = kwargs.get("max_bs_units", "kN")
        self._bs_units: str = kwargs.get("bs_units", "kN")
        self._linearity: int = kwargs.get("linearity", 1)
        self._fidelity: int = kwargs.get("fidelity", 0)
        self._test_mode: bool = kwargs.get("test_mode", False)

        # Initialize Model Info
        self.model_info = ModelInfo(fidelity=self._fidelity)
        self.path = Path(__file__).parent
        accelerations_file = self.path / "accelerations.xlsx"
        displacements_file = self.path / "displacements.xlsx"

        # Compute model info parameters
        (
            self.nnodes,
            self.nelements,
            self.npartitions,
        ) = self.model_info.give_model_info()
        (
            self.coordenates,
            self.drift_nodes,
            self.story_nodes,
            self.stories,
            self.subs,
            self.heights,
        ) = self.model_info.give_coords_info()

        # Initialize Accelerations and Displacements DF
        if accelerations_file.exists():
            self.acc_matrixes = self._computeAbsAccelerationsDF()
        if displacements_file.exists():
            self.disp_matrixes = self._computeRelativeDisplacementsDF()

        # Initialize Database Manager and Cursor
        if not self._test_mode:
            self.db_manager = DataBaseManager(
                db_user, db_password, db_host, db_database
            )

    # ==================================================================================
    # SQL FUNCTIONS
    # ==================================================================================
    def simulation(self, **kwargs):
        """
        This is the main function to export the simulation into the database.
        """
        # Initialize parameters
        cursor = self.db_manager.cursor
        sim_comments = kwargs.get("sim_comments", self._sim_comments)
        sim_opt = kwargs.get("sim_opt", self._sim_opt)
        sim_stage = kwargs.get("sim_stage", self._sim_stage)
        sim_type = kwargs.get("sim_type", self._sim_type)

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
            "idModel, idSM_Input, idType, SimStage, SimOptions, Simdate,"
            "Comments) VALUES(%s,%s,%s,%s,%s,%s,%s)"
        )
        values = (Model, SM_Input, sim_type, sim_stage, sim_opt, date, sim_comments)
        self.db_manager.insert_data(insert_query, values)
        self.db_manager.close_connection()

        print("simulation table updated correctly!\n")
        print("---------------------------------------------|")
        print("---------------------------------------------|")
        print("---------------------------------------------|\n")

    def simulation_sm_input(self, **kwargs):
        """
        This function is used to export the simulation sm input into the database.
        """
        # Initialize parameters
        cursor = self.db_manager.cursor
        sm_input_comments = kwargs.get("sm_input_comments", self._sm_input_comments)

        # Get magnitude
        magnitude = Path(__file__).parents[2].name[1:]
        magnitude = f"{magnitude} Mw"

        # Get rupture type
        rupture_types = {"bl": "Bilateral", "ns": "North-South", "sn": "South-North"}
        folder_name = Path(__file__).parents[1].name
        rup_type = folder_name.split("_")[1]
        rupture = rupture_types.get(rup_type)
        if not rupture:
            raise Warning(
                "Folders name are not following the format rup_[bl/ns/sn]_[iteration]."
            )

        # Get realization id
        iter_name = Path(__file__).parents[1].name
        iteration = (
            iter_name.split("_")[2]
            if len(iter_name.split("_")) == 3
            else f"Unknown Iteration for {iter_name=}. Check folder iteration name!"
        )

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
            9: "Far field South",
        }
        station = int((Path(__file__).parents[0].name).split("_")[1][-1])
        location = location_mapping.get(station, None)
        if location is None:
            warnings.warn("Location code not recognized in location_mapping.")
            location = "Unknown location"

        # TODO: This has to change to the new algorithm to extract the data from the
        # TODO: hdf5 file reader py.
        # PGA y Spectrum
        Pga = self.get_sm_id()
        Spectrum = self.get_sm_id()

        # Insert data into database
        insert_query = (
            "INSERT INTO simulation_sm_input(idPGA, idSpectrum, Magnitude,"
            "Rupture_type, Location, RealizationID, Comments)"
            " VALUES(%s,%s,%s,%s,%s,%s,%s)"
        )
        values = (
            Pga,
            Spectrum,
            magnitude,
            rupture,
            location,
            iteration,
            sm_input_comments,
        )  # noqa: E501
        cursor.execute(insert_query, values)
        print("simulation_sm_input table updated correctly!\n")

    def simulation_model(self, **kwargs):
        """
        This function is used to export data into the simulation_model table database.
        """
        # Initialize parameters
        cursor = self.db_manager.cursor
        model_name = kwargs.get("model_name", self._model_name)
        model_comments = kwargs.get("model_comments", self._model_comments)

        # Fills benchmark, structure perfomance and specs structure tables
        self.model_benchmark()
        Benchmark = cursor.lastrowid
        self.model_structure_perfomance()
        StructurePerfomance = cursor.lastrowid
        self.model_specs_structure()
        SpecsStructure = cursor.lastrowid

        insert_query = (
            "INSERT INTO simulation_model("
            "idBenchmark,idStructuralPerfomance,idSpecsStructure,"
            "ModelName,Comments) VALUES(%s,%s,%s,%s,%s)"
        )
        values = (
            Benchmark,
            StructurePerfomance,
            SpecsStructure,
            model_name,
            model_comments,
        )
        cursor.execute(insert_query, values)
        print("simulation_model table updated correctly!\n")

    def model_benchmark(self, **kwargs):
        # ------------------------------------------------------------------------------------------------------------------------------------
        # Get calculus time from log file, nodes, threads and comments
        # ------------------------------------------------------------------------------------------------------------------------------------
        # Initialize parameters
        cursor = self.db_manager.cursor
        bench_cluster = kwargs.get("bench_cluster", self._bench_cluster)
        comments = kwargs.get("bench_comments", self._bench_comments)

        # Get job name, nodes, threads and logname
        with open("run.sh") as data:
            lines = data.readlines()
            jobname = lines[1].split(" ")[1].split("=")[1]
            nodes = int(lines[2].split("=")[1])
            threads = int(lines[3].split("=")[1])
            logname = lines[4].split("=")[1].strip()

        # Get simulation time
        with open(logname) as log:
            time = ""
            for row in log:
                if "Elapsed:" in row:
                    value = row.split(" ")[1]
                    time = f"{value} seconds"  # first value of query
                    break

        # Get memort by results
        folder_names = ["Accelerations", "Displacements", "PartitionsInfo"]
        memory_by_results = sum(
            sum(
                file.stat().st_size
                for file in (Path(__file__).parent / folder).iterdir()
            )
            for folder in folder_names
        ) / (1024 * 1024)

        # Get model memory
        model_name = next(Path(".").glob("*.scd"))
        memory_by_model = f"{model_name.stat().st_size / (1024 * 1024):.2f} Mb"

        # Insert data into database
        insert_query = (
            "INSERT INTO model_benchmark (JobName,SimulationTime,"
            "MemoryResults,MemoryModel,ClusterNodes,CpuPerNodes,ClusterName,"
            "Comments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        )
        values = (
            jobname,
            time,
            memory_by_results,
            memory_by_model,
            nodes,
            threads,
            bench_cluster,
            comments,
        )
        cursor.execute(insert_query, values)
        print("model_benchmark table updated correctly!\n")

    def model_specs_structure(self, **kwargs):
        """
        This function is used to export data into the model_specs_structure table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        comments = kwargs.get("specs_comments", self._specs_comments)

        if self._linearity < 1 or self._linearity > 2:
            raise TypeError("The Linearity parameter can only take 1 or 2 values(int).")

        insert_query = (
            "INSERT INTO model_specs_structure ("
            "idLinearity, Nnodes, Nelements, Nstories, Nsubs,"
            "InterstoryHeight, Comments) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        )
        values = (
            self._linearity,
            self.nnodes,
            self.nelements,
            self.stories,
            self.subs,
            json.dumps(self.heights),
            comments,
        )
        cursor.execute(insert_query, values)
        print("model_specs_structure table updated correctly!\n")

    def model_structure_perfomance(self, **kwargs):
        """
        This function is used to export data into the model_structure_perfomance table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        fidelity = kwargs.get("fidelity", self._fidelity)
        comments = kwargs.get("perf_comments", self._perf_comments)

        # Base shear calculations
        if fidelity == 0:
            # fills base shear
            self.structure_base_shear_byReactionForces()
            BaseShear = cursor.lastrowid
            # fills max base shear
            self.structure_max_base_shear_byReactionForces()
            MaxBaseShear = cursor.lastrowid

        else:
            # fills base shear
            self.structure_base_shear_byAccelerations()

            # fills max base shear
            self.structure_max_base_shear_byReactionForces()
            MaxBaseShear = cursor.lastrowid
        # fills absolute accelerations
        self.structure_abs_acceleration()
        AbsAccelerations = cursor.lastrowid

        # fills relative displacements
        self.structure_relative_displacements()
        RelativeDisplacements = cursor.lastrowid

        # fills max drift per floor
        self.structure_max_drift_per_floor()
        MaxDriftPerFloor = cursor.lastrowid

        # this is going to change in the future
        mta = "Not implemented yet"  # max torsion angle
        fas = "Not implemented yet"  # floor acceleration spectra

        # insert data into database
        if not fidelity:
            insert_query = (
                "INSERT INTO model_structure_perfomance "
                "(idBaseShear,idAbsAccelerations,idRelativeDisplacements,"
                "idMaxBaseShear,idMaxDriftPerFloor,MaxTorsionAngle,"
                "FloorAccelerationSpectra,Comments)"
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            )
            values = (
                BaseShear,
                AbsAccelerations,
                RelativeDisplacements,
                MaxBaseShear,
                MaxDriftPerFloor,
                mta,
                fas,
                comments,
            )  # mta and fas vars has to change
            cursor.execute(insert_query, values)
            print("model_structure_perfomance table updated correctly!\n")
        else:
            insert_query = (
                "INSERT INTO model_structure_perfomance "
                "(idAbsAccelerations,idRelativeDisplacements,"
                "idMaxDriftPerFloor,MaxTorsionAngle,"
                "FloorAccelerationSpectra,Comments)"
                " VALUES (%s,%s,%s,%s,%s,%s)"
            )
            values = (
                AbsAccelerations,
                RelativeDisplacements,
                MaxDriftPerFloor,
                mta,
                fas,
                comments,
            )  # mta and fas vars has to change
            cursor.execute(insert_query, values)
            print("model_structure_perfomance table updated correctly!\n")

    def structure_base_shear_byReactionForces(self, **kwargs):
        """
        This function is used to export data into the structure_base_shear table database using
        the reactions obtained in the simulation.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units = kwargs.get("bs_units", self._bs_units)

        # get base shear
        reactions = pd.read_excel("reactions.xlsx", sheet_name=None)
        sheet_names = list(reactions.keys())
        base_shears = []

        for sheet_name in sheet_names:
            df = reactions[sheet_name].iloc[:, 1:].dropna()
            timeseries = json.dumps(reactions[sheet_name].iloc[:, 0].tolist())
            summ = json.dumps((df.sum(axis=1).values).tolist())
            base_shears.append(summ)

        insert_query = "INSERT INTO structure_base_shear (TimeSeries, ShearX, ShearY, ShearZ, Units) VALUES (%s,%s,%s,%s,%s)"
        values = (timeseries, base_shears[0], base_shears[1], base_shears[2], units)
        cursor.execute(insert_query, values)
        print("structure_base_shear table updated correctly!\n")

    def structure_max_base_shear_byReactionForces(self, **kwargs):
        """
        This function is used to export data into the structure_max_base_shear table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units = kwargs.get("max_bs_units", self._max_bs_units)

        # get max base shear
        reactions = pd.read_excel("reactions.xlsx", sheet_name=None)
        sheet_names = list(reactions.keys())
        max_shears = []

        for sheet_name in sheet_names:
            df = reactions[sheet_name].iloc[:, 1:].dropna()
            summ = json.dumps(max(df.sum(axis=1).values).tolist())
            max_shears.append((summ))
        max_shears = [float(num) for num in max_shears]
        max_shears = [round(num, 2) for num in max_shears]

        insert_query = (
            "INSERT INTO structure_max_base_shear ("
            "MaxX, MaxY, MaxZ, Units) VALUES (%s,%s,%s,%s)"
        )
        values = (max_shears[0], max_shears[1], max_shears[2], units)
        cursor.execute(insert_query, values)
        print("structure_max_base_shear table updated correctly!\n")

    def structure_abs_acceleration(self, **kwargs):
        """
        This function is used to export data into the structure_abs_acceleration table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units = kwargs.get("abs_acc_units", self._abs_acc_units)
        acc_timeseries = json.dumps(
            self.acc_matrixes[0].index.get_level_values(0).tolist()
        )
        matrixes = [
            json.dumps(self.disp_matrixes[i].iloc[::8].to_dict()) for i in range(3)
        ]

        insert_query = (
            "INSERT INTO structure_abs_acceleration ("
            "TimeSeries, AbsAccX, AbsAccY, AbsAccZ, Units) "
            "VALUES(%s,%s,%s,%s,%s)"
        )
        values = (acc_timeseries, matrixes[0], matrixes[1], matrixes[2], units)
        cursor.execute(insert_query, values)
        print("structure_abs_acceleration table updated correctly!\n")

    def structure_relative_displacements(self, **kwargs):
        """
        This function is used to export data into the structure_relative_displacements table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units = kwargs.get("rel_displ_units", self._rel_displ_units)
        time_series = json.dumps(
            self.disp_matrixes[0].index.get_level_values(0).tolist()
        )
        matrixes = [
            json.dumps(self.disp_matrixes[i].iloc[::8].to_dict()) for i in range(3)
        ]
        insert_query = (
            "INSERT INTO structure_relative_displacements ("
            "TimeSeries, DispX, DispY, DispZ, Units) "
            "VALUES(%s,%s,%s,%s,%s)"
        )
        values = (time_series, matrixes[0], matrixes[1], matrixes[2], units)
        cursor.execute(insert_query, values)
        print("structure_relative_displacements table updated correctly!\n")

    def structure_max_drift_per_floor(self, **kwargs):
        """
        This function is used to export data into the structure_max_drift_per_floor table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units = kwargs.get("max_drift_units", self._max_drift_units)
        displacements = self.disp_matrixes
        center_drifts = [[], []]
        corner_drifts = [[], []]

        # Compute Drifts
        for loc, df in enumerate(displacements[:2]):
            df = df.iloc[:, 1:].dropna()
            for i in range(self.stories):
                current = f"Level {i}"
                following = f"Level {i+1}"
                compute_drifts = [abs(pd.to_numeric(df[current_node]) - pd.to_numeric(df[following_node])) / self.heights[i]
                    for current_node, following_node in zip(self.story_nodes[current].keys(),self.story_nodes[following].keys())]
                drift_df = pd.concat(compute_drifts, axis=1)
                center = drift_df.mean(axis=1).max()
                corner = drift_df.max().max()
                center_drifts[loc].append(center)

        # Upload results to the database
        insert_query = (
            "INSERT INTO structure_max_drift_per_floor ("
            "MaxDriftCornerX, MaxDriftCornerY, MaxDriftCenterX, "
            "MaxDriftCenterY, Units) VALUES (%s,%s,%s,%s,%s)"
        )
        values = (
            json.dumps(corner_drifts[0]),
            json.dumps(corner_drifts[1]),
            json.dumps(center_drifts[0]),
            json.dumps(center_drifts[1]),
            units,
        )
        cursor.execute(insert_query, values)
        print("structure_max_drift_per_floor table updated correctly!\n")

    # ==================================================================================
    # SQL FUNCTIONS NOT FINISHEED
    # =================================================================================
    # TODO: Include the columns in the area and length dictionaries.
    def structure_base_shear_byAccelerations(self, **kwargs):
        """
        This function is used to export data into the structure_base_shear table database using
        the accelerations obtained in the simulation for every story.

        Compute shear by story and direction, and then the base shear.
        Story shear is computed as:
          -> The mean of the acceleration in the 4 nodes of the story dot mass of the story
          -> Story mass: Area * Thickness * Density + Core Area * Core Thickness * Density
        Then, summ all the story shears to get the base shear
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units = kwargs.get("bs_units", self._bs_units)
        accelerations = self.acc_matrixes
        base_reactions = [[], [], []]
        # Define areas and core thicknesses, areas in m2 and thicknesses in m
        # TODO: Include the columns in the area and length dictionaries.
        areas = {
            20: {
                "slabs_area": 704.0,
                "external_core": 28.0,
                "internal_core_x": 112.0,
                "internal_core_y": 94.5,
            }
        }

        # Define thicknesses
        thickness = {
            20: {
                "slabs_thickness": [0.15] * self.stories,
                "external_core": [0.40] * 4 + [0.30] * 6 + [0.25] * 5 + [0.15] * 5,
                "internal_core_x": [0.35] * 4 + [0.25] * 6 + [0.15] * 5 + [0.15] * 5,
                "internal_core_y": [0.25] * 4 + [0.15] * 6 + [0.15] * 5 + [0.15] * 5,
            }
        }

        # Define densities
        density = 2.400  # tonf/m3

        # Compute Story Mases in a dict
        masses = {
            20: {
                k: areas[20]["slabs_area"]
                * thickness[20]["slabs_thickness"][k]
                * density
                + areas[20]["external_core"]
                * thickness[20]["external_core"][k]
                * density
                + areas[20]["internal_core_x"]
                * thickness[20]["internal_core_x"][k]
                * density
                + areas[20]["internal_core_y"]
                * thickness[20]["internal_core_y"][k]
                * density
                for k in range(self.stories)
            }
        }

        # For each story, compute the mean acceleration in the 4 nodes of the story

        # Compute the shear for every story and direction (X,Y,Z) and store it in a dict

        # Finally, compute the base shear for every story and direction

        # Return the base shear for every direction in the same format as the function
        # structure_base_shear_byReactionForces

        # Upload results to the database

    def structure_max_base_shear_byAccelerations(self, **kwargs):
        pass

    # ==================================================================================
    # COMPLEMENTARY FUNCTIONS
    # ==================================================================================
    # FIXME: sm_input_pga and sm_input_spectrum are not working cause they needs
    # FIXME: the ShakerMaker package to be installed in the computer to work.
    # FIXME: ShakeMaker is not implemented in Windows yet. On the other hand,
    # FIXME: all the input data is already in the database, so this functions are
    # FIXME: not necessary for the moment.
    # NOTE: YOU HAVE TO CHANGE SM_INPUT PGA AND SM_INPUT SPECTRUM TO WORK WITH THE
    # NOTE: NEW ALGORITH TO EXTRACT THE DATA FROM THE ACCELERATIONS FILE.
    # NOTE: THE CODE EXIST AND LETS TRY EXTRACT THE DATA AS A PANDAS DF AND THEN COMPUTE
    # NOTE: THE PGA AND SPECTRUM, BUT IT IS NOT WORKING YET.
    @staticmethod
    def pwl(vector_a, w, chi):
        # variables
        h = 0.005
        u_t = [0.0]
        up_t = [0.0]
        upp_t = [0.0]
        m = 1
        w_d = w * np.sqrt(1 - chi**2)  # 1/s

        sin = np.sin(w_d * h)
        cos = np.cos(w_d * h)
        e = np.exp(-chi * w * h)
        raiz = np.sqrt(1 - chi**2)
        división = 2 * chi / (w * h)

        A = e * (chi * sin / raiz + cos)  # check
        B = e * (sin / w_d)  # check
        C = (1 / w**2) * (
            división
            + e
            * (
                ((1 - (2 * chi**2)) / (w_d * h) - chi / raiz) * sin
                - (1 + división) * cos
            )
        )  # check
        D = (1 / w**2) * (
            1 - división + e * ((2 * chi**2 - 1) * sin / (w_d * h) + división * cos)
        )  # check

        A1 = -e * ((w * sin) / raiz)  # check
        B1 = e * (cos - chi * sin / raiz)  # check
        C1 = (1 / w**2) * (
            -1 / h + e * ((w / raiz + chi / (h * raiz)) * sin + cos / h)
        )  # check
        D1 = (1 / w**2) * (1 / h - (e / h * (chi * sin / raiz + cos)))  # check

        vector_a.insert(0, 0)

        for i in range(len(vector_a) - 1):
            pi = -(vector_a[i]) * m  # pi
            pi1 = -(vector_a[i + 1]) * m  # pi+1

            ui = u_t[i]  # u_i(t)
            vi = up_t[i]  # v_i(t)
            ui1 = A * ui + B * vi + C * pi + D * pi1  # u_i+1
            upi1 = A1 * ui + B1 * vi + C1 * pi + D1 * pi1  # up_i+1

            u_t.append(ui1)
            up_t.append(upi1)

        vector_a.pop(0)
        u_t.pop(0)
        up_t.pop(0)

        return u_t, up_t

    def model_linearity(self):
        """
        This function is used to create the model_linearity table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        cnx = self.db_manager.cnx

        # create table
        insert_query = "INSERT INTO model_linearity(Type) VALUES (%s)"
        values = ("Linear",)
        cursor.execute(insert_query, values)
        insert_query = "INSERT INTO model_linearity(Type) VALUES (%s)"
        values = ("Non Linear",)
        cursor.execute(insert_query, values)
        cnx.commit()
        print("model_linearity created correctly!\n")

    def simulation_type(self):
        """
        This function is used to create the simulation_type table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        cnx = self.db_manager.cnx

        # create table
        insert_query = "INSERT INTO simulation_type(Type) VALUES (%s)"
        values = ("Fix Base Model",)
        cursor.execute(insert_query, values)
        insert_query = "INSERT INTO simulation_type(Type) VALUES (%s)"
        values = ("Soil Structure Interaction Model",)
        cursor.execute(insert_query, values)
        cnx.commit()
        print("simulation_type created correctly!\n")

    def sm_input_pga(self, **kwargs):
        pass

    def sm_input_spectrum(self, **kwargs):
        pass

    # ==================================================================================
    # COMPUTE DATAFRAMES FOR ACCELERATIONS AND DISPLACEMENTS
    # ==================================================================================
    def _computeAbsAccelerationsDF(self):
        accelerations = pd.read_excel("accelerations.xlsx", sheet_name=None)
        sheet_names = list(accelerations.keys())

        # Define file names
        file_name = "resultado_s0"
        files = {"e": [], "n": [], "z": []}
        for key in files:
            with open(f"{file_name}{key}.txt") as f:
                files[key] = [float(line.strip()) for line in f]
        acc = list(files.values())

        # Get results
        def process_data(sheet_name, counter):
            df = (
                accelerations[sheet_name].dropna().copy()
            )  # Make a copy to avoid operating on a view
            timeseries = [(round(v, 2)) for v in df.iloc[:, 0]]
            for col in df.columns[1:]:
                df.loc[:, col] += acc[counter]
            df = df.iloc[:, 1:].applymap(lambda x: "{:.2e}".format(x))
            df.index = timeseries
            return df

        df = [process_data(sheet, count) for count, sheet in enumerate(sheet_names)]
        return df

    def _computeRelativeDisplacementsDF(self):
        displacements = pd.read_excel("displacements.xlsx", sheet_name=None)
        sheet_names = list(displacements.keys())

        def process_data(sheet_name):
            df = displacements[sheet_name].dropna()
            timeseries = [(round(v, 2)) for v in df.iloc[:, 0]]
            df = df.iloc[:, 1:].copy().applymap(lambda x: "{:.2e}".format(x))
            df.index = pd.Index(timeseries, name="TimeSeries")
            return df

        df = [process_data(sheet) for sheet in sheet_names]
        return df


    # ==================================================================================
    # STATIC METHODS
    # ==================================================================================
    # NOTE: IN THE FUTURE, LET'S SEE HOW IT IS TO DIRECTLY OBTAIN A DATAFRAME AS A
    # NOTE: ATRIBUTE OF THE CLASS, INSTEAD OF CREATING A FILE AND THEN READING IT.
    """
    @staticmethod
    def create_reaction_df(self):
        # Obtener la lista de archivos de reacción
        path = os.getcwd()
        results = os.listdir(f'{path}/Reactions/')
        results_sorted = sorted(results, key=lambda x: int(x.split('-')[1].split('_')[1]))

        # Crear el DataFrame de reacciones
        nodes = [int(result.split('-')[1].split('_')[1]) for result in results_sorted]
        timesteps = np.arange(0, 50.00, 0.025)
        self.reaction_df = pd.DataFrame(index=timesteps, columns=nodes)

        # Llenar el DataFrame con valores
        for result in results_sorted:
            node = int(result.split('-')[1].split('_')[1])
            with open(f'Reactions/{result}', 'r') as file:
                for i, line in enumerate(file):
                    if i >= len(timesteps): break  # Asegúrate de no exceder el rango de timesteps
                    values = [float(num) for num in line.split()]
                    self.reaction_df.loc[timesteps[i], node] = values  # Asumiendo que cada línea tiene 3 valores para X, Y, Z

    def save_reaction_xlsx(self):
        # Guardar el DataFrame como Excel
        with pd.ExcelWriter('reactions.xlsx') as writer:
            self.reaction_df.to_excel(writer, sheet_name='Reaction East')  # X values
            self.reaction_df.to_excel(writer, sheet_name='Reaction North')  # Y values
            self.reaction_df.to_excel(writer, sheet_name='Reaction Vertical')  # Z values
    """

    @staticmethod
    def create_reaction_xlsx():
        import xlsxwriter
        import os

        # create nodes sorted list
        nodes = []
        path = os.getcwd()
        results = os.listdir(f"{path}/Reactions/")

        # sorting nodes
        for result in results:
            node = int(result.split("-")[1].split("_")[1])
            nodes.append(node)
        nodes.sort()

        # sorting files in list
        results_sorted = []
        counter = 0
        for node in nodes:
            nodeid = f"_{node}-"
            for result in results:
                if nodeid in result:
                    results_sorted.append(result)

        # define format
        workbook = xlsxwriter.Workbook("reactions.xlsx")
        main_format = workbook.add_format({"bold": True})
        main_format.set_align("center")
        second_format = workbook.add_format({"font_color": "black"})
        second_format.set_align("center")

        # open book and start writing in shells
        x_sheet = workbook.add_worksheet("Reaction East")
        y_sheet = workbook.add_worksheet("Reaction North")
        z_sheet = workbook.add_worksheet("Reaction Vertical")
        x_sheet.write(0, 0, "Timestep/NodeID", main_format)
        y_sheet.write(0, 0, "Timestep/NodeID", main_format)
        z_sheet.write(0, 0, "Timestep/NodeID", main_format)
        x_sheet.set_column(0, 0, 17, main_format)
        y_sheet.set_column(0, 0, 17, main_format)
        z_sheet.set_column(0, 0, 17, main_format)

        # fill rows names
        row = 1
        column = 0
        time_step = 0.0
        while time_step < 50.00:
            x_sheet.write(row, column, f"{time_step:.3f}", main_format)
            y_sheet.write(row, column, f"{time_step:.3f}", main_format)
            z_sheet.write(row, column, f"{time_step:.3f}", main_format)

            time_step += 0.025
            row += 1

        # fill columns names
        row = 0
        column = 1
        files = []
        for node in range(len(nodes)):
            x_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            y_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            z_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            column += 1

        # fill matrix in correct values, here the file is the column and it's results are the rows
        files = [open(f"Reactions/{file}", "r") for file in results_sorted]
        column = 1
        for file in range(len(files)):
            nodal_result = [[(num) for num in line.split("\n")] for line in files[file]]
            row = 1
            for row_val in nodal_result:
                reaction_X = float(row_val[0].split(" ")[0])
                reaction_Y = float(row_val[0].split(" ")[1])
                reaction_Z = float(row_val[0].split(" ")[2])
                x_sheet.write(row, column, reaction_X, second_format)
                y_sheet.write(row, column, reaction_Y, second_format)
                z_sheet.write(row, column, reaction_Z, second_format)
                row += 1

            column += 1

        workbook.close()

    @staticmethod
    def create_displacement_xlsx():
        import xlsxwriter
        import os

        # create nodes sorted list
        nodes = []
        path = os.getcwd()
        results = os.listdir(f"{path}/Displacements/")

        # sorting nodes
        for result in results:
            node = int(result.split("-")[1].split("_")[1])
            nodes.append(node)
        nodes.sort()

        # sorting files in list
        results_sorted = []
        counter = 0
        for node in nodes:
            nodeid = f"_{node}-"
            for result in results:
                if nodeid in result:
                    results_sorted.append(result)

        # define format
        workbook = xlsxwriter.Workbook("displacements.xlsx")
        main_format = workbook.add_format({"bold": True})
        main_format.set_align("center")
        second_format = workbook.add_format({"font_color": "black"})
        second_format.set_align("center")

        # open book and start writing in shells
        x_sheet = workbook.add_worksheet("Displacements East")
        y_sheet = workbook.add_worksheet("Displacements North")
        z_sheet = workbook.add_worksheet("Displacements Vertical")
        x_sheet.write(0, 0, "Timestep/NodeID", main_format)
        y_sheet.write(0, 0, "Timestep/NodeID", main_format)
        z_sheet.write(0, 0, "Timestep/NodeID", main_format)

        x_sheet.set_column(0, 0, 17, main_format)
        y_sheet.set_column(0, 0, 17, main_format)
        z_sheet.set_column(0, 0, 17, main_format)

        # fill rows names
        row = 1
        column = 0
        time_step = 0.0
        while time_step < 50:
            x_sheet.write(row, column, time_step, main_format)
            y_sheet.write(row, column, time_step, main_format)
            z_sheet.write(row, column, time_step, main_format)

            time_step += 0.025
            row += 1

        # fill columns names
        row = 0
        column = 1
        files = []
        for node in range(len(nodes)):
            x_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            y_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            z_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            column += 1

        # fill matrix in correct values, here the file is the column and it's results are the rows
        files = [open(f"Displacements/{file}", "r") for file in results_sorted]
        column = 1
        for file in range(len(files)):
            nodal_result = [[(num) for num in line.split("\n")] for line in files[file]]
            row = 1
            for row_val in nodal_result:
                acceleration_X = float(row_val[0].split(" ")[0])
                acceleration_Y = float(row_val[0].split(" ")[1])
                acceleration_Z = float(row_val[0].split(" ")[2])
                x_sheet.write(row, column, acceleration_X, second_format)
                y_sheet.write(row, column, acceleration_Y, second_format)
                z_sheet.write(row, column, acceleration_Z, second_format)
                row += 1

            column += 1

        workbook.close()

    @staticmethod
    def create_accelerations_xlsx():
        import xlsxwriter
        import os

        # create nodes sorted list
        nodes = []
        path = os.getcwd()
        results = os.listdir(f"{path}/Accelerations/")

        # sorting nodes
        for result in results:
            node = int(result.split("-")[1].split("_")[1])
            nodes.append(node)
        nodes.sort()

        # sorting files in list
        results_sorted = []
        counter = 0
        for node in nodes:
            nodeid = f"_{node}-"
            for result in results:
                if nodeid in result:
                    results_sorted.append(result)

        # define format
        workbook = xlsxwriter.Workbook("accelerations.xlsx")
        main_format = workbook.add_format({"bold": True})
        main_format.set_align("center")
        second_format = workbook.add_format({"font_color": "black"})
        second_format.set_align("center")

        # open book and start writing in shells
        x_sheet = workbook.add_worksheet("Accelerations East")
        y_sheet = workbook.add_worksheet("Accelerations North")
        z_sheet = workbook.add_worksheet("Accelerations Vertical")
        x_sheet.write(0, 0, "Timestep/NodeID", main_format)
        y_sheet.write(0, 0, "Timestep/NodeID", main_format)
        z_sheet.write(0, 0, "Timestep/NodeID", main_format)

        x_sheet.set_column(0, 0, 17, main_format)
        y_sheet.set_column(0, 0, 17, main_format)
        z_sheet.set_column(0, 0, 17, main_format)

        # fill rows names
        row = 1
        column = 0
        time_step = 0.0
        while time_step < 50:
            x_sheet.write(row, column, time_step, main_format)
            y_sheet.write(row, column, time_step, main_format)
            z_sheet.write(row, column, time_step, main_format)

            time_step += 0.025
            row += 1

        # fill columns names
        row = 0
        column = 1
        files = []
        for node in range(len(nodes)):
            x_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            y_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            z_sheet.write(row, column, f"Node {nodes[node]}", main_format)
            column += 1

        # fill matrix in correct values, here the file is the column and it's results are the rows
        files = [open(f"Accelerations/{file}", "r") for file in results_sorted]
        column = 1
        for file in range(len(files)):
            nodal_result = [[(num) for num in line.split("\n")] for line in files[file]]
            row = 1
            for row_val in nodal_result:
                acceleration_X = float(row_val[0].split(" ")[0])
                acceleration_Y = float(row_val[0].split(" ")[1])
                acceleration_Z = float(row_val[0].split(" ")[2])
                x_sheet.write(row, column, acceleration_X, second_format)
                y_sheet.write(row, column, acceleration_Y, second_format)
                z_sheet.write(row, column, acceleration_Z, second_format)
                row += 1

            column += 1

        workbook.close()

    # ==================================================================================
    # DEPRECATED METHODS
    # ==================================================================================
    def get_sm_id(self):

        path = Path(__file__).parent.parts
        magnitude = path[-3][-3:]
        rupture = path[-2][-4:]
        station = int(path[-1][-1]) + 1
        m = 0
        if magnitude == "6.5":
            m = 0
        elif magnitude == "6.7":
            m = 90
        elif magnitude == "6.9":
            m = 180
        elif magnitude == "7.0":
            m = 270

        r = (int(rupture[-1]) - 1) * 10
        if rupture[0:2] == "bl":
            r = (int(rupture[-1]) - 1) * 10
        elif rupture[0:2] == "ns":
            r = (int(rupture[-1]) - 1) * 10 + 30
        elif rupture[0:2] == "sn":
            r = (int(rupture[-1]) - 1) * 10 + 60

        id = m + r + station
        return id

# ==================================================================================
# SECONDARY CLASSES
# ==================================================================================
class DataBaseManager:
    """
    This class is used to manage the connection to the database.
    """

    def __init__(self, user: str, password: str, host: str, database: str):
        self.cnx = mysql.connector.connect(
            user=user, password=password, host=host, database=database
        )
        self.cursor = self.cnx.cursor()

    def insert_data(self, query: str, values: tuple):
        self.cursor.execute(query, values)
        self.cnx.commit()

    def close_connection(self):
        self.cursor.close()
        self.cnx.close()


class Plotting:
    """
    This class is used to perform the seismic analysis of the structure.
    It's used to analyse quiclky the structure and get the results of the analysis.
    You use it in the main after the results are uploaded to the database.
    """

    @staticmethod
    def pwl(vector_a, w, chi):
        # variables
        h = 0.005
        u_t = [0.0]
        up_t = [0.0]
        upp_t = [0.0]
        m = 1
        w_d = w * np.sqrt(1 - chi**2)  # 1/s

        sin = np.sin(w_d * h)
        cos = np.cos(w_d * h)
        e = np.exp(-chi * w * h)
        raiz = np.sqrt(1 - chi**2)
        división = 2 * chi / (w * h)

        A = e * (chi * sin / raiz + cos)  # check
        B = e * (sin / w_d)  # check
        C = (1 / w**2) * (
            división
            + e
            * (
                ((1 - (2 * chi**2)) / (w_d * h) - chi / raiz) * sin
                - (1 + división) * cos
            )
        )  # check
        D = (1 / w**2) * (
            1 - división + e * ((2 * chi**2 - 1) * sin / (w_d * h) + división * cos)
        )  # check

        A1 = -e * ((w * sin) / raiz)  # check
        B1 = e * (cos - chi * sin / raiz)  # check
        C1 = (1 / w**2) * (
            -1 / h + e * ((w / raiz + chi / (h * raiz)) * sin + cos / h)
        )  # check
        D1 = (1 / w**2) * (1 / h - (e / h * (chi * sin / raiz + cos)))  # check

        vector_a.insert(0, 0)

        for i in range(len(vector_a) - 1):
            pi = -(vector_a[i]) * m  # pi
            pi1 = -(vector_a[i + 1]) * m  # pi+1

            ui = u_t[i]  # u_i(t)
            vi = up_t[i]  # v_i(t)
            ui1 = A * ui + B * vi + C * pi + D * pi1  # u_i+1
            upi1 = A1 * ui + B1 * vi + C1 * pi + D1 * pi1  # up_i+1

            u_t.append(ui1)
            up_t.append(upi1)

        vector_a.pop(0)
        u_t.pop(0)
        up_t.pop(0)

        return u_t, up_t

    @staticmethod
    def NCh433Spectrum(S, Ao, R, I, To, p):
        T = np.linspace(0, 3, 2000)
        Sah = np.zeros(2000)
        Sav = np.zeros(2000)

        for i in range(2000):
            tn = T[i]
            alpha = (1 + 4.5 * (tn / To) ** p) / (1 + (tn / To) ** 3)
            Sah[i] = S * Ao * alpha / (R / I)
            Sav[i] = 2 / 3 * S * Ao * alpha / (R / I)
        Sah = np.delete(Sah, 0)
        Sav = np.delete(Sav, 0)
        return T, Sah, Sav

    @staticmethod
    def plotDrift(driftx, drifty, stories, title):
        plt.plot(driftx, stories)
        plt.plot(drifty, stories)
        plt.yticks(range(1, 21))  # Rango del eje y de 1 a 20
        plt.ylabel("Story")
        plt.xlabel("Drift")
        plt.title(title)
        plt.legend(["Drift X", "DriftY"])
        # Establecer el formato de porcentaje en el eje y
        plt.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
        plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

        plt.axvline(x=0.002, color="r", linestyle="--")
        plt.grid()
        plt.show()

    def plotFileSpectrum(self, fileX, fileY, fileZ):
        S = 0.9
        To = 0.15  # [s]
        p = 2
        Ao = 0.3 * 9.81
        I = 1.2
        R = 1
        T, Sah_433, Sav_433 = self.NCh433Spectrum(S, Ao, R, I, To, p)

        plt.figure(figsize=(23.54, 13.23), dpi=108)
        nu = 0.05
        dt = T
        dt = np.delete(dt, 0)
        w = np.zeros(len(dt))

        for i in range(len(dt)):
            if dt[i] != 0.0:
                w[i] = 2 * np.pi / dt[i]

        with open(fileZ) as filez:
            dataz = filez.read()
        dataz = dataz.split("\n")
        dataz.pop(-1)
        dataz.pop(-1)
        az = [float(acce) for acce in dataz]
        Spaz = []
        for j in range(len(w)):
            wi = w[j]
            u_z, v_z = self.pwl(az, wi, nu)
            Saz = max(max(u_z), (abs(min(u_z)))) * wi**2
            Spaz.append(Saz)

        plt.plot(dt, Sav_433, "k--", label="NCh433")
        plt.plot(dt, Spaz, "-", label="Record 6.5BL1S4 Vertical", color="blue")

        y433 = np.interp(2.4, dt, Sav_433)
        year = np.interp(2.4, dt, Spaz)
        plt.scatter(
            2.4, y433, color="black", label=f"Value for T=2.4: Spa={round(y433,2)}"
        )
        plt.scatter(
            2.4, year, color="blue", label=f"Value for T=2.4: Spa={round(year,2)}"
        )
        plt.plot([2.4, 2.4], [0, y433], "--r")
        plt.text(2.4, y433 + 0.1, f"({2.4},{y433:.2f})")
        plt.text(2.4, year + 0.1, f"({2.4},{year:.2f})")
        plt.title("Spa Vertical")
        plt.xlabel("Period T [s]")
        plt.ylabel("Acceleration [m/s/s]")
        plt.legend()
        plt.grid()
        plt.show()

        plt.figure(figsize=(23.54, 13.23), dpi=108)
        with open(fileX) as filex:
            datax = filex.read()
        datax = datax.split("\n")
        datax.pop(-1)
        datax.pop(-1)
        ae = [float(acce) for acce in datax]
        Spe = []
        for j in range(len(w)):
            wi = w[j]
            u_x, v_x = self.pwl(ae, wi, nu)
            Sae = max(max(u_x), (abs(min(u_x)))) * wi**2
            Spe.append(Sae)
        with open(fileY) as filey:
            datay = filey.read()
        datay = datay.split("\n")
        datay.pop(-1)
        datay.pop(-1)
        an = [float(acce) for acce in datay]
        Spn = []
        for j in range(len(w)):
            wi = w[j]
            u_y, v_y = self.pwl(an, wi, nu)
            San = max(max(u_y), (abs(min(u_y)))) * wi**2
            Spn.append(San)

        y433 = np.interp(2.4, dt, Sah_433)
        year1 = np.interp(2.4, dt, Spe)
        year2 = np.interp(2.4, dt, Spn)
        plt.scatter(
            2.4, y433, color="black", label=f"Value for x = 2.4: Spa={round(y433,2)}"
        )
        plt.scatter(
            2.4, year1, color="blue", label=f"Value for x = 2.4: Spa={round(year1,2)}"
        )
        plt.scatter(
            2.4, year2, color="orange", label=f"Value for x = 2.4: Spa={round(year2,2)}"
        )
        plt.plot([2.4, 2.4], [0, y433], "--r")

        plt.plot(dt, Sah_433, "k--", label="NCh433")
        plt.plot(dt, Spe, "-", label="Registro 6.5BL1S4 Este", color="blue")
        plt.plot(dt, Spn, "-", label="Registro 6.5BL1S4 Norte", color="orange")
        plt.title("Spa Horizontal")
        plt.xlabel("Period T [s]")
        plt.ylabel("Acceleration [m/s/s]")
        plt.legend()
        plt.grid()
        plt.show()

    @staticmethod
    def plotFileAccelerations(fileX, fileY, fileZ):
        time = np.arange(0, 50, 0.025)  # len = 2000

        with open(fileX) as filex:
            datax = filex.read()
        datax = datax.split("\n")
        datax.pop(-1)
        datax.pop(-1)
        datax = [float(acce) for acce in datax]

        with open(fileY) as filey:
            datay = filey.read()
        datay = datay.split("\n")
        datay.pop(-1)
        datay.pop(-1)
        datay = [float(acce) for acce in datay]

        with open(fileZ) as filez:
            dataz = filez.read()
        dataz = dataz.split("\n")
        dataz.pop(-1)
        dataz.pop(-1)
        dataz = [float(acce) for acce in dataz]

        plt.plot(time, datax)
        plt.plot(time, datay)
        plt.plot(time, dataz, "--")

        plt.legend(["East", "North", "Vertical"])
        plt.title("Earthquake")
        plt.ylabel("Acceleration[m/s/s]")
        plt.xlabel("Time[s]")
        plt.grid()
        plt.tight_layout()
        plt.show()

    def plotInputSpectrum(
        self,
        input1,
        input2,
        input3,
        label1="",
        label2="",
        label3="",
        nch433=False,
        title="",
        option="",
        fourier=False,
    ):
        S = 0.9
        To = 0.15  # [s]
        p = 2
        Ao = 0.3 * 9.81
        I = 1.2
        R = 1
        T, Sah_433, Sav_433 = self.NCh433Spectrum(S, Ao, R, I, To, p)
        nu = 0.05
        dt = T
        dt = np.delete(dt, 0)
        w = np.zeros(len(dt))
        for i in range(len(dt)):
            if dt[i] != 0.0:
                w[i] = 2 * np.pi / dt[i]

        if fourier == True:
            w = np.delete(w, np.s_[0:139])
            fft_result1 = np.fft.fft(input1)
            fft_result2 = np.fft.fft(input2)
            fft_result3 = np.fft.fft(input3)
            amplitude_spectrum1 = np.abs(fft_result1)
            amplitude_spectrum2 = np.abs(fft_result2)
            amplitude_spectrum3 = np.abs(fft_result3)
            amplitude_spectrum1 = np.delete(amplitude_spectrum1, np.s_[0:140])
            amplitude_spectrum2 = np.delete(amplitude_spectrum2, np.s_[0:140])
            # plt.loglog(w,amplitude_spectrum1,label=label1)
            # plt.loglog(w,amplitude_spectrum2,label=label2)
            plt.loglog(w, amplitude_spectrum3, label=label3)
            plt.yscale("log")
            plt.xlabel("Frequency w [Hz]")
            plt.ylabel("Log Acceleration [m/s/s]")
        else:
            plt.figure(figsize=(23.54, 13.23), dpi=108)

            i1 = []
            for j in range(len(w)):
                wi = w[j]
                u_x, v_x = self.pwl(input1, wi, nu)
                Sae = max(max(u_x), (abs(min(u_x)))) * wi**2
                i1.append(Sae)
            i2 = []
            for j in range(len(w)):
                wi = w[j]
                u_y, v_y = self.pwl(input2, wi, nu)
                San = max(max(u_y), (abs(min(u_y)))) * wi**2
                i2.append(San)
            i3 = []
            for j in range(len(w)):
                wi = w[j]
                u_y, v_y = self.pwl(input3, wi, nu)
                San = max(max(u_y), (abs(min(u_y)))) * wi**2
                i3.append(San)

            if nch433 == True:
                plt.plot(dt, Sah_433, "k--", label="NCh433")
            if option == "loglog":
                plt.loglog(dt, i1, "-", label=label1, color="blue")
                plt.loglog(dt, i2, "-", label=label2, color="orange")
                plt.loglog(dt, i3, "-", label=label3, color="red")
            elif option == "":
                plt.plot(dt, i1, "-", label=label1, color="blue")
                plt.plot(dt, i2, "-", label=label2, color="orange")
                plt.plot(dt, i3, "-", label=label3, color="red")
            plt.xlabel("Period T [s]")
            plt.ylabel("Acceleration [m/s/s]")
        plt.title(title)
        plt.legend()
        plt.grid()
        plt.show()


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

    def __init__(self, fidelity=0):
        # Set the path to the 'PartitionsInfo' subfolder
        current_path = Path(__file__).parent
        self.path = Path(__file__).parent / "PartitionsInfo"

        # Check if the 'PartitionsInfo' subfolder exists
        if not self.path.exists():
            raise Exception(
                "The PartitionsInfo folder does not exist!\n"
                "Current path = {}".format(current_path)
            )
        # Access to folders within the 'PartitionsInfo' subfolder
        folders = self.path.iterdir()
        for folder in folders:
            if folder.is_dir():  # Asegurarse de que solo se procesen directorios
                folder_name = folder.name
                setattr(self, f"folder_{folder_name}", folder)
        dict_folders = {
            f"folder_{folder.name}": folder for folder in folders if folder.is_dir()
        }
        # Call the methods to initialize the data
        (
            self.coordenates,
            self.drift_nodes,
            self.stories_nodes,
            self.stories,
            self.subs,
            self.heights,
        ) = self.give_coords_info()

        self.accelerations, self.acce_nodes = self.give_accelerations()
        self.displacements, self.displ_nodes = self.give_displacements()
        if fidelity == 0:
            self.reactions, self.reaction_nodes = self.give_reactions()
        self.nnodes, self.nelements, self.npartitions = self.give_model_info()

    def give_accelerations(self):
        # check nodes
        files_accel = self.path / self.folder_accel
        files = [open(file, "r") for file in files_accel.iterdir() if file.is_file()]
        # create dictionary
        accelerations = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")] for line in files[file]]
            file_id = (
                str(files[file])
                .split("/")[-1]
                .split("-")[1]
                .split(" ")[0]
                .split(".")[0]
            )
            accelerations[f"Partition {file_id}"] = {}
            for nodei in range(len(nodes)):
                accelerations[f"Partition {file_id}"][f"Node {nodei}"] = nodes[nodei][0]

        # create list with nodes sorted
        acce_nodes = []
        for values in accelerations.values():
            for node in values.values():
                acce_nodes.append(int(node))
        acce_nodes.sort()

        listed = set(acce_nodes)
        if len(acce_nodes) == len(listed):
            print("Accelerations: No nodes repeated")
        else:
            raise Exception("WARNING: NODES REPEATED")

        return accelerations, acce_nodes

    def give_displacements(self):
        # check nodes
        files_disp = self.path / self.folder_disp
        files = [open(file, "r") for file in files_disp.iterdir() if file.is_file()]

        # create dictionary
        displacements = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")] for line in files[file]]
            file_id = (
                str(files[file])
                .split("/")[-1]
                .split("-")[1]
                .split(" ")[0]
                .split(".")[0]
            )
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
            print("Displacements: No nodes repeated")
        else:
            raise Exception("WARNING: NODES REPEATED")

        return displacements, displ_nodes

    def give_reactions(self):
        # check nodes
        files_reaction = self.path / self.folder_reaction
        files = [open(f"{self.folder_reaction}/{file}", "r") for file in files_reaction]

        # create dictionary
        reactions = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")] for line in files[file]]
            file_id = (
                str(files[file])
                .split("/")[-1]
                .split("-")[1]
                .split(" ")[0]
                .split(".")[0]
            )
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
            print("Reactions:     No nodes repeated ")
        else:
            raise Exception("WARNING: NODES REPEATED")
        return reactions, reaction_nodes

    def give_coords_info(self):
        # check nodes
        files_coords = self.path / self.folder_coords
        print(files_coords)
        files = [open(file, "r") for file in files_coords.iterdir() if file.is_file()]
        # files = [open(f'{self.folder_coords()}/{file}','r') for file in files_coords]
        # files = [open(f'{self.folder_coords}/{file.name}', 'r') for file in files_coords if file.is_file()]

        # create dictionary
        coordenates = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split("\n")] for line in files[file]]
            file_id = str(files[file]).split("_")[2].split(".")[0]

            for nodei in range(1, len(nodes)):
                node_id = nodes[nodei][0].split(" ")[0]
                coord_x = round(float(nodes[nodei][0].split(" ")[1]), 1)
                coord_y = round(float(nodes[nodei][0].split(" ")[2]), 1)
                coord_z = round(float(nodes[nodei][0].split(" ")[3]), 1)
                coordenates[f"Node {node_id}"] = {}
                coordenates[f"Node {node_id}"] = {}
                coordenates[f"Node {node_id}"] = {}
                coordenates[f"Node {node_id}"]["coord x"] = float(f"{coord_x:.1f}")
                coordenates[f"Node {node_id}"]["coord y"] = float(f"{coord_y:.1f}")
                coordenates[f"Node {node_id}"]["coord z"] = float(f"{coord_z:.1f}")

        # sort every node per level
        sorted_nodes = sorted(
            coordenates.items(),
            key=lambda x: (x[1]["coord x"], x[1]["coord y"], x[1]["coord z"]),
        )
        # create dictionary with specific nodes per corner to calculate directly the drift
        drift_nodes = {"corner1": [], "corner2": [], "corner3": [], "corner4": []}

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
                drift_nodes["corner1"][data + 1].split("|")[1]
            ) - float(drift_nodes["corner1"][data].split("|")[1])
            heights.append(current_height)

        # create dict with nodes per historie
        sort_by_historie = sorted(
            coordenates.items(),
            key=lambda x: (x[1]["coord z"], x[1]["coord x"], x[1]["coord y"]),
        )
        stories_nodes = {}
        counter = 0
        for i in range(stories + subs + 1):
            i -= subs
            if i < 0:
                counter += 4
                continue
            stories_nodes[f"Level {i}"] = {}
            node1 = sort_by_historie[counter][0]
            node2 = sort_by_historie[counter + 1][0]
            node3 = sort_by_historie[counter + 2][0]
            node4 = sort_by_historie[counter + 3][0]
            # print(node1,node2,node3,node4)
            stories_nodes[f"Level {i}"][node1] = sort_by_historie[counter][1]
            stories_nodes[f"Level {i}"][node2] = sort_by_historie[counter + 1][1]
            stories_nodes[f"Level {i}"][node3] = sort_by_historie[counter + 2][1]
            stories_nodes[f"Level {i}"][node4] = sort_by_historie[counter + 3][1]
            counter += 4
        heights.insert(
            0,
            (
                coordenates[list(stories_nodes["Level 1"])[0]]["coord z"]
                - coordenates[list(stories_nodes["Level 0"])[0]]["coord z"]
            ),
        )
        return coordenates, drift_nodes, stories_nodes, stories, subs, heights

    def give_model_info(self):
        # read file
        file = open(f"{self.folder_info}/model_info.csv", "r")

        # get number of nodes and number of elements
        info = [[row for row in line.split(" ")] for line in file]
        nnodes = int(info[0][4])
        nelements = int(info[1][4])
        npartitions = int(info[2][4])
        file.close()
        return nnodes, nelements, npartitions
