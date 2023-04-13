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
model_structure_perfomance('unidad al azar')
#close sql
cursor.close()
cnx.close()