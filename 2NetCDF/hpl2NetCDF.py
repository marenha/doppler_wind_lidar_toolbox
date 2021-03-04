#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conversion tool for StreamLine .hpl files into netCDF

hpl_to_netcdf(file_path,path_out=None,instituation=None,contact=None)
    data_temp=hpl2dict(file_path)
NetCDF files will be stored in
path_out\level0\lidar_id\yyyy\yyyymm\yyyymmdd\file_name.nc

--> structure equals structure on lidar systems
"""
import numpy as np
from netCDF4 import Dataset
import os
import datetime
import xarray as xr
import matplotlib.dates as mdates

'''
import of .hpl files and return data as dictionary;
in newer versions of the StreamLine software, the spectral width can be 
stored as additional parameter; in case, the spectral width is not included
in the .hpl file, the item "spectral_width" is filled with NaNs
'''
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
    
    '''
    number of lines does not math expected format if the number of gates 
    changed in the measuring period of the data file
    '''
    if not rays_n.is_integer():
        print('Number of lines does not match expected format')
        return np.nan
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

    # item of measurement variables are predefined as symetric numpy arrays filled with NaN values
    data_temp['radial_velocity'] = np.full([gates_n,rays_n],np.nan) #m s-1
    data_temp['intensity'] = np.full([gates_n,rays_n],np.nan) #SNR+1
    data_temp['beta'] = np.full([gates_n,rays_n],np.nan) #m-1 sr-1
    data_temp['spectral_width'] = np.full([gates_n,rays_n],np.nan)
    data_temp['elevation'] = np.full(rays_n,np.nan) #degrees
    data_temp['azimuth'] = np.full(rays_n,np.nan) #degrees
    data_temp['decimal_time'] = np.full(rays_n,np.nan) #hours
    data_temp['pitch'] = np.full(rays_n,np.nan) #degrees
    data_temp['roll'] = np.full(rays_n,np.nan) #degrees
    for ri in range(0,rays_n): #loop through rays
        lines_temp = lines[header_n+(ri*gates_n)+ri+1:header_n+(ri*gates_n)+gates_n+ri+1]
        header_temp = np.asarray(lines[header_n+(ri*gates_n)+ri].split(),dtype=float)
        data_temp['decimal_time'][ri] = header_temp[0]
        data_temp['azimuth'][ri] = header_temp[1]
        data_temp['elevation'][ri] = header_temp[2]
        data_temp['pitch'][ri] = header_temp[3]
        data_temp['roll'][ri] = header_temp[4]
        for gi in range(0,gates_n): #loop through range gates
            line_temp=np.asarray(lines_temp[gi].split(),dtype=float)
            data_temp['radial_velocity'][gi,ri] = line_temp[1]
            data_temp['intensity'][gi,ri] = line_temp[2]
            data_temp['beta'][gi,ri] = line_temp[3]
            if line_temp.size>4:
                data_temp['spectral_width'][gi,ri] = line_temp[4]

    return data_temp

'''
write .hpl into netCDF l0 data; no data is added, changed or removed;
infromation about institution and contact are optional; 
'''
def hpl_to_netcdf(file_path,path_out,institution=None,contact=None,overwrite=False):
    #check if import file exists
    if not os.path.exists(file_path):
        print('%s cannot be found' %os.path.basename(file_path))
        return
    
    # import data as dictionary
    data_temp = hpl2dict(file_path)
    if type(data_temp) is not dict: return
    
    '''
    Level0 netCDF files will be stored in folder structure which equals the 
    structure on the StreamLine software
    path_out\level0\lidar_id\yyyy\yyyymm\yyyymmdd\file_name.nc
    '''
    datestr=[fns for fns in data_temp['filename'].split('_') if len(fns)==8][0]
    path_out_date=os.path.join(path_out, datestr[0:4], datestr[0:6], datestr)
    # test if file already exists
    if not os.path.exists(path_out_date):
        os.makedirs(path_out_date)

    file_name_out = data_temp['filename'].split('.')[0]+'_l0.nc'
    path_file = os.path.join(path_out_date,file_name_out)
    if os.path.isfile(path_file):
        if overwrite == False:
            raise Exception('%s already exists' % path_file)
        else:
            os.remove(path_file)

    dataset_temp = Dataset(path_file,'w',format ='NETCDF4')
    # define dimensions
    dataset_temp.createDimension('NUMBER_OF_GATES',data_temp['number_of_gates'])
    dataset_temp.createDimension('NUMBER_OF_RAYS',data_temp['no_of_rays_in_file'])
    # Metadata
    dataset_temp.description = "non-processed data of Halo Photonics Streamline"
    if institution:
        dataset_temp.institution = institution
    if contact:
        dataset_temp.contact = contact
    dataset_temp.focus_range = '%s m' % data_temp['focus_range']
    dataset_temp.range_gate_length = '%i m' % data_temp['range_gate_length_m']
    dataset_temp.pulses_per_ray = data_temp['pulses_per_ray']
    dataset_temp.start_time = data_temp['start_time']
    dataset_temp.system_id = data_temp['system_id']
    dataset_temp.scan_type = data_temp['scan_type']
    dataset_temp.resolution = data_temp['resolution']
    dataset_temp.number_waypoint = data_temp['number_of_waypoints_in_file']
    dataset_temp.history = 'File created on %s ' % datetime.datetime.now().strftime('%d %b %Y %H:%M')
    
    decimal_time = dataset_temp.createVariable('decimal_time', np.float64, ('NUMBER_OF_RAYS'))
    decimal_time.units = 'decimal time (hours) UTC'
    decimal_time.long_name = 'start time of each ray'
    decimal_time[:] = data_temp['decimal_time']
    
    azi = dataset_temp.createVariable('azimuth', np.float32, ('NUMBER_OF_RAYS'))
    azi.units = 'degrees, meteorologically'
    azi.long_name = 'azimuth angle'
    azi[:] = data_temp['azimuth']
    
    ele = dataset_temp.createVariable('elevation', np.float32, ('NUMBER_OF_RAYS'))
    ele.units = 'degrees, meteorologically'
    ele.long_name = 'elevation angle'
    ele[:] = data_temp['elevation']
    
    pitch = dataset_temp.createVariable('pitch_angle', np.float32, ('NUMBER_OF_RAYS'))
    pitch.units = 'degrees'
    pitch.long_name = 'pitch angle'
    pitch[:] = data_temp['pitch']
    
    roll = dataset_temp.createVariable('roll_angle', np.float32, ('NUMBER_OF_RAYS'))
    roll.units = 'degrees'
    roll.long_name = 'roll angle'
    roll[:] = data_temp['roll']
    
    rv = dataset_temp.createVariable('radial_velocity', np.float32,('NUMBER_OF_GATES','NUMBER_OF_RAYS'))
    rv.units = 'm s-1'
    rv.long_name = 'Doppler velocity along line of sight'
    rv[:,:] = data_temp['radial_velocity']

    intensity = dataset_temp.createVariable('intensity', np.float32,('NUMBER_OF_GATES','NUMBER_OF_RAYS'))
    intensity.units = 'unitless'
    intensity.long_name = 'SNR + 1'
    intensity[:,:] = data_temp['intensity']
    
    beta = dataset_temp.createVariable('beta', np.float32,('NUMBER_OF_GATES','NUMBER_OF_RAYS'))
    beta.units = 'm-1 sr-1'
    beta.long_name = 'attenuated backscatter'
    beta[:,:] = data_temp['beta']
    
    gate_centers = dataset_temp.createVariable('gate_centers',np.float32,('NUMBER_OF_GATES'))
    gate_centers.units = 'm'
    gate_centers.long_name = 'center of range gates'
    gate_centers[:] = data_temp['center_of_gates']
    dataset_temp.close()
    print('%s is created succesfully' % path_file)

'''
convert level0 netCDF data into level1 data
input variables:
    file_path       - string
    file_name_out   - string
    lidar_info      - class lidar_location(lat,lon,zsl,name,lidar_id,bearing,gc_corr,pulse_frequency,start_str,end_str,diff_WGS84=np.nan,diff_geoid=np.nan,diff_bessel=np.nan)
    path_out        - string
The lidar_info variables needs the 
'''
def to_netcdf_l1(file_path,file_name_out,lidar_info,path_out):
    
    ds_temp=xr.open_dataset(file_path)
    
    if not os.path.exists(path_out): os.makedirs(path_out)
                    
    ds_temp.azimuth.values=ds_temp.azimuth.values-lidar_info.bearing
    ds_temp.azimuth.attrs['comment']='corrected azimuth angle (az_corrected=az_measured-bearing) --> az_corrected = 0 deg points to geographical North'
    if lidar_info.bearing!=0:
        ds_temp.attrs['description']='corrected data of Halo Photonics Streamline, corrected variables: azimuth'
    elif lidar_info.gc_corr!=0 and lidar_info.bearing!=0:
        ds_temp.attrs['description']='corrected data of Halo Photonics Streamline, corrected variables: azimuth, gate_centers'
    elif lidar_info.gc_corr==0 and lidar_info.bearing==0:
        ds_temp.attrs['description']='corrected data of Halo Photonics Streamline, corrected variables: none'
             
    lat_var=xr.Variable([],lidar_info.lat,\
                        attrs={'units':'decimal degree north',\
                                'long_name':'latitude',\
                                'description':'latitude, north is positive',\
                                'missing_value':-999.})
    ds_temp=ds_temp.assign(lat=lat_var)
    
    lon_var=xr.Variable([],lidar_info.lon,\
                        attrs={'units':'decimal degrees east',\
                                'long_name':'longitude',\
                                'description':'longitude, east is positive',\
                                'missing_value':-999.})
    ds_temp=ds_temp.assign(lon=lon_var)
    
    
    zsl_var=xr.Variable([],lidar_info.zsl,\
                        attrs={'units':'m',\
                                'long_name':'altitude',\
                                'description':'Height above mean sea leval, Gebrauchshoehe Adria; Transformation to other references is possible by using the additive factor supplied in the fields \"difference_to_geoid\", \"difference_to_bessel\" and \"difference_to_WGS84\", which are added as a list of values, with each entry corresponging to one station, e.g. zsl[1]+zsl.differenve_to_geoid[1] = height above Geoid for the first station',\
                                'missing_value':-999.,\
                                'difference_to_geoid':lidar_info.diff_geoid,\
                                'difference_to_geoid_descr':'Difference between zsl and height above geoid for each STATION_KEY, e.g. zsl[1] + zsl.difference_to_geoid[1] = Height above Geoid in m',\
                                'difference_to_bessel':lidar_info.diff_bessel,\
                                'difference_to_bessel_descr':'Difference between zsl and height above Bessel 1841 reference ellipsoid for geodetic datum MGI for each STATION_KEY; e.g. zsl[1] + zsl.difference_to_bessel[1] = Height above Bessel ellipsoid in m',\
                                'difference_to_WGS84':lidar_info.diff_WGS84,\
                                'difference_to_WGS_descr':'Difference between zsl and height above WGS84 reference ellipsoid  for each STATION_KEY, e.g., zsl[1] + zsl.difference_to_WGS84[1] = Height above WGS84 ellispoid'})
    ds_temp=ds_temp.assign(zsl=zsl_var)
    
    bearing_var=xr.Variable([],lidar_info.bearing,\
                        attrs={'units':'degrees',\
                                'long_name':'angle of bearing offset',\
                                'description':'angle between the theoretical position of North direction in projected plane (epsg:31254) and North alignment of the instrument: bearing = North_lidar - North_projected ',\
                                'missing_value':-999.})
    ds_temp=ds_temp.assign(bearing=bearing_var)

    dec_time_temp=ds_temp.decimal_time.values
    
    # if data from the next day is collected
    import sys
    if dec_time_temp[-1]<dec_time_temp[0]:
        sys.exit()
    
    date_num=mdates.datestr2num(ds_temp.start_time.split()[0])
    dn_time_temp=date_num+dec_time_temp/24
    date_time=mdates.num2date(dn_time_temp)
    unix_time=[(dt- datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc)).total_seconds() for dt in date_time]
    
    dn_time_temp_var=xr.Variable(['NUMBER_OF_RAYS'],dn_time_temp,\
                        attrs={'units': 'Days since 01-01-0001 00:00:00',\
                                'long_name':'start time number of each ray'})
    ds_temp=ds_temp.assign(datenum_time=dn_time_temp_var)
    
    dt_time_temp_var=xr.Variable(['NUMBER_OF_RAYS'],unix_time,\
                        attrs={'units': 'Seconds since 01-01-1970 00:00:00',\
                                'long_name':'start time number of each ray',\
                                'description':'UNIX timestamp'})
    ds_temp=ds_temp.assign(time=dt_time_temp_var)
       
    path_out_temp = os.path.join(path_out,file_name_out)

    if os.path.isfile(path_out_temp): os.remove(path_out_temp)
    
    ds_temp.to_netcdf(path_out_temp)
    ds_temp.close()