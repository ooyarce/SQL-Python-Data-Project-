# IMPORT LIBRARIES
#---------------------------------------------------------------------------------------
from sql_functions import ModelSimulation

#%% INIT AND CONNECT TO DATABASE
#---------------------------------------------------------------------------------------
# Init the SeismicSimulation class
user     = 'omarson'
password = 'Mackbar2112!'
host     = 'localhost'
database = 'stkodatabase'

# Press insert key and fill the parameters you want to change the default values.
parameters = {# Remember that the Db has a max lenght from:
             #Here   :                                      to here ->,
'bs_units'          : 'kN'                                           ,
'max_bs_units'      : 'kN'                                           ,
'rel_displ_units'   : 'm'                                            ,
'max_drift_units'   : 'm'                                            ,
'abs_acc_units'     : 'm/s/s'                                        ,
'pga_units'         : 'm/s/s'                                        ,
'resp_spectrum'     : 'm/s/s'                                        ,
'sim_comments'      : 'Abosrbing Boundaries Test 1'                  ,
'sm_input_comments' : 'ShakerMaker Input for Abosrbing Boundaries'   ,
'model_comments'    : 'Model of Abosrbing Boundaries Test 1'         ,
'bench_comments'    : 'Model w/ 2.5meter spacemenet structured mesh ',
'perf_comments'     : 'Model with shear,displacement & acce metrics ',
'specs_comments'    : 'Model with linear-elastic-beam-column-shells ',
'clustername'       : 'Esmeralda cluster HPC Uandes by jaabel       ',
'model_name'        : 'AbsBound Test01                  '            ,
'stage'             : 'Here it goes the simulation stage            ',
'options'           : 'Here it goes the simulation options          ',
'linearity'         : 1                                              ,
'sim_type'          : 1                                              ,
'fidelity'          : 1                                              ,
'windows_os'        : True                                          ,
'step'              : 0.025                                          ,
'total_time'        : 50}

DataBase = ModelSimulation(**parameters)


#%% FILL DATABASE
#---------------------------------------------------------------------------------------
DataBase.simulation()
#---------------------------------------------------------------------------------------