#---------------------------------------------------------------------------------------------------------------------------------------------------------
#THIS CODE DESCRIBES ALL THE NODES FOR EACH PARTITION FOR EACH TYPE OF RESULT (REACTION, ACCELERATION, DISPLACEMENT)									 |
#YOU CAN ACCES TO YOUR DATA OF INTEREST VIA CHECKING THE DICTIONARIES IT CREATES (reactions, accelerations and displacements)							 |
#YOU CAN SEE ALL THE NODES RELATED TO THE SPECIFIC TYPE OF RESULT IN THE LIST (reaction_nodes, acce_nodes and displ_nodes)								 |
#YOU CAN USE THE Counter(LIST).values() TO CHECK IF SOME NODES ARE IN MULTIPLES PARTITIONS																 |
#---------------------------------------------------------------------------------------------------------------------------------------------------------
import os
from collections import Counter

#access to folders
path = os.path.dirname(os.path.abspath(__file__))
folders = os.listdir(path)

#access to folders files
for i in range(len(folders)):
	if folders[i] == 'accel':
		folder_acc = f'{path}/{folders[i]}'
	elif folders[i] == 'coords':
		folder_coord = f'{path}/{folders[i]}'
	elif folders[i] == 'disp':
		folder_disp = f'{path}/{folders[i]}'
	elif folders[i] == 'reaction':
		folder_reaction = f'{path}/{folders[i]}'
	elif folders[i] == 'info':
		folder_info = f'{path}/{folders[i]}'
#---------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------ACCELERATIONS------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
def give_accelerations():
	#check nodes
	files_accel = os.listdir(folder_acc)
	files = [open(f'{folder_acc}/{file}','r') for file in files_accel]

	#create dictionary
	accelerations = {}
	for file in range(len(files)):
		nodes = [[(num) for num in line.split('\n')] for line in files[file]]
		file_id = str(files[file]).split('-')[1].split(' ')[0].split('.')[0]
		accelerations[f'Partition {file_id}'] = {}
		for nodei in range(len(nodes)):
			accelerations[f'Partition {file_id}'][f'Node {nodei}'] = nodes[nodei][0]

	#create list with nodes sorted
	acce_nodes = []
	for values in accelerations.values():
		for node in values.values():
			acce_nodes.append(int(node))
	acce_nodes.sort()

	return accelerations,acce_nodes
#---------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------DISPLACEMENTS------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
def give_displacements():
	#check nodes
	files_disp = os.listdir(folder_disp)
	files = [open(f'{folder_disp}/{file}','r') for file in files_disp]

	#create dictionary
	displacements = {}
	for file in range(len(files)):
		nodes = [[(num) for num in line.split('\n')] for line in files[file]]
		file_id = str(files[file]).split('-')[1].split(' ')[0].split('.')[0]
		displacements[f'Partition {file_id}'] = {}
		for nodei in range(len(nodes)):
			displacements[f'Partition {file_id}'][f'Node {nodei}'] = nodes[nodei][0]

	#create list with nodes sorted
	displ_nodes = []

	for values in displacements.values():
		for node in values.values():
			displ_nodes.append(int(node))

	displ_nodes.sort()

	return displacements,displ_nodes
#---------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------REACTIONS--------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
def give_reactions():
	#check nodes
	files_reaction = os.listdir(folder_reaction)
	files = [open(f'{folder_reaction}/{file}','r')for file in files_reaction]

	#create dictionary
	reactions = {}
	for file in range(len(files)):
		nodes = [[(num) for num in line.split('\n')] for line in files[file]]
		file_id = str(files[file]).split('-')[1].split(' ')[0].split('.')[0]
		reactions[f'Partition {file_id}'] = {}
		for nodei in range(len(nodes)):
			reactions[f'Partition {file_id}'][f'Node {nodei}'] = nodes[nodei][0]

	#create list with nodes sorted
	reaction_nodes = []
	for values in reactions.values():
		for node in values.values():
			reaction_nodes.append(int(node))
	reaction_nodes.sort()

	return reactions,reaction_nodes

