# Doppler wind lidar toolbox

This toolbox contains modules for 
- data formatting (e.g., `2NetCDF`)
- estimating retrievals from Doppler wind lidar data (e.g., `coplanar_retrieval` and `VAD_retrieval`)
- creating figures of lidar data (e.g., `quicklooks`) 
- writing scan files and scan schedules for the StreamLine (SL) software (`SL_scan_files`). 

## 2NetCDF 
This directory contains modules for the convertion of Doppler wind lidar data into netCDF. 

- `hpl2NetCDF.py`: data formatting of StreamLine .hpl files into level 0 (l0) .nc files and convertion from l0 .nc files into corrected level 1 (l1) .nc files.

- `vad2NetCDF.py`: write daily .nc files of retrieved vertical profiles of horizontal wind. 

## colpanar_retrievals
Calculation of two-dimensional wind fields from Doppler wind lidar coplanar scans. 
- `calc_retrieval.py`:  coplanar retrievals can be estimated for both: horizontal and vertical plane. Estimateions of the two-dimensional wind field along the vertical plane is based on Range-Height-Indicator (RHI) scans performed with two Doppler wind lidars (dual Doppler lidar). For two-dimensional wind fields along  the horizontal plane, data from Plan-Position-Indicator (PPI) scans is used. The estimation of the horizontal wind field can be done for radial velocity measurements of two or three Doppler wind lidars.  

## VAD_retrieval
Retrive vertical profiles of horizontal wind from radial velocities. 

- `calc_vad.py`: two different methods are used to retrieve the horizontal wind. 

## quicklooks
Scripts to create figures of raw data or retrieved variables. 

- `plot_vad.py`: time-height diagrams of horizontal wind.

## SL_scanfiles
Writing .txt files which can be used in the StreamLine (SL) software to perform different scan pattern and scan scenarios

- `write_scan_file.py`: creating scan files for various scan pattern like RHI and PPI scans. 

- `write_dss_example.py`: write daily scan scedule (dss) for example scan secanio.




