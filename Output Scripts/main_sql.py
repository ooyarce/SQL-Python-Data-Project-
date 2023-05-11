#-----------------------------------------------------------------------------------------------------------------------------------
#THIS FILLS THE SQL DATABASE																										|	
#-----------------------------------------------------------------------------------------------------------------------------------
from sql_functions import *

#Press insert key and fill the parameters you want to change the default values, then press insert again to keep format sorted.
parameters = {
    'bs_units'          : 'kN'                                                 ,                                                            
    'max_bs_units'      : 'kN'                                                 ,                                                                
    'rel_displ_units'   : 'm'                                                  ,             
    'max_drift_units'   : 'm'                                                  ,             
    'abs_acc_units'     : 'm/s/s'                                              ,  
    'pga_units'         : 'm/s/s'                                              , 
    'resp_spectrum'     : 'm/s/s'                                              ,
    'sim_comments'      : 'Testint units and input putting in function'        ,
    'sm_input_comments' : 'Testint units and input putting in function'        ,
    'model_comments'    : 'Testint units and input putting in function'        ,
    'bench_comments'    : 'Testint units and input putting in function'        ,
    'perf_comments'     : 'Testint units and input putting in function'        ,
    'specs_comments'    : 'Testint units and input putting in function'        ,
    'clustername'       : 'Here it goes the cluster name'                      ,
    'model_name'        : 'Here it goes the model name'                        ,     
    'stage'             : 'Here it goes the simulation stage'                  ,
    'options'           : 'Here it goes the simulation options'                , 
    'linearity'         : 1                                                    ,
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
#names                                                                                                                               #|             
model_name        = parameters['model_name']                                                                                         #|                                                 
clustername       = parameters['clustername']                                                                                        #|                                                 
                                                                                                                                     #|         
#comments                                                                                                                            #|                 
sim_comments      = parameters['sim_comments']                                                                                       #|                                                     
sm_input_comments = parameters['sm_input_comments']                                                                                  #|  
model_comments    = parameters['model_comments']                                                                                     #|                                                     
bench_comments    = parameters['bench_comments']                                                                                     #|                                                     
perf_comments     = parameters['perf_comments']                                                                                      #|                                                     
specs_comments    = parameters['specs_comments']                                                                                     #|
                                                                                                                                     #|                                                     
                                                                                                                                     #|         
#model type and linearity                                                                                                            #|                                 
sim_type          = parameters['type']                                                                                               #|                                             
linearity         = parameters['linearity']                                                                                          #|
stage             = parameters['stage']                                                                                              #|
options           = parameters['options']                                                                                            #|                                                 
#-------------------------------------------------------------------------------------------------------------------------------------|

simulation()

#close sql
cursor.close()
cnx.close()