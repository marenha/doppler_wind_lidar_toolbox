#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculation of two dimensional wind fields for a plane (vertical or horizontal)
In the horizontal plane (u,v) components will be calculated assuming that
azimuth=0 corresponds with north direction. Therefore  u corresponds to the 
westerly wind component and v to southerly. For vertical measurements, the plane 
will be rotated along vertical coordinate z in a way that u correspons to horizontal 
wind vector along the plane and v to vertical wind component.
 
classes:
    scan: el_deg, az_deg, vr, snr, dl_log, delta_g
    grid: delta_l, (x,y,z) 
    retrieval: grid, (u,v), weigth,(sigma_u, sigma_v) #TODO: adapt
  

The DL delivers measurement of radial velocity and signal-to-noise ratio for 
different range gates of fixed length delta_g. These gates have a distance of r from the 

variables:
    el_deg      elevation of measruemtn in degrees
    az_deg      azimuth of measurement in degerees
    delta_g     range gate length  
    gr          distance of range gate center to lidar
    gn          number of range gates
    (gx,gy,gz)  coordinates of range gate
    gxy         horizontal distance of gate centers from origin 
    rn          number of rays (measured profiles)
    vr          radial velocity (gn x rn)
    delta_l     lattice width
    (u,v,w)     two dimensional wind vector
    (x,y,z)     two dimensional coordiate system of grid 
    dl_loc      location of Doppler lidar
    [dlx,dly,dlyz] coordinates of Doppler lidar in global coordinate system 
    weigth      used method to weight the collected measurements for each grid point
