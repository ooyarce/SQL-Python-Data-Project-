#%% ------------------------------------------------------------------------------------
# IMPORT LIBRARIES																		
#---------------------------------------------------------------------------------------
from sql_functions import ModelSimulation
import os
#%% ------------------------------------------------------------------------------------
# INIT AND CONNECT TO DATABASE															
#---------------------------------------------------------------------------------------
# Folder path
print("---------------------------------------------|")
folder_path = os.path.dirname(os.path.abspath(__file__))

# Init the SeismicSimulation class
user     = 'root'
password = 'g3drGvwkcmcq'
host     = '34.176.187.208'
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
'sim_comments'      : 'Simulation for 55floors and 7basements model ',
'sm_input_comments' : 'ShakerMaker Input for 55floors-7basements sim',
'model_comments'    : 'Model of 55floors and 7basements with FixBase',
'bench_comments'    : 'Model w/ 2.5meter spacemenet structured mesh ',
'perf_comments'     : 'Model with shear,displacement & acce metrics ',
'specs_comments'    : 'Model with linear-elastic-beam-column-shells ',
'clustername'       : 'Here it goes the cluster name                ',
'model_name'        : 'Here it goes the model name                  ',     
'stage'             : 'Here it goes the simulation stage            ',
'options'           : 'Here it goes the simulation options          ', 
'linearity'         : 1                                              ,
'type'              : 1                                                }

DataBase = ModelSimulation(user, password, host, database, **parameters)
#%% ------------------------------------------------------------------------------------
# CREATE XLSX FILES
#---------------------------------------------------------------------------------------
accelerations_file = os.path.join(folder_path, 'accelerations.xlsx')
displacements_file = os.path.join(folder_path, 'displacements.xlsx')
reactions_file     = os.path.join(folder_path, 'reactions.xlsx')

if not os.path.exists(accelerations_file):
    DataBase.create_accelerations_xlsx()
    print("Accelerations xlsx file created.")

if not os.path.exists(displacements_file):
    DataBase.create_displacement_xlsx()
    print("Displacementes xlsx file crated.")

if not os.path.exists(reactions_file):
    DataBase.create_reaction_xlsx()
    print("Reactions xlsx file crated.")

if (os.path.exists(accelerations_file)
    and os.path.exists(displacements_file)
    and os.path.exists(reactions_file)):
    print("Files xlsx already created. Proceeding to fill the database.")
#%% ------------------------------------------------------------------------------------
# FILL DATABASE
#---------------------------------------------------------------------------------------
DataBase.simulation()
#---------------------------------------------------------------------------------------