reactions,reaction_nodes = give_reactions()
print(reaction_nodes)
#---------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------COORDINATES--------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
def give_coords_info():
	#check nodes
	files_coords = os.listdir(folder_coord)
	files = [open(f'{folder_coord}/{file}','r') for file in files_coords]

	#create dictionary
	coordenates = {}
	for file in range(len(files)):
		nodes = [[(num) for num in line.split('\n')] for line in files[file]]
		file_id = str(files[file]).split('_')[2].split('.')[0]
		for nodei in range(1,len(nodes)):
			node_id = nodes[nodei][0].split(' ')[0]
			coord_x = float(nodes[nodei][0].split(' ')[1])
			coord_y = float(nodes[nodei][0].split(' ')[2])
			coord_z = float(nodes[nodei][0].split(' ')[3])

			coordenates[f'Node {node_id}'] = {}
			coordenates[f'Node {node_id}'] = {}
			coordenates[f'Node {node_id}'] = {}
			coordenates[f'Node {node_id}']['coord x'] = float(f'{coord_x:.1f}')
			coordenates[f'Node {node_id}']['coord y'] = float(f'{coord_y:.1f}')
			coordenates[f'Node {node_id}']['coord z'] = float(f'{coord_z:.1f}')

	#sort every node per level 
	sorted_nodes = sorted(coordenates.items(), key = lambda x: (x[1]['coord x'],x[1]['coord y'], x[1]['coord z']))
	#create dictionary with specific nodes per corner to calculate directly the drift
	drift_nodes = {'corner1':[],'corner2':[],'corner3':[],'corner4':[]}
	
	#calculate subs, histories, and fill drift nodes with heights
	height = 0
	id_corner = 0
	subs = 0
	histories = 0
	for tuple_i in sorted_nodes:
		z = (tuple_i[1]['coord z'])
		node = tuple_i[0]
		if z< 0:
			subs +=1
			continue
		elif z > height:
			height = z
			drift_nodes[f'corner{id_corner}'].append(f'{node}|{z}')
			histories += 1
			continue
		height = 0.0
		id_corner +=1

	histories = int(histories/4)
	subs = int(subs/4)

	#list of heigths
	heights = []
	for data in range(len(drift_nodes['corner1'])-1):
		current_height = (float(drift_nodes['corner1'][data+1].split('|')[1])-float(drift_nodes['corner1'][data].split('|')[1]))
		heights.append(current_height)

	
	#create dict with nodes per historie 
	sort_by_historie = sorted(coordenates.items(), key = lambda x: (x[1]['coord z'],x[1]['coord x'], x[1]['coord y']))
	histories_nodes = {}
	counter = 0
	for i in range(histories+subs+1):
		i -= 4
		if i < 0:
			counter+=4
			continue
		histories_nodes[f'Level {i}'] = {}
		node1 = sort_by_historie[counter][0]
		node2 = sort_by_historie[counter+1][0]
		node3 = sort_by_historie[counter+2][0]
		node4 = sort_by_historie[counter+3][0]
		#print(node1,node2,node3,node4)
		histories_nodes[f'Level {i}'][node1] = sort_by_historie[counter][1]
		histories_nodes[f'Level {i}'][node2] = sort_by_historie[counter+1][1]
		histories_nodes[f'Level {i}'][node3] = sort_by_historie[counter+2][1]
		histories_nodes[f'Level {i}'][node4] = sort_by_historie[counter+3][1]
		counter+=4
	heights.insert(0,(coordenates[list(histories_nodes["Level 1"])[0]]["coord z"] - coordenates[list(histories_nodes["Level 0"])[0]]["coord z"]))
	return coordenates, drift_nodes,histories_nodes, histories, subs, heights

#coordenates, drift_nodes,histories_nodes, histories, subs, heights = give_coords_info()

#--------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------MODEL INFO---------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------
def give_info():
	#read file
	files_info = os.listdir(folder_info)
	file = open(f'{folder_info}/model_info.csv','r') 

	#get number of nodes and number of elements
	info = [[row for row in line.split(' ')] for line in file]
	nnodes = (int(info[0][4]))
	nelements = (int(info[1][4]))

	return nnodes, nelements