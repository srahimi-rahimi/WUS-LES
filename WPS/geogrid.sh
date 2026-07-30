#!/bin/bash
#PBS -N GEOGRID
#PBS -l select=1:ncpus=32:mpiprocs=32
#PBS -l walltime=02:00:00
#PBS -A WYOM0247
#PBS -j oe
#PBS -q main
#PBS -l job_priority=premium

module --force purge
module load ncarenv/23.06
module load intel-classic/2023.0.0
module load hdf5/1.12.2
module load cray-mpich/8.1.25
module load ncview/2.1.8
module load craype/2.7.20
module load netcdf/4.9.2
module load ncarcompilers/1.0.0 

mpiexec ./geogrid.exe  > geogrid.out
