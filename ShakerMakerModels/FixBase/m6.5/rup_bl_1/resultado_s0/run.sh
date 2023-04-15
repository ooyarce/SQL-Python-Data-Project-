#!/bin/bash
m=$(basename $(dirname $(dirname $(pwd))) | cut -c 2-)
rup=$(basename $(dirname $(pwd)) | cut -c -5)
result=$(basename $(pwd))
job="${m}_${rup}_${result##*_}"
echo "$job"

#SBATCH --job-name=${job}    # Job name
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --output=${job}.log   # Standard output and error log
pwd; hostname; date

export OMP_NUM_THREADS=1
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/mnt/nfshare/lib
SECONDS = 0
mpirun /mnt/nfshare/bin/openseesmp main.tcl
echo "Elapsed: $SECONDS seconds."
echo "Code finished succesfully."
echo "Ready to import files!"
