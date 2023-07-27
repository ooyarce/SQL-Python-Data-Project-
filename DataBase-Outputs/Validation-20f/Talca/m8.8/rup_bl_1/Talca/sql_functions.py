# from shakermaker.tools.plotting import ZENTPlot,cumulative_trapezoid
# from shakermaker.station import Station
# from shakermaker import shakermaker
from Results.check_nodes import *

import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd
import numpy as np
import datetime
import glob
import json	
import os

cnx = mysql.connector.connect(user='root', password='g3drGvwkcmcq', host='34.176.187.208', database='stkodatabase')
cursor = cnx.cursor()

def simulation(sim_type = 1,
	simstage = 'No stage yet',
	simopt = 'No options yet',
	sim_comments = 'No comments',
	sm_input_comments = 'No comments',
	pga_units = 'm/s/s',
	resp_spectrum = 'm/s/s',
	model_name = glob.glob("*.scd")[0],
	model_comments = 'No comments', 
	bs_units='kN',
	abs_acc_units='m/s/s',
	rel_displ_units='m',
	max_bs_units='kN',
	max_drift_units='m',
	perf_comments = 'No comments',
	linearity = 1,
	specs_comments = 'No comments', 
	clustername = 'Esmeralda HPC Cluster by jaabell@uandes.cl',
	bench_comments = 'No comments'):
	print("---------------------------------------------|")
	print("----------EXPORTING INTO DATABASE------------|")
	print("---------------------------------------------|")
	simulation_model(model_name,model_comments,bs_units,abs_acc_units,rel_displ_units,max_bs_units,max_drift_units,perf_comments, linearity, specs_comments, clustername, bench_comments)
	Model = cursor.lastrowid
	simulation_sm_input(sm_input_comments,pga_units,resp_spectrum)
	SM_Input = cursor.lastrowid

	date = datetime.datetime.now()
	date = date.strftime("%B %d, %Y")

	insert_query = 'INSERT INTO simulation(idModel, idSM_Input, idType, SimStage, SimOptions, Simdate, Comments) VALUES(%s,%s,%s,%s,%s,%s,%s)'
	values = (Model, SM_Input, sim_type, simstage, simopt, date, sim_comments)
	cursor.execute(insert_query,values)
	cnx.commit()
	print('simulation table updated correctly!\n')
	print("---------------------------------------------|")
	print("---------------------------------------------|")
	print("---------------------------------------------|\n")

def simulation_sm_input(sm_input_comments = 'No comments', pga_units = 'm/s/s', resp_spectrum = 'm/s/s'): #this functions should be modified acording to the format of 
	#get magnitude
	Magnitude = (os.path.dirname(__file__).split('\\')[-3][1:])
	Magnitude = (f'{Magnitude}Mw')

	#get rupture type
	Rup_name = os.path.dirname(__file__).split('\\')[-2]
	try:
		#get realization id
		iteration = Rup_name.split('_')[2]
		Rup_type = Rup_name.split('_')[1]
		if Rup_type == 'bl':
			rupture = 'Bilateral'
		elif Rup_type == 'ns':
			rupture = 'North-South'
		elif Rup_type == 'sn':
			rupture = 'South-North'
		else:
			raise TypeError('Folders name are not following the format rup_[bl/ns/sn]_[iteration].')
	except IndexError:
		rupture = 'Unknow'
		iteration = 'No Iteration'

	#get location
	try:
		station = int(os.path.dirname(__file__).split('\\')[-1][-1])
		if station >= 0 and station <= 3:
			location = 'Near field'
		elif station >= 4 and station <=6:
			location = 'Intermediate field'
		elif station >= 7 and station <=9:
			location = 'Far field'
	except ValueError:
		location = os.path.dirname(__file__).split('\\')[-1]

	#PGA y Spectrum
	try:
		PGA = get_sm_id()
		Spectrum = get_sm_id()
	except ValueError:
		PGA = 1
		Spectrum = 1
	insert_query = 'INSERT INTO simulation_sm_input(idPGA, idSpectrum, Magnitude, Rupture_type, Location, RealizationID, Comments) VALUES(%s,%s,%s,%s,%s,%s,%s)'
	values = (PGA, Spectrum, Magnitude, rupture, location, iteration, sm_input_comments)
	#print(f'{PGA=}, {Spectrum=}, {Magnitude=}, {rupture=}, {location=}, {iteration=}, {sm_input_comments=}')
	cursor.execute(insert_query,values)
	print('simulation_sm_input table updated correctly!\n')

