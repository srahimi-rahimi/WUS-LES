#Created by S. Rahimi on 18 Dec 2025 by S. Rahimi
#to dyanmically create intermediate bianries for
#ERA5 (isobaric inputs)

###################################################
###################################################
###################################################
###################################################

#For TGW experiments
#Only works for a single month at a time!!!

###################################################
###################################################
###################################################
###################################################

#Run by month and year in parallel; these data are big
#f2py3.7 -c binary_era5.f90 -m binary_era5

import xarray as xr
import numpy as np
import gc
import os
import matplotlib.pyplot as P
import pandas as pd
import datetime
import xesmf as xe
import warnings
import dask
import glob
import time

warnings.simplefilter(action='ignore', category=FutureWarning)

def _readERA5(var,ncvar,dir,start_date):

    import dask
    dask.config.set(**{'array.slicing.split_large_chunks': True})
    #This is the ERA5 data reader. Only selects
    #a narrow window of files
    year, month = start_date.split("-")[0], start_date.split("-")[1]
    
    sub_dir = dir+str(year)+month+'/'+'*%s*nc' %(var)
   
    files = sorted(glob.glob(sub_dir))

    data = xr.open_mfdataset(files,
         #chunks=100,
         chunks={'latitude': -1, 'longitude': -1,'level': -1, 'time': 1},
         cache=False,
         decode_times=True,
         parallel=True,
         combine='by_coords').sel(longitude=slice(lon_min_master,lon_max_master),
                        latitude=slice(lat_max_master,lat_min_master) )
    
    data = data.reindex(latitude=list(reversed(data.latitude)))

    data = data.sel(time= \
                         (data.time.dt.hour == 0) |
                         (data.time.dt.hour == 6) |
                         (data.time.dt.hour == 12) |
                         (data.time.dt.hour == 18)
                            )
    print (ncvar)
    return(data[ncvar])

def _prep4fortran_real(array):

    #Preps the data for the fortran subroutine
    #and WRF metgrid.exe

    bad = -99999
    array = array.fillna(bad)
    return (np.array(array,dtype=float,order='F'))

start_date = "2024-10-01 00"
end_date = "2024-10-02 06"

delta = -1.3
dir_binaries = './pi/'

#Only foocus on the northern and western hemispher
lat_min_master, lat_max_master = 0, 60
lon_min_master, lon_max_master = 0, 360

#Constants that are used in calculations
g = 9.81
T0 = 273.15
rho_w = 1000.
Rd = 287.
p0 = 101325

#6-hourly files

dir = '/glade/campaign/collections/rda/data/d633000/e5.oper.an.pl/'

var, ncvar = '_u.', 'U'
u = _readERA5(var,ncvar,dir,start_date)

var, ncvar = '_v.', 'V'
v = _readERA5(var,ncvar,dir,start_date)

var, ncvar = '_t.', 'T'
t = _readERA5(var,ncvar,dir,start_date) + delta

var, ncvar = '_z.', 'Z'
z = _readERA5(var,ncvar,dir,start_date) / 9.81

var, ncvar = '_q.', 'Q'
rh = _readERA5(var,ncvar,dir,start_date)

#2-D
dir = "/glade/campaign/collections/rda/data/d633000/e5.oper.an.sfc/"
var, ncvar = '_sp.', 'SP'
ps = _readERA5(var,ncvar,dir,start_date)

var, ncvar = '_msl.', 'MSL'
psl = _readERA5(var,ncvar,dir,start_date)

var, ncvar = '_stl1.', 'STL1'
tsoil1 = _readERA5(var,ncvar,dir,start_date) + delta

var, ncvar = '_stl2.', 'STL2'
tsoil2 = _readERA5(var,ncvar,dir,start_date) + delta

var, ncvar = '_stl3.', 'STL3'
tsoil3 = _readERA5(var,ncvar,dir,start_date) + delta

var, ncvar = '_stl4.', 'STL4'
tsoil4 = _readERA5(var,ncvar,dir,start_date) + delta

var, ncvar = '_swvl1.', 'SWVL1'
qsoil1 = _readERA5(var,ncvar,dir,start_date)

var, ncvar = '_swvl2.', 'SWVL2'
qsoil2 = _readERA5(var,ncvar,dir,start_date)

var, ncvar = '_swvl3.', 'SWVL3'
qsoil3 = _readERA5(var,ncvar,dir,start_date)

var, ncvar = '_swvl4.', 'SWVL4'
qsoil4 = _readERA5(var,ncvar,dir,start_date)

var, ncvar = '_sstk.', 'SSTK'
sst = _readERA5(var,ncvar,dir,start_date) + delta

var, ncvar = '_skt.', 'SKT'
tskin = _readERA5(var,ncvar,dir,start_date) + delta

var, ncvar = '_ci.', 'CI'
seaice = _readERA5(var,ncvar,dir,start_date)

#Soil height
z_sfc = xr.open_dataset( \
    '/glade/campaign/collections/rda/data/d633000/e5.oper.invariant/197901/e5.oper.invariant.128_129_z.ll025sc.1979010100_1979010100.nc').Z.isel(time=0)
z_sfc = z_sfc.sel(longitude=slice(lon_min_master,lon_max_master),
                        latitude=slice(lat_max_master,lat_min_master) ) / g
z_sfc = z_sfc.reindex(latitude=list(reversed(z_sfc.latitude)))

startlat = np.min(ps.latitude.values)
startlon = np.min(ps.longitude.values)

#Grid spacing
deltalon = np.mean( np.diff(ps.longitude) )
deltalat = np.mean( np.diff(ps.latitude) )

