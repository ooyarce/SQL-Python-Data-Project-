#-----------------------------------------------------------------------------------------------------------------------------------
#THIS FILLS THE SQL DATABASE																										|	
#-----------------------------------------------------------------------------------------------------------------------------------
from SQL_functions import *

#put into tables

model_benchmark()
structure_base_shear()
structure_relative_displacements()
structure_abs_acceleration()

#close sql
cursor.close()
cnx.close()