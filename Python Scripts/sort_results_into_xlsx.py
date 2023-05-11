#------------------------------------------------------------------------------------------------------------------------------------
#THIS CODE USES THE DATA FROM THE REACTIONS FOLDER AND SORT IT IN A BIG MATRIX SO YOU CAN MANIPULATE RESULTS FROM THIS FILE CREATED |
#IT WILL CREATE 1 FILE CURRENTLY, AND IT WILL SEPARATED IN 3 SHEETS AND IT'S ALL ABOUT THE REACTIONS IN THE TIME SERIES				|	
#------------------------------------------------------------------------------------------------------------------------------------
def create_reaction_xlsx():
	import xlsxwriter
	import os

	#create nodes sorted list 
	nodes = []
	path = os.getcwd()
	results = os.listdir(f'{path}/Reactions/')

	#sorting nodes
	for result in results:
		node = (int(result.split('-')[1].split('_')[1]))
		nodes.append(node)
	nodes.sort()

	#sorting files in list
	results_sorted = []
	counter = 0
	for node in nodes:
		nodeid = f'_{node}-'
		for result in results:
			if nodeid in result:
				results_sorted.append(result)

	#define format
	workbook = xlsxwriter.Workbook('reactions.xlsx')
	main_format = workbook.add_format({'bold':True})
	main_format.set_align('center')
	second_format = workbook.add_format({'font_color': 'black'})
	second_format.set_align('center')


	#open book and start writing in shells
	x_sheet = workbook.add_worksheet('Reaction East')
	y_sheet = workbook.add_worksheet('Reaction North')
	z_sheet = workbook.add_worksheet('Reaction Vertical')
	x_sheet.write(0,0,'Timestep/NodeID',main_format)
	y_sheet.write(0,0,'Timestep/NodeID',main_format)
	z_sheet.write(0,0,'Timestep/NodeID',main_format)
	x_sheet.set_column(0,0,17,main_format)
	y_sheet.set_column(0,0,17,main_format)
	z_sheet.set_column(0,0,17,main_format)


	#fill rows names
	row = 1
	column = 0
	time_step = 0.0
	while time_step < 50.00:
		x_sheet.write(row,column,f'{time_step:.3f}',main_format)
		y_sheet.write(row,column,f'{time_step:.3f}',main_format)
		z_sheet.write(row,column,f'{time_step:.3f}',main_format)

		time_step += 0.025
		row +=1

	#fill columns names
	row = 0
	column = 1
	files = []
	for node in (range(len(nodes))):
		x_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		y_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		z_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		column+=1

	#fill matrix in correct values, here the file is the column and it's results are the rows
	files = [open(f'Reactions/{file}','r') for file in results_sorted]
	column = 1
	for file in range(len(files)):
		
		nodal_result = [[(num) for num in line.split('\n')] for line in files[file]]
		row = 1
		for row_val in nodal_result:
			reaction_X = float(row_val[0].split(' ')[0])
			reaction_Y = float(row_val[0].split(' ')[1])
			reaction_Z = float(row_val[0].split(' ')[2])
			x_sheet.write(row,column,reaction_X,second_format)
			y_sheet.write(row,column,reaction_Y,second_format)
			z_sheet.write(row,column,reaction_Z,second_format)
			row += 1
		
		column += 1

	workbook.close()

#------------------------------------------------------------------------------------------------------------------------------------

