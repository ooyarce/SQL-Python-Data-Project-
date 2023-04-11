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

coordenates, drift_nodes,histories_nodes, histories, subs, heights = give_coords_info()

for idx, level in enumerate(list(histories_nodes)):
	if idx <20:
		for idy, nodo in enumerate(list(histories_nodes[level])):
			if idy%3 == 0 and idy != 0:

				#to check the nodes coordenates and see that drift is well calculated
				print(f'Level {idx} - Level {idx+1} {heights[idx]=}')
				print(coordenates[list(histories_nodes[f'Level {idx}'])[0]],coordenates[list(histories_nodes[f'Level {idx+1}'])[0]])
				print(coordenates[list(histories_nodes[f'Level {idx}'])[1]],coordenates[list(histories_nodes[f'Level {idx+1}'])[1]])
				print(coordenates[list(histories_nodes[f'Level {idx}'])[2]],coordenates[list(histories_nodes[f'Level {idx+1}'])[2]])
				print(coordenates[list(histories_nodes[f'Level {idx}'])[3]],coordenates[list(histories_nodes[f'Level {idx+1}'])[3]],'\n')


"""
insert_query = 'INSERT INTO structure_base_shear (TimeSeries,ShearX,ShearY,ShearZ) VALUES (%s,%s,%s,%s)'
values = (timeseries,base_shears[0],base_shears[1],base_shears[2])
#------------------------------------------------------------------------------------------------------------------------------------
cursor.execute(insert_query, values)
cnx.commit()		

print('structure_base_shear table updated correctly!')
"""