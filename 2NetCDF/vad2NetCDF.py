# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 19:41:18 2021

@author: Maren
"""
import numpy as np
from netCDF4 import Dataset
import os
from datetime import date
import xarray as xr
import matplotlib.dates as mdates

'''
Define class for retrieved data of vertical profiles of horizontal wind
Input:
    dn in days      - time in matplotlib.dates
    gz in m         - height above lidar
    (u,v,w) in m/s  - components of 3D wind vector
    ws in m/s       - wind speed
    wd in deg       - wind direction
    rv_fluc in m/s  - deviation of radial velocity from homogenous wind (u,v,w)
    snr in dB       - Averaged Signal-to-Noise ratio
    el_deg in deg   - Elevation angle of scan
    an              - number of used azimuth angles
    range_gate_length in m - range gate length of scan
    snr_threshold   - used Signal-to-Noise ratio for data filtering
'''
class vad():
    def __init__(self,dn,gz,u,v,w,ws,wd,rv_fluc,snr,range_gate_length,snr_threshold,el_deg,an,u_nf,v_nf):
        self.dn = dn 
        self.u, self.v, self.w = u, v, w 
        self.ws, self. wd = ws, wd 
        self.rv_fluc = rv_fluc
        self.snr = snr
        
        self.el_deg = el_deg
        self.an = an
        self.range_gate_length = range_gate_length
        self.snr_threshold = snr_threshold
        
        self.u_nf, self.v_nf = u_nf, v_nf
        
        self.gn = gz.size # number of time stamps
        self.tn = dn.size # number of range gates
        
'''

Input:
    lidar_info  - ditionary containing info of used lidar: lidar_id; lat; lon; alt
    vad         - vad class containing retrieved variables
    path_out    - directory path for output .nc files
'''
def to_netcdf(lidar_info, vad, path_out):
    
    # create output directory if non-existant
    if not os.path.exists(path_out):
        os.makedirs(path_out)  
        
    day_str = mdates.num2datestr(vad.dn[0],'%Y%m%d')
    file_name='%s_%s_vad.nc' %(lidar_info['lidar_id'],day_str)
    file_path=os.path.join(path_out,file_name)

    if os.path.isfile(file_path):
        os.remove(file_path)
    
    dataset_temp=Dataset(file_path,'w',format ='NETCDF4')
    # define dimensions
    dataset_temp.createDimension('NUMBER_OF_GATES',vad.gn)
    dataset_temp.createDimension('NUMBER_OF_SCANS',vad.tn)
    dataset_temp.createDimension('STATION_KEY',1)
    #    dataset_temp.createDimension('TEXT',1)
    
    # Metadata
    dataset_temp.description = "Profiles of horizontal wind speed and direction"
    dataset_temp.institution = "Department of Atmospheric and Cryospheric sciences (ACINN), University of Innsbruck, AUSTRIA",
    dataset_temp.contact = "Alexander Gohm (alexander.gohm@uibk.ac.at),Maren Haid, Lukas Lehner"
    dataset_temp.range_gate_length = vad.range_gate_length
    dataset_temp.system_id = lidar_info['lidar_id']
    dataset_temp.history = 'File created %s by M. Haid' %date.today().strftime('%d %b %Y')
    dataset_temp.lat = lidar_info['lat']
    dataset_temp.lon = lidar_info['lon']
    dataset_temp.alt = lidar_info['lat']
    dataset_temp.snr_threshold = '%.2f dB' %vad.snr_threshold
    dataset_temp.location_information = 'SLX142 located in trailer next to i-Box station in Kolsass during CROSSINN field campaign. Location coordinates are taken from tiris map'
    
    elevation = dataset_temp.createVariable('elevation',np.int64, ('STATION_KEY'))
    elevation.units = 'degrees'
    elevation.long_name = 'elevation'
    elevation.description = 'elevation of rays (number of rays specified in variable: rays) for VAD scan'
    elevation[:] = vad.el_deg
    
    rays = dataset_temp.createVariable('rays',np.int64, ('STATION_KEY'))
    rays.units = 'unitless'
    rays.long_name = 'number of rays'
    rays.description = 'number of rays used to calculate mean wind profile (VAD algorithm) within the interval'
    rays[:] = vad.an
    
    datenum = dataset_temp.createVariable('datenum',np.float64, ('NUMBER_OF_SCANS'))
    datenum.units = 'Number of days from January 0, 0000'
    datenum.long_name = 'start time of each conical scan'
    datenum.description = 'datenum (matlab) timestamp'
    datenum[:] = vad.dn
    
    unixtime = (vad.dn-mdates.datestr2num('19700101'))*(24*60*60)
    
    time = dataset_temp.createVariable('time',np.int64, ('NUMBER_OF_SCANS'))
    time.units = 'Seconds since 01-01-1970 00:00:00'
    time.long_name = 'start time of each conical scan'
    time.description = 'UNIX timestamp'
    time[:] = unixtime
    
    ff = dataset_temp.createVariable('ff', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    ff.units  ='m s-1'
    ff.long_name = 'mean horizontal wind speed'
    ff.description = 'wind speed filtered with snr threshold'
    ff[:,:] = vad.ws
    
    dd = dataset_temp.createVariable('dd', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    dd.units = 'degrees'
    dd.long_name = 'mean horizontal wind direction'
    dd.description = 'wind direction filtered with snr threshold'
    dd[:,:] = vad.wd
    
    ucomp = dataset_temp.createVariable('ucomp', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    ucomp.units = 'm s-1'
    ucomp.long_name = 'u component of horizontal wind vector'
    ucomp.description = 'u component filtered with snr threshold'
    ucomp[:,:] = vad.u
    
    vcomp = dataset_temp.createVariable('vcomp', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    vcomp.units = 'm s-1'
    vcomp.long_name = 'v component of horizontal wind vector'
    vcomp.description = 'v component filtered with snr threshold of'
    vcomp[:,:] = vad.v
    
    wcomp = dataset_temp.createVariable('wcomp', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    wcomp.units = 'm s-1'
    wcomp.long_name = 'vertical velocity component'
    wcomp.description = 'v component filtered with snr threshold'
    wcomp[:,:] = vad.w
    
    vr_fluc_var = dataset_temp.createVariable('vr_fluc_var', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    vr_fluc_var.units = 'm2 s-2'
    vr_fluc_var.long_name = 'variance of radial velocity fluctuations'
    vr_fluc_var.description = 'variance of radial velocity variations around mean (u,v,w) retrieval'
    vr_fluc_var[:,:] = vad.rv_fluc
    
    ucomp_unfiltered = dataset_temp.createVariable('ucomp_unfiltered', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    ucomp_unfiltered.units = 'm s-1'
    ucomp_unfiltered.long_name = 'u component of horizontal wind vector'
    ucomp_unfiltered.description = 'non filtered u component'
    ucomp_unfiltered[:,:] = vad.u_nf
    
    vcomp_unfiltered = dataset_temp.createVariable('vcomp_unfiltered', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    vcomp_unfiltered.units = 'm s-1'
    vcomp_unfiltered.long_name = 'v component of horizontal wind vector'
    vcomp_unfiltered.description = 'non filtered v component'
    vcomp_unfiltered[:,:] = vad.v_nf
    
    snr_var = dataset_temp.createVariable('snr', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'),)
    snr_var.units = 'unitless'
    snr_var.long_name = 'signal to noise ratio (SNR)'
    snr_var.description = 'averaged profiles of snr'
    snr_var[:,:] = vad.snr
    
    height = dataset_temp.createVariable('height',np.float32,('NUMBER_OF_GATES'))
    height.units = 'm'
    height.long_name = 'heigth of range gate centers'
    height.description = 'height of range gate centers above ground: gate_centers = (range_gate + 0.5) * range_gate_length * sin(elevation)'
    height[:] = vad.gz
        
    dataset_temp.close()
    
    return file_path