def simulation_model(model_name = '', model_comments = '', bs_units='', abs_acc_units='', rel_displ_units='', max_bs_units='', max_drift_units='', perf_comments = '',  linearity = 1, specs_comments = '', clustername = '',bench_comments = ''):
	model_benchmark(clustername,bench_comments)
	Benchmark = cursor.lastrowid
	model_structure_perfomance(bs_units,abs_acc_units,rel_displ_units,max_bs_units,max_drift_units,perf_comments)
	StructurePerfomance = cursor.lastrowid
	model_specs_structure(linearity,specs_comments)
	SpecsStructure = cursor.lastrowid

	insert_query = 'INSERT INTO simulation_model(idBenchmark, idStructuralPerfomance, idSpecsStructure, ModelName, Comments) VALUES(%s,%s,%s,%s,%s)'
	values = (Benchmark,StructurePerfomance,SpecsStructure,model_name, model_comments)
	cursor.execute(insert_query,values)
	print('simulation_model table updated correctly!\n')

def model_benchmark(clustername = '',comments = '' ):
	#------------------------------------------------------------------------------------------------------------------------------------
	#Get calculus time from log file, nodes, threads and comments
	#------------------------------------------------------------------------------------------------------------------------------------

	data = open('run.sh')
	counter = 0

	for row in data:
		#get job name
		if counter == 1:
			jobname = (row.split(' ')[1].split('=')[1])
		#get nodes
		if counter == 2:
			nodes = int(row.split('=')[1].split('\n')[0])

		#get threads
		if counter == 3:
			threads = int(row.split('=')[1].split('\n')[0])

		#get logname
		if counter == 4:
			logname = (row.split('=')[1].split(' ')[0])

		counter += 1

	log = open(logname)
	for row in log:
		if 'Elapsed:' in row:
			value = row.split(' ')[1]
			time = (f'{value} seconds') #first value of query

	path1 = f'{os.path.dirname(__file__)}/Accelerations/'
	path2 = f'{os.path.dirname(__file__)}/Displacements/'
	path3 = f'{os.path.dirname(__file__)}/Reactions/'
	path4 = f'{os.path.dirname(__file__)}/Results/'

	acc_results = 0
	displ_results = 0
	react_results = 0
	results_results = 0

	#get accelerations
	for file in os.listdir(path1):
		path = os.path.join(path1,file)
		acc_results += os.path.getsize(path)
	acc_size = acc_results/(1024*1024)

	#get displacements
	for file in os.listdir(path2):
		path = os.path.join(path2,file)
		displ_results += os.path.getsize(path)
	displ_size = displ_results/(1024*1024)

	#get reactions 
	for file in os.listdir(path3):
		path = os.path.join(path3,file)
		react_results += os.path.getsize(path)
	react_size = react_results/(1024*1024)

	#get results
	for file in os.listdir(path4):
		path = os.path.join(path4,file)
		results_results += os.path.getsize(path)
	results_size = results_results/(1024*1024)
	memory_by_results = f'{acc_size + displ_size + react_size + results_size:.2f} Mb' #this value goes as second column in the query

	#get model memory
	model_name = glob.glob("*.scd")[0]
	memory_by_model = f'{os.path.getsize(model_name)/(1024*1024):.2f} Mb' #this value goes for query

	insert_query = 'INSERT INTO model_benchmark (JobName,SimulationTime,MemoryResults,MemoryModel,ClusterNodes,CpuPerNodes,ClusterName,Comments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
	values = (jobname,time,memory_by_results,memory_by_model,nodes,threads,clustername,comments)
	cursor.execute(insert_query, values)	
	print('model_benchmark table updated correctly!\n')

def model_structure_perfomance(bs_units='', abs_acc_units='', rel_displ_units='', max_bs_units='', max_drift_units='', comments = ''):
	#fills base shear
	structure_base_shear(bs_units)
	BaseShear = cursor.lastrowid

	#fills absolute accelerations
	structure_abs_acceleration(abs_acc_units)
	AbsAccelerations = cursor.lastrowid
	
	#fills relative displacements
	structure_relative_displacements(rel_displ_units)
	RelativeDisplacements = cursor.lastrowid
	
	#fills max base shear
	structure_max_base_shear(max_bs_units)
	MaxBaseShear = cursor.lastrowid

	#fills max drift per floor
	structure_max_drift_per_floor(max_drift_units)
	MaxDriftPerFloor = cursor.lastrowid

	#this is going to change in the future
	mta = 'Not sure how to calculate this'
	fas = 'Not sure how to calculate this'

	#insert data into database
	insert_query = 'INSERT INTO model_structure_perfomance (idBaseShear,idAbsAccelerations,idRelativeDisplacements,idMaxBaseShear,idMaxDriftPerFloor,MaxTorsionAngle,FloorAccelerationSpectra,Comments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
	values = (BaseShear,AbsAccelerations,RelativeDisplacements,MaxBaseShear,MaxDriftPerFloor,mta,fas,comments) #mta and fas vars has to change
	cursor.execute(insert_query, values)		
	print('model_structure_perfomance table updated correctly!\n')

