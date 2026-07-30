#Pparralellize's WPS
#Modified beautifully by Lei Huang on 24 April 2025

#Updates the namelist.wps and submission
#template

import subprocess as sb
import os
import shutil

run = False

#WPS located in
dir = "/glade/derecho/scratch/srahimi/wrf480/"

#binaries located in
binary_dir = "/glade/derecho/scratch/srahimi/ERA5/Qbinaries/binary_files/"

cur_dir = dir
met_em_dir = dir+'met_em_files'
if not os.path.exists(met_em_dir):
    os.makedirs(met_em_dir)

year1, year2 = 2013, 2026

# ------------ if you only want to run things; WPS_* already
# ------------ created

if run == True:
 for count, iyear in enumerate(range(year1,year2+1)):

    dir_new = dir+"WPS_%s" %("{0:0=2d}".format(iyear))
    os.chdir(dir_new)

    print (dir_new)

    os.system("qsub metgrid.sh")

    #Return to the parent codes directory
    os.chdir(cur_dir)

 exit()

bogey = 'xxx'

# ------------ Create WPS* directories

for count, iyear in enumerate(range(year1,year2+1)):
    os.chdir(dir)

    # Create directories
    dir_new = dir+"WPS_%s" %("{0:0=2d}".format(iyear))
    directive = "cp -R %s%s %s" %(dir,"WPS",dir_new)
    print (dir_new)
    os.system(directive)

    os.chdir(dir_new)

    # Link binaries
    for iiyear in range(iyear,iyear+2):
        directive = "ln -sf %sFILE:%s* ./" %(binary_dir,iiyear)
        os.system(directive)

    # Update the namelist.wps file
    file_orig = cur_dir+"template_WPS"

    fo = open(file_orig,"r")
    lines_old = fo.readlines()

    new_file = "namelist.wps"
    fnew_namelist = open(dir_new+"/"+new_file,"w")

    # Set the start and end time
    startd_str = " start_date  = '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00',\n" %(iyear,iyear,iyear,iyear,iyear,iyear)
    if iyear == 2099:
        endd_str = " end_date  = '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00', '%s-08-01_00:00:00',\n" %(iyear+1,iyear+1,iyear+1,iyear+1,iyear+1,iyear+1)
    else:
        endd_str = " end_date  = '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00',  '%s-08-01_00:00:00', '%s-08-01_00:00:00',\n" %(iyear+1,iyear+1,iyear+1,iyear+1,iyear+1,iyear+1)

    for jj in lines_old:
        if not jj.startswith(" start_date ") and not jj.startswith(" end_date "):
            fnew_namelist.writelines(jj)
        if jj.startswith(" start_date "):
            fnew_namelist.writelines(startd_str)
        if jj.startswith(" end_date "):
            fnew_namelist.writelines(endd_str)

    fnew_namelist.close()
    fo.close()

    #Update the submission script
    file_orig = cur_dir+"template_metgrid"

    foo = open(file_orig,"r")
    lines_old = foo.readlines()

    new_file = "metgrid.sh"
    fnew_metgrid = open(dir_new+"/"+new_file,"w")

    for line in lines_old:
      if bogey in line:
        newline = line.replace(bogey,str(iyear))
        fnew_metgrid.writelines(newline)
      else:
        fnew_metgrid.writelines(line)

    fnew_metgrid.close()
    foo.close()

    #Return to the parent codes directory
    os.chdir(cur_dir)
