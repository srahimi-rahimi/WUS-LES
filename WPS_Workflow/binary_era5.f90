subroutine binary_creator(T,RH,U,V,PHI,ps,pmsl,landmask, &
	     tsoil_total, qsoil_total, &
	     t2, &
	     sst_regrid, seaice_regrid, tskin, z_sfc, &
   	     startlat,startlon,deltalat,deltalon, &
	     lev_p_pa, &
	     year6,month6,day6,hour6, &
             nx,ny,np,n_soil_layers)


IMPLICIT NONE

real, dimension(nx,ny,np), intent(in) :: T, RH, U, V, PHI
real, dimension(nx,ny), intent(in) :: ps, pmsl, t2
real, dimension(nx,ny), intent(in) :: landmask, z_sfc, tskin
real, dimension(nx,ny), intent(in) :: sst_regrid, seaice_regrid
real, dimension(nx,ny,n_soil_layers), intent(in) :: qsoil_total, tsoil_total

real, dimension(np), intent(in) :: lev_p_pa

real, intent(in) :: startlat, startlon, deltalat, deltalon

integer, intent(in) :: nx, ny ,np, n_soil_layers
integer, intent(in) :: year6, month6, day6, hour6

!local variables
character*9, dimension(n_soil_layers) :: qsoil_char, tsoil_char
character*10 :: soil_dummy

character (len=18) :: filename
character (len=32) :: map_source
character (len=8) :: startloc
real :: earth_radius, hour_sum
integer :: input_unit, version
integer :: k
character (len=100) :: format_string
character (len=4) :: yyy
character (len=2) :: mmm, ddd, hh
character (len=24) :: hdate
logical :: is_wind_grid_rel= .FALSE.

tsoil_char = (/"ST000007 ", "ST007028 ", &
                "ST028100 ", "ST100289 " /)

qsoil_char = (/"SM000007 ", "SM007028 ", &
                "SM028100 ", "SM100289 " /)

!Date integers to character
write (yyy,fmt='(i0)') year6

!For month
if (month6 < 10) then
        format_string = "(a,i0)"
        write (mmm,fmt=format_string) '0', month6
else
    	format_string = "(i0)"
        write (mmm,fmt=format_string) month6
endif

!For day
if (day6 < 10) then
        format_string = "(a,i0)"
        write (ddd,fmt=format_string) '0', day6
else
    	format_string = "(i0)"
        write (ddd,fmt=format_string) day6
endif

!For hour
if (hour6 < 10) then
        format_string = "(a,i0)"
        write (hh,fmt=format_string) '0', hour6
else
    	format_string = "(i0)"
        write (hh,fmt=format_string) hour6
endif

map_source = "CAM model BAU                   "
startloc = "SWCORNER"

earth_radius = 6378.135
input_unit = 300
version = 5
hour_sum = 0

!Open the binary file (should be in the form FILE:2016-12-15_18)
filename = 'FILE:'//yyy//'-'//mmm//'-'//ddd//'_'//hh
print*, filename
open (unit=input_unit, file=filename, status='new',&
                form='unformatted',convert='big_endian')

hdate = yyy//':'//mmm//':'//ddd//'_'//hh//':00:00'

!Write variables to binary files
!3-D variables first | must loop over vertical dimension

!201300 is for height of SLP and 200100 is for surface data

do k = 1, np

!----1
      	call write_met_field(input_unit, version, 'TT       ', hdate, &
             hour_sum, lev_p_pa(k), 'K                        ',         &
             'Temperature                                   ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, T(:,:,k),    &
             is_wind_grid_rel)

!----2
      	call write_met_field(input_unit, version, 'UU       ', hdate, &
             hour_sum, lev_p_pa(k), 'm s-1                    ',         &
             'U                                             ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, U(:,:,k),    &
             is_wind_grid_rel)

!----3
      	call write_met_field(input_unit, version, 'VV       ', hdate, &
             hour_sum, lev_p_pa(k), 'm s-1                    ',         &
             'V                                             ', 0,     &
              startloc, startlat, startlon, deltalat, deltalon,          &
             earth_radius, nx, ny, map_source, V(:,:,k),    &
             is_wind_grid_rel)

!----4
      	call write_met_field(input_unit, version, 'RH       ', hdate, &
             hour_sum, lev_p_pa(k), '%                        ',         &
             'Specic Humidity                               ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, RH(:,:,k),  &
             is_wind_grid_rel)

!----5
      	call write_met_field(input_unit, version, 'GHT      ', hdate, &
             hour_sum, lev_p_pa(k), 'm                        ',         &
             'Height                                        ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, PHI(:,:,k),  &
             is_wind_grid_rel)