def model_specs_structure(linearity = 1, comments = ''):
	if linearity < 1 or linearity > 2:
		raise TypeError('The Linearity parameter can only take the values of 1 or 2.')  

	nnodes, nelements, npartitions = give_info()
	coordenates, drift_nodes,histories_nodes, histories, subs, heights = give_coords_info()

	insert_query = 'INSERT INTO model_specs_structure (idLinearity, Nnodes, Nelements, Nhistories, Nsubs, InterstoryHeight, Comments) VALUES (%s,%s,%s,%s,%s,%s,%s)'
	values = (linearity, nnodes, nelements,histories,subs, json.dumps(heights), comments) #mta and fas vars has to change
	cursor.execute(insert_query, values)		
	print('model_specs_structure table updated correctly!\n')

def structure_base_shear(units = 'kN'):
	reactions = pd.read_excel('reactions.xlsx', sheet_name = None)
	sheet_names = list(reactions.keys())
	base_shears = []

	for sheet_name in sheet_names:
		df = reactions[sheet_name].iloc[:,1:].dropna()
		timeseries = json.dumps(reactions[sheet_name].iloc[:,0].tolist())
		summ = json.dumps((df.sum(axis = 1).values).tolist())
		base_shears.append(summ)

	insert_query = 'INSERT INTO structure_base_shear (TimeSeries, ShearX, ShearY, ShearZ, Units) VALUES (%s,%s,%s,%s,%s)'
	values = (timeseries, base_shears[0], base_shears[1], base_shears[2], units)
	cursor.execute(insert_query, values)		
	print('structure_base_shear table updated correctly!\n')

def structure_max_base_shear(units = 'kN'):
	reactions = pd.read_excel('reactions.xlsx', sheet_name = None)
	sheet_names = list(reactions.keys())
	max_shears = []

	for sheet_name in sheet_names:
		df = reactions[sheet_name].iloc[:,1:].dropna()
		summ = json.dumps(max(df.sum(axis = 1).values).tolist())
		max_shears.append((summ))
	max_shears = [float(num) for num in max_shears]
	max_shears = [round(num,2) for num in max_shears]
	
	insert_query = 'INSERT INTO structure_max_base_shear (MaxX, MaxY, MaxZ, Units) VALUES (%s,%s,%s,%s)'
	values = (max_shears[0], max_shears[1], max_shears[2],units)
	cursor.execute(insert_query,values)
	print('structure_max_base_shear table updated correctly!\n')

def structure_max_drift_per_floor(units = 'm'):
	coordenates, drift_nodes,histories_nodes, histories, subs, heights = give_coords_info()
	displacements = pd.read_excel('displacements.xlsx', sheet_name = None)
	sheet_names = list(displacements.keys())
	sheet_names.pop(2)
	drifts = []

	for sheet_name in sheet_names:
		df = displacements[sheet_name].iloc[:,1:].dropna()
		sheet_corners = []
		sheet_centers = []
		for idx, level in enumerate(list(histories_nodes)):
			if idx == 20:
				break
			for idy, nodo in enumerate(list(histories_nodes[level])):
				if idy%3 == 0 and idy != 0:
					#define nodes
					node1,node5 = list(histories_nodes[f'Level {idx}'])[0],list(histories_nodes[f'Level {idx+1}'])[0]
					node2,node6 = list(histories_nodes[f'Level {idx}'])[1],list(histories_nodes[f'Level {idx+1}'])[1]
					node3,node7 = list(histories_nodes[f'Level {idx}'])[2],list(histories_nodes[f'Level {idx+1}'])[2]
					node4,node8 = list(histories_nodes[f'Level {idx}'])[3],list(histories_nodes[f'Level {idx+1}'])[3]
					
					#corner drift absolute value
					drift1,drift2 = ((df[node5] - df[node1])/heights[idx]).abs().max(),	((df[node6] - df[node2])/heights[idx]).abs().max()
					drift3,drift4 = ((df[node7] - df[node3])/heights[idx]).abs().max(),	((df[node8] - df[node4])/heights[idx]).abs().max()
					max_corner = (max((drift1),(drift2),(drift3),(drift4)))

					#center drift absolute value
					mean_displ2 = df[[node5,node6,node7,node8]].mean(axis=1)
					id_center = (mean_displ2.abs()).argmax()
					mean_displ1 = sum([df[node1][id_center],df[node2][id_center],df[node3][id_center],df[node4][id_center]])/4
					max_center = abs(mean_displ2[id_center]- mean_displ1)/heights[idx]

					#add to data
					sheet_corners.append(max_corner)
					sheet_centers.append(max_center)
		#data
		drifts.append(sheet_corners)
		drifts.append(sheet_centers)	

	insert_query = 'INSERT INTO structure_max_drift_per_floor (MaxDriftCornerX, MaxDriftCornerY, MaxDriftCenterX, MaxDriftCenterY, Units) VALUES (%s,%s,%s,%s,%s)'
	values = (json.dumps(drifts[0]), json.dumps(drifts[2]), json.dumps(drifts[1]), json.dumps(drifts[3]), units)
	cursor.execute(insert_query,values)
	print('structure_max_drift_per_floor table updated correctly!\n')

