#-----------------------------------------------------------------------------------------------------------------------------------
#THIS FILLS THE SQL DATABASE																										|	
#-----------------------------------------------------------------------------------------------------------------------------------
from sql_functions import *

#put into tables
"""
clustername = 'Omar-Ubuntu'
comments = 'Just testing model_benchmark function'
model_benchmark(clustername,comments)
"""
parameters = {
    'bs_units'       : 'kN',                                                            
    'max_bs_units'   : 'kN',                                                                
    'rel_displ_units': 'm',             
    'max_drift_units': 'm',             
    'abs_acc_units'  : 'm/s/s',         
    'model_name'     : 'FixBaseV3',     
    'clustername'    : 'Esmeralda HPC Cluster by jaabell@uandes.cl',
    'perf_comments'  : 'Comments for model_structure_perfomance',
    'specs_comments' : 'Comments for model_specs_structure',
    'sim_comments'   : 'Comments for simulation_model',
    'bench_comments' : 'Comments for model_benchmark',
    'linearity'      : 1
}
bsunits, absacc_units, rel_displ_units, maxbs_units, maxd_units = 'tonf', 'cm/hrs/hrs', 'in', 'kgf', 'km'
model_structure_perfomance(bsunits, absacc_units, rel_displ_units, maxbs_units, maxd_units)

#close sql
cursor.close()
cnx.close()