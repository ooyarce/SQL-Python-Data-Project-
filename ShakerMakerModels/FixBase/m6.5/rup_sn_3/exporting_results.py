from shakermaker import shakermaker
from shakermaker.station import Station
from shakermaker.tools.plotting import ZENTPlot
from scipy.integrate import cumulative_trapezoid
import numpy as np 

nu = 0.05
tmax = 50.

files = [
    "resultado_s0.npz",
    "resultado_s1.npz",
    "resultado_s2.npz",
    "resultado_s3.npz",
    "resultado_s4.npz",
    "resultado_s5.npz",
    "resultado_s6.npz",
    "resultado_s7.npz",
    "resultado_s8.npz",
    "resultado_s9.npz"]

names = []

for f in files:
    names.append(f[:12]+'z.txt')
    names.append(f[:12]+'e.txt')
    names.append(f[:12]+'n.txt')

text_files = [open(name,"w") for name in names]

counter = 0
for i in range(len(files)):
    
    s = Station()
    s.load(files[i])
    z,e,n,t = s.get_response()

    z = z[t<tmax]
    e = e[t<tmax]
    n = n[t<tmax]
    t = t[t<tmax]

    az = np.gradient(z,t)
    ae = np.gradient(e,t)
    an = np.gradient(n,t)


    for j in range(len(z)):
        text_files[counter].write(f'{az[j]}\n')
        text_files[counter+1].write(f'{ae[j]}\n')
        text_files[counter+2].write(f'{an[j]}\n')
        
    counter += 3



    

    
    