def structure_relative_displacements(units = 'm'):
	displacements = pd.read_excel('displacements.xlsx',sheet_name = None)
	sheet_names = list(displacements.keys())
	matrixes = []

	for sheet_name in sheet_names:
		pd.options.display.float_format = '{:.2E}'.format
		df = displacements[sheet_name].dropna()
		timeseries = df.iloc[:,0].to_list()
		timeseries = [int(round(valor,2)) for valor in timeseries if round(valor,2) % 1 == 0]
		timeseries = json.dumps(timeseries)
		df = df.iloc[:, 1:].copy()

		optimized_matrix = {}
		matrix = df.to_dict()
		for keys, vals in matrix.items():
			optimized_matrix[keys] = {k: v for k, v in vals.items() if (int(k)+1) % 40 == 0}
		values = []
		for vals in optimized_matrix.values():
			sublist = list(vals.values())
			values.append(sublist)
		values = [[float(val) for val in sublist] for sublist in values]
		matrixes.append(json.dumps(values))
	insert_query =	'INSERT INTO structure_relative_displacements (TimeSeries, DispX, DispY, DispZ, Units) VALUES(%s,%s,%s,%s,%s)'
	values = (timeseries,matrixes[0],matrixes[1],matrixes[2],units)
	cursor.execute(insert_query, values)	
	print('structure_relative_displacements table updated correctly!\n')

def structure_abs_acceleration(units = 'm/s/s'):
	accelerations = pd.read_excel('accelerations.xlsx',sheet_name = None)
	sheet_names = list(accelerations.keys())
	matrixes = []

	#nombre archivos
	folder = os.path.basename(os.getcwd())
	east = open(os.path.join(f'{folder}e.txt'))
	north = open(os.path.join(f'{folder}n.txt'))
	vertical = open(os.path.join(f'{folder}z.txt'))

	acc_e = []
	acc_n = []
	acc_z = []

	for i in east:
		acc_e.append(float(i.split('\n')[0]))
	for i in north:
		acc_n.append(float(i.split('\n')[0]))
	for i in vertical:
		acc_z.append(float(i.split('\n')[0]))
	acc = [acc_e,acc_n,acc_z]
	counter = 0
	# manipulación de dataframe
	for sheet_name in sheet_names:
		df = accelerations[sheet_name].dropna()
		timeseries = df.iloc[:,0].to_list()
		timeseries = [int(round(valor,2)) for valor in timeseries if round(valor,2) % 1 == 0]
		timeseries = json.dumps(timeseries)
		df = df.iloc[:, 1:].copy()
		for column in df.columns:
			df.loc[:,column] += acc[counter][0:2000]
		df = df.applymap(lambda x: ('{:.2e}'.format(x)))
		
		#OPTIMIZING RESULTS
		optimized_matrix = {}
		matrix = df.to_dict()
		for keys, vals in matrix.items():
			optimized_matrix[keys] = {k: v for k, v in vals.items() if (int(k)+1) % 40 == 0}
		values = []
		for vals in optimized_matrix.values():
			sublist = list(vals.values())
			values.append(sublist)
		values = [[float(val) for val in sublist] for sublist in values]
		matrixes.append(json.dumps(values))
		counter +=1

	insert_query = 'INSERT INTO structure_abs_acceleration (TimeSeries, AbsAccX, AbsAccY, AbsAccZ, Units) VALUES(%s,%s,%s,%s,%s)'
	values = (timeseries, matrixes[0], matrixes[1], matrixes[2], units)
	cursor.execute(insert_query, values)		
	print('structure_abs_acceleration table updated correctly!\n')

