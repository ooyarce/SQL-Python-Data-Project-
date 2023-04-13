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
structure_max_drift_per_floor()
#close sql
cursor.close()
cnx.close()