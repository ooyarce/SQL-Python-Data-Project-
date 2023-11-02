from matplotlib import pyplot as plt
from pathlib import Path
import mysql.connector
import pandas as pd
import numpy as np
import glob
import datetime
import json	
import os


class DataBaseManager:
    """
    This class is used to manage the connection to the database.
    """
    def __init__(self, user, password, host, database):
        self.cnx = mysql.connector.connect(
            user=user, 
            password=password, 
            host=host, 
            database=database)
        self.cursor = self.cnx.cursor()

    def insert_data(self, query, values):
        self.cursor.execute(query, values)
        self.cnx.commit()
        
    def close_connection(self):
        self.cursor.close()
        self.cnx.close()

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
    def __init__(self, db_user, db_password, db_host, db_database, **kwargs):
        """
        This function is used to initialize the parameters.
        """
        # initialize database manager and cursor
        self.db_manager = DataBaseManager(db_user, db_password, db_host, db_database)
        
        # initialize parameters
        bench_cluster             = 'Esmeralda HPC Cluster by jaabell@uandes.cl'
        modelname               = glob.glob("*.scd")[0]
        self._sim_comments      = kwargs.get('sim_comments'     , 'No comments'   )
        self._sim_opt           = kwargs.get('sim_opt'          , 'No options yet')
        self._sim_stage         = kwargs.get('sim_stage'        , 'No stage yet'  )
        self._sim_type          = kwargs.get('sim_type'         , 1               )
        self._sm_input_comments = kwargs.get('sm_input_comments', 'No comments'   )
        self._model_name        = kwargs.get('model_name'       , modelname       )
        self._model_comments    = kwargs.get('model_comments'   , 'No comments'   ) 
        self._bench_cluster     = kwargs.get('bench_cluster'    , bench_cluster   )
        self._bench_comments    = kwargs.get('bench_comments'   , 'No comments'   )
        self._perf_comments     = kwargs.get('perf_comments'    , 'No comments'   )
        self._specs_comments    = kwargs.get('specs_comments'   , 'No comments'   ) 
        self._pga_units         = kwargs.get('pga_units'        , 'm/s/s'         )
        self._resp_spectrum     = kwargs.get('resp_spectrum'    , 'm/s/s'         )
        self._abs_acc_units     = kwargs.get('abs_acc_units'    , 'm/s/s'         )
        self._rel_displ_units   = kwargs.get('rel_displ_units'  , 'm'             )
        self._max_drift_units   = kwargs.get('max_drift_units'  , 'm'             )
        self._max_bs_units      = kwargs.get('max_bs_units'     , 'kN'            )
        self._bs_units          = kwargs.get('bs_units'         , 'kN'            )
        self._linearity         = kwargs.get('linearity'        , 1               )
        self._fidelity          = kwargs.get('fidelity'         , False           )
        
        # initialize model info class
        self.model_info = ModelInfo(fidelity=self._fidelity)
        
    # ==================================================================================
    # SQL FUNCTIONS
    # ==================================================================================
    def simulation(self, **kwargs):
        """
        This is the main function to export the simulation into the database.
        """
        # initialize parameters
        cursor            = self.db_manager.cursor
        sim_comments      = kwargs.get('sim_comments', self._sim_comments)
        sim_opt           = kwargs.get('sim_opt'     , self._sim_opt     )
        sim_stage         = kwargs.get('sim_stage'   , self._sim_stage   ) 
        sim_type          = kwargs.get('sim_type'    , self._sim_type    )
        
        print("---------------------------------------------|")
        print("----------EXPORTING INTO DATABASE------------|")
        print("---------------------------------------------|")
        
        # fills simulation and simulation_sm_input tables
        self.simulation_model()
        Model = cursor.lastrowid
        self.simulation_sm_input()
        SM_Input = cursor.lastrowid
        
        # get date
        date = datetime.datetime.now()
        date = date.strftime("%B %d, %Y")
        
        # insert data into database
        insert_query = ('INSERT INTO simulation('
                        'idModel, idSM_Input, idType, SimStage, SimOptions, Simdate,'
                        'Comments) VALUES(%s,%s,%s,%s,%s,%s,%s)')
        values       = (Model, SM_Input, sim_type, sim_stage, sim_opt, date, sim_comments)
        self.db_manager.insert_data(insert_query, values)
        self.db_manager.close_connection()
        
        print('simulation table updated correctly!\n')
        print("---------------------------------------------|")
        print("---------------------------------------------|")
        print("---------------------------------------------|\n")
    def simulation_sm_input(self, **kwargs):
        """
        This function is used to export the simulation sm input into the database.
        """
        # initialize parameters
        cursor            = self.db_manager.cursor
        sm_input_comments = kwargs.get('sm_input_comments', self._sm_input_comments)
        
        # get magnitude
        Magnitude = (os.path.dirname(__file__).split('\\')[-3][1:])
        Magnitude = (f'{Magnitude} Mw')

        # get rupture type
        Rup_type = os.path.dirname(__file__).split('\\')[-2].split('_')[1]
        if   Rup_type == 'bl':rupture = 'Bilateral'
        elif Rup_type == 'ns':rupture = 'North-South'
        elif Rup_type == 'sn':rupture = 'South-North'
        else:
            raise TypeError('Folders name are not following the format'
                             'rup_[bl/ns/sn]_[iteration].')

        # get realization id
        iteration = os.path.dirname(__file__).split('\\')[-2].split('_')[2]
        
        # get location
        location_mapping = {
        0: 'UAndes Campus',
        1: 'Near field North',
        2: 'Near field Center',
        3: 'Near field South',
        4: 'Intermediate field North',
        5: 'Intermediate field Center',
        6: 'Intermediate field South',
        7: 'Far field North',
        8: 'Far field Center',
        9: 'Far field South'
        }
        
        station = int(os.path.dirname(__file__).split('\\')[-1][-1])
        location = location_mapping.get(station, 'Unknown location')
        
        # PGA y Spectrum
        Pga          = self.get_sm_id()
        Spectrum     = self.get_sm_id()
        
        # Insert data into database
        insert_query = ('INSERT INTO simulation_sm_input(idPGA, idSpectrum, Magnitude,'
                        'Rupture_type, Location, RealizationID, Comments)'
                        ' VALUES(%s,%s,%s,%s,%s,%s,%s)')
        values       = (Pga, Spectrum, Magnitude, rupture, location, iteration, sm_input_comments)  # noqa: E501
        cursor.execute(insert_query,values)
        print('simulation_sm_input table updated correctly!\n')
    def simulation_model(self, **kwargs):
        """
        This function is used to export data into the simulation_model table database.
        """
        # initialize parameters
        cursor          = self.db_manager.cursor
        model_name      = kwargs.get('model_name'    , self._model_name    )
        model_comments  = kwargs.get('model_comments', self._model_comments)

        # fills benchmark, structure perfomance and specs structure tables
        self.model_benchmark()
        Benchmark = cursor.lastrowid
        self.model_structure_perfomance()
        StructurePerfomance = cursor.lastrowid
        self.model_specs_structure()
        SpecsStructure = cursor.lastrowid

        insert_query = ('INSERT INTO simulation_model('
                        'idBenchmark,idStructuralPerfomance,idSpecsStructure,'
                        'ModelName,Comments) VALUES(%s,%s,%s,%s,%s)')
        values = (Benchmark,StructurePerfomance,SpecsStructure,model_name, model_comments)
        cursor.execute(insert_query,values)
        print('simulation_model table updated correctly!\n')  
    def model_benchmark(self, **kwargs):
        #------------------------------------------------------------------------------------------------------------------------------------
        # Get calculus time from log file, nodes, threads and comments
        #------------------------------------------------------------------------------------------------------------------------------------
        # initialize parameters
        cursor        = self.db_manager.cursor
        bench_cluster = kwargs.get('bench_cluster' , self._bench_cluster )
        comments      = kwargs.get('bench_comments', self._bench_comments)
        
        # get job name, nodes, threads and logname
        data = open('run.sh')
        counter = 0

        for row in data:
            #get job name
            if counter == 1:
                jobname = (row.split(' ')[1].split('=')[1])
            #get nodes
            if counter == 2:
                nodes = int(row.split('=')[1].split('\n')[0])

            #get threads
            if counter == 3:
                threads = int(row.split('=')[1].split('\n')[0])

            #get logname
            if counter == 4:
                logname = (row.split('=')[1].split(' ')[0])

            counter += 1

        log = open(logname)
        for row in log:
            if 'Elapsed:' in row:
                value = row.split(' ')[1]
                time = (f'{value} seconds') #first value of query

        path1 = f'{os.path.dirname(__file__)}/Accelerations/'
        path2 = f'{os.path.dirname(__file__)}/Displacements/'
        path3 = f'{os.path.dirname(__file__)}/Reactions/'
        path4 = f'{os.path.dirname(__file__)}/PartitionsInfo/'

        acc_results = 0
        displ_results = 0
        react_results = 0
        results_results = 0

        #get accelerations
        for file in os.listdir(path1):
            path = os.path.join(path1,file)
            acc_results += os.path.getsize(path)
        acc_size = acc_results/(1024*1024)

        #get displacements
        for file in os.listdir(path2):
            path = os.path.join(path2,file)
            displ_results += os.path.getsize(path)
        displ_size = displ_results/(1024*1024)

        #get reactions 
        for file in os.listdir(path3):
            path = os.path.join(path3,file)
            react_results += os.path.getsize(path)
        reac_size = react_results/(1024*1024)

        #get results
        for file in os.listdir(path4):
            path = os.path.join(path4,file)
            results_results += os.path.getsize(path)
        results_size = results_results/(1024*1024)
        memory_by_results = f'{acc_size + displ_size + reac_size + results_size:.2f} Mb'
        
        #get model memory
        model_name = glob.glob("*.scd")[0]
        memory_by_model = f'{os.path.getsize(model_name)/(1024*1024):.2f} Mb'
        insert_query = ('INSERT INTO model_benchmark (JobName,SimulationTime,'
                        'MemoryResults,MemoryModel,ClusterNodes,CpuPerNodes,ClusterName,'
                        'Comments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)')
        values = (jobname,
                  time,
                  memory_by_results,
                  memory_by_model,
                  nodes,
                  threads,
                  bench_cluster,
                  comments)
        cursor.execute(insert_query, values)	
        print('model_benchmark table updated correctly!\n') 
    def model_specs_structure(self, **kwargs):
        """
        This function is used to export data into the model_specs_structure table database.
        """
        # initialize parameters
        cursor          = self.db_manager.cursor
        linearity       = kwargs.get('linearity'     , self._linearity     )
        comments        = kwargs.get('specs_comments', self._specs_comments)
        
        if linearity < 1 or linearity > 2:
            raise TypeError('The Linearity parameter can only take 1 or 2 values(int).')

        nnodes, nelements, npartitions = self.model_info.give_model_info()
        (coordenates, drift_nodes, story_nodes,
         stories    , subs       , heights    ) = self.model_info.give_coords_info()

        insert_query = ('INSERT INTO model_specs_structure ('
                        'idLinearity, Nnodes, Nelements, Nstories, Nsubs,'
                        'InterstoryHeight, Comments) VALUES (%s,%s,%s,%s,%s,%s,%s)')
        values = (
            linearity,
            nnodes,
            nelements,
            stories,
            subs,
            json.dumps(heights),
            comments)
        cursor.execute(insert_query, values)		
        print('model_specs_structure table updated correctly!\n') 
    def model_structure_perfomance(self, **kwargs):
        """
        This function is used to export data into the model_structure_perfomance table database.
        """
        # initialize parameters
        cursor          = self.db_manager.cursor
        fidelity        = kwargs.get('fidelity'      , self._fidelity      )
        comments        = kwargs.get('perf_comments' , self._perf_comments )
        
        # Base shear calculations
        if not fidelity:
            #fills base shear
            self.structure_base_shear_byReactionForces()
            BaseShear = cursor.lastrowid
            #fills max base shear
            self.structure_max_base_shear_byReactionForces()
            MaxBaseShear = cursor.lastrowid
        
        if fidelity:
            #fills base shear
            self.structure_base_shear_byAccelerations()
            
            #fills max base shear
            self.structure_max_base_shear()
            MaxBaseShear = cursor.lastrowid
        #fills absolute accelerations
        self.structure_abs_acceleration()
        AbsAccelerations = cursor.lastrowid
        
        #fills relative displacements
        self.structure_relative_displacements()
        RelativeDisplacements = cursor.lastrowid

        #fills max drift per floor
        self.structure_max_drift_per_floor()
        MaxDriftPerFloor = cursor.lastrowid

        #this is going to change in the future
        mta = 'Not implemented yet' #max torsion angle
        fas = 'Not implemented yet' #floor acceleration spectra

        #insert data into database
        if not fidelity:
            insert_query = ('INSERT INTO model_structure_perfomance '
                            '(idBaseShear,idAbsAccelerations,idRelativeDisplacements,'
                            'idMaxBaseShear,idMaxDriftPerFloor,MaxTorsionAngle,'
                            'FloorAccelerationSpectra,Comments)'
                            ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s)')
            values = (
                BaseShear,
                AbsAccelerations,
                RelativeDisplacements,
                MaxBaseShear,
                MaxDriftPerFloor,
                mta,
                fas,
                comments) #mta and fas vars has to change
            cursor.execute(insert_query, values)		
            print('model_structure_perfomance table updated correctly!\n')
        else:
            insert_query = ('INSERT INTO model_structure_perfomance '
                            '(idAbsAccelerations,idRelativeDisplacements,'
                            'idMaxDriftPerFloor,MaxTorsionAngle,'
                            'FloorAccelerationSpectra,Comments)'
                            ' VALUES (%s,%s,%s,%s,%s,%s)')
            values = (
                AbsAccelerations,
                RelativeDisplacements,
                MaxDriftPerFloor,
                mta,
                fas,
                comments) #mta and fas vars has to change
            cursor.execute(insert_query, values)		
            print('model_structure_perfomance table updated correctly!\n')
    def structure_base_shear_byAccelerations(self, **kwargs):
        """
        This function is used to export data into the structure_base_shear table database using
        the accelerations obtained in the simulation for every story.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units  = kwargs.get('bs_units', self._bs_units)
        
        # get base shear for every story
        
    def structure_base_shear_byReactionForces(self, **kwargs):
        """
        This function is used to export data into the structure_base_shear table database using
        the reactions obtained in the simulation.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units  = kwargs.get('bs_units', self._bs_units)
        
        # get base shear
        reactions = pd.read_excel('reactions.xlsx', sheet_name = None)
        sheet_names = list(reactions.keys())
        base_shears = []

        for sheet_name in sheet_names:
            df = reactions[sheet_name].iloc[:,1:].dropna()
            timeseries = json.dumps(reactions[sheet_name].iloc[:,0].tolist())
            summ = json.dumps((df.sum(axis = 1).values).tolist())
            base_shears.append(summ)

        insert_query = ('INSERT INTO structure_base_shear (TimeSeries, ShearX, ShearY, ShearZ, Units) VALUES (%s,%s,%s,%s,%s)')
        values = (timeseries, base_shears[0], base_shears[1], base_shears[2], units)
        cursor.execute(insert_query, values)		
        print('structure_base_shear table updated correctly!\n')  
    def structure_max_base_shear_byReactionForces(self, **kwargs):
        """
        This function is used to export data into the structure_max_base_shear table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units  = kwargs.get('max_bs_units', self._max_bs_units)
        
        # get max base shear
        reactions = pd.read_excel('reactions.xlsx', sheet_name = None)
        sheet_names = list(reactions.keys())
        max_shears = []

        for sheet_name in sheet_names:
            df = reactions[sheet_name].iloc[:,1:].dropna()
            summ = json.dumps(max(df.sum(axis = 1).values).tolist())
            max_shears.append((summ))
        max_shears = [float(num) for num in max_shears]
        max_shears = [round(num,2) for num in max_shears]
        
        insert_query = ('INSERT INTO structure_max_base_shear ('
                        'MaxX, MaxY, MaxZ, Units) VALUES (%s,%s,%s,%s)')
        values = (
            max_shears[0],
            max_shears[1],
            max_shears[2],
            units)
        cursor.execute(insert_query,values)
        print('structure_max_base_shear table updated correctly!\n') 
    def structure_abs_acceleration(self, **kwargs):
        """
        This function is used to export data into the structure_abs_acceleration table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units  = kwargs.get('abs_acc_units', self._abs_acc_units)
        
        # get absolute accelerations
        accelerations = pd.read_excel('accelerations.xlsx',sheet_name = None)
        sheet_names = list(accelerations.keys())
        matrixes = []

        # file names
        folder = os.path.basename(os.getcwd())
        east = open(os.path.join(f'{folder}e.txt'))
        north = open(os.path.join(f'{folder}n.txt'))
        vertical = open(os.path.join(f'{folder}z.txt'))

        acc_e = []
        acc_n = []
        acc_z = []

        for i in east:
            acc_e.append(float(i.split('\n')[0]))
        for i in north:
            acc_n.append(float(i.split('\n')[0]))
        for i in vertical:
            acc_z.append(float(i.split('\n')[0]))
        acc = [acc_e,acc_n,acc_z]
        counter = 0
        
        # Dataframe manipulation
        for sheet_name in sheet_names:
            df = accelerations[sheet_name].dropna()
            timeseries = df.iloc[:,0].to_list()
            timeseries = [int(round(valor,2)) for valor in timeseries if round(valor,2) % 1 == 0]
            timeseries = json.dumps(timeseries)
            df = df.iloc[:, 1:].copy()
            for column in df.columns:
                df.loc[:,column] += acc[counter][0:2000]
            df = df.applymap(lambda x: ('{:.2e}'.format(x)))
            
            #OPTIMIZING RESULTS
            optimized_matrix = {}
            matrix = df.to_dict()
            for keys, vals in matrix.items():
                optimized_matrix[keys] = {k: v for k, v in vals.items() if (int(k)+1) % 40 == 0} # 40 is the separation between values
            values = []                                                                          # change it if you want to change the separation
            for vals in optimized_matrix.values():
                sublist = list(vals.values())
                values.append(sublist)
            values = [[float(val) for val in sublist] for sublist in values]
            matrixes.append(json.dumps(values))
            counter +=1

        insert_query = ('INSERT INTO structure_abs_acceleration ('
                        'TimeSeries, AbsAccX, AbsAccY, AbsAccZ, Units) '
                        'VALUES(%s,%s,%s,%s,%s)')
        values = (
            timeseries,
            matrixes[0],
            matrixes[1],
            matrixes[2],
            units)
        cursor.execute(insert_query, values)		
        print('structure_abs_acceleration table updated correctly!\n') 
    def structure_relative_displacements(self, **kwargs):
        """
        This function is used to export data into the structure_relative_displacements table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units  = kwargs.get('rel_displ_units', self._rel_displ_units)
        
        # get relative displacements
        displacements = pd.read_excel('displacements.xlsx',sheet_name = None)
        sheet_names = list(displacements.keys())
        matrixes = []

        for sheet_name in sheet_names:
            pd.options.display.float_format = '{:.2E}'.format
            df = displacements[sheet_name].dropna()
            timeseries = df.iloc[:,0].to_list()
            timeseries = [int(round(valor,2)) for valor in timeseries if round(valor,2) % 1 == 0]
            timeseries = json.dumps(timeseries)
            df = df.iloc[:, 1:].copy()

            optimized_matrix = {}
            matrix = df.to_dict()
            for keys, vals in matrix.items():
                optimized_matrix[keys] = {k: v for k, v in vals.items() if (int(k)+1) % 40 == 0}
            values = []
            for vals in optimized_matrix.values():
                sublist = list(vals.values())
                values.append(sublist)
            values = [[float(val) for val in sublist] for sublist in values]
            matrixes.append(json.dumps(values))
        insert_query =	('INSERT INTO structure_relative_displacements ('
                        'TimeSeries, DispX, DispY, DispZ, Units) '
                        'VALUES(%s,%s,%s,%s,%s)')
        values = (timeseries,matrixes[0],matrixes[1],matrixes[2],units)
        cursor.execute(insert_query, values)	
        print('structure_relative_displacements table updated correctly!\n')
    def structure_max_drift_per_floor(self, **kwargs):
        """
        This function is used to export data into the structure_max_drift_per_floor table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        units  = kwargs.get('max_drift_units', self._max_drift_units)
        
        # get max drift per floor
        (coordenates, drift_nodes,
         story_nodes, stories    ,
         subs       , heights    ) = self.model_info.give_coords_info()
        displacements = pd.read_excel('displacements.xlsx', sheet_name = None)
        sheet_names = list(displacements.keys())
        sheet_names.pop(2)
        drifts = []

        for sheet_name in sheet_names:
            df = displacements[sheet_name].iloc[:,1:].dropna()
            sheet_corners = []
            sheet_centers = []
            for idx, level in enumerate(list(story_nodes)):
                if idx == stories:
                    break
                for idy, nodo in enumerate(list(story_nodes[level])):
                    if idy%3 == 0 and idy != 0:
                        #define nodes
                        node1 = list(story_nodes[f'Level {idx}'  ])[0]
                        node5 = list(story_nodes[f'Level {idx+1}'])[0]
                        node2 = list(story_nodes[f'Level {idx}'  ])[1]
                        node6 = list(story_nodes[f'Level {idx+1}'])[1]
                        node3 = list(story_nodes[f'Level {idx}'  ])[2]
                        node7 = list(story_nodes[f'Level {idx+1}'])[2]
                        node4 = list(story_nodes[f'Level {idx}'  ])[3]
                        node8 = list(story_nodes[f'Level {idx+1}'])[3]
                        
                        #corner drift absolute value
                        drift1 = ((df[node5] - df[node1])/heights[idx]).abs().max()
                        drift2 = ((df[node6] - df[node2])/heights[idx]).abs().max()
                        drift3 = ((df[node7] - df[node3])/heights[idx]).abs().max()
                        drift4 = ((df[node8] - df[node4])/heights[idx]).abs().max()
                        max_corner = (max((drift1),(drift2),(drift3),(drift4)))

                        #center drift absolute value
                        mean_displ2 = df[[node5,node6,node7,node8]].mean(axis=1)
                        id_center = (mean_displ2.abs()).argmax()
                        mean_displ1 = sum([df[node1][id_center],
                                           df[node2][id_center],
                                           df[node3][id_center],
                                           df[node4][id_center]])/4
                        max_center = abs(mean_displ2[id_center]- mean_displ1)/heights[idx]

                        #add to data
                        sheet_corners.append(max_corner)
                        sheet_centers.append(max_center)
            #data
            drifts.append(sheet_corners)
            drifts.append(sheet_centers)	

        insert_query = ('INSERT INTO structure_max_drift_per_floor ('
                        'MaxDriftCornerX, MaxDriftCornerY, MaxDriftCenterX, '
                        'MaxDriftCenterY, Units) VALUES (%s,%s,%s,%s,%s)')
        values = (json.dumps(drifts[0]),
                 json.dumps(drifts[2]),
                 json.dumps(drifts[1]),
                 json.dumps(drifts[3]), units)
        cursor.execute(insert_query,values)
        print('structure_max_drift_per_floor table updated correctly!\n')

    
    # ==================================================================================
    # COMPLEMENTARY FUNCTIONS
    # ==================================================================================
    #FIXME: sm_input_pga and sm_input_spectrum are not working cause they needs 
    #FIXME: the ShakerMaker package to be installed in the computer to work.
    #FIXME: ShakeMaker is not implemented in Windows yet. On the other hand, 
    #FIXME: all the input data is already in the database, so this functions are
    #FIXME: not necessary for the moment.    
    @staticmethod
    def pwl(vector_a,w,chi):         
        #variables 
        h = 0.005
        u_t = [0.]
        up_t = [0.]
        upp_t = [0.]
        m = 1
        w_d = w*np.sqrt(1-chi**2) #1/s 
        
        sin = np.sin(w_d*h)
        cos = np.cos(w_d*h)
        e = np.exp(-chi*w*h)
        raiz = np.sqrt(1-chi**2)
        división = 2*chi/(w*h)
        
        A = e * (chi*sin/raiz+cos) #check
        B = e * (sin/w_d) #check
        C = (1/w**2) * (división  + e * (((1 - (2*chi**2))/(w_d*h) - chi/raiz)*sin - (1+división)*cos)) #check
        D = (1/w**2) * (1-división + e * ((2*chi**2-1)*sin/(w_d*h)+división*cos)) #check
        
        A1 = -e * ((w*sin)/raiz) #check
        B1 =  e * ( cos - chi*sin/raiz  ) #check
        C1 = (1/w**2) * (- 1/h + e*((w/raiz + chi/(h*raiz) ) * sin + cos/h)) #check 
        D1 = (1/w**2) * (1/h - (e/h*( chi*sin/raiz + cos   ))) #check
        
        vector_a.insert(0,0)
        
        for i in range(len(vector_a)-1):
            pi = -(vector_a[i])*m#pi
            pi1 = -(vector_a[i+1])*m #pi+1
            
            ui = u_t[i] #u_i(t)
            vi = up_t[i] #v_i(t)
            ui1 = A*ui + B*vi + C*pi + D*pi1 #u_i+1
            upi1 = A1*ui + B1*vi + C1*pi + D1*pi1 #up_i+1 
            
            u_t.append(ui1)
            up_t.append(upi1)
            
        vector_a.pop(0)
        u_t.pop(0)
        up_t.pop(0)

        return u_t,up_t
    def model_linearity(self):
        """
        This function is used to create the model_linearity table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        cnx    = self.db_manager.cnx
        
        # create table
        insert_query = 'INSERT INTO model_linearity(Type) VALUES (%s)' 
        values = ('Linear',)
        cursor.execute(insert_query,values)
        insert_query = 'INSERT INTO model_linearity(Type) VALUES (%s)'
        values = ('Non Linear',)
        cursor.execute(insert_query,values)
        cnx.commit()
        print('model_linearity created correctly!\n')   
    def simulation_type(self):
        """
        This function is used to create the simulation_type table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        cnx    = self.db_manager.cnx
        
        # create table
        insert_query = 'INSERT INTO simulation_type(Type) VALUES (%s)' 
        values = ('Fix Base Model',)
        cursor.execute(insert_query,values)
        insert_query = 'INSERT INTO simulation_type(Type) VALUES (%s)'
        values = ('Soil Structure Interaction Model',)
        cursor.execute(insert_query,values)
        cnx.commit()
        print('simulation_type created correctly!\n')
    def sm_input_pga(self, **kwargs):
        """
        This function is used to export data into the sm_input_pga table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        cnx    = self.db_manager.cnx
        units  = kwargs.get('pga_units', self._pga_units)
        
        folder = os.path.basename(os.getcwd())
        npz = os.path.join('..',f'{folder}.npz')
        nu = 0.05
        tmax = 50.

        s = Station()
        s.load(npz)
        z,e,n,t = s.get_response()
        z = z[t<tmax]
        e = e[t<tmax]
        n = n[t<tmax]
        t = t[t<tmax]

        az = np.gradient(z,t)
        ae = np.gradient(e,t)
        an = np.gradient(n,t)

        PGA_max_z = az.argmax()
        PGA_max_e = ae.argmax()
        PGA_max_n = an.argmax()
        PGA_min_n = an.argmin()
        PGA_min_z = az.argmin()   
        PGA_min_e = ae.argmin()
            
        PGAx = json.dumps({'max':round(ae[PGA_max_e],2),'min':round(ae[PGA_min_e],2)})
        PGAy = json.dumps({'max':round(an[PGA_max_n],2),'min':round(an[PGA_min_n],2)})
        PGAz = json.dumps({'max':round(az[PGA_max_z],2),'min':round(az[PGA_min_z],2)})
        
        insert_query = ('INSERT INTO sm_input_pga ('
                        'PGA_X, PGA_Y, PGA_Z, Units) VALUES(%s,%s,%s,%s)')
        values = (PGAx, PGAy, PGAz, units)
        cursor.execute(insert_query, values)
        cnx.commit()
        print('sm_input_pga table updated correctly!\n')
    def sm_input_spectrum(self, **kwargs):
        """
        This function is used to export data into the sm_input_spectrum table database.
        """
        # initialize parameters
        cursor = self.db_manager.cursor
        cnx    = self.db_manager.cnx
        units  = kwargs.get('resp_spectrum', self._resp_spectrum)
        
        # get spectrum
        folder = os.path.basename(os.getcwd())
        npz = os.path.join('..',f'{folder}.npz')
        nu = 0.05
        tmax = 50.
        dt = np.linspace(0,1.,2000)
        dt = np.delete(dt,0)
        w = np.zeros(len(dt))

        for i in range(len(dt)):
            if dt[i] != 0.:    
                w[i] = 2*np.pi/dt[i]
            
        #SPECTRUM VERTICAL
        s = Station()
        s.load(npz)
        z,e,n,t = s.get_response()
        z = z[t<tmax] 
        t = t[t<tmax]
        az = np.gradient(z,t).tolist()
        Spaz = []

        for j in range(len(w)):
            wi = w[j]
            u_z,v_z = self.pwl(az,wi,nu)
            Saz = max(max(u_z),(abs(min(u_z))))*wi**2
            Spaz.append(Saz)

        #SPECTRUM EAST
        s = Station()
        s.load(npz)
        z,e,n,t = s.get_response()
        e = e[t<tmax]
        t = t[t<tmax]
        ae = np.gradient(e,t).tolist()
        Spe = []

        for j in range(len(w)):
            wi = w[j]
            u_x,v_x = self.pwl(ae,wi,nu)
            Sae = max(max(u_x),(abs(min(u_x))))*wi**2
            Spe.append(Sae)

        #SPECTRUM NORTH
        s = Station()
        s.load(npz)
        z,e,n,t = s.get_response()
        n = n[t<tmax]
        t = t[t<tmax]
        an = np.gradient(n,t).tolist()
        Spn = []

        for j in range(len(w)):
            wi = w[j]
            u_y,v_y = self.pwl(an,wi,nu)
            San = max(max(u_y),(abs(min(u_y))))*wi**2
            Spn.append(San)

        insert_query = ('INSERT INTO sm_input_spectrum('
                        'SpectrumX, SpectrumY, SpectrumZ, Units) '
                        'VALUES (%s,%s,%s,%s)')
        values = (json.dumps(Spe), json.dumps(Spn), json.dumps(Spaz), units)
        cursor.execute(insert_query, values)
        cnx.commit()
        print('sm_input_spectrum table updated correctly!\n')    
    def get_sm_id(self):
        path = os.path.dirname(os.path.abspath(__file__)).split('\\')
        path = list(Path(__file__).resolve().parent)
        magnitude = path[-3][-3:]
        rupture = path[-2][-4:]
        station = int(path[-1][-1])+1

        if magnitude   == '6.5':m = 0
        elif magnitude == '6.7':m = 90
        elif magnitude == '6.9':m = 180
        elif magnitude == '7.0':m = 270

        if rupture[0:2]   == 'bl':r = (int(rupture[-1])-1)*10
        elif rupture[0:2] == 'ns':r = (int(rupture[-1])-1)*10 + 30
        elif rupture[0:2] == 'sn':r = (int(rupture[-1])-1)*10 + 60
            
        id = m+r+station
        return id  
    
    
    # ==================================================================================
    # STATIC METHODS
    # ==================================================================================
    @staticmethod
    def create_reaction_xlsx():
        import xlsxwriter
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
        counter = 0
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
        while time_step < 50.00:
            x_sheet.write(row,column,f'{time_step:.3f}',main_format)
            y_sheet.write(row,column,f'{time_step:.3f}',main_format)
            z_sheet.write(row,column,f'{time_step:.3f}',main_format)

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
        import xlsxwriter
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
        counter = 0
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
        import xlsxwriter
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
        counter = 0
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

class Plotting:
    """
    This class is used to perform the seismic analysis of the structure.
    It's used to analyse quiclky the structure and get the results of the analysis.
    You use it in the main after the results are uploaded to the database.
    """
    @staticmethod
    def pwl(vector_a,w,chi):         
        #variables 
        h = 0.005
        u_t = [0.]
        up_t = [0.]
        upp_t = [0.]
        m = 1
        w_d = w*np.sqrt(1-chi**2) #1/s 
        
        sin = np.sin(w_d*h)
        cos = np.cos(w_d*h)
        e = np.exp(-chi*w*h)
        raiz = np.sqrt(1-chi**2)
        división = 2*chi/(w*h)
        
        A = e * (chi*sin/raiz+cos) #check
        B = e * (sin/w_d) #check
        C = (1/w**2) * (división  + e * (((1 - (2*chi**2))/(w_d*h) - chi/raiz)*sin - (1+división)*cos)) #check
        D = (1/w**2) * (1-división + e * ((2*chi**2-1)*sin/(w_d*h)+división*cos)) #check
        
        A1 = -e * ((w*sin)/raiz) #check
        B1 =  e * ( cos - chi*sin/raiz  ) #check
        C1 = (1/w**2) * (- 1/h + e*((w/raiz + chi/(h*raiz) ) * sin + cos/h)) #check 
        D1 = (1/w**2) * (1/h - (e/h*( chi*sin/raiz + cos   ))) #check
        
        vector_a.insert(0,0)
        
        for i in range(len(vector_a)-1):
            pi = -(vector_a[i])*m#pi
            pi1 = -(vector_a[i+1])*m #pi+1
            
            ui = u_t[i] #u_i(t)
            vi = up_t[i] #v_i(t)
            ui1 = A*ui + B*vi + C*pi + D*pi1 #u_i+1
            upi1 = A1*ui + B1*vi + C1*pi + D1*pi1 #up_i+1 
            
            u_t.append(ui1)
            up_t.append(upi1)
            
        vector_a.pop(0)
        u_t.pop(0)
        up_t.pop(0)

        return u_t,up_t
        
    @staticmethod
    def NCh433Spectrum(S,Ao,R,I,To,p):
        T = np.linspace(0,3,2000)
        Sah = np.zeros(2000)
        Sav = np.zeros(2000)

        for i in range(2000):
            tn = T[i]
            alpha = (1 + 4.5*(tn/To)**p)/(1 +(tn/To)**3)
            Sah[i] = S*Ao*alpha/(R/I)
            Sav[i] = 2/3 * S*Ao*alpha/(R/I)
        Sah = np.delete(Sah,0)
        Sav = np.delete(Sav,0)
        return T,Sah,Sav

    @staticmethod
    def plotDrift(driftx, drifty, stories,title):
        plt.plot(driftx,stories)
        plt.plot(drifty,stories)
        plt.yticks(range(1, 21))  # Rango del eje y de 1 a 20
        plt.ylabel('Story')
        plt.xlabel('Drift')
        plt.title(title)
        plt.legend(['Drift X', 'DriftY'])
        # Establecer el formato de porcentaje en el eje y
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

        plt.axvline(x=0.002, color='r', linestyle='--')
        plt.grid()
        plt.show()
    def plotFileSpectrum(self, fileX,fileY,fileZ):
        S = 0.9
        To = 0.15 #[s]
        p = 2
        Ao = 0.3*9.81  
        I = 1.2
        R = 1
        T,Sah_433,Sav_433 = self.NCh433Spectrum(S,Ao,R,I,To,p)


        plt.figure(figsize=(23.54,13.23),dpi=108)
        nu = 0.05
        dt = T
        dt = np.delete(dt,0)
        w = np.zeros(len(dt))

        for i in range(len(dt)):
            if dt[i] != 0.:    
                w[i] = 2*np.pi/dt[i]

        with open(fileZ) as filez:
            dataz = filez.read()
        dataz = dataz.split('\n')
        dataz.pop(-1)
        dataz.pop(-1)
        az = [float(acce) for acce in dataz]
        Spaz = []
        for j in range(len(w)):
            wi = w[j]
            u_z,v_z = self.pwl(az,wi,nu)
            Saz = max(max(u_z),(abs(min(u_z))))*wi**2
            Spaz.append(Saz)

        plt.plot(dt, Sav_433,'k--',label='NCh433')
        plt.plot(dt,Spaz,'-',label='Record 6.5BL1S4 Vertical', color = 'blue')
        
        y433 = np.interp(2.4, dt, Sav_433)
        year = np.interp(2.4, dt, Spaz)
        plt.scatter(2.4, y433, color='black', label=f'Value for T=2.4: Spa={round(y433,2)}')
        plt.scatter(2.4, year, color='blue', label=f'Value for T=2.4: Spa={round(year,2)}')
        plt.plot([2.4,2.4],[0,y433], '--r')
        plt.text(2.4, y433+.1,f"({2.4},{y433:.2f})")
        plt.text(2.4, year+.1,f"({2.4},{year:.2f})")
        plt.title('Spa Vertical')
        plt.xlabel('Period T [s]')
        plt.ylabel('Acceleration [m/s/s]')
        plt.legend()
        plt.grid()
        plt.show()

        plt.figure(figsize=(23.54,13.23),dpi=108)
        with open(fileX) as filex:
            datax = filex.read()
        datax = datax.split('\n')
        datax.pop(-1)
        datax.pop(-1)
        ae = [float(acce) for acce in datax]
        Spe = []
        for j in range(len(w)):
            wi = w[j]
            u_x,v_x = self.pwl(ae,wi,nu)
            Sae = max(max(u_x),(abs(min(u_x))))*wi**2
            Spe.append(Sae)
        with open(fileY) as filey:
            datay = filey.read()
        datay = datay.split('\n')
        datay.pop(-1)
        datay.pop(-1)
        an = [float(acce) for acce in datay]
        Spn = []
        for j in range(len(w)):
            wi = w[j]
            u_y,v_y = self.pwl(an,wi,nu)
            San = max(max(u_y),(abs(min(u_y))))*wi**2
            Spn.append(San)
    
        y433 = np.interp(2.4, dt, Sah_433)
        year1 = np.interp(2.4,dt,Spe)
        year2 = np.interp(2.4,dt,Spn)
        plt.scatter(2.4, y433, color='black', label=f'Value for x = 2.4: Spa={round(y433,2)}')
        plt.scatter(2.4, year1, color='blue', label=f'Value for x = 2.4: Spa={round(year1,2)}')
        plt.scatter(2.4, year2, color='orange', label=f'Value for x = 2.4: Spa={round(year2,2)}')
        plt.plot([2.4,2.4],[0,y433],'--r')

        plt.plot(dt, Sah_433,'k--',label = 'NCh433')
        plt.plot(dt,Spe,'-',label='Registro 6.5BL1S4 Este' ,color='blue')
        plt.plot(dt,Spn,'-',label='Registro 6.5BL1S4 Norte',color='orange')
        plt.title('Spa Horizontal')
        plt.xlabel('Period T [s]')
        plt.ylabel('Acceleration [m/s/s]')
        plt.legend()
        plt.grid()
        plt.show()    

    @staticmethod
    def plotFileAccelerations(fileX,fileY,fileZ):
        time = np.arange(0,50,0.025) #len = 2000 

        with open(fileX) as filex:
            datax = filex.read()
        datax = datax.split('\n')
        datax.pop(-1)
        datax.pop(-1)
        datax = [float(acce) for acce in datax]
        
        with open(fileY) as filey:
            datay = filey.read()
        datay = datay.split('\n')
        datay.pop(-1)
        datay.pop(-1)
        datay = [float(acce) for acce in datay]
    
        with open(fileZ) as filez:
            dataz = filez.read()
        dataz = dataz.split('\n')
        dataz.pop(-1)
        dataz.pop(-1)
        dataz = [float(acce) for acce in dataz]

        plt.plot(time,datax)
        plt.plot(time,datay)
        plt.plot(time,dataz,'--')
    
    
        plt.legend(['East','North','Vertical'])
        plt.title('Earthquake')
        plt.ylabel('Acceleration[m/s/s]')
        plt.xlabel('Time[s]')
        plt.grid()
        plt.tight_layout()
        plt.show()
    def plotInputSpectrum(self, input1, input2, input3, label1='', label2='', label3='',
                          nch433=False,title='',option='', fourier=False) :
        S = 0.9
        To = 0.15 #[s]
        p = 2
        Ao = 0.3*9.81  
        I = 1.2
        R = 1
        T,Sah_433,Sav_433 = self.NCh433Spectrum(S,Ao,R,I,To,p)
        nu = 0.05
        dt = T
        dt = np.delete(dt,0)
        w = np.zeros(len(dt))
        for i in range(len(dt)):
            if dt[i] != 0.:    
                w[i] = 2*np.pi/dt[i]

        if fourier==True:
            w = np.delete(w,np.s_[0:139])
            fft_result1 = np.fft.fft(input1)
            fft_result2 = np.fft.fft(input2)
            fft_result3 = np.fft.fft(input3)
            amplitude_spectrum1 = np.abs(fft_result1)
            amplitude_spectrum2 = np.abs(fft_result2)
            amplitude_spectrum3 = np.abs(fft_result3)
            amplitude_spectrum1 = np.delete(amplitude_spectrum1,np.s_[0:140])
            amplitude_spectrum2 = np.delete(amplitude_spectrum2,np.s_[0:140])
            #plt.loglog(w,amplitude_spectrum1,label=label1)
            #plt.loglog(w,amplitude_spectrum2,label=label2)
            plt.loglog(w,amplitude_spectrum3,label=label3)
            plt.yscale('log')
            plt.xlabel('Frequency w [Hz]')
            plt.ylabel('Log Acceleration [m/s/s]')
        else:
            plt.figure(figsize=(23.54,13.23),dpi=108)

            i1 = []
            for j in range(len(w)):
                wi = w[j]
                u_x,v_x = self.pwl(input1,wi,nu)
                Sae = max(max(u_x),(abs(min(u_x))))*wi**2
                i1.append(Sae)
            i2 = []
            for j in range(len(w)):
                wi = w[j]
                u_y,v_y = self.pwl(input2,wi,nu)
                San = max(max(u_y),(abs(min(u_y))))*wi**2
                i2.append(San)
            i3 = []
            for j in range(len(w)):
                wi = w[j]
                u_y,v_y = self.pwl(input3,wi,nu)
                San = max(max(u_y),(abs(min(u_y))))*wi**2
                i3.append(San)

            if nch433 == True:
                plt.plot(dt, Sah_433,'k--',label = 'NCh433')
            if option == 'loglog':
                plt.loglog(dt,i1,'-',label=label1 ,color='blue')
                plt.loglog(dt,i2,'-',label=label2,color='orange')
                plt.loglog(dt,i3,'-',label=label3,color='red')
            elif option == '':
                plt.plot(dt,i1,'-',label=label1 ,color='blue')
                plt.plot(dt,i2,'-',label=label2,color='orange')
                plt.plot(dt,i3,'-',label=label3,color='red')
            plt.xlabel('Period T [s]')
            plt.ylabel('Acceleration [m/s/s]')
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
    def __init__(self, fidelity = False):
        # Set the path to the 'PartitionsInfo' subfolder
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(current_path, 'PartitionsInfo')
        
        # Check if the 'PartitionsInfo' subfolder exists
        if not os.path.exists(self.path):
            raise Exception('The PartitionsInfo folder does not exist!\n'
                            'Current path = {}'.format(current_path))
        # Access to folders within the 'PartitionsInfo' subfolder
        folders = os.listdir(self.path)
        for folder_name in folders:
            setattr(self, f'folder_{folder_name}', os.path.join(self.path, folder_name))
        
        # Call the methods to initialize the data
        (self.coordenates  , self.drift_nodes,
         self.stories_nodes, self.stories    ,
         self.subs         , self.heights    ) = self.give_coords_info()
        
        self.accelerations, self.acce_nodes = self.give_accelerations()
        self.displacements, self.displ_nodes = self.give_displacements()
        if fidelity == False:
            self.reactions, self.reaction_nodes = self.give_reactions()
        self.nnodes, self.nelements, self.npartitions = self.give_model_info()     
    def give_accelerations(self):
        #check nodes
        files_accel = os.listdir(self.folder_accel)
        files = [open(f'{self.folder_accel}/{file}','r') for file in files_accel]

        #create dictionary
        accelerations = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split('\n')] for line in files[file]]
            file_id = str(files[file]).split('/')[-1].split('-')[1].split(' ')[0].split('.')[0]
            accelerations[f'Partition {file_id}'] = {}
            for nodei in range(len(nodes)):
                accelerations[f'Partition {file_id}'][f'Node {nodei}'] = nodes[nodei][0]

        #create list with nodes sorted
        acce_nodes = []
        for values in accelerations.values():
            for node in values.values():
                acce_nodes.append(int(node))
        acce_nodes.sort()

        listed = set(acce_nodes)
        if len(acce_nodes) == len(listed):
            print('Accelerations: No nodes repited')
        else:
            raise Exception('WARNING: NODES REPITED')

        return accelerations,acce_nodes 
    def give_displacements(self):
        #check nodes
        files_disp = os.listdir(self.folder_disp)
        files = [open(f'{self.folder_disp}/{file}','r') for file in files_disp]

        #create dictionary
        displacements = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split('\n')] for line in files[file]]
            file_id = str(files[file]).split('/')[-1].split('-')[1].split(' ')[0].split('.')[0]
            displacements[f'Partition {file_id}'] = {}
            for nodei in range(len(nodes)):
                displacements[f'Partition {file_id}'][f'Node {nodei}'] = nodes[nodei][0]

        #create list with nodes sorted
        displ_nodes = []

        for values in displacements.values():
            for node in values.values():
                displ_nodes.append(int(node))
        displ_nodes.sort()

        listed = set(displ_nodes)
        if len(displ_nodes) == len(listed):
            print('Displacements: No nodes repited')
        else:
            raise Exception('WARNING: NODES REPITED')

        return displacements,displ_nodes
    def give_reactions(self):
        #check nodes
        files_reaction = os.listdir(self.folder_reaction)
        files = [open(f'{self.folder_reaction}/{file}','r')for file in files_reaction]

        #create dictionary
        reactions = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split('\n')] for line in files[file]]
            file_id = str(files[file]).split('/')[-1].split('-')[1].split(' ')[0].split('.')[0]
            reactions[f'Partition {file_id}'] = {}
            for nodei in range(len(nodes)):
                reactions[f'Partition {file_id}'][f'Node {nodei}'] = nodes[nodei][0]

        #create list with nodes sorted
        reaction_nodes = []
        for values in reactions.values():
            for node in values.values():
                reaction_nodes.append(int(node))
        reaction_nodes.sort()

        listed = set(reaction_nodes)
        if len(reaction_nodes) == len(listed):
            print('Reactions:     No nodes repited ')
        else:
            raise Exception('WARNING: NODES REPITED')
        return reactions,reaction_nodes  
    def give_coords_info(self):
        #check nodes
        files_coords = os.listdir(self.folder_coords)
        files = [open(f'{self.folder_coords}/{file}','r') for file in files_coords]

        #create dictionary
        coordenates = {}
        for file in range(len(files)):
            nodes = [[(num) for num in line.split('\n')] for line in files[file]]
            file_id = str(files[file]).split('_')[2].split('.')[0]
            
            for nodei in range(1,len(nodes)):
                node_id = nodes[nodei][0].split(' ')[0]
                coord_x = round(float(nodes[nodei][0].split(' ')[1]),1)
                coord_y = round(float(nodes[nodei][0].split(' ')[2]),1)
                coord_z = round(float(nodes[nodei][0].split(' ')[3]),1)
                coordenates[f'Node {node_id}'] = {}
                coordenates[f'Node {node_id}'] = {}
                coordenates[f'Node {node_id}'] = {}
                coordenates[f'Node {node_id}']['coord x'] = float(f'{coord_x:.1f}')
                coordenates[f'Node {node_id}']['coord y'] = float(f'{coord_y:.1f}')
                coordenates[f'Node {node_id}']['coord z'] = float(f'{coord_z:.1f}')

        #sort every node per level 
        sorted_nodes = sorted(coordenates.items(), key = lambda x: (x[1]['coord x'],x[1]['coord y'], x[1]['coord z']))
        #create dictionary with specific nodes per corner to calculate directly the drift
        drift_nodes = {'corner1':[],'corner2':[],'corner3':[],'corner4':[]}
        
        #calculate subs, stories, and fill drift nodes with heights
        height = 0
        id_corner = 1
        subs = []
        stories = 0
        for tuple_i in sorted_nodes:
            z = (tuple_i[1]['coord z'])
            #print(z)
            node = tuple_i[0]
            if z < 0 and z != height:
                subs.append(z)
                continue
            elif z == height and z <0:
                continue
            elif z == height and z >=0:
                continue
            elif z > height:
                height = z
                drift_nodes[f'corner{id_corner}'].append(f'{node}|{z}')
                stories += 1
                continue
            height = 0.0
            id_corner +=1

        subs = (sorted(set(subs)))
        subs = len(subs)
        stories = int(stories/4)
        #list of heigths
        heights = []
        for data in range(len(drift_nodes['corner1'])-1):
            current_height = (float(drift_nodes['corner1'][data+1].split('|')[1])-float(drift_nodes['corner1'][data].split('|')[1]))
            heights.append(current_height)

        #create dict with nodes per historie 
        sort_by_historie = sorted(coordenates.items(), key = lambda x: (x[1]['coord z'],x[1]['coord x'], x[1]['coord y']))
        stories_nodes = {}
        counter = 0
        for i in range(stories+subs+1):
            i -= subs
            if i < 0:
                counter+=4
                continue
            stories_nodes[f'Level {i}'] = {}
            node1 = sort_by_historie[counter][0]
            node2 = sort_by_historie[counter+1][0]
            node3 = sort_by_historie[counter+2][0]
            node4 = sort_by_historie[counter+3][0]
            #print(node1,node2,node3,node4)
            stories_nodes[f'Level {i}'][node1] = sort_by_historie[counter][1]
            stories_nodes[f'Level {i}'][node2] = sort_by_historie[counter+1][1]
            stories_nodes[f'Level {i}'][node3] = sort_by_historie[counter+2][1]
            stories_nodes[f'Level {i}'][node4] = sort_by_historie[counter+3][1]
            counter+=4
        heights.insert(0,(coordenates[list(stories_nodes["Level 1"])[0]]["coord z"] - coordenates[list(stories_nodes["Level 0"])[0]]["coord z"]))
        return coordenates, drift_nodes,stories_nodes, stories, subs, heights  
    def give_model_info(self):
        #read file
        files_info = os.listdir(self.folder_info)
        file = open(f'{self.folder_info}/model_info.csv','r') 

        #get number of nodes and number of elements
        info = [[row for row in line.split(' ')] for line in file]
        nnodes = (int(info[0][4]))
        nelements = (int(info[1][4]))
        npartitions = (int(info[2][4]))
        file.close()
        return nnodes, nelements, npartitions