def sm_input_pga(units = 'm/s/s'):
	folder = os.path.basename(os.getcwd())
	npz = os.path.join('..',f'{folder}.npz')
	nu = 0.05
	tmax = 50.

	s = Station()
	s.load(npz)
	z,e,n,t = s.get_response()
	z = z[t<tmax]
	e = e[t<tmax]
	n = n[t<tmax]
	t = t[t<tmax]

	az = np.gradient(z,t)
	ae = np.gradient(e,t)
	an = np.gradient(n,t)

	PGA_max_z = az.argmax()
	PGA_max_e = ae.argmax()
	PGA_max_n = an.argmax()
	PGA_min_n = an.argmin()
	PGA_min_z = az.argmin()   
	PGA_min_e = ae.argmin()
		
	PGAx = json.dumps({'max':round(ae[PGA_max_e],2),'min':round(ae[PGA_min_e],2)})
	PGAy = json.dumps({'max':round(an[PGA_max_n],2),'min':round(an[PGA_min_n],2)})
	PGAz = json.dumps({'max':round(az[PGA_max_z],2),'min':round(az[PGA_min_z],2)})
	
	insert_query = 'INSERT INTO sm_input_pga (PGA_X, PGA_Y, PGA_Z, Units) VALUES(%s,%s,%s,%s)'
	values = (PGAx, PGAy, PGAz, units)
	cursor.execute(insert_query, values)
	cnx.commit()
	print('sm_input_pga table updated correctly!\n')

def sm_input_spectrum(units = 'm/s/s'):
	folder = os.path.basename(os.getcwd())
	npz = os.path.join('..',f'{folder}.npz')
	nu = 0.05
	tmax = 50.
	dt = np.linspace(0,1.,2000)
	dt = np.delete(dt,0)
	w = np.zeros(len(dt))

	for i in range(len(dt)):
		if dt[i] != 0.:    
			w[i] = 2*np.pi/dt[i]
		
	#SPECTRUM VERTICAL
	s = Station()
	s.load(npz)
	z,e,n,t = s.get_response()
	z = z[t<tmax] 
	t = t[t<tmax]
	az = np.gradient(z,t).tolist()
	Spaz = []

	for j in range(len(w)):
		wi = w[j]
		u_z,v_z = pwl(az,wi,nu)
		Saz = max(max(u_z),(abs(min(u_z))))*wi**2
		Spaz.append(Saz)

	#SPECTRUM EAST
	s = Station()
	s.load(npz)
	z,e,n,t = s.get_response()
	e = e[t<tmax]
	t = t[t<tmax]
	ae = np.gradient(e,t).tolist()
	Spe = []

	for j in range(len(w)):
		wi = w[j]
		u_x,v_x = pwl(ae,wi,nu)
		Sae = max(max(u_x),(abs(min(u_x))))*wi**2
		Spe.append(Sae)

	#SPECTRUM NORTH
	s = Station()
	s.load(npz)
	z,e,n,t = s.get_response()
	n = n[t<tmax]
	t = t[t<tmax]
	an = np.gradient(n,t).tolist()
	Spn = []

	for j in range(len(w)):
		wi = w[j]
		u_y,v_y = pwl(an,wi,nu)
		San = max(max(u_y),(abs(min(u_y))))*wi**2
		Spn.append(San)

	insert_query = 'INSERT INTO sm_input_spectrum(SpectrumX, SpectrumY, SpectrumZ, Units) VALUES (%s,%s,%s,%s)'
	values = (json.dumps(Spe), json.dumps(Spn), json.dumps(Spaz), units)
	cursor.execute(insert_query, values)
	cnx.commit()
	print('sm_input_spectrum table updated correctly!\n')

def pwl(vector_a,w,chi): #retorna la integral de p(t) entre 0 y vectort[-1] por el método de Trapecio
	#print("Piese wise linear")   
	
	#variables 
	h = 0.005
	u_t = [0.]
	up_t = [0.]
	upp_t = [0.]
	m = 1
	w_d = w*np.sqrt(1-chi**2) #1/s 
	
	sin = np.sin(w_d*h)
	cos = np.cos(w_d*h)
	e = np.exp(-chi*w*h)
	raiz = np.sqrt(1-chi**2)
	división = 2*chi/(w*h)
	
	A = e * (chi*sin/raiz+cos) #check
	B = e * (sin/w_d) #check
	C = (1/w**2) * (división  + e * (((1 - (2*chi**2))/(w_d*h) - chi/raiz)*sin - (1+división)*cos)) #check
	D = (1/w**2) * (1-división + e * ((2*chi**2-1)*sin/(w_d*h)+división*cos)) #check
	
	A1 = -e * ((w*sin)/raiz) #check
	B1 =  e * ( cos - chi*sin/raiz  ) #check
	C1 = (1/w**2) * (- 1/h + e*((w/raiz + chi/(h*raiz) ) * sin + cos/h)) #check 
	D1 = (1/w**2) * (1/h - (e/h*( chi*sin/raiz + cos   ))) #check
	
	vector_a.insert(0,0)
	
	for i in range(len(vector_a)-1):
		pi = -(vector_a[i])*m#pi
		pi1 = -(vector_a[i+1])*m #pi+1
		
		ui = u_t[i] #u_i(t)
		vi = up_t[i] #v_i(t)
		ui1 = A*ui + B*vi + C*pi + D*pi1 #u_i+1
		upi1 = A1*ui + B1*vi + C1*pi + D1*pi1 #up_i+1 
		
		u_t.append(ui1)
		up_t.append(upi1)
		
	vector_a.pop(0)
	u_t.pop(0)
	up_t.pop(0)

	return u_t,up_t