def create_displacement_xlsx():
	import xlsxwriter
	import os

	#create nodes sorted list 
	nodes = []
	path = os.getcwd()
	results = os.listdir(f'{path}/Displacements/')

	#sorting nodes
	for result in results:
		node = (int(result.split('-')[1].split('_')[1]))
		nodes.append(node)
	nodes.sort()

	#sorting files in list
	results_sorted = []
	counter = 0
	for node in nodes:
		nodeid = f'_{node}-'
		for result in results:
			if nodeid in result:
				results_sorted.append(result)

	#define format
	workbook = xlsxwriter.Workbook('displacements.xlsx')
	main_format = workbook.add_format({'bold':True})
	main_format.set_align('center')
	second_format = workbook.add_format({'font_color': 'black'})
	second_format.set_align('center')

	#open book and start writing in shells
	x_sheet = workbook.add_worksheet('Displacements East')
	y_sheet = workbook.add_worksheet('Displacements North')
	z_sheet = workbook.add_worksheet('Displacements Vertical')
	x_sheet.write(0,0,'Timestep/NodeID',main_format)
	y_sheet.write(0,0,'Timestep/NodeID',main_format)
	z_sheet.write(0,0,'Timestep/NodeID',main_format)

	x_sheet.set_column(0,0,17,main_format)
	y_sheet.set_column(0,0,17,main_format)
	z_sheet.set_column(0,0,17,main_format)

	#fill rows names
	row = 1
	column = 0
	time_step = 0.0
	while time_step < 50:
		x_sheet.write(row,column,time_step,main_format)
		y_sheet.write(row,column,time_step,main_format)
		z_sheet.write(row,column,time_step,main_format)

		time_step += 0.025
		row +=1

	#fill columns names
	row = 0
	column = 1
	files = []
	for node in (range(len(nodes))):
		x_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		y_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		z_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		column+=1

	#fill matrix in correct values, here the file is the column and it's results are the rows
	files = [open(f'Displacements/{file}','r') for file in results_sorted]
	column = 1
	for file in range(len(files)):
		
		nodal_result = [[(num) for num in line.split('\n')] for line in files[file]]
		row = 1
		for row_val in nodal_result:
			acceleration_X = float(row_val[0].split(' ')[0])
			acceleration_Y = float(row_val[0].split(' ')[1])
			acceleration_Z = float(row_val[0].split(' ')[2])
			x_sheet.write(row,column,acceleration_X,second_format)
			y_sheet.write(row,column,acceleration_Y,second_format)
			z_sheet.write(row,column,acceleration_Z,second_format)
			row += 1
		
		column += 1

	workbook.close()
#------------------------------------------------------------------------------------------------------------------------------------

def create_accelerations_xlsx():
	import xlsxwriter
	import os

	#create nodes sorted list 
	nodes = []
	path = os.getcwd()
	results = os.listdir(f'{path}/Accelerations/')

	#sorting nodes
	for result in results:
		node = (int(result.split('-')[1].split('_')[1]))
		nodes.append(node)
	nodes.sort()

	#sorting files in list
	results_sorted = []
	counter = 0
	for node in nodes:
		nodeid = f'_{node}-'
		for result in results:
			if nodeid in result:
				results_sorted.append(result)

	#define format
	workbook = xlsxwriter.Workbook('accelerations.xlsx')
	main_format = workbook.add_format({'bold':True})
	main_format.set_align('center')
	second_format = workbook.add_format({'font_color': 'black'})
	second_format.set_align('center')

	#open book and start writing in shells
	x_sheet = workbook.add_worksheet('Accelerations East')
	y_sheet = workbook.add_worksheet('Accelerations North')
	z_sheet = workbook.add_worksheet('Accelerations Vertical')
	x_sheet.write(0,0,'Timestep/NodeID',main_format)
	y_sheet.write(0,0,'Timestep/NodeID',main_format)
	z_sheet.write(0,0,'Timestep/NodeID',main_format)

	x_sheet.set_column(0,0,17,main_format)
	y_sheet.set_column(0,0,17,main_format)
	z_sheet.set_column(0,0,17,main_format)

	#fill rows names
	row = 1
	column = 0
	time_step = 0.0
	while time_step < 50:
		x_sheet.write(row,column,time_step,main_format)
		y_sheet.write(row,column,time_step,main_format)
		z_sheet.write(row,column,time_step,main_format)

		time_step += 0.025
		row +=1

	#fill columns names
	row = 0
	column = 1
	files = []
	for node in (range(len(nodes))):
		x_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		y_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		z_sheet.write(row,column,f'Node {nodes[node]}',main_format)
		column+=1

	#fill matrix in correct values, here the file is the column and it's results are the rows
	files = [open(f'Accelerations/{file}','r') for file in results_sorted]
	column = 1
	for file in range(len(files)):
		
		nodal_result = [[(num) for num in line.split('\n')] for line in files[file]]
		row = 1
		for row_val in nodal_result:
			acceleration_X = float(row_val[0].split(' ')[0])
			acceleration_Y = float(row_val[0].split(' ')[1])
			acceleration_Z = float(row_val[0].split(' ')[2])
			x_sheet.write(row,column,acceleration_X,second_format)
			y_sheet.write(row,column,acceleration_Y,second_format)
			z_sheet.write(row,column,acceleration_Z,second_format)
			row += 1
		
		column += 1

	workbook.close()

create_reaction_xlsx()
create_displacement_xlsx()
create_accelerations_xlsx()