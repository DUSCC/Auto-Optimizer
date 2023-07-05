#!/bin/bash

# Request resources:
#SBATCH -n 8
#SBATCH -N 1
#SBATCH -t 00:15:00
#SBATCH -p test
#SBATCH --output=auto-opt/deleteme

module purge
module load aocc/3.2.0 openmpi/4.1.3 openblas/0.3.18

./configure --prefix=$PWD/auto-opt/build

make clean
make -j8
make install -j8

rm $PWD/auto-opt/deleteme