#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conversion tool for StreamLine .hpl files into netCDF
  
hpl_to_netcdf(file_path,path_out)
data_temp=hpl2dict(file_path)
   
NetCDF files will be stored in 
path_out\level0\lidar_id\yyyy\yyyymm\yyyymmdd\file_name.nc

--> structure equals structure on lidar systems
"""
import numpy as np
from netCDF4 import Dataset
import os
from datetime import datetime

#function imports .hpl file and stores information in dictionary data_temp
def hpl2dict(file_path):
    #import hpl files into intercal storage
    with open(file_path, 'r') as text_file:
        lines=text_file.readlines()
    
    #write lines into Dictionary
    data_temp=dict()
    
    header_n=17 #length of header
    data_temp['filename']=lines[0].split()[-1]
    data_temp['system_id']=int(lines[1].split()[-1])
    data_temp['number_of_gates']=int(lines[2].split()[-1])
    data_temp['range_gate_length_m']=float(lines[3].split()[-1])
    data_temp['gate_length_pts']=int(lines[4].split()[-1])
    data_temp['pulses_per_ray']=int(lines[5].split()[-1])
    data_temp['number_of_waypoints_in_file']=int(lines[6].split()[-1])
    rays_n=(len(lines)-header_n)/(data_temp['number_of_gates']+1)
    if not rays_n.is_integer():
        raise Exception('Number of lines does not match expected format')
    data_temp['no_of_rays_in_file']=int(rays_n)
    data_temp['scan_type']=' '.join(lines[7].split()[2:])
    data_temp['focus_range']=lines[8].split()[-1]
    data_temp['start_time']=' '.join(lines[9].split()[-2:])
    data_temp['resolution']=('%s %s' % (lines[10].split()[-1],'m s-1'))
    data_temp['range_gates']=np.arange(0,data_temp['number_of_gates'])
    data_temp['center_of_gates']=(data_temp['range_gates']+0.5)*data_temp['range_gate_length_m']
    
    #dimensions of data set
    gates_n=data_temp['number_of_gates']
    rays_n=data_temp['no_of_rays_in_file']
    
    #keys for measurement variables are predefined as symetric numpy arrays filled with NaN values
    data_temp['radial_velocity']=np.full([gates_n,rays_n],np.nan) #m/s
    data_temp['intensity']=np.full([gates_n,rays_n],np.nan) #SNR+1
    data_temp['beta']=np.full([gates_n,rays_n],np.nan) #m-1 sr-1
    data_temp['elevation']=np.full(rays_n,np.nan) #degrees
    data_temp['azimuth']=np.full(rays_n,np.nan) #degrees
    data_temp['decimal_time']=np.full(rays_n,np.nan) #hours
    data_temp['pitch']=np.full(rays_n,np.nan) #degrees
    data_temp['roll']=np.full(rays_n,np.nan) #degrees
    for ri in range(0,rays_n): #loop through rays
        lines_temp=lines[header_n+(ri*gates_n)+ri+1:header_n+(ri*gates_n)+gates_n+ri+1]
        header_temp=np.asarray(lines[header_n+(ri*gates_n)+ri].split(),dtype=float)
        data_temp['decimal_time'][ri]=header_temp[0]
        data_temp['azimuth'][ri]=header_temp[1]
        data_temp['elevation'][ri]=header_temp[2]
        data_temp['pitch'][ri]=header_temp[3]
        data_temp['roll'][ri]=header_temp[4]
        for gi in range(0,gates_n): #loop through range gates
            line_temp=np.asarray(lines_temp[gi].split(),dtype=float)
            data_temp['radial_velocity'][gi,ri]=line_temp[1]
            data_temp['intensity'][gi,ri]=line_temp[2]
            data_temp['beta'][gi,ri]=line_temp[3]    
        
    return data_temp

#write Dictionary into netCDF file
def hpl_to_netcdf(file_path,path_out=None):
    
    #check if file exists
    if not os.path.exists(file_path):
        raise Exception('%s cannot be found' %os.path.basename(file_path))
    
    data_temp=hpl2dict(file_path)
    
    # create output directory if non-existant
    if path_out==None:
        current_folder_path, current_folder_name = os.path.split(os.getcwd())
        path_out=current_folder_path
          
    
    
    #NetCDF files will be stored in folder structure which equals the structure on the Lidar systems
    # path_out\level0\lidar_id\yyyy\yyyymm\yyyymmdd\file_name.nc
    datestr=[fns for fns in data_temp['filename'].split('_') if len(fns)==8][0]
    path_out_=os.path.join(path_out,'NetCDF','level0',str(data_temp['system_id']),datestr[0:4],datestr[0:6],datestr)
    
    # test if file already exists
    if not os.path.exists(path_out_):
        os.makedirs(path_out_)

    
    path_file=os.path.join(path_out_,data_temp['filename'].split('.')[0]+'_l0.nc')
    if os.path.isfile(path_file):
        raise Exception('%s already exists' % path_file)

    dataset_temp=Dataset(path_file,'w',format ='NETCDF4')
        
    # define dimensions
    dataset_temp.createDimension('NUMBER_OF_GATES',data_temp['number_of_gates'])
    dataset_temp.createDimension('NUMBER_OF_RAYS',data_temp['no_of_rays_in_file'])
    # Metadata
    dataset_temp.description="non-processed data of Halo Photonics Streamline"
#    dataset_temp.institution="University of Innsbruck, Department of Atmospheric and Cryospheric sciences (ACINN), AUSTRIA",
#    dataset_temp.contact="Alexander Gohm, Maren Haid (maren.haid@uibk.ac.at), Lukas Lehner"
    dataset_temp.focus_range='%s m' % data_temp['focus_range']
    dataset_temp.range_gate_length='%i m' % data_temp['range_gate_length_m']
    dataset_temp.pulses_per_ray=data_temp['pulses_per_ray']
    dataset_temp.start_time=data_temp['start_time']
    dataset_temp.system_id=data_temp['system_id']
    dataset_temp.scan_type=data_temp['scan_type']
    dataset_temp.resolution=data_temp['resolution']
    dataset_temp.number_waypoint=data_temp['number_of_waypoints_in_file']
    dataset_temp.history='File created on %s ' % datetime.now().strftime('%d %b %Y %H:%M')
    
    decimal_time=dataset_temp.createVariable('decimal_time', np.float64, ('NUMBER_OF_RAYS'))
    decimal_time.units='decimal time (hours) UTC'
    decimal_time.long_name='start time of each ray'
    decimal_time[:]=data_temp['decimal_time']
    
    azi=dataset_temp.createVariable('azimuth', np.float32, ('NUMBER_OF_RAYS'))
    azi.units='degrees, meteorologically'
    azi.long_name='azimuth angle'
    azi[:]=data_temp['azimuth']
    
    ele=dataset_temp.createVariable('elevation', np.float32, ('NUMBER_OF_RAYS'))
    ele.units='degrees, meteorologically'
    ele.long_name='elevation angle'
    ele[:]=data_temp['elevation']
    
    pitch=dataset_temp.createVariable('pitch', np.float32, ('NUMBER_OF_RAYS'))
    pitch.units='degrees'
    pitch.long_name='pitch angle'
    pitch[:]=data_temp['pitch']
    
    roll=dataset_temp.createVariable('roll', np.float32, ('NUMBER_OF_RAYS'))
    roll.units='degrees'
    roll.long_name='roll angle'
    roll[:]=data_temp['roll']
    
    rv=dataset_temp.createVariable('radial_velocity', np.float32,('NUMBER_OF_GATES','NUMBER_OF_RAYS'))
    rv.units='m s-1'
    rv.long_name='Doppler velocity along line of sight'
    rv[:,:]=data_temp['radial_velocity']

    intensity=dataset_temp.createVariable('intensity', np.float32,('NUMBER_OF_GATES','NUMBER_OF_RAYS'))
    intensity.units='unitless'
    intensity.long_name='SNR + 1'
    intensity[:,:]=data_temp['intensity']
    
    beta=dataset_temp.createVariable('beta', np.float32,('NUMBER_OF_GATES','NUMBER_OF_RAYS'))
    beta.units='m-1 sr-1'
    beta.long_name='attenuated backscatter'
    beta[:,:]=data_temp['beta']
    
    gate_centers=dataset_temp.createVariable('gate_centers',np.float32,('NUMBER_OF_GATES'))
    gate_centers.units='m'
    gate_centers.long_name='center of range gates'
    gate_centers[:]=data_temp['center_of_gates']
    
    dataset_temp.close()
    
    print('%s is created succesfully' % path_file)
    