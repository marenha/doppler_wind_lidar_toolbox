#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 07:54:59 2018
colormaps
@author: maren
"""
import matplotlib as mpl
    
def load_colormaps():
    c_map=reverse_colourmap(mpl.cm.get_cmap('Spectral'))
#    c_map=replace_middle_colourmap(c_map)
#    c_map_snr=reverse_colourmap(mpl.cm.get_cmap('winter'))
    c_map_snr=load_colormap_snr()
    c_map_ws=load_color_ws()
    c_map_rv=load_colormap_rv()
    
    return c_map,c_map_snr,c_map_ws,c_map_rv

#def replace_middle_colourmap(cmap_str):
#    cmap=plt.get_cmap(cmap_str)
#    cmaplist=[cmap(i) for i in range(cmap.N)]
#    ind_middle=np.arange(0,(len(cmaplist)))
#    for ind in ind_middle:
#        cmaplist[ind]=tuple([cmaplist[ind][0]-0.2,cmaplist[ind][1]-0.2,cmaplist[ind][2]-0.5,1.0])
#
#    c_map = cmap.from_list('Custom cmap', cmaplist, cmap.N)
#    
#    return c_map

def load_colormap_snr():
    C=["#DCF2F4","#D1ECF0","#C6E7ED","#BBE0E9","#B0DAE5","#A5D4E2",
          "#9BCDDE","#90C6DB","#86BFD8","#7CB7D4","#72AFD0","#69A7CD",
          "#609FC8","#5796C4","#4F8CBF","#4782BA","#3E77B4","#366BAE",
          "#2C5DA6","#134899",  "#1F4D9D","#00529B","#005798","#005C94","#006190","#00658C",
          "#006987","#006D82","#00727E","#007779","#007C74","#00836F",
          "#008A6A","#009165","#009A60","#00A45A","#00B054","#00BC4D",
          "#2CCA46","#65DA3E",  "#65DA3E","#6ECF1D","#75C500","#7ABB00","#7FB200","#82A900",
          "#85A100","#889900","#8A9100","#8B8A00","#8D8300","#8E7C00",
          "#8E7600","#8F7000","#906A00","#906500","#915F00","#915A00",
          "#915600","#925100","#924D00","#924800","#934400","#934003",
          "#933C1A","#943826","#943430","#953138","#952D40","#952A47",
          "#95264D","#962353","#962059","#951D5F","#951A65","#95186A",
          "#94166F","#931574","#921579","#90167E"]
    c_map=mpl.colors.ListedColormap(C)
    
    return c_map

def load_colormap_rv():
    C = ("#023FA5","#2447A4","#344FA5","#4157A7","#4D5FA9","#5768AC","#6170AF","#6B78B2","#7580B6","#7E88BA","#8890BD","#9199C1","#9BA1C5","#A4AAC9","#AEB2CD","#B7BBD1","#C1C3D5","#CACCD9","#D4D5DD","#DDDEE0","#E1DDDE","#DED3D5","#DAC9CB","#D7BEC2","#D3B4BA","#D0AAB1","#CCA0A8","#C8969F","#C48C96","#BF828E","#BB7885","#B76E7D","#B26374","#AD596C","#A84F64","#A3445C","#9E3953","#992C4B","#941D43","#8E063B")
    c_map=mpl.colors.ListedColormap(C)
#    c_map=reverse_colourmap(mpl.cm.get_cmap('RdBu'))
    return c_map

def reverse_colourmap(cmap,name='my_cmap_r'): 
    reverse=[]
    k=[]   

    for key in cmap._segmentdata:    
        k.append(key)
        channel=cmap._segmentdata[key]
        data = []

        for t in channel:                    
            data.append((1-t[0],t[2],t[1]))            
        reverse.append(sorted(data))    

    LinearL=dict(zip(k,reverse))
    my_cmap_r=mpl.colors.LinearSegmentedColormap(name, LinearL) 
    return my_cmap_r

def load_color_ws():
    
    C=[[	1,1,	1],[1,.9882352941,.7960784314	],
        [.8784313725,.9529411765,0.5450980392],[.6705882353,.9058823529,0.5137254902],
        [.4274509804,.862745098,0.5333333333],[0,.8156862745,.5843137255],
        [0,.7725490196,.6470588235],[0,.7254901961,.7058823529],
        [0,.6784313725,.7568627451],[0,.6235294118,.8],
        [0,.5647058824,.831372549],[.2156862745,.4980392157,.8470588235],
        [.4392156863,.4235294118,.8470588235],[.568627451,.3490196078,.8274509804],
        [.6588235294,.2705882353,.7882352941],[.7176470588,.1960784314,.737254902],
        [.7529411765,.137254902,.6784313725],[.7647058824,.1882352941,.3647058824],
        [.823529412,.403921569,.28627451],[.964705882,.543137255,.270588235]]

    c_map=mpl.colors.ListedColormap(C)
    
    return c_map