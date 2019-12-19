# Doppler wind lidar

Script collection for Doppler wind lidar scripts.

## 2NetCDF 
### hpl2NetCDF.py
functions
- `hpl2dict`: import of Halo Photonics .hpl files. Local storage as Python `dictionary`.
- `hpl_to_netcdf`: export of Python `dictionary` as netCDF file. No information is added or removed. Measured profiles of `radial_velocity`, `intensity` and `beta` are stored into two-dimensional variables with dimensions: `NUMBER_OF_GATES`, `NUMBER_OF_RAYS`.  

## colpanar_retrievals
### calc_retrieval.py
Calculation of two-dimensional wind fields from Doppler wind lidar coplanar scans. Coplanar retrievals can be estimated for both: horizontal and vertical plane. Estimateions of the two-dimensional wind field along the vertical plane is based on Range-Height-Indicator (RHI) scans performed with two Doppler wind lidars (dual Doppler lidar). For two-dimensional wind fields along  the horizontal plane, data from Plan-Position-Indicator (PPI) scans is used. The estimation of the horizontal wind field can be done for radial velocity measurements of two or three Doppler wind lidars.  

