# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 19:41:18 2021

@author: Maren
"""
import numpy as np
from netCDF4 import Dataset
import os
import datetime
import xarray as xr
import matplotlib.dates as mdates

class vad():
    def __init__(self,datenum):
        set
        

def to_netcdf(file_path):
    # create output directory if non-existant
    if not os.path.exists(path_out):
        os.makedirs(path_out)  
        
    file_name='%s_%s_vad.nc' %(lidar_id,mdates.num2datestr(date_num,'%Y%m%d'))
    file_path=os.path.join(path_out,file_name)

    if os.path.isfile(file_path):
        os.remove(file_path)
    
    dataset_temp=Dataset(file_path,'w',format ='NETCDF4')
    # define dimensions
    dataset_temp.createDimension('NUMBER_OF_GATES',gn)
    dataset_temp.createDimension('NUMBER_OF_SCANS',tn)
    dataset_temp.createDimension('STATION_KEY',1)
    #    dataset_temp.createDimension('TEXT',1)
    
    # Metadata
    dataset_temp.description = "Profiles of horizontal wind speed and direction"
    dataset_temp.institution = "Department of Atmospheric and Cryospheric sciences (ACINN), University of Innsbruck, AUSTRIA",
    dataset_temp.contact = "Alexander Gohm (alexander.gohm@uibk.ac.at),Maren Haid, Lukas Lehner"
    dataset_temp.range_gate_length = range_gate_length
    dataset_temp.system_id = lidar_id
    dataset_temp.history = 'File created %s by M. Haid' %date.today().strftime('%d %b %Y')
    dataset_temp.lat = lat
    dataset_temp.lon = lon
    dataset_temp.alt = alt
    dataset_temp.snr_threshold = '%.2f dB' %snr_threshold
    dataset_temp.location_information = 'SLX142 located in trailer next to i-Box station in Kolsass during CROSSINN field campaign. Location coordinates are taken from tiris map'
    
    elevation = dataset_temp.createVariable('elevation',np.int64, ('STATION_KEY'))
    elevation.units = 'degrees'
    elevation.long_name = 'elevation'
    elevation.description = 'elevation of rays (number of rays specified in variable: rays) for VAD scan'
    elevation[:] = el_deg
    
    rays = dataset_temp.createVariable('rays',np.int64, ('STATION_KEY'))
    rays.units = 'unitless'
    rays.long_name = 'number of rays'
    rays.description = 'number of rays used to calculate mean wind profile (VAD algorithm) within the interval'
    rays[:] = an
    
    datenum = dataset_temp.createVariable('datenum',np.float64, ('NUMBER_OF_SCANS'))
    datenum.units = 'Number of days from January 0, 0000'
    datenum.long_name = 'start time of each conical scan'
    datenum.description = 'datenum (matlab) timestamp'
    datenum[:] = datenum_array
    
    unixtime = (datenum_array-mdates.datestr2num('19700101'))*(24*60*60)
    
    time = dataset_temp.createVariable('time',np.int64, ('NUMBER_OF_SCANS'))
    time.units = 'Seconds since 01-01-1970 00:00:00'
    time.long_name = 'start time of each conical scan'
    time.description = 'UNIX timestamp'
    time[:] = unixtime
    
    ff = dataset_temp.createVariable('ff', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    ff.units  ='m s-1'
    ff.long_name = 'mean horizontal wind speed'
    ff.description = 'wind speed filtered with snr threshold'
    ff[:,:] = ws_lin
    
    dd = dataset_temp.createVariable('dd', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    dd.units = 'degrees'
    dd.long_name = 'mean horizontal wind direction'
    dd.description = 'wind direction filtered with snr threshold'
    dd[:,:] = wd_lin
    
    ucomp = dataset_temp.createVariable('ucomp', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    ucomp.units = 'm s-1'
    ucomp.long_name = 'u component of horizontal wind vector'
    ucomp.description = 'u component filtered with snr threshold'
    ucomp[:,:] = u_lin
    
    vcomp = dataset_temp.createVariable('vcomp', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    vcomp.units = 'm s-1'
    vcomp.long_name = 'v component of horizontal wind vector'
    vcomp.description = 'v component filtered with snr threshold of'
    vcomp[:,:] = v_lin
    
    wcomp = dataset_temp.createVariable('wcomp', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    wcomp.units = 'm s-1'
    wcomp.long_name = 'vertical velocity component'
    wcomp.description = 'v component filtered with snr threshold'
    wcomp[:,:] = w_lin
    
    vr_fluc_var = dataset_temp.createVariable('vr_fluc_var', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    vr_fluc_var.units = 'm2 s-2'
    vr_fluc_var.long_name = 'variance of radial velocity fluctuations'
    vr_fluc_var.description = 'variance of radial velocity variations around mean (u,v,w) retrieval'
    vr_fluc_var[:,:] = rv_fluc
    
    ucomp_unfiltered = dataset_temp.createVariable('ucomp_unfiltered', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    ucomp_unfiltered.units = 'm s-1'
    ucomp_unfiltered.long_name = 'u component of horizontal wind vector'
    ucomp_unfiltered.description = 'non filtered u component'
    ucomp_unfiltered[:,:] = u_nf
    
    vcomp_unfiltered = dataset_temp.createVariable('vcomp_unfiltered', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'))
    vcomp_unfiltered.units = 'm s-1'
    vcomp_unfiltered.long_name = 'v component of horizontal wind vector'
    vcomp_unfiltered.description = 'non filtered v component'
    vcomp_unfiltered[:,:] = v_nf
    
    snr_var = dataset_temp.createVariable('snr', np.float32,('NUMBER_OF_GATES','NUMBER_OF_SCANS'),)
    snr_var.units = 'unitless'
    snr_var.long_name = 'signal to noise ratio (SNR)'
    snr_var.description = 'averaged profiles of snr'
    snr_var[:,:] = snr
    
    height = dataset_temp.createVariable('height',np.float32,('NUMBER_OF_GATES'))
    height.units = 'm'
    height.long_name = 'heigth of range gate centers'
    height.description = 'height of range gate centers above ground: gate_centers = (range_gate + 0.5) * range_gate_length * sin(elevation)'
    height[:] = gz_temp
        
    dataset_temp.close()
    
    return file_path