from shakermaker.tools.plotting import ZENTPlot,cumulative_trapezoid
from shakermaker.station import Station
from shakermaker import shakermaker
from Results.check_nodes import *

import mysql.connector
import pandas as pd
import numpy as np
import json	
import os

cnx = mysql.connector.connect(user='root', password='g3drGvwkcmcq', host='localhost', database='stkodatabase')
cursor = cnx.cursor()

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

def simulation(sm_input_comments = 'No comments',pga_units = 'm/s/s', resp_spectrum = 'm/s/s', type = 1, stage = 'No stage yet', options='No options yet',sim_comments = 'No comments',model_name = 'FixBaseV3', model_comments = 'No comments', bs_units='kN', abs_acc_units='m/s/s', rel_displ_units='m', max_bs_units='kN', max_drift_units='m', perf_comments = 'No comments',  linearity = 1, specs_comments = 'No comments', clustername = 'Esmeralda HPC Cluster by jaabell@uandes.cl',bench_comments = 'No comments'):
	simulation_model()
	Model = cursor.lastrowid
	simulation_sm_input()

def simulation_sm_input(sm_input_comments = 'No comments',pga_units = 'm/s/s', resp_spectrum = 'm/s/s'): #this functions should be modified acording to the format of 
	#get magnitude
	Magnitude = (os.path.dirname(__file__).split('/')[-3])

	#get rupture type
	Rup_type = os.path.dirname(__file__).split('/')[-2].split('_')[1]
	if Rup_type == 'bl':
		rupture = 'Bilateral'
	elif Rup_type == 'ns':
		rupture = 'North-South'
	elif Rup_type == 'sn':
		rupture = 'South-North'
	else:
		raise TypeError('Folders name are not following the format rup_[bl/ns/sn]_[iteration].')

	#get realization id
	iteration = Rup_type = os.path.dirname(__file__).split('/')[-2].split('_')[2]
	
	#get location
	station = int(os.path.dirname(__file__).split('/')[-1][-1])
	if station >= 0 and station <= 3:
		location = 'Near field'
	elif station >= 4 and station <=6:
		location = 'Intermediate field'
	elif station >= 7 and statio <=9:
		location = 'Far field'
	
	#PGA y Spectrum
	sm_input_pga()
	PGA = cursor.lastrowid
	sm_input_spectrum()
	Spectrum = cursor.lastrowid

	insert_query = 'INSERT INTO simulation_sm_input(idPGA, idSpectrum, Magnitude, Rupture_type, Location, RealizationID, Comments) VALUES(%s,%s,%s,%s,%s,%s,%s)'
	values = (PGA, Spectrum, Magnitude, rupture, location, iteration, sm_input_comments)
	cursor.execute(insert_query,values)
	cnx.commit()
	print('simulation_sm_input table updated correctly!\n')



def simulation_model(model_name = '', model_comments = '', bs_units='', abs_acc_units='', rel_displ_units='', max_bs_units='', max_drift_units='', perf_comments = '',  linearity = 1, specs_comments = '', clustername = '',bench_comments = ''):
	model_benchmark(clustername,bench_comments)
	Benchmark = cursor.lastrowid
	model_structure_perfomance(bs_units,abs_acc_units,rel_displ_units,max_bs_units,max_drift_units,perf_comments)
	StructurePerfomance = cursor.lastrowid
	model_specs_structure(linearity,specs_comments)
	SpecsStructure = cursor.lastrowid

	insert_query = 'INSERT INTO simulation_model(idBenchmark, idStructuralPerfomance, idSpecsStructure, ModelName, Comments) VALUES(%s,%s,%s,%s,%s)'
	values = (Benchmark,StructurePerfomance,SpecsStructure,model_name,comments)
	cursor.execute(insert_query,values)
	cnx.commit()
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
	model_name = 'FixBaseV3.scd'
	memory_by_model = f'{os.path.getsize(model_name)/(1024*1024):.2f} Mb' #this value goes for query

	insert_query = 'INSERT INTO model_benchmark (JobName,SimulationTime,MemoryResults,MemoryModel,ClusterNodes,CpuPerNodes,ClusterName,Comments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
	values = (jobname,time,memory_by_results,memory_by_model,nodes,threads,clustername,comments)
	cursor.execute(insert_query, values)
	cnx.commit()	
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
	cnx.commit()		
	print('model_structure_perfomance table updated correctly!\n')