def get_sm_id():
	path = os.path.dirname(os.path.abspath(__file__)).split('\\')
	magnitude = path[-3][-3:]
	rupture = path[-2][-4:]
	station = int(path[-1][-1])+1

	if magnitude == '6.5':
		m = 0
	elif magnitude == '6.7':
		m = 90
	elif magnitude == '6.9':
		m = 180
	elif magnitude == '7.0':
		m = 270

	if rupture[0:2] == 'bl':
		r = (int(rupture[-1])-1)*10
	elif rupture[0:2] == 'ns':
		r = (int(rupture[-1])-1)*10 + 30
	elif rupture[0:2] == 'sn':
		r = (int(rupture[-1])-1)*10 +60
		
	id = m+r+station
	return id

def model_linearity():
	insert_query = 'INSERT INTO model_linearity(Type) VALUES (%s)' 
	values = ('Linear',)
	cursor.execute(insert_query,values)
	insert_query = 'INSERT INTO model_linearity(Type) VALUES (%s)'
	values = ('Non Linear',)
	cursor.execute(insert_query,values)
	cnx.commit()
	print('model_linearity created correctly!\n')

def simulation_type():
	insert_query = 'INSERT INTO simulation_type(Type) VALUES (%s)' 
	values = ('Fix Base Model',)
	cursor.execute(insert_query,values)
	insert_query = 'INSERT INTO simulation_type(Type) VALUES (%s)'
	values = ('Soil Structure Interaction Model',)
	cursor.execute(insert_query,values)
	cnx.commit()
	print('simulation_type created correctly!\n')

def espectro433(S,Ao,R,I,To,p):
	T = np.linspace(0,3,2000)
	Sah = np.zeros(2000)
	Sav = np.zeros(2000)

	for i in range(2000):
		tn = T[i]
		alpha = (1 + 4.5*(tn/To)**p)/(1 +(tn/To)**3)
		Sah[i] = S*Ao*alpha/(R/I)
		Sav[i] = 2/3 * S*Ao*alpha/(R/I)
	Sah = np.delete(Sah,0)
	Sav = np.delete(Sav,0)
	return T,Sah,Sav

def plotDrift(driftx, drifty, stories,title):
	plt.plot(driftx,stories)
	plt.plot(drifty,stories)
	plt.yticks(range(1, len(stories)+1))  # Rango del eje y de 1 a 20
	plt.ylabel('Story')
	plt.xlabel('Drift')
	plt.title(title)
	plt.legend(['Drift X', 'DriftY'])
	# Establecer el formato de porcentaje en el eje y
	plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
	plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

	plt.axvline(x=0.007, color='r', linestyle='--')
	plt.grid()
	plt.show()