print ("ERA5", start_date,end_date)
print ("lat/lon grid spacing",deltalat,deltalon)
print ("starting lat/lon is", startlat,startlon)

gc.collect()

import binary_era5

#One less as we are considering a 1-month start and end date
master_time = pd.date_range(start=start_date.split("_")[0], \
                            end=end_date.split("_")[0], \
                            freq='6H')[:-1]

#Loop through times
for itime in master_time:
    
    time6 = str(itime)
    time6 = time6[0:13]
    time24 = time6[0:10]

    year_str, month_str, day_str, hour_str = time6[0:4], \
    time6[5:7], time6[8:10], time6[11:13]
    #print ('%s-%s-%s %sz' %(year_str,month_str,day_str,hour_str))

    FILE_str = "FILE:%s-%s-%s_%s" %(year_str,month_str,day_str,hour_str)
    
    u_era5 = u.sel(time=time6).transpose('longitude','latitude','level').load()
    v_era5 = v.sel(time=time6).transpose('longitude','latitude','level').load()
    t_era5 = t.sel(time=time6).transpose('longitude','latitude','level').load()
    rh_era5 = rh.sel(time=time6).transpose('longitude','latitude','level').load()
    z_era5 = z.sel(time=time6).transpose('longitude','latitude','level').load()

    t2_era5 = t_era5.sel(level=1000).transpose('longitude','latitude').load()
    u10_era5 = u_era5.sel(level=1000).transpose('longitude','latitude').load()
    v10_era5 = v_era5.sel(level=1000).transpose('longitude','latitude').load()
    rh2_era5 = rh_era5.sel(level=1000).transpose('longitude','latitude').load()
    rh2_era5 = xr.where(rh2_era5>=0,rh2_era5,0)

    lev_p_pa = u_era5.level * 100.

    ps_era5 = ps.sel(time=time6).transpose('longitude','latitude').load()
    psl_era5 = psl.sel(time=time6).transpose('longitude','latitude').load()
    
    tsoil1_era5 = tsoil1.sel(time=time6).transpose('longitude','latitude').load()
    tsoil2_era5 = tsoil2.sel(time=time6).transpose('longitude','latitude').load()
    tsoil3_era5 = tsoil3.sel(time=time6).transpose('longitude','latitude').load()
    tsoil4_era5 = tsoil4.sel(time=time6).transpose('longitude','latitude').load()

    tsoil_era5 = xr.concat([tsoil1_era5,tsoil2_era5,tsoil3_era5,tsoil4_era5],dim='depth')
    tsoil_era5 = tsoil_era5.transpose('longitude','latitude','depth').load()
    tsoil_era5['depth'] = np.arange(1,5)

    qsoil1_era5 = qsoil1.sel(time=time6).transpose('longitude','latitude').load()
    qsoil2_era5 = qsoil2.sel(time=time6).transpose('longitude','latitude').load()
    qsoil3_era5 = qsoil3.sel(time=time6).transpose('longitude','latitude').load()
    qsoil4_era5 = qsoil4.sel(time=time6).transpose('longitude','latitude').load()

    qsoil_era5 = xr.concat([qsoil1_era5,qsoil2_era5,qsoil3_era5,qsoil4_era5],dim='depth')
    qsoil_era5 = qsoil_era5.transpose('longitude','latitude','depth').load()
    qsoil_era5['depth'] = np.arange(1,5)
    
    tskin_era5 = tskin.sel(time=time6).transpose('longitude','latitude').load()
    sst_era5 = sst.sel(time=time6).transpose('longitude','latitude').load()
    seaice_era5 = seaice.sel(time=time6).transpose('longitude','latitude').load()
    z_sfc_era5 = z_sfc.transpose('longitude','latitude').load()
        
    landmask = xr.where(np.isnan(sst_era5),1,0)
    
    #Prep for subroutine
    t_era5 = _prep4fortran_real (t_era5)
    u_era5 = _prep4fortran_real (u_era5)
    v_era5 = _prep4fortran_real (v_era5)
    rh_era5 = _prep4fortran_real (rh_era5)
    z_era5 = _prep4fortran_real (z_era5)
    
    t2_era5 = _prep4fortran_real (t2_era5)
    rh2_era5 = _prep4fortran_real (rh2_era5)
    u10_era5 = _prep4fortran_real (u10_era5)
    v10_era5 = _prep4fortran_real (v10_era5)

    ps_era5 = _prep4fortran_real (ps_era5)
    psl_era5 = _prep4fortran_real (psl_era5)
    
    tsoil_era5 = _prep4fortran_real (tsoil_era5)
    qsoil_era5 = _prep4fortran_real (qsoil_era5)
    
    tskin_era5 = _prep4fortran_real (tskin_era5)
    sst_era5 = _prep4fortran_real (sst_era5)
    seaice_era5 = _prep4fortran_real (seaice_era5)
    
    landmask = _prep4fortran_real (landmask)
    z_sfc_era5 = _prep4fortran_real (z_sfc_era5)
    
    #Write to subrouting (29 in total)
    #f2py3.7 -c binary_era5.f90 -m binary_era5
    binary_era5.binary_creator(t_era5,rh_era5,u_era5,v_era5,z_era5,
             ps_era5,psl_era5,landmask,
             tsoil_era5,qsoil_era5,
             t2_era5,u10_era5,v10_era5,rh2_era5,
             sst_era5, seaice_era5, tskin_era5, z_sfc_era5,
             startlat,startlon,deltalat,deltalon,
             lev_p_pa.values,
             int(year_str),int(month_str),int(day_str),int(hour_str)
                  )

    directive = 'mv %s %s' %(FILE_str,dir_binaries)
    os.system(directive)
    
gc.collect()