def model_specs_structure(linearity = 1, comments = ''):
	if linearity < 1 or linearity > 2:
		raise TypeError('The Linearity parameter can only take the values of 1 or 2.')  

	nnodes, nelements = give_info()
	coordenates, drift_nodes,histories_nodes, histories, subs, heights = give_coords_info()

	insert_query = 'INSERT INTO model_specs_structure (idLinearity, Nnodes, Nelements, Nhistories, Nsubs, InterstoryHeight, Comments) VALUES (%s,%s,%s,%s,%s,%s,%s)'
	values = (linearity, nnodes, nelements,histories,subs, json.dumps(heights), comments) #mta and fas vars has to change
	cursor.execute(insert_query, values)
	cnx.commit()		
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
	cnx.commit()		
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
	cnx.commit()
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
	cnx.commit()
	print('structure_max_drift_per_floor table updated correctly!\n')

def structure_relative_displacements(units = 'm'):
	displacements = pd.read_excel('displacements.xlsx',sheet_name = None)
	sheet_names = list(displacements.keys())
	matrixes = []

	for sheet_name in sheet_names:
		pd.options.display.float_format = '{:.2E}'.format
		df = displacements[sheet_name].dropna()
		timeseries = json.dumps(df.iloc[:,0].to_list())
		my_dic = {}

		for i, row in df.iterrows():
			sub_dict = {}
			for col in df.columns[1:]:
				sub_dict[col] = float('{:.1E}'.format(row[col]))
			my_dic[i+1] = sub_dict

		my_dic = json.dumps(my_dic)
		matrixes.append(my_dic)

	insert_query =	'INSERT INTO structure_relative_displacements (TimeSeries, DispX, DispY, DispZ, Units) VALUES(%s,%s,%s,%s,%s)'
	values = (timeseries,matrixes[0],matrixes[1],matrixes[2],units)
	cursor.execute(insert_query, values)
	cnx.commit()		
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

	# manipulación de dataframe
	for sheet_name in sheet_names:
		if sheet_name == 'Accelerations East':
			df = accelerations[sheet_name].dropna()
			timeseries = json.dumps(df.iloc[:,0].to_list())
			df = df.iloc[:, 1:].copy()
			for column in df.columns:
				df.loc[:,column] += acc_e
			df = df.applymap(lambda x: ('{:.2e}'.format(x)))
			matrixes.append(json.dumps(df.to_dict()))

		elif sheet_name == 'Accelerations North':
			df = accelerations[sheet_name].dropna()
			df = df.iloc[:, 1:].copy()
			for column in df.columns:
				df.loc[:,column] += acc_n
			df = df.applymap(lambda x: ('{:.2e}'.format(x)))
			matrixes.append(json.dumps(df.to_dict()))
					
		elif sheet_name == 'Accelerations Vertical':
			df = accelerations[sheet_name].dropna()
			df = df.iloc[:, 1:].copy()
			for column in df.columns:
				df.loc[:,column] += acc_z
			df = df.applymap(lambda x: ('{:.2e}'.format(x)))
			matrixes.append(json.dumps(df.to_dict()))

	insert_query = 'INSERT INTO structure_abs_acceleration (TimeSeries, AbsAccX, AbsAccY, AbsAccZ, Units) VALUES(%s,%s,%s,%s,%s)'
	values = (timeseries, matrixes[0], matrixes[1], matrixes[2], units)
	cursor.execute(insert_query, values)
	cnx.commit()		
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
	w = np.zeros(len(dt))

	for i in range(len(dt)):
	    if dt[i] != 0:    
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