def plotFileSpectrum(fileX,fileY,fileZ):
	S = 0.9
	To = 0.15 #[s]
	p = 2
	Ao = 0.3*9.81  
	I = 1.2
	R = 1
	T,Sah_433,Sav_433 = espectro433(S,Ao,R,I,To,p)


	plt.figure(figsize=(23.54,13.23),dpi=108)
	nu = 0.05
	dt = T
	dt = np.delete(dt,0)
	w = np.zeros(len(dt))

	for i in range(len(dt)):
		if dt[i] != 0.:    
			w[i] = 2*np.pi/dt[i]

	with open(fileZ) as filez:
		dataz = filez.read()
	dataz = dataz.split('\n')
	dataz.pop(-1)
	dataz.pop(-1)
	az = [float(acce) for acce in dataz]
	Spaz = []
	for j in range(len(w)):
		wi = w[j]
		u_z,v_z = pwl(az,wi,nu)
		Saz = max(max(u_z),(abs(min(u_z))))*wi**2
		Spaz.append(Saz)

	plt.plot(dt, Sav_433,'k--',label='NCh433')
	plt.plot(dt,Spaz,'-',label='Record 6.5BL1S4 Vertical', color = 'blue')
	
	y433 = np.interp(2.4, dt, Sav_433)
	year = np.interp(2.4, dt, Spaz)
	plt.scatter(2.4, y433, color='black', label=f'Value for T=2.4: Spa={round(y433,2)}')
	plt.scatter(2.4, year, color='blue', label=f'Value for T=2.4: Spa={round(year,2)}')
	plt.plot([2.4,2.4],[0,y433], '--r')
	plt.text(2.4, y433+.1,f"({2.4},{y433:.2f})")
	plt.text(2.4, year+.1,f"({2.4},{year:.2f})")
	plt.title('Spa Vertical')
	plt.xlabel('Period T [s]')
	plt.ylabel('Acceleration [m/s/s]')
	plt.legend()
	plt.grid()
	plt.show()

	plt.figure(figsize=(23.54,13.23),dpi=108)
	with open(fileX) as filex:
		datax = filex.read()
	datax = datax.split('\n')
	datax.pop(-1)
	datax.pop(-1)
	ae = [float(acce) for acce in datax]
	Spe = []
	for j in range(len(w)):
		wi = w[j]
		u_x,v_x = pwl(ae,wi,nu)
		Sae = max(max(u_x),(abs(min(u_x))))*wi**2
		Spe.append(Sae)
	with open(fileY) as filey:
		datay = filey.read()
	datay = datay.split('\n')
	datay.pop(-1)
	datay.pop(-1)
	an = [float(acce) for acce in datay]
	Spn = []
	for j in range(len(w)):
		wi = w[j]
		u_y,v_y = pwl(an,wi,nu)
		San = max(max(u_y),(abs(min(u_y))))*wi**2
		Spn.append(San)
 
	y433 = np.interp(2.4, dt, Sah_433)
	year1 = np.interp(2.4,dt,Spe)
	year2 = np.interp(2.4,dt,Spn)
	plt.scatter(2.4, y433, color='black', label=f'Value for x = 2.4: Spa={round(y433,2)}')
	plt.scatter(2.4, year1, color='blue', label=f'Value for x = 2.4: Spa={round(year1,2)}')
	plt.scatter(2.4, year2, color='orange', label=f'Value for x = 2.4: Spa={round(year2,2)}')
	plt.plot([2.4,2.4],[0,y433],'--r')

	plt.plot(dt, Sah_433,'k--',label = 'NCh433')
	plt.plot(dt,Spe,'-',label='Registro 6.5BL1S4 Este' ,color='blue')
	plt.plot(dt,Spn,'-',label='Registro 6.5BL1S4 Norte',color='orange')
	plt.title('Spa Horizontal')
	plt.xlabel('Period T [s]')
	plt.ylabel('Acceleration [m/s/s]')
	plt.legend()
	plt.grid()
	plt.show()

def plotFileAccelerations(fileX,fileY,fileZ):
	time = np.arange(0,50,0.025) #len = 2000 

	with open(fileX) as filex:
		datax = filex.read()
	datax = datax.split('\n')
	datax.pop(-1)
	datax.pop(-1)
	datax = [float(acce) for acce in datax]
	
	with open(fileY) as filey:
		datay = filey.read()
	datay = datay.split('\n')
	datay.pop(-1)
	datay.pop(-1)
	datay = [float(acce) for acce in datay]
 
	with open(fileZ) as filez:
		dataz = filez.read()
	dataz = dataz.split('\n')
	dataz.pop(-1)
	dataz.pop(-1)
	dataz = [float(acce) for acce in dataz]

	plt.plot(time,datax)
	plt.plot(time,datay)
	plt.plot(time,dataz,'--')
 
 
	plt.legend(['East','North','Vertical'])
	plt.title('Earthquake')
	plt.ylabel('Acceleration[m/s/s]')
	plt.xlabel('Time[s]')
	plt.grid()
	plt.tight_layout()
	plt.show()

