import os, glob
for filename in glob.glob('*.txt'):
	if len(filename) == 17:
		if filename[12] == 'e':
			accelerations = open(filename,'r')
			#print(f'east file = {filename}')
		elif filename[12] == 'n':
			accelerations2 = open(filename,'r')
			#print(f'north file = {filename}')
		elif filename[12] == 'z':
			accelerations3 = open(filename,'r')
			#print(f'vertical file = {filename}\n')

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#WRITTING EAST VALUES INPUT IN TCL 
tcl_format = open('tcl_format_east.tcl','w')

values = []
counter = 0
for i in accelerations:
	values.append(i)	

for i in range(0,2000,10):
	if i == 0:
		tcl_format.write(f'set timeSeries_list_of_values_2 {{{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])} \\\n' )
	elif i != 0 and i < 1989:
		tcl_format.write(f'\t\t\t\t\t\t\t\t{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])} \\\n')
	else:
		tcl_format.write(f'\t\t\t\t\t\t\t\t{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])}}}\n')
tcl_format.write('timeSeries Path 2 -time $timeSeries_list_of_times_2 -values $timeSeries_list_of_values_2\n')
tcl_format.close()
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#WRITTING NORTH VALUES INPUT IN TCL
tcl_format2 = open('tcl_format_north.tcl','w')

values = []
counter = 0
for i in accelerations2:
	values.append(i)	

for i in range(0,2000,10):
	if i == 0:
		tcl_format2.write(f'set timeSeries_list_of_values_3 {{{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])} \\\n' )
	elif i != 0 and i < 1989:
		tcl_format2.write(f'\t\t\t\t\t\t\t\t{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])} \\\n')
	else:
		tcl_format2.write(f'\t\t\t\t\t\t\t\t{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])}}}\n')
tcl_format2.write('timeSeries Path 3 -time $timeSeries_list_of_times_3 -values $timeSeries_list_of_values_3\n')
tcl_format2.close()
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#WRITTING NORTH VALUES INPUT IN TCL
tcl_format3 = open('tcl_format_vertical.tcl','w')

values = []
counter = 0
for i in accelerations3:
	values.append(i)	

for i in range(0,2000,10):
	if i == 0:
		tcl_format3.write(f'set timeSeries_list_of_values_4 {{{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])} \\\n' )
	elif i != 0 and i < 1989:
		tcl_format3.write(f'\t\t\t\t\t\t\t\t{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])} \\\n')
	else:
		tcl_format3.write(f'\t\t\t\t\t\t\t\t{float(values[i])} {float(values[i+1])} {float(values[i+2])} {float(values[i+3])} {float(values[i+4])} {float(values[i+5])} {float(values[i+6])} {float(values[i+7])} {float(values[i+8])} {float(values[i+9])}}}\n')
tcl_format3.write('timeSeries Path 4 -time $timeSeries_list_of_times_4 -values $timeSeries_list_of_values_4\n')
tcl_format3.close()
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
definitions = open('definitions.tcl','r')
east_file = open('tcl_format_east.tcl','r')
north_file = open('tcl_format_north.tcl','r')
vertical_file = open('tcl_format_vertical.tcl','r')
created_file = open('definitions2.tcl','w')

#writting first vector time
counter = 0
for row in definitions:
	if counter < 202:
		created_file.write(row)
	elif counter ==202:
		break
	counter += 1
#writting east vector acceleration
counter2 = 0
for row in east_file:
	created_file.write(row)
	
#writting second vector time
for row in definitions:
	if 401 < counter < 602:
		created_file.write(row)
	elif counter == 603:
		break
	counter += 1
#writting north vector acceleration
for row in north_file:
	created_file.write(row)

#writting third vector time
for row in definitions:
	if 801 < counter < 1002:
		created_file.write(row)
	elif counter == 1002:
		break
	counter += 1
#writting vertical vector acceleration
for row in vertical_file:
	created_file.write(row)

#writting rest of the values
for row in definitions:
	if 1201 < counter:
		created_file.write(row)
	counter += 1

