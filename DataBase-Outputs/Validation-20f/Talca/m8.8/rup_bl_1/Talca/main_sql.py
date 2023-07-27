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
	'sim_comments'      : 'Validation for 20floors and 4basements model ',
	'sm_input_comments' : 'No SM Input for this model, real record input',
	'model_comments'    : 'Model of 20floors and 4basements with FixBase',
	'bench_comments'    : 'Model w/ 2.0meter spacemenet structured mesh ',
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

# simulation(sim_comments=sim_comments, 
# 		sm_input_comments=sm_input_comments,  
# 		model_comments=model_comments, 
# 		bench_comments=bench_comments, 
# 		perf_comments=perf_comments, 
# 		specs_comments=specs_comments)


#-------------------------------------------------------------------------------------------------------------------------------------|
#close sql
cursor.close()
cnx.close()
#-------------------------------------------------------------------------------------------------------------------------------------|

# X = 'NEWagReg2_X.txt'
# Y = 'NEWagReg2_Y.txt'
# Z = 'NEWagReg2_Z.txt'
# 




stories = np.arange(1,21)
print(stories)
#plotFileAccelerations(X,Y,Z,separated=True)
driftx = [0.00017487892857142857, 0.00015873685714285713, 0.00014429071428571433, 0.00015128785714285713, 0.00017124857142857133, 0.00016607500000000004, 0.0001521521428571429, 0.0001331021428571428, 0.00011237928571428557, 0.00008926285714285736, 0.00006425071428571422, 0.00016559928571428572, 0.0001715300000000001, 0.00017094642857142854, 0.00017272571428571446, 0.0001842914285714287, 0.00018252, 0.00018401428571428576, 0.00031503714285714343, 0.0003041857142857144]
drifty = [0.00023033614285714285, 0.0002546457142857143, 0.0002625649999999999, 0.0002824092857142858, 0.000303847142857143, 0.00031901571428571426, 0.00032935428571428553, 0.00033533857142857164, 0.0003394878571428571, 0.00034390642857142834, 0.0003858000000000001, 0.00044854285714285785, 0.0004972857142857145, 0.0004962142857142854, 0.0005192142857142855, 0.0005106428571428583, 0.0005004785714285717, 0.0005325785714285709, 0.0005739285714285705, 0.0006004500000000004]
title = 'Edificio 20 pisos | Terremoto 1985, estación Ranco, Magnitud 7.9Mw'
plotDrift(driftx,drifty,stories,title)



 


