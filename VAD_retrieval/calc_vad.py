#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 13:02:47 2017
Estimation of horizontal wind from Velocity-Azimuth Display (VAD) scans 

These methods are based on the following literature (i.a.,):
    - Browning and Wexler (1968); DOI: 10.1175/1520-0450(1968)007<0105:TDOKPO>2.0.CO;2
    - Eberhard et al. (1989); DOI: 10.1175/1520-0426(1989)006<0809:DLMOPO>2.0.CO;2
    
@author: maren
"""
import sys
import numpy as np

'''
Convert components of the horizontal 2d wind vector (u,v) to 
wind direction (dd_deg) and wind speed (ff)
Input:
    - u in m/s: component of 2D wind vector pointing east
    - v in m/s: component of 2D wind vector pointing north
Output:
    - ff in m/s: horizontal wind speed
    - dd in deg: wind direction of horizontal wind
'''
def uv2ffdd(u,v):
        ff = np.sqrt(u**2+v**2)
        dd_rad = np.arctan2(u,v)
        dd_deg = np.rad2deg(dd_rad) - 180 
        if u.size == 1:
            if dd_deg < 0:
                dd_deg += 360
        else:
            dd_deg[dd_deg<0] = dd_deg[dd_deg<0] + 360
 
        return ff,dd_deg

'''
Convert wind direction (dd) and wind speed (ff) into components of 
2D wind vector (uv)
Input:
    - ff in m/s: horizontal wind speed
    - dd in deg: wind direction of horizontal wind
Output:
    - u in m/s: component of 2D wind vector pointing east
    - v in m/s: component of 2D wind vector pointing north
'''
def ffdd2uv(ff,dd):
    
        u=-ff*np.sin(np.deg2rad(dd))
        v=-ff*np.cos(np.deg2rad(dd))
        
        return u,v

'''
Estimation of horizontal wind vector from Velocity-Azimuth Display (VAD) scans

Input:
    - rv in m/s: radial velocity
    - az in deg: azimuth angle 
    - el in deg: elevation angle
Output:
    - ws in m/s: horizontal wind speed
    - wd in deg: wind direction of horizontal wind
    - u in m/s: component of 2D wind vector pointing east
    - v in m/s: component of 2D wind vector pointing north
'''
def calc_vad_2d(rv,az_deg,el_deg):
    az_rad = np.deg2rad(az_deg)
    el_rad = np.deg2rad(el_deg)
    
    b1 = np.nansum(rv*np.cos(el_rad)*np.sin(az_rad))
    b2 = np.nansum(rv*np.cos(el_rad)*np.cos(az_rad))
    a11 = np.nansum(np.cos(el_rad)**2*np.sin(az_rad)**2)
    a12 = np.nansum(np.cos(el_rad)**2*np.cos(az_rad)*np.sin(az_rad))
    a21 = np.nansum(np.cos(el_rad)**2*np.cos(az_rad)*np.sin(az_rad))
    a22 = np.nansum(np.cos(el_rad)**2*np.cos(az_rad)**2)

    detA = a11*a22-a12*a21
    
    if detA!=0:
        
        u=(b1*a22-b2*a12)/detA
        v=(b2*a11-b1*a21)/detA
    
        ws,wd=uv2ffdd(u,v)
        
    return ws,wd,u,v


'''
Estimate three dimensional wind vector by solving an overdetermined system of
linear equations

'''
def calc_vad_3d(rv,el_rad,az_rad):
    
    rn=rv.size
    
    M=np.array([[np.cos(phi)*np.sin(theta),np.cos(phi)*np.cos(theta),np.sin(phi)] for (phi,theta) in zip(el_rad,az_rad)])
    W_weight=np.zeros((rn,rn))
    W=np.full(rn,1)
    np.fill_diagonal(W_weight,W)
    
    
    u_lin,v_lin,w_lin=np.dot(np.dot(np.dot(np.linalg.inv(np.dot(np.dot(M.T,W_weight),M)),M.T),W_weight),rv)
    ws_lin,wd_lin=uv2ffdd(u_lin,v_lin)
    
    '''
    retrieve variance fluctuations of v_r around mean wind speed
    '''
    rv_mean=u_lin*np.cos(el_rad)*np.sin(az_rad)\
            +v_lin*np.cos(el_rad)*np.cos(az_rad)\
            +w_lin*np.sin(el_rad)
    
    rv_fluc=np.mean((rv_mean-rv)**2)
    
    
    return u_lin,v_lin,w_lin,ws_lin,wd_lin,rv_fluc