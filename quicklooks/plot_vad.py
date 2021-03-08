# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 15:28:43 2021
Plot VAD scans
@author: Maren
"""
import os,sys
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates

import colormap_costumn as cm

mpl.rcParams.update({'font.size':16})
c_map,c_map_snr,c_map_ws,c_map_rv=cm.load_colormaps() 
dtn=(24*60*60)

'''
Create Plot for one day of retrieved horizontal wind
'''
def plot_VAD_day(file_path,path_out,lidar_str,date_str,z_ref,location):
    plt.ioff()
    date_num=mdates.datestr2num(date_str)
    
    with xr.open_dataset(file_path) as data_temp:
        datenum_plot=data_temp.datenum.values
        ff_plot=data_temp.ff.values
        u_plot=data_temp.ucomp.values
        v_plot=data_temp.vcomp.values
        w_plot=data_temp.wcomp.values
        rv_fluc_var_plot=data_temp.vr_fluc_var.values
        height=data_temp.height.values+data_temp.alt-z_ref
        
    # axis limits and ticks
    x_lim=[date_num,date_num+1]
    x_ticks=np.arange(x_lim[0],x_lim[1]+3/24,3/24)
    x_ticklabels=mdates.num2datestr(x_ticks,'%H%M')
    y_lim=[0,2000]
    y_ticks=np.arange(y_lim[0],y_lim[1]+1,500)
    y_ticklabels=y_ticks/1000
    
    #%%  create figure with three subplots
    fig=plt.figure(figsize=(20,10))
    ax=[]
    ax.append(fig.add_axes([.15,.69,.7,.25]))
    ax.append(fig.add_axes([.15,.42,.7,.25]))
    ax.append(fig.add_axes([.15,.15,.7,.25]))
    
    cax=[]
    cax.append(fig.add_axes([.87,.69,.01,.25]))
    cax.append(fig.add_axes([.87,.42,.01,.25]))
    cax.append(fig.add_axes([.87,.15,.01,.25]))
    
    
    #%% Estimate the number of wind barbs depicted in the plot

    time_plot=datenum_plot+np.median(np.diff(datenum_plot))/2
    gc_plot=height+np.median(np.diff(height))/2
    
    dn_delta=np.mean(np.diff(time_plot))*dtn
    barbs_x_n=50
    barb_delta_x=int(np.diff(x_lim)*dtn/barbs_x_n/dn_delta)
    barbs_y_n=25
    gc_delta=np.mean(np.diff(height))
    barb_delta_y=int(y_lim[1]/barbs_y_n/gc_delta)
    
    ff_plot_ext=np.hstack([ff_plot,np.full([ff_plot.shape[0],1],np.nan)])
    datenum_plot_ext=np.hstack([datenum_plot,datenum_plot[-1]+np.median(np.diff(datenum_plot))])
    
    #%% Plot vertical profiles of horizontal wind
    ax_temp=ax[0]
    
    ax_temp.set_facecolor('#DDDDDD')
    pc_temp=ax_temp.contourf(datenum_plot_ext,height,ff_plot_ext,levels=np.arange(0,21,1),cmap=c_map_ws)
    
    X,Y=np.meshgrid(time_plot,gc_plot)
    X_plot, Y_plot = X[::barb_delta_y,::barb_delta_x], Y[::barb_delta_y,::barb_delta_x]
    U_plot, V_plot =  u_plot[::barb_delta_y,::barb_delta_x], v_plot[::barb_delta_y,::barb_delta_x]
    
    ax_temp.plot(X_plot[~np.isnan(U_plot)],Y_plot[~np.isnan(U_plot)],'k.',ms=3)
    
    ax_temp.barbs(X_plot,Y_plot,\
                  U_plot*1.94,V_plot*1.94,\
                  pivot='tip',length=4.8,fill_empty=False,rounding=False,\
                   sizes=dict(emptybarb=0.04,spacing=0.2,height=0.4))
    
    ax_temp.set(xlim=x_lim,xticks=x_ticks,xticklabels=[])
    ax_temp.set(ylim=y_lim,yticks=y_ticks,yticklabels=y_ticklabels) 
    ax_temp.grid()

    cb_temp=fig.colorbar(pc_temp,cax=cax[0],ticks=np.arange(0,21,4),extend='max')
    cb_temp.set_label('$\overline{u_h}$ (m s$^{-1}$)')
    #    cb_temp.ax.tick_params(labelsize=fs)
            
    legend_axes = fig.add_axes([0.1, 0.95, 0.18, 0.04]) 
    #legend_axes.set_frame_on(False)
    legend_axes.patch.set_visible(False)
    legend_axes.axis('off')
    legend_axes.axes.get_xaxis().set_visible(False)
    legend_axes.axes.get_yaxis().set_visible(False)
    #    rectangle = plt.matplotlib.patches.Rectangle((0,-1.3),2,5, ec='#DDDDDD', fc='#BBBBBB', zorder=1) #set relativ position of rectangle
    rectangle = plt.matplotlib.patches.Rectangle((0,-1.3),2,5, zorder=1, ec=[1,1,1], fc=[1,1,1])    
    legend_axes.add_patch(rectangle) 

    fs_temp=10
    legend_axes.barbs([0.65, 0.13, 0.22, 0.32, 0.41, 0.52],[0,0,0,0,0,0], [-26, 0, -2, -5, -10, -50],[0, 0 ,0, 0, 0, 0], pivot='tip',
        fill_empty=False, length=6, rounding=False,sizes=dict(emptybarb=0.04,spacing=0.2,height=0.4),zorder=3)
    legend_axes.plot([0.65, 0.13, 0.22, 0.32, 0.41, 0.52],[0,0,0,0,0,0], 'o', color='black', markersize=2.5)
    legend_axes.annotate('50 kn', xy=(0.5,1), fontsize=fs_temp)
    legend_axes.annotate('10 kn', xy=(0.4,1), fontsize=fs_temp)
    legend_axes.annotate(' 5 kn', xy=(0.3,1), fontsize=fs_temp)
    legend_axes.annotate('<5 kn', xy=(0.2,1), fontsize=fs_temp)
    legend_axes.annotate('Calm',  xy=(0.1,1), fontsize=fs_temp)
    legend_axes.annotate('25 kn from East', xy=(0.6, 1), fontsize=fs_temp)
    legend_axes.set_ylim([-1.3, 2.5])
    legend_axes.set_xlim([0.08, 0.8])
    
    #%% Create plot of vertical velocity retrieved from VAD algorithm
    ax_temp=ax[1]
    
    w_plot_ext=np.hstack([w_plot,np.full([w_plot.shape[0],1],np.nan)])
    datenum_plot_ext=np.hstack([datenum_plot,datenum_plot[-1]+np.median(np.diff(datenum_plot))])
    
    ax_temp.set_facecolor('#DDDDDD')
    pc_temp=ax_temp.pcolormesh(datenum_plot_ext,height,w_plot_ext,\
                   cmap=c_map_rv,vmin=-3,vmax=3)
    ax_temp.set(xlim=x_lim,xticks=x_ticks,xticklabels=[])
    ax_temp.set(ylim=y_lim,yticks=y_ticks,yticklabels=y_ticklabels) 
    ax_temp.grid()
    
    cb_temp=fig.colorbar(pc_temp,cax=cax[1],ticks=np.arange(-3,4,1),extend='both')
    cb_temp.set_label('w (m s$^{-1}$)')
    
    #%% Variance of variations from the estimated wind vector
    ax_temp=ax[2]
    
    rv_fluc_var_plot_ext=np.hstack([rv_fluc_var_plot,np.full([rv_fluc_var_plot.shape[0],1],np.nan)])
    datenum_plot_ext=np.hstack([datenum_plot,datenum_plot[-1]+np.median(np.diff(datenum_plot))])
    
    ax_temp.set_facecolor('#DDDDDD')
    pc_temp=ax_temp.pcolormesh(datenum_plot_ext,height,rv_fluc_var_plot_ext,\
                   cmap=c_map_snr,vmin=0,vmax=4)
    ax_temp.set(xlim=x_lim,xticks=x_ticks,xticklabels=x_ticklabels)
    ax_temp.set(ylim=y_lim,yticks=y_ticks,yticklabels=y_ticklabels) 
    ax_temp.set_xlabel('time (UTC)')
    ax_temp.grid()
    
    cb_temp=fig.colorbar(pc_temp,cax=cax[2],ticks=np.arange(0,4.1,1),extend='both')
    cb_temp.set_label('$\overline{v_r^{\prime 2}}$ (m$^2$ s$^{-1}$)')
    
    fig.text(.1,.5,'height above reference level (km)',rotation=90,va='center')
    fig.text(.16,.93,'reference level: %i m MSL' %z_ref,ha='left',va='top',size=12)
    fig.text(0.5,0.95,'%s lidar at %s (%s m MSL): %s' %(lidar_str,location,z_ref,mdates.num2datestr(date_num,'%d-%b-%Y')),ha='center',va='bottom')
    
    # save figure
    plot_file_name='%s_%s_vad.png' %(lidar_str,date_str)
    plt.savefig(os.path.join(path_out,plot_file_name),bbox_inches='tight')
    plt.close(fig)
    
    plt.ion()