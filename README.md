# Doppler wind lidar toolbox

This toolbox contains modules for 
- data formatting (e.g., `2NetCDF`)
- estimating retrievals from Doppler wind lidar data (e.g., `coplanar_retrieval` and `VAD_retrieval`)
- creating figures of lidar data (e.g., `quicklooks`) 
- writing scan files and scan schedules for the StreamLine (SL) software (`SL_scan_files`). 

**These modules do not constitute any claim with regard to correctness or completeness. Everyone is welcome to contribute and improve.**

## 2NetCDF 
### hpl2NetCDF.py
functions
- `hpl2dict`: import of Halo Photonics .hpl files. Local storage as Python `dictionary`.
- `hpl_to_netcdf`: export of Python `dictionary` as netCDF file. No information is added or removed. Measured profiles of `radial_velocity`, `intensity` and `beta` are stored into two-dimensional variables with dimensions: `NUMBER_OF_GATES`, `NUMBER_OF_RAYS`.  

## colpanar_retrievals
### calc_retrieval.py
Calculation of two-dimensional wind fields from Doppler wind lidar coplanar scans. Coplanar retrievals can be estimated for both: horizontal and vertical plane. Estimateions of the two-dimensional wind field along the vertical plane is based on Range-Height-Indicator (RHI) scans performed with two Doppler wind lidars (dual Doppler lidar). For two-dimensional wind fields along  the horizontal plane, data from Plan-Position-Indicator (PPI) scans is used. The estimation of the horizontal wind field can be done for radial velocity measurements of two or three Doppler wind lidars.  

