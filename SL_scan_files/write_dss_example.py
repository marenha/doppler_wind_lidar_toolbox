# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 10:08:33 2018
Write daily scan scedule (dss) for Halo Photonics StreamLine software and
create necessary scan files
Example:
    For the StreamLine XR lidar SLXR_142 the dss "scanrio0" is created which perfomrs
    within one hour 28 min vertical stare ("stare") measurements; one conical vad scan
    at 70 deg ("ppi70"); 28 min of PPI scans at two different elevation angles ("rhi_ppi")
    and again one conical vad scan at 70 deg ("ppi70")
    
    scan_shedule=[stare,ppi70,ppi_el,ppi70]
@author: maren
"""
import sys
import os
import numpy as np
import pandas as pd
import datetime as dt

# Import own modules
import write_scan_file as wsf

class scan_pattern():
    def __init__(self,sd,rays_avg,name):
        self.sd=sd #scan duration in minutes
        self.name=name #name of scan file
        self.rays_avg=rays_avg  #refers to average configuarion in SL software
        self.start_delay=0 #in case delay is necessary to syncronize single scans

#%% name of the used lidar system and of the scan scenario
lidar_id = 'SLXR_142'
scan_shedule_name = 'scenario0'


#%% StreaLine Lidars parameters 
'''
The dss contains information about the sampling frequqncy wich depends on
the pulse repetition frequency (pulse_frequency) of the used instrument; 
The scan files are defined assuming a perfect orientation to North of the 
lidar scanner heads. Since this is not necessarily achieved for lidars installed
in the filed, a bearing angle can be defined 
TODO these paramters have to be changed for other lidars
'''
focus=7     #sl xr does not have a focus any longer
wait=0 
if lidar_id=='SL_88':
    pulse_frequency=15000
    bearing=1.7
elif lidar_id=='SLXR_142': 
    pulse_frequency=10000
    bearing=18.4  #bearing during the test campaing in autumn 2018 SLXR_142:194.2

#%% define scan pattern which should be performed in the dss
stare=scan_pattern(28,1,'stare')
ppi70=scan_pattern(2,1,'ppi70')
ppi_el=scan_pattern(28,1,'rhi_ppi')

#%% Create scan pattern and return scan file name
ppi70.scan_file=wsf.write_ppi(lidar_id,0,360,el=70,s=3,c=1,bearing=bearing)
ppi_el.scan_file=wsf.write_ppi_el(lidar_id,0,360,el=[4,7],d=28,s=3,bearing=bearing)
stare.scan_file='stare'

#%% here, scan starts can be tuned; e.g., in case of coordinated scans
ppi70.start_delay=0
stare.start_delay=0
ppi_el.start_delay=0


#%% order in the list corresponds order in scan schedule
scan_shedule=[stare,ppi70,ppi_el,ppi70]

#%% write scan scedule
time_delta=[scan.sd for scan in scan_shedule]
date_array=pd.date_range('20170101 00:00','20170102 00:00',freq=('%imin' % sum(time_delta)))
scans_n=len(scan_shedule)

text_file=open(os.path.join(lidar_id,'%s.dss' % (scan_shedule_name)),'w')

for date in date_array:
    date_temp=date
    for si in range(scans_n):
        scan=scan_shedule[si]
        scan_name=scan.scan_file
        if date_temp>=date_array[-1]:
            break
        if (scan_name!='stare'):
            date_write=date_temp+dt.timedelta(0,scan.start_delay)
            if date_write<date_array[0]:
                rays_av_temp=(scan.rays_avg*pulse_frequency)/1000
                str_end='%s\t%s\t%s\t%s\t%s\r\n' % (date_write.strftime('%H%M%S'),scan_name,int(rays_av_temp),'C',focus)
                continue                
            if scan_name[0:3]=='csm':
                rays_av_temp=(scan.rays_avg*pulse_frequency)/1000
                text_file.write('%s\t%s\t%s\t%s\t%s\r\n' % (date_write.strftime('%H%M%S'),scan_name,int(rays_av_temp),'C',focus))
            elif scan_name[0:2]=='ss':
                text_file.write('%s\t%s\t%s\t%s\t%s\r\n' % (date_write.strftime('%H%M%S'),scan_name,scan.rays_av,'S',focus))
        date_temp=date_temp+dt.timedelta(minutes=scan.sd)
#text_file.write(str_end)
text_file.close()



