#-----------------------------------------------------------------------------------------------------------------------------------
#THIS FILLS THE SQL DATABASE																										|	
#-----------------------------------------------------------------------------------------------------------------------------------
from sql_functions import *
import os

print("---------------------------------------------|")
#folder path
folder_path = os.path.dirname(os.path.abspath(__file__))


#Create 
accelerations_file = os.path.join(folder_path, 'accelerations.xlsx')
displacements_file = os.path.join(folder_path, 'displacements.xlsx')
reactions_file = os.path.join(folder_path, 'reactions.xlsx')

if not os.path.exists(accelerations_file):
    create_accelerations_xlsx()
    print("Accelerations xlsx file created.")

if not os.path.exists(displacements_file):
    create_displacement_xlsx()
    print("Displacementes xlsx file crated.")

if not os.path.exists(reactions_file):
    create_reaction_xlsx()
    print("Reactions xlsx file crated.")

#
if (os.path.exists(accelerations_file) and os.path.exists(displacements_file) and os.path.exists(reactions_file)):
    print("Files xlsx already created. Proceeding to fill the database.")

#Press insert key and fill the parameters you want to change the default values, then press insert again to keep format sorted.
parameters = {
	'bs_units'          : 'kN'                                           ,                                                            
	'max_bs_units'      : 'kN'                                           ,                                                                
	'rel_displ_units'   : 'm'                                            ,             
	'max_drift_units'   : 'm'                                            ,             
	'abs_acc_units'     : 'm/s/s'                                        ,  
	'pga_units'         : 'm/s/s'                                        , 
	'resp_spectrum'     : 'm/s/s'                                        ,
	'sim_comments'      : 'Simulation for 20floors and 4basements model ',
	'sm_input_comments' : 'ShakerMaker Input for 20floors-4basements sim',
	'model_comments'    : 'Model of 20floors and 4basements with FixBase',
	'bench_comments'    : 'Model w/ 2.5meter spacemenet structured mesh ',
	'perf_comments'     : 'Model with shear,displacement & acce metrics ',
	'specs_comments'    : 'Model with linear-elastic-beam-column-shells ',
	'clustername'       : 'Here it goes the cluster name                ',
	'model_name'        : 'Here it goes the model name                  ',     
	'stage'             : 'Here it goes the simulation stage            ',
	'options'           : 'Here it goes the simulation options          ', 
	'linearity'         : 1                                              ,
	'type'              : 1                                                    }

#-------------------------------------------------------------------------------------------------------------------------------------|
#-----------------------------------------------DON'T CHANGE THIS---------------------------------------------------------------------|
#-------------------------------------------------------------------------------------------------------------------------------------|
#units                                                                                                                               #|                                                                                                                                          
bs_units          = parameters['bs_units']                                                                                           #|                                                                                                                                                                                                                                          
max_bs_units      = parameters['max_bs_units']                                                                                       #|                                                                                                                                          
rel_displ_units   = parameters['rel_displ_units']                                                                                    #|                                                     
max_drift_units   = parameters['max_drift_units']                                                                                    #|                                                     
abs_acc_units     = parameters['abs_acc_units']                                                                                      #|                                                     
pga_units         = parameters['pga_units']                                                                                          #|
spectrum_units    = parameters['resp_spectrum']                                                                                      #|
																																	 #|        
																																	 #|         
#comments                                                                                                                            #|                 
sim_comments      = parameters['sim_comments']                                                                                       #|                                                     
sm_input_comments = parameters['sm_input_comments']                                                                                  #|  
model_comments    = parameters['model_comments']                                                                                     #|                                                     
bench_comments    = parameters['bench_comments']                                                                                     #|                                                     
perf_comments     = parameters['perf_comments']                                                                                      #|                                                     
specs_comments    = parameters['specs_comments']                                                                                     #|
																																	 #|                                                     
#names                                                                                                                               #|             
clustername       = parameters['clustername']                                                                                        #|                                                 
model_name        = parameters['model_name']                                                                                         #|                                                 
																																	 #|         
#model type and linearity                                                                                                            #|                                 
stage             = parameters['stage']                                                                                              #|
options           = parameters['options']                                                                                            #|                                                 
linearity         = parameters['linearity']                                                                                          #|
sim_type          = parameters['type']                                                                                               #|                                             
#-------------------------------------------------------------------------------------------------------------------------------------|
#write your database script in here

simulation(sim_comments=sim_comments, 
		sm_input_comments=sm_input_comments,  
		model_comments=model_comments, 
		bench_comments=bench_comments, 
		perf_comments=perf_comments, 
		specs_comments=specs_comments)

#-------------------------------------------------------------------------------------------------------------------------------------|
#close sql
cursor.close()
cnx.close()
#-------------------------------------------------------------------------------------------------------------------------------------|
