import os

# Define el nombre del archivo y la ruta completa
Magnitude = (os.path.dirname(__file__).split('/')[-3][1:])
Rup_type = os.path.dirname(__file__).split('/')[-2].split('_')[1]
iteration = os.path.dirname(__file__).split('/')[-2].split('_')[2]
station = int(os.path.dirname(__file__).split('/')[-1][-1])
jobname = f'2s{Magnitude}_{Rup_type}{iteration}_s{station}'
logname = f'Fix_{jobname}.log'

with open('run.sh', 'w') as f:
        f.write(f"""#!/bin/bash
#SBATCH --job-name={jobname}    # Job name
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --output={logname}   # Standard output and error log
pwd; hostname; date

export OMP_NUM_THREADS=1
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/mnt/nfshare/lib
SECONDS=0
mpirun /mnt/nfshare/bin/openseesmp main.tcl
echo "Elapsed: $SECONDS seconds."
echo "Code finished succesfully."
echo "Ready to import files!"
""")
