#!/bin/bash

#SBATCH --job-name=memory_seff
#SBATCH --partition=cpu
#SBATCH -n 1
#SBATCH --output=%j.out
#SBATCH --error=%j.err

cd ..
./efficiency_seff.sh memory