"""
import numpy as np
'''
Defintion of classes: scan, grid, retrieval
'''

# variable contains measurements of DL scan
# for each DL one scan class is defined which includes one scan
class scan:     
    def __init__(self,el_deg,az_deg,vr,snr,dl_loc,delta_g):
        #get dimesnions of scan
        [self.gn,self.rn]=vr.shape
        
        #set attributes to class 
        self.el_deg,self.az_deg=el_deg,az_deg
        self.vr,self.snr=vr,snr
        self.dl_loc=dl_loc
        
        #distance of range gates centers from lidar
        r=np.arange(0,self.gn,1)*delta_g+delta_g*.5
        
        [dlx,dly,dlz]=dl_loc
        
        self.el_rad,self.az_rad=np.deg2rad(el_deg),np.deg2rad(az_deg)
        
        #coordinates of measurement in lidar local coordinate system
        gx_loc=np.outer(r,np.cos(self.el_rad)*np.sin(self.az_rad))
        gy_loc=np.outer(r,np.cos(self.el_rad)*np.cos(self.az_rad))
        gz_loc=np.outer(r,np.sin(self.el_rad))
        
        #coordinates of measurements in gloabl coordinate sytem
        self.gx,self.gy,self.gz=gx_loc+dlx,gy_loc+dly,gz_loc+dlz
        
        #horizontal distance from origin; defined in a way that distance is 
        # smaller zero when measurement is taken west (negative x dir.) from origin 
        gxy=np.sqrt(self.gx**2+self.gy**2)
        gxy[self.gx<0]*=-1
        self.gxy=gxy
        
        #flatten variables
        self.gx_flat,self.gy_flat,self.gz_flat=self.gx.flatten(),self.gy.flatten(),self.gz.flatten()
        self.gxy_flat=self.gxy.flatten()
        self.vr_flat,self.snr_flat=self.vr.flatten(),self.snr.flatten()
        self.el_deg_flat,self.az_deg_flat=np.tile(self.el_deg,(self.gn,1)).flatten(),np.tile(self.az_deg,(self.gn,1)).flatten()
        self.el_rad_flat,self.az_rad_flat=np.tile(self.el_rad,(self.gn,1)).flatten(),np.tile(self.az_rad,(self.gn,1)).flatten()
      
# grid for which coplanar retrieval is calculted (inclined planes are NOT possible)
# x,y,z one dimensional (requirement: uniform grid)
# xx,yy,zz two dimensional
# TODO: write python function which finds optimum grid for used scans
class grid:
    def __init__(self,x,y,z,delta_l):
        self.delta_l=delta_l
        self.x,self.y,self.z=x,y,z
        
        if type(z)==int:
        
            plane_orientation='horizontal'

            xx,yy=np.meshgrid(x,y)
            zz=np.full(xx.shape,z)
        else:    
            plane_orientation='vertical'
            
            xx,zz=np.meshgrid(x,z)
            yy,zz=np.meshgrid(y,z)
            
        self.xx,self.yy,self.zz=xx,yy,zz    
            
        self.plane_orientation=plane_orientation
        
        # horizontal distance of grid points from origin
        # negative for negative x direction (see scan.xy)
        if plane_orientation=='vertical':
            self.xy=np.sqrt(self.x**2+self.y**2)
            self.xy[(self.x<0)]*=-1
            self.xxyy=np.sqrt(self.xx**2+self.yy**2)
            self.xxyy[self.xx<0]*=-1
            self.xxyy_flat=self.xxyy.flatten()

        
        #flatten variables
        self.xx_flat,self.yy_flat,self.zz_flat=self.xx.flatten(),self.yy.flatten(),self.zz.flatten()
        self.n=self.xx_flat.shape[0]
        
        
# retrieval contains results of calculation
# u_flat,v_flat retrieved velocity components on lidar plane
# n_flat number of valid measuremetns of each lidar per grid cell
# error_flat error prefactor !!! has to be improved
class retrieval:
    def __init__(self,grid,lidar_n,weight):
        self.u_flat,self.v_flat=np.full(grid.n,np.nan),np.full(grid.n,np.nan)
        self.error_flat=np.full(grid.n,np.nan)
        self.n_flat=np.full((grid.n,lidar_n),np.nan)
        self.scan_type=None
        self.grid=grid
        self.weight=weight
    
    #calculation of wind speed and reshape of 1d arrays into 2d fields
    def reshape(self):
        self.ws_flat=np.sqrt(self.u_flat**2+self.v_flat**2)
        
        grid_shape=self.grid.xx.shape
        self.u,self.v=np.reshape(self.u_flat,grid_shape),np.reshape(self.v_flat,grid_shape)
        self.ws=np.reshape(self.ws_flat,grid_shape)
        self.error=np.reshape(self.error_flat,grid_shape)
        self.n=np.reshape(self.n_flat,grid_shape+(self.n_flat.shape[1],))

def vr2uv(angles_rad,W_weight,vr_array):
    
    A=np.column_stack((np.cos(angles_rad),np.sin(angles_rad)))
    u,v=np.dot(np.dot(np.dot(np.linalg.inv(np.dot(np.dot(A.T,W_weight),A)),A.T),W_weight),vr_array) 
    
    return u,v

def valid_angle(angle):
    return ((angle>30)and(angle<150))
   
'''
Main dual Doppler algorithm
assumptions: grid plane is alogned horizontal (ppis) or vertical (rhi), 
inclination is NOT possible
'''
def calc_retrieval(scan_list,grid,weight=None):
    R=grid.delta_l/np.sqrt(2)
    
    retrieval_temp=retrieval(grid,len(scan_list),weight)
    
    if grid.plane_orientation=='horizontal': #ppi, horizontal plane
#        dd_retrieval_temp.scan_type='ppi'
        for gi,(x_temp,y_temp,z_temp) in enumerate(zip(grid.xx_flat,grid.yy_flat,grid.zz_flat)): #loop through all grid points
            # close measurements will be selected in lists 
            
            # close measurements will be selected in lists 
            rv_,az_,w_,li_m=[],[],[],[]
            temp=[]
            for li,scan in enumerate(scan_list):
                R_dist=np.sqrt((scan.gx_flat-x_temp)**2\
                    +(scan.gy_flat-y_temp)**2)
                
                #distance of measurement center to grid point has to be smaller 
                #R=delta_g/sqrt(2) and only valid measurements are counted
                ind_temp=np.where((R_dist<=R)&(~np.isnan(scan.vr_flat)))[0]
                temp.append(len(ind_temp))
                if len(ind_temp)>0:
                    w_.append(R_dist[ind_temp])
                    az_.append(scan.az_deg_flat[ind_temp])
                    rv_.append(scan.vr_flat[ind_temp])
                    li_m.append(li)
                    
            if len(rv_)>1:
                retrieval_temp.n_flat[gi,:]=temp
                
                if len(rv_)==2:
                    az_mean_rad=[np.mean(np.deg2rad(az)) for az in az_]
                    az_diff=np.rad2deg(np.abs(np.arctan2(np.sin(az_mean_rad[0]-az_mean_rad[1]),np.cos(az_mean_rad[0]-az_mean_rad[1]))))
                    lidar_n_list=[[0,1]]
                    if not valid_angle(az_diff): continue
                elif len(rv_)==3:
                    az_mean_rad=[np.mean(np.deg2rad(az)) for az in az_]
                    #calc mean angle between different lidars
                    az_diff01=np.rad2deg(np.abs(np.arctan2(np.sin(az_mean_rad[0]-az_mean_rad[1]),np.cos(az_mean_rad[0]-az_mean_rad[1]))))
                    az_diff02=np.rad2deg(np.abs(np.arctan2(np.sin(az_mean_rad[0]-az_mean_rad[2]),np.cos(az_mean_rad[0]-az_mean_rad[2]))))
                    az_diff12=np.rad2deg(np.abs(np.arctan2(np.sin(az_mean_rad[1]-az_mean_rad[2]),np.cos(az_mean_rad[1]-az_mean_rad[2]))))
        
                    az_diff01_valid,az_diff02_valid,az_diff12_valid=valid_angle(az_diff01),valid_angle(az_diff02),valid_angle(az_diff12)
                    az_diff_valid_sum=sum([az_diff01_valid,az_diff02_valid,az_diff12_valid])
        
                    if az_diff_valid_sum==3:
                        lidar_n_list=[[0,1,2]]
                    elif az_diff_valid_sum==2:
                        if not valid_angle(az_diff01):
                            lidar_n_list=[[0,2],[1,2]]
                        elif not valid_angle(az_diff02):
                            lidar_n_list=[[0,1],[1,2]] 
                        elif not valid_angle(az_diff12):
                            lidar_n_list=[[0,1],[0,2]] 
                    elif az_diff_valid_sum==1:
                        if valid_angle(az_diff01):
                            lidar_n_list=[[0,1]]
                        if valid_angle(az_diff02):
                            lidar_n_list=[[0,2]] 
                        if valid_angle(az_diff12):
                            lidar_n_list=[[1,2]] 
                    else: lidar_n_list=[]

                v_list,u_list=[],[]  
                error_list=[]
                for lidar_n in lidar_n_list:
                    w_flat=[w_[t] for t in lidar_n]
                    az_flat=[az_[t] for t in lidar_n]
                    rv_flat=[rv_[t] for t in lidar_n]
                    li_m=lidar_n
                    
                    az_temp=np.concatenate(az_flat)
    
                    az_mean_rad=np.deg2rad([np.mean(at) for at in az_flat])
                    error_temp=1/(np.sin(az_mean_rad[1]-az_mean_rad[0])**2)
                    
                    rv_temp=np.concatenate(rv_flat)
                    n=[rv.shape[0] for rv in rv_flat] # number of measurement points of each lidar
                    N=rv_temp.shape[0] #total number of measurement points
                    
                    W_weight=np.zeros((N,N))
                    retrieval_temp.n_flat[gi,li_m]=n
    
                    W=np.full(N,1)
        
                    np.fill_diagonal(W_weight,W)
                    # calc 2d wind vector weighted
                    u_temp,v_temp=vr2uv(np.deg2rad(az_temp),W_weight,rv_temp)
                    v_list.append(v_temp)
                    u_list.append(u_temp)
                    error_list.append(error_temp)
                #TODO average according to specific error
                retrieval_temp.error_flat[gi]=np.nanmean(error_list)
                retrieval_temp.v_flat[gi],retrieval_temp.u_flat[gi]=np.nanmean(u_list),np.nanmean(v_list)
                
    elif grid.plane_orientation=='vertical': 

        for gi,(x_temp,y_temp,z_temp) in enumerate(zip(grid.xx_flat,grid.yy_flat,grid.zz_flat)): #loop through all grid points
            # close measurements will be selected in lists 
            rv_,el_,w_=[],[],[]
            for scan in scan_list:
                R_dist=np.sqrt((scan.gx_flat-x_temp)**2\
                    +(scan.gy_flat-y_temp)**2\
                    +(scan.gz_flat-z_temp)**2)
                
                #distance of measurement center to grid point has to be smaller 
                #R=delta_g/sqrt(2) and only valid measurements are counted
                ind_temp=np.where((R_dist<=R)&(~np.isnan(scan.vr_flat)))[0]
                if len(ind_temp)>0:
                    w_.append(R_dist[ind_temp])
                    el_.append(scan.el_deg_flat[ind_temp])
                    rv_.append(scan.vr_flat[ind_temp])
                    
            if len(rv_)>1:
                el_[1]=180-el_[1] #both angles must refer to the same system (more universal solution: angle in dependence to vertical??)
                
                el_temp=np.concatenate(el_)
                el_temp_rad=np.deg2rad(el_temp)

                # if angle between the measurements is too flat, no wind vector is calculated due to too big errors
                # see Christinas paper
                # to do: complete error calculations including mean angle between the two measurements!!!!
                # + number of measurements for each grid point
                #calculate error prefactor due to difference in angles
                el_mean_rad=np.deg2rad([np.mean(el) for el in el_])
                el_diff=np.rad2deg(np.abs(np.arctan2(np.sin(el_mean_rad[0]-el_mean_rad[1]),np.cos(el_mean_rad[0]-el_mean_rad[1]))))
                if (el_diff>160)|(el_diff<20):
                    continue

                rv_temp=np.concatenate(rv_)
                n=[rv.shape[0] for rv in rv_] # number of measurement points of each lidar
                N=rv_temp.shape[0] #total number of measurement points

                retrieval_temp.error_flat[gi]=1/(np.sin(el_mean_rad[1]-el_mean_rad[0])**2)
                
                W_weight=np.zeros((N,N))
                retrieval_temp.n_flat[gi,:]=n

                W=np.full(N,1)
    
                np.fill_diagonal(W_weight,W)
               
                A=np.column_stack((np.cos(el_temp_rad),np.sin(el_temp_rad)))
                u_temp,v_temp=np.dot(np.dot(np.dot(np.linalg.inv(np.dot(np.dot(A.T,W_weight),A)),A.T),W_weight),rv_temp)
        
                retrieval_temp.u_flat[gi],retrieval_temp.v_flat[gi]=u_temp,v_temp
            
    retrieval_temp.reshape()
    return retrieval_temp


 
