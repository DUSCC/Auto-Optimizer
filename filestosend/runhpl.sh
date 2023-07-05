#!/bin/bash

# Request resources:
#SBATCH -n 128
#SBATCH -N 1
#SBATCH -t 00:15:00
#SBATCH -p test
#SBATCH --output=auto-opt/out/HPL.out

module purge
module load aocc/3.2.0 openmpi/4.1.3 openblas/0.3.18

mpirun -np 128 $PWD/auto-opt/build/bin/xhpl