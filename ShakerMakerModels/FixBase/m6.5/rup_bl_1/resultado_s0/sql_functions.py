import mysql.connector
cnx = mysql.connector.connect(user='root', password='g3drGvwkcmcq', host='localhost', database='stkodatabase')
cursor = cnx.cursor()

def pwl(vector_a,w,chi): #retorna la integral de p(t) entre 0 y vectort[-1] por el método de Trapecio
    #print("Piese wise linear")   
    import numpy as np
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

def model_benchmark():
	#-------------------------------------------------------------------------------------------------------------------------------------
	#THIS FILLS THE MODEL-BENCHMARK TABLE (JobName,SimulationTime,MemoryResults,MemoryModel,ClusterNodes,CpuPerNodes,ClusterName,Comments)|	
	#-------------------------------------------------------------------------------------------------------------------------------------
	#Get calculus time from log file, nodes, threads and comments
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


	#Write some comments
	clustername = 'Esmeralda HPC Cluster by jaabell@uandes.cl'
	comments = 'This is a test model for beta_0.0' #for query

	#------------------------------------------------------------------------------------------------------------------------------------
	#Get MODEL-BENCHMARK from folder read																								|
	#------------------------------------------------------------------------------------------------------------------------------------
	import os
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

	#------------------------------------------------------------------------------------------------------------------------------------
	#write query to put data in table
	insert_query = 'INSERT INTO model_benchmark (JobName,SimulationTime,MemoryResults,MemoryModel,ClusterNodes,CpuPerNodes,ClusterName,Comments) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
	values = (jobname,time,memory_by_results,memory_by_model,nodes,threads,clustername,comments)
	cursor.execute(insert_query, values)
	cnx.commit()	
	print('model_benchmark table updated correctly!\n')

	 
	#------------------------------------------------------------------------------------------------------------------------------------

def structure_base_shear():
	#------------------------------------------------------------------------------------------------------------------------------------
	#THIS FILLS THE STRUCTURE_BASE_SHEAR
	#------------------------------------------------------------------------------------------------------------------------------------
	import pandas as pd
	import json
	Units = 'kN'
	#reactions
	reactions = pd.read_excel('reactions.xlsx', sheet_name = None)
	sheet_names = list(reactions.keys())
	base_shears = []

	for sheet_name in sheet_names:
		df = reactions[sheet_name].iloc[:,1:].dropna()
		timeseries = json.dumps(reactions[sheet_name].iloc[:,0].tolist())
		summ = json.dumps((df.sum(axis = 1).values).tolist())
		base_shears.append(summ)

	insert_query = 'INSERT INTO structure_base_shear (TimeSeries, ShearX, ShearY, ShearZ, Units) VALUES (%s,%s,%s,%s,%s)'
	values = (timeseries, base_shears[0], base_shears[1], base_shears[2], Units)
	cursor.execute(insert_query, values)
	cnx.commit()		
	print('structure_base_shear table updated correctly!\n')

def structure_max_base_shear():
	import pandas as pd 
	import json
	Units = 'kN'
	#reactions
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
	values = (max_shears[0], max_shears[1], max_shears[2],Units)
	cursor.execute(insert_query,values)
	cnx.commit()
	print('structure_max_base_shear table updated correctly!\n')

def structure_max_drift_per_floor():
	import pandas as pd 
	import json
	units = 'm'

	displacements = pd.read_excel('displacements.xlsx', sheet_name = None)
	sheet_name = list(displacements.keys)
	
	drift_corners = []
	drift_centers = []
def structure_relative_displacements():
	#------------------------------------------------------------------------------------------------------------------------------------
	#THIS FILLS THE STRUCTURE_RELATIVE_DISPLACEMENT
	#------------------------------------------------------------------------------------------------------------------------------------
	import pandas as pd
	import json
	units = 'm'
	#displacements
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
 
def structure_abs_acceleration():
	#------------------------------------------------------------------------------------------------------------------------------------
	#THIS FILLS THE RESULTS TABLE (REACTIONS-RELATIVE DISPLACEMENTS - ABSOLUTE ACCELERATIONS)
	#------------------------------------------------------------------------------------------------------------------------------------
	import pandas as pd 
	import json
	import os 
	Units = 'm/s/s'
	#accelerations
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
	values = (timeseries, matrixes[0], matrixes[1], matrixes[2], Units)
	cursor.execute(insert_query, values)
	cnx.commit()		
	print('structure_abs_acceleration table updated correctly!\n')
	
def sm_input_pga():
	from shakermaker import shakermaker
	from shakermaker.station import Station
	from shakermaker.tools.plotting import ZENTPlot,cumulative_trapezoid
	import os
	import numpy as np 
	import json
	Units = 'g'
	folder = os.path.basename(os.getcwd())
	npz = os.path.join('..',f'{folder}.npz')

	spectra = []
	nu = 0.05
	tmax = 50.
	dt = np.linspace(0,1,2000)
	w = np.zeros(len(dt))

	for i in range(len(dt)):
	    if dt[i] != 0:    
	        w[i] = 2*np.pi/dt[i]

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


	PGA_max_e = ae.argmax()
	PGA_min_e = ae.argmin()

	PGA_max_n = an.argmax()
	PGA_min_n = an.argmin()

	PGA_max_z = az.argmax()
	PGA_min_z = az.argmin()   
	    
	PGAx = json.dumps({'max':str(PGA_max_e),'min':str(PGA_min_e)})
	PGAy = json.dumps({'max':str(PGA_max_n),'min':str(PGA_min_n)})
	PGAz = json.dumps({'max':str(PGA_max_z),'min':str(PGA_min_z)})
	
	insert_query = 'INSERT INTO sm_input_pga (PGA_X, PGA_Y, PGA_Z, Units) VALUES(%s,%s,%s,%s)'
	values = (PGAx, PGAy, PGAz, Units)
	cursor.execute(insert_query, values)
	cnx.commit()
	print('sm_input_pga table updated correctly!\n')

def sm_input_spectrum():
	from shakermaker import shakermaker
	from shakermaker.station import Station
	from shakermaker.tools.plotting import ZENTPlot,cumulative_trapezoid
	import numpy as np
	import os 
	import json
	Units = 'm/s/s'
	nu = 0.05
	tmax = 50.
	dt = np.linspace(0,1.,2000)
	dt = np.delete(dt,0)
	w = np.zeros(len(dt))

	for i in range(len(dt)):
	    if dt[i] != 0.:    
	        w[i] = 2*np.pi/dt[i]
	    
	folder = os.path.basename(os.getcwd())
	npz = os.path.join('..',f'{folder}.npz')


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
	values = (json.dumps(Spe), json.dumps(Spn), json.dumps(Spaz), Units)
	cursor.execute(insert_query, values)
	cnx.commit()
	print('sm_input_spectrum table updated correctly!\n')