end do

!2-D variables

!----1
      	call write_met_field(input_unit, version, 'PSFC     ', hdate, &
             hour_sum, 200100., 'Pa                       ',        &
             'Surface Pressure                              ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, ps,	 &
             is_wind_grid_rel)
!----2
      	call write_met_field(input_unit, version, 'PMSL     ', hdate, &
             hour_sum, 201300., 'Pa                       ',        &
             'Sea-level Pressure                            ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, pmsl,        &
             is_wind_grid_rel)

!----3
        call write_met_field(input_unit, version, 'TT       ', hdate, &
             hour_sum, 200100., 'K                        ',        &
             'Temperature at 2m                             ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, t2,         &
             is_wind_grid_rel)

!----5
      	call write_met_field(input_unit, version, 'SST      ', hdate, &
             hour_sum, 200100., 'K                        ',        &
             'Sea-Surface Temperature                       ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, sst_regrid,         &
             is_wind_grid_rel)

!----6
      	call write_met_field(input_unit, version, 'SOILHGT  ', hdate, &
             hour_sum, 200100., '   m                     ',        &
             'Terrain Height                                ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, z_sfc,       &
             is_wind_grid_rel)

!----7
      	call write_met_field(input_unit, version, 'LANDSEA  ', hdate, &
             hour_sum, 200100., '0/1 Flag                 ',        &
             'Land/Sea flag                                 ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, landmask,    &
             is_wind_grid_rel)

!----10
      	call write_met_field(input_unit, version, 'SEAICE   ', hdate, &
             hour_sum, 200100., 'K                        ',        &
             'Sea-Surface Ice Fraction                      ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, seaice_regrid,         &
             is_wind_grid_rel)

!Soil
do k = 1, n_soil_layers

        soil_dummy = qsoil_char(k)//' '

        call write_met_field(input_unit, version, soil_dummy, hdate, &
             hour_sum, 200100., 'fraction                 ',        &
             'Soil Moisture of x-xx cm sub_soil layer       ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, qsoil_total(:,:,k),     &
             is_wind_grid_rel)

        soil_dummy = tsoil_char(k)//' '

        call write_met_field(input_unit, version, soil_dummy, hdate, &
             hour_sum, 200100., 'K                        ',        &
             'Soil Temperature of x-xx cm sub_soil layer      ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, tsoil_total(:,:,k),     &
             is_wind_grid_rel)

end do

!Skin temperature
        call write_met_field(input_unit, version, 'SKINTEMP ', hdate, &
             hour_sum, 200100., 'K                        ',        &
             'Skin Temperature                              ', 0,     &
             startloc, startlat, startlon, deltalat, deltalon,           &
             earth_radius, nx, ny, map_source, tskin,         &
             is_wind_grid_rel)

close(input_unit)

end subroutine binary_creator

subroutine write_met_field(iunits,version, field, hdate, xfcst,   &
             xlvl, units, desc, iproj, startloc, startlat, startlon,    &
             deltalat, deltalon, earth_radius, nx, ny, map_source, slab,   &
             is_wind_grid_rel)

IMPLICIT NONE

integer :: version, nx, ny, iproj, iunits,i,j
real :: xfcst, xlvl, startlat, startlon,  deltalon, dx, dy, earth_radius
real :: deltalat
real, dimension(nx,ny) :: slab
logical :: is_wind_grid_rel
character (len=9), intent(in) :: field
character (len=24), intent(in) :: hdate
character (len=25), intent(in) :: units
character (len=32), intent(in) :: map_source
character (len=46), intent(in) :: desc
character (len=8) :: startloc

!     print*,"startloc,hdate, xfcst, map_source, field, units, desc, xlvl, &
!          nx, ny, iproj"
!     print*,startloc,hdate, xfcst, map_source, field, units, desc, xlvl, &
!          nx, ny, iproj
!      print*, "startloc, startlat, startlon, deltalat, deltalon, earth_radius"
!      print*, startloc, startlat, startlon, deltalat, deltalon, earth_radius
!      print*, is_wind_grid_rel

!  1) WRITE FORMAT VERSION
write(unit=iunits) version

!  2) WRITE METADATA(Cylindrical equidistant)
write(unit=iunits) hdate, xfcst, map_source, field, &
        units, desc, xlvl, nx, ny, iproj

write(unit=iunits) startloc, startlat, startlon,   &
  deltalat, deltalon, earth_radius

!  3) WRITE WIND ROTATION FLAG
write(unit=iunits) is_wind_grid_rel

!  4) WRITE 2D ARRAY OF DATA
write(unit=iunits) slab

return

end subroutine write_met_field