def plotInputSpectrum(input1,input2,input3,label1='',label2='',label3='',nch433=False,title='',option='', fourier=False) :
	S = 0.9
	To = 0.15 #[s]
	p = 2
	Ao = 0.3*9.81  
	I = 1.2
	R = 1
	T,Sah_433,Sav_433 = espectro433(S,Ao,R,I,To,p)
	nu = 0.05
	dt = T
	dt = np.delete(dt,0)
	w = np.zeros(len(dt))
	for i in range(len(dt)):
		if dt[i] != 0.:    
			w[i] = 2*np.pi/dt[i]

	if fourier==True:
		w = np.delete(w,np.s_[0:139])
		fft_result1 = np.fft.fft(input1)
		fft_result2 = np.fft.fft(input2)
		fft_result3 = np.fft.fft(input3)
		amplitude_spectrum1 = np.abs(fft_result1)
		amplitude_spectrum2 = np.abs(fft_result2)
		amplitude_spectrum3 = np.abs(fft_result3)
		amplitude_spectrum1 = np.delete(amplitude_spectrum1,np.s_[0:140])
		amplitude_spectrum2 = np.delete(amplitude_spectrum2,np.s_[0:140])
		#plt.loglog(w,amplitude_spectrum1,label=label1)
		#plt.loglog(w,amplitude_spectrum2,label=label2)
		plt.loglog(w,amplitude_spectrum3,label=label3)
		plt.yscale('log')
		plt.xlabel('Frequency w [Hz]')
		plt.ylabel('Log Acceleration [m/s/s]')
	else:
		plt.figure(figsize=(23.54,13.23),dpi=108)

		i1 = []
		for j in range(len(w)):
			wi = w[j]
			u_x,v_x = pwl(input1,wi,nu)
			Sae = max(max(u_x),(abs(min(u_x))))*wi**2
			i1.append(Sae)
		i2 = []
		for j in range(len(w)):
			wi = w[j]
			u_y,v_y = pwl(input2,wi,nu)
			San = max(max(u_y),(abs(min(u_y))))*wi**2
			i2.append(San)
		i3 = []
		for j in range(len(w)):
			wi = w[j]
			u_y,v_y = pwl(input3,wi,nu)
			San = max(max(u_y),(abs(min(u_y))))*wi**2
			i3.append(San)

		if nch433 == True:
			plt.plot(dt, Sah_433,'k--',label = 'NCh433')
		if option == 'loglog':
			plt.loglog(dt,i1,'-',label=label1 ,color='blue')
			plt.loglog(dt,i2,'-',label=label2,color='orange')
			plt.loglog(dt,i3,'-',label=label3,color='red')
		elif option == '':
			plt.plot(dt,i1,'-',label=label1 ,color='blue')
			plt.plot(dt,i2,'-',label=label2,color='orange')
			plt.plot(dt,i3,'-',label=label3,color='red')
		plt.xlabel('Period T [s]')
		plt.ylabel('Acceleration [m/s/s]')
	plt.title(title)
	plt.legend()
	plt.grid()
	plt.show()

# def get_story_nodes(level=int)
# 	story = list(list(stories_nodes.values())[-1].keys())
# 


def spectralRatio():
	coordenates, drift_nodes,stories_nodes, stories, subs, heights = give_coords_info()
	level0 = list(next(iter(stories_nodes.values())).keys()) #get base nodes as list
	roof = list(list(stories_nodes.values())[-1].keys()) #get roof nodes as list
	print(level0)
	print(roof)
	#access to RELATIVE accelerations 
	accelerations = pd.read_excel('accelerations.xlsx',sheet_name = None)
	sheet_names = list(accelerations.keys())
	matrixes = []

	#acces to INPUT accelerations 
	folder = os.path.basename(os.getcwd())
	east = open(os.path.join(f'{folder}e.txt'))
	north = open(os.path.join(f'{folder}n.txt'))
	vertical = open(os.path.join(f'{folder}z.txt'))

	acc_e = []
	acc_n = []
	acc_z = []

	for i in east:
		acc_e.append(float(i.split('\n')[0]))
	for i in north:
		acc_n.append(float(i.split('\n')[0]))
	for i in vertical:
		acc_z.append(float(i.split('\n')[0]))
	acc = [acc_e,acc_n,acc_z]
	counter = 0
	#acces to ABSOLUTE acceleration (abs acce = input + relative)
	for sheet_name in sheet_names[0:2]:
		print(sheet_name)
		df = accelerations[sheet_name].dropna()
		timeseries = df.iloc[:,0].to_list()
		timeseries = [int(round(valor,2)) for valor in timeseries if round(valor,2) % 1 == 0]
		timeseries = json.dumps(timeseries)
		df = df.iloc[:, 1:].copy()
		for column in df.columns:
			df.loc[:,column] += acc[counter][0:2000]
		df1 = df.copy()
		df2 = df.copy()
		df_level0 = df1.filter(items = level0)
		df_roof = df2.filter(items = roof)
		df_level0['Mean']=df_level0.mean(axis=1)
		df_roof['Mean']=df_roof.mean(axis=1)  
		level0_spectrum = df_level0['Mean'].tolist()
		roof_spectrum = df_roof['Mean'].tolist()
		ratio = (df_roof['Mean']/df_level0['Mean']).dropna().tolist()
		print(f'{ratio=}')
		plotInputSpectrum(level0_spectrum,
			roof_spectrum,
			ratio,
			'Base Spectrum',
			'Roof Spectrum', 
			'Roof/Base Spectrum',
			title=f'Fourier Spectrum | {sheet_name}',
			fourier=True)
		counter +=1
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

