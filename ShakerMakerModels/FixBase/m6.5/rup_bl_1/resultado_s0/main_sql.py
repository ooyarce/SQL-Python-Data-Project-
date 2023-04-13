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
bsunits, absacc_units, rel_displ_units, maxbs_units, maxd_units = 'kN', 'm/s/s', 'm', 'kN', 'm'

model_structure_perfomance(bsunits, absacc_units, rel_displ_units, maxbs_units, maxd_units)
#close sql
cursor.close()
cnx.close()