#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 15:17:42 2017
Functions to write scan files for the Halo Photonics StreamLine software
The scans can be performed in csm (continous scanning mode) or ss (step and stare mode)
functions:
    write_ppi       - PPI scan for fixed elevation angle and changing azimuth angle
    write_rhi       - RHI scan for fices azimuth angle and changing elevtion angle
    write_ppi_rhi   - PPI and RHI scan consecutively
    write_vad_csm   - Perform 360 deg PPI scans at different elevation angles
    write_vad       - conical scan in ss mode for fixed elevation angle and a given number of azimuth angles
    write_ppi_el    - PPI scans at different elevation angles performed consecutively
    write_ht_scan   - PPI scans at different elevation angles performed consecutively; distance between elevation angles is very small
    
TODO: in windows, line break might not work correctly...
@author: maren      
"""
import numpy as np
import sys,os
#paths
path_=os.getcwd()

'''
PPI (Plan Position Indicator) scans are scans at a fixed elevation angle and 
changing azimuth angle performed in csm mode
input: 
    lidar_id        - name of the lidar; defines the output folder
    az_start in deg - start azimuth angle
    az_end in deg   - end azimuth angle
    el in deg       - define elevation angle for which PPI is performed (default = 0)
    s in deg/sec    - scanner speed 
    d in min        - duration the scan should run; defines the number of cycles
or  c               - number of repetitions
    w in msec       - milliseconds the scanner head is waiting before going to the next point
    bearing in deg  - devation of the lidar north to true north
return:
    file_name       - csm_ppi_[el]_[az_start]-[az_end]_[n]x_s[S1_deg]_w[wait]
'''
def write_ppi(lidar_id,az_start,az_end,**kwargs):
    
    delta_az=np.abs(az_end-az_start)
    
    #fixed elevation, default: 0 deg
    if 'el' in kwargs: el=kwargs['el'] 
    else: el=0
       
    #speed in deg/sec, default: 1 deg/sec
    if 's' in kwargs: S1_deg=kwargs['s']
    else: S1_deg=1
     
    '''
    estimation of the cycles (c) the scan pattern is performed
    if there is a duration (d in min) given for the scan pattern, c is estimated using 
    the azimuth range and the motor speed
    '''
    if 'd' in kwargs: n=int(np.floor((kwargs['d']*60-5)/((delta_az/S1_deg+4)*2)))*2
    elif 'c' in kwargs: n=kwargs['c']
    else: n=1
        
    # milliseconds the scanner head is waiting before going to the next point
    if 'w' in kwargs: wait=kwargs['w']
    else: wait=500
        
    # devation of the lidar north to true north
    if 'bearing' in kwargs: bearing=kwargs['bearing']
    else: bearing=0
       
    # motor points per complete circle
    el1=250000/360
    az1=500000/360
    
    S1=np.round(S1_deg*az1/10)
    A1=30
    S2=5000
    A2=50 
    
    P11=-np.round((az_start+bearing)*az1)
    P12=-np.round((az_end+bearing)*az1)
    
    P2=-np.round(el*el1)
    
    path_out=os.path.join(path_,lidar_id)   
    # the file name contains all information about the scan
    file_name=('csm_ppi_%.2f_%.2f-%.2f_%ix_s%i_w%i.txt' %(el,az_start,az_end,n,S1_deg,wait))
    
    text_file=open(os.path.join(path_out,file_name),'w')
    #go to start position
    text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S2,P11,A2,S2,P2))
    text_file.write('W%i\r\n' %wait)
    c=0
    for ni in range(0,n):
        if c==0:
            text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P12,A2,S2,P2))
            text_file.write('W%i\r\n' %wait)
            c=1
        elif c==1:
            text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P11,A2,S2,P2))
            text_file.write('W%i\r\n' %wait)
            c=0
    text_file.close()
    
    return file_name[0:-4]

'''
RHI (Range Height Indicator) scans are scans at a fixed azimuth angle and 
changing elevation angle performed in csm mode
input: 
    lidar_id        - name of the lidar; defines the output folder
    el_start in deg - start elevation angle
    el_end in deg   - end elevation angle
    az in deg       - define azimuth angle for which PPI is performed (default = 0)
    s in deg/sec    - scanner speed 
    d in min        - duration the scan should run; defines the number of cycles
or  c               - number of repetitions
    w in msec       - milliseconds the scanner head is waiting before going to the next point
    bearing in deg  - devation of the lidar north to true north
return:
    file_name       - csm_rhi_[az]_[el_start]-[el_end]_[n]x_s[S2_deg]_w[wait]
'''
def write_rhi(lidar_id,el_start,el_end,**kwargs):
    delta_el=np.abs(el_start-el_end)
    
    if 'az' in kwargs: az=kwargs['az']
    else: az=0
        
    if 's' in kwargs: S2_deg=kwargs['s']
    else: S2_deg=1
        
    if 'd' in kwargs: n=int(np.floor((kwargs['d']*60-5)/((delta_el/S2_deg+4)*2)))*2
    elif 'c' in kwargs: n=kwargs['c']
    else: n=1
        
    if 'w' in kwargs: wait=kwargs['w']
    else: wait=500
        
    if 'bearing' in kwargs: bearing=kwargs['bearing']
    else: bearing=0
    
    # motor points per complete circle
    el1=250000/360
    az1=500000/360
    
    S1=5000
    A1=30
    S2=np.round(S2_deg*el1/10) #points/sec
    A2=50 
    
    P1=-np.round((az+bearing)*az1)
    
    P21=-np.round(el_start*el1)
    P22=-np.round(el_end*el1)
    
    path_out=os.path.join(path_,lidar_id)
    
    # the file name contains all information about the scan
    file_name=('csm_rhi_%.2f_%.2f-%.2f_%ix_s%i_w%i.txt' %(az,el_start,el_end,n,S2_deg,wait))
    
    text_file=open(os.path.join(path_out,file_name),'w')
    #go to start position
    text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P1,A2,S1,P21))
    text_file.write('W%i\r\n' %wait)
    c=0
    for ni in range(0,n):
        if c==0:
            text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P1,A2,S2,P22))
            text_file.write('W%i\r\n' %wait)
            c=1
        elif c==1:   
            text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P1,A2,S2,P21))
            text_file.write('W%i\r\n' %wait)
            c=0
    text_file.close()
    
    return file_name[0:-4]

'''
Scans performs alternately RHI and PPI scans in continous scanning moder (csm)
input: 
    lidar_id        - name of the lidar; defines the output folder
    el_ppi in deg   - elevation angle of the PPI scan
    az_rhi in deg   - azimuth angle of the RHI scan
    s in deg/sec    - scanner speed 
    d in min        - duration the scan should run; defines the number of cycles
or  c               - number of repetitions
    w in msec       - milliseconds the scanner head is waiting before going to the next point
    bearing in deg  - devation of the lidar north to true north
    
return:
    file_name       - csm_ppi_rhi_[el_ppi]_[az_rhi]_[n]x_s[S1_deg]_w[wait]
'''
def write_ppi_rhi(lidar_id,el_ppi,az_rhi,**kwargs):
    #TODO rewrite for varying sectors
    '''
    this function only can PPI scans of 360 deg (0 - 360 deg)
    and RHI scans of 180 deg (0 - 180 deg)
    '''
    delta_el=180
    delta_az=360

    #TODO different scanner speeds for RHI and PPI
    # S1_deg and S2_deg denote scanner speed in degree/sec
    if 's' in kwargs: S2_deg,S1_deg = kwargs['s'],kwargs['s']
    else: S2_deg,S1_deg=1,1

        
    if 'd' in kwargs: n=int(np.floor((kwargs['d']*60-5)/((delta_el/S2_deg+4)+(delta_az/S1_deg+4))))
    elif 'c' in kwargs: n=kwargs['c']
    else: n=1

    if 'w' in kwargs: wait = kwargs['w']
    else: wait = 100
        
    if 'bearing' in kwargs: bearing = kwargs['bearing']
    else: bearing = 0
    
    # motor points per complete circle
    el1 = 250000/360
    az1 = 500000/360
    
    S_max=5000
    
    S1=np.round(S1_deg*az1/10) #points/sec
    A1=50
    S2=np.round(S2_deg*el1/10) #points/sec
    A2=50 
    
    
    P11=-np.round((az_rhi+bearing)*az1)
    P12=-np.round((az_rhi+360+bearing)*az1)
    
    P21=-np.round(0*el1)
    P22=-np.round(180*el1)
    
    P2=-np.round(el_ppi*el1)
    P1=-np.round((az_rhi+bearing)*az1)
    
    path_out=os.path.join(path_,lidar_id)
    
    file_name=('csm_ppi_rhi_el%.2f_az%.2f_%ix_s%i_w%i.txt' %(el_ppi,az_rhi,n,S1_deg,wait))
    
    text_file=open(os.path.join(path_out,file_name),'w')
    for ni in range(n):
        #start with PPI
        text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S_max,P11,A2,S_max,P2))
        text_file.write('W%i\r\n' %wait)
        text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P12,A2,S_max,P2))
        text_file.write('W%i\r\n' %wait)
        #start here with RHI
        text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S_max,P1,A2,S_max,P21))
        text_file.write('W%i\r\n' %wait)     
        text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P1,A2,S2,P22))
        text_file.write('W%i\r\n' %wait)
    text_file.close()
    
    return file_name[0:-4]

'''
Performing contical scans consecutively for different elevation angles in csm mode
input: 
    lidar_id        - name of the lidar; defines the output folder
    el_start in deg - first elevation angle
    el_end in deg   - last elevation angle
    el_delta in deg - difference between elevation angles
    s in deg/sec    - scanner speed 
    d in min        - duration the scan should run; defines the number of cycles
or  c               - number of repetitions
    w in msec       - milliseconds the scanner head is waiting before going to the next point
    bearing in deg  - devation of the lidar north to true north
    
return:
    file_name       - csm_vad_ppi_[el_start]-[el_end]_[el_delta]_s[S1_deg]_w[wait]
'''
def write_vad_csm(lidar_id,el_start,el_end,el_delta,**kwargs):
    
    el_array=np.arange(el_start,el_end,el_delta)
    eln=el_array.size
    
    #speed in deg/sec, default: 1 deg/sec
    if 's' in kwargs: S1_deg=kwargs['s']
    else: S1_deg=1
        
    # milliseconds the scanner head is waiting before going to the next point
    if 'w' in kwargs: wait=kwargs['w']
    else: wait=100
        
    # devation of the lidar north to true north
    if 'bearing' in kwargs: bearing=kwargs['bearing']
    else: bearing=0
       
    # motor points per complete circle
    el1=250000/360
    az1=500000/360
    
    S1=np.round(S1_deg*az1/10)
    A1=30
    S2=5000
    A2=50 
    
    P11=-np.round((0+bearing)*az1)
    P12=-np.round((360+bearing)*az1)
    

    path_out=os.path.join(path_,lidar_id)
    file_name=('csm_vad_ppi_%.2f-%.2f_%.2f_s%i_w%i.txt' %(el_start,el_end,el_delta,S1_deg,wait))
    text_file=open(os.path.join(path_out,file_name),'w')
    
    
    #go to start position
    P2=-np.round(el_array[0]*el1)
    text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S2,P11,A2,S2,P2))
    text_file.write('W%i\r\n' %wait)
    
    c=0
    for eli in range(1,eln):
        P2=-np.round(el_array[eli]*el1)
        if c==0:
            text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P11,A2,S2,P2))
            text_file.write('W%i\r\n' %wait)
            text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P12,A2,S2,P2))
            text_file.write('W%i\r\n' %wait)
            c=1
        elif c==1:
            text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P12,A2,S2,P2))
            text_file.write('W%i\r\n' %wait)
            text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P11,A2,S2,P2))
            text_file.write('W%i\r\n' %wait)
            c=0
    text_file.close()
    
    return file_name[0:-4]


'''
Conical scan in ss mode with fixed elevation angle and a certain number of azimuth angles
input: 
    lidar_id    - name of the lidar; defines the output folder
    rays_n      - number of azimuth angles; angles will be distributed uniformly in a cone
    el          - elevation angle
    c           - number of repetitions
return: 
    file_name   - ss_vad_[el]_[rays_n]rays_[c]x
'''
def write_vad(lidar_id,rays_n,el,**kwargs):
    if 'c' in kwargs:
        n=kwargs['cycles']
    else:
        n=1
    
    azis=np.linspace(0,360-360/rays_n,rays_n)
    
    path_out=os.path.join(path_,lidar_id)
    file_name=('ss_vad_%.2f_%irays_%ix.txt' %(el,rays_n,n))
    text_file=open(os.path.join(path_out,file_name),'w')
    for ni in range(0,n):
        for azi in azis:
           text_file.write('%07.3f%07.3f\r\n' % (azi,el))
    text_file.close()
    
    
    return file_name[0:-4]


'''
Perform PPI scans for alternately different elevation angle  in csm mode
input: 
    lidar_id        - name of the lidar; defines the output folder
    az_start in deg - azimuth angle start of PPI scan
    az_end in deg   - azimuth angle end of PPI scan
    el in deg       - array containing elevation angles for which PPI scans should be performed
    s in deg/sec    - scanner speed 
    d in min        - duration the scan should run; defines the number of cycles
or  c               - number of repetitions
    w in msec       - milliseconds the scanner head is waiting before going to the next point
    bearing in deg  - devation of the lidar north to true north
    
return:
    file_name       - csm_ppi_[el]_az_start-az_end_[n]x_s[S1_deg]_w[wait]
'''
def write_ppi_el(lidar_id,az_start,az_end,**kwargs):
    
    delta_az=np.abs(az_end-az_start)
    
    
    #fixed elevation, default: 0 deg
    if 'el' in kwargs: el=kwargs['el'] 
    else: el=0
       
    eln=len(el)
    #speed in deg/sec, default: 1 deg/sec
    if 's' in kwargs: S1_deg=kwargs['s']
    else: S1_deg=1
     
    '''
    estimation of the cycles (c) the scan pattern is performed
    if there is a duration (d in min) given for the scan pattern, c is estimated using 
    the azimuth range and the motor speed
    '''
    if 'd' in kwargs: n=int(np.floor((kwargs['d']*60-5)/(((delta_az/S1_deg+4)*2)*eln)))*2
    elif 'c' in kwargs: n=kwargs['c']
    else: n=1
        
    # milliseconds the scanner head is waiting before going to the next point
    if 'w' in kwargs: wait=kwargs['w']
    else: wait=500
        
    # devation of the lidar north to true north
    if 'bearing' in kwargs: bearing=kwargs['bearing']
    else: bearing=0
       
#    sys.exit()
    # motor points per complete circle
    el1=250000/360
    az1=500000/360
    
    S_max=5000
    S1=np.round(S1_deg*az1/10)
    A1=30
    S2=5000
    A2=50 
    
    P11=-np.round((az_start+bearing)*az1)
    P12=-np.round((az_end+bearing)*az1)
    
    
    path_out=os.path.join(path_,lidar_id)
    file_name=('csm_ppi_%s_%.2f-%.2f_%ix_s%i_w%i.txt' %(str(el).replace(', ','_')[1:-1],az_start,az_end,n,S1_deg,wait))
    
    check=True
    text_file=open(os.path.join(path_out,file_name),'w')
    for ni in range(n):
        #start with PPI
        for el_temp in el:
            P2=-np.round(el_temp*el1)
            if check:
                text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S_max,P11,A2,S_max,P2))
                text_file.write('W%i\r\n' %wait)
                text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P12,A2,S_max,P2))
                text_file.write('W%i\r\n' %wait)
            if not check:
                text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S_max,P12,A2,S_max,P2))
                text_file.write('W%i\r\n' %wait)
                text_file.write('A.1=%i,S.1=%i,P.1=%i*A.2=%i,S.2=%i,P.2=%i\r\n' %(A1,S1,P11,A2,S_max,P2))
                text_file.write('W%i\r\n' %wait)
            
            check= not check 
    text_file.close()
    
    return file_name[0:-4]


'''
Hart target scans were performed to check the orientation and position of a 
lidar installed in the field
Therefore the PPI scans at different elevation angles for a little azimuth sector
are performed. The distane between the elevation angles (delta_el) should be small 
if the hart target is far away
input: 
    site        - str used for path_out and file_name
    el_lim      - (2,) array containin el_start and el_end
    az_lim      - (2,) array containin az_start and az_end
    speed       - scanner speed in deg/sec
    delta_el    - elevation angle difference between consecutive PPI scans
return: 
    file_name   - ht_[site]
'''
def write_ht_scan(site,el_lim,az_lim,speed,delta_el):
    
    # motor points per complete circle
    el1=250000/360
    az1=500000/360
    wait=500
    
    el_start,el_end=el_lim[0],el_lim[-1]
    az_start,az_end=az_lim[0],az_lim[-1]

    S1_deg = speed
    
    
    S1=np.round(S1_deg*az1/10)
    azis=-np.round([az1*(az_start),az1*(az_end)]).astype(int)
    elis=-np.round(np.arange(el1*(el_start),el1*(el_end),el1*delta_el)).astype(int)
    
    path_out=os.path.join(path_,site)
    file_name=('ht_%s.txt' % site)
    text_file=open(os.path.join(path_out,file_name),'w')
    #text_file=open(os.path.join(path_out,('CSM_ht_%iaz_%iel.txt' %(delta_az,(el_end-el_start)))),'w')
    c=0
    for ei in elis:
        if c==0:
            text_file.write('A.1=30,S.1=%i,P.1=%i*A.2=50,S.2=5000,P.2=%i\r\n' %(S1,azis[0],ei))
            text_file.write('W%i\r\n' %wait)
            text_file.write('A.1=30,S.1=%i,P.1=%i*A.2=50,S.2=5000,P.2=%i\r\n' %(S1,azis[1],ei))
            c=1
        else:
            text_file.write('A.1=30,S.1=%i,P.1=%i*A.2=50,S.2=5000,P.2=%i\r\n' %(S1,azis[1],ei))
            text_file.write('W%i\r\n' %wait)
            text_file.write('A.1=30,S.1=%i,P.1=%i*A.2=50,S.2=5000,P.2=%i\r\n' %(S1,azis[0],ei))
            c=0
        text_file.write('W%i\r\n' %wait)
    text_file.close()
    
    return file_name[0:-4]