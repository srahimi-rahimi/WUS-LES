#!/bin/bash
#PBS -N GEOGRID
#PBS -A WYOM0247
#PBS -q main
#PBS -l select=1:ncpus=128:mpiprocs=16
#PBS -l walltime=02:00:00
#PBS -l job_priority=premium
#PBS -j oe

set -euo pipefail

module --force purge
module load ncarenv/23.06
module load intel-classic/2023.0.0
module load hdf5/1.12.2
module load cray-mpich/8.1.25
module load craype/2.7.20
module load netcdf/4.9.2
module load ncarcompilers/1.0.0

# Avoid accidental threaded oversubscription from linked libraries.
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# Keep temporary files away from the shared WPS directory when possible.
export TMPDIR="${TMPDIR:-/tmp}"

echo "Job started: $(date)"
echo "Working directory: ${PBS_O_WORKDIR}"
echo "MPI ranks: 64"

cd "${PBS_O_WORKDIR}"

rm -f geogrid.log.*
rm -f geogrid.out

mpiexec -n 16 ./geogrid.exe > geogrid.out 2>&1

status=$?

echo "Job finished: $(date)"
echo "Exit status: ${status}"

exit "${status}"
