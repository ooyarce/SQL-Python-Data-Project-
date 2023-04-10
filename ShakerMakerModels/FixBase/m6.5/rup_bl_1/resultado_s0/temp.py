#------------------------------------------------------------------------------------------------------------------------------------
#THIS FILLS THE RESULTS TABLE (REACTIONS-RELATIVE DISPLACEMENTS - ABSOLUTE ACCELERATIONS)
#------------------------------------------------------------------------------------------------------------------------------------
"""
import pandas as pd
import json
displacementes = pd.read_excel('displacements.xlsx', sheet_name = None)
sheet_names = list(displacementes.keys())
rel_displ = []

for sheet_name in sheet_names:
	df = displacementes[sheet_name].iloc[:10,1:10].dropna()
	timeseries = json.dumps(displacementes[sheet_name].iloc[:,0].tolist())
	rel_displ.append(df)

results_list = []
for index, row in rel_displ[0].iterrows():
	results_list.append(row.tolist())
"""
from Results.check_nodes import *
give_coords()
"""
insert_query = 'INSERT INTO structure_base_shear (TimeSeries,ShearX,ShearY,ShearZ) VALUES (%s,%s,%s,%s)'
values = (timeseries,base_shears[0],base_shears[1],base_shears[2])
#------------------------------------------------------------------------------------------------------------------------------------
cursor.execute(insert_query, values)
cnx.commit()		

print('structure_base_shear table updated correctly!')
"""