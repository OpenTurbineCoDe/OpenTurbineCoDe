#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 15:55:09 2021

@author: seager
"""
import os
import numpy as np
import subprocess
import matplotlib.pyplot as plt 
#%%
def fun_mode_tracking(ElastoBldNodes,BModes_path,BModes_file):
    #%%
    BModes_dir=os.path.join(BModes_path,BModes_file)
    
    #BModes_dir='/home/seager/Downloads/CCD_controller/Source/DTU10MWAero15/DTU10MW_ModeTracking/DTU10MWBlade.bmi'
    with open(BModes_dir, 'r') as BMFile:
        lines=BMFile.readlines()
    for i in range(len(lines)):
        if lines[i].find('sec_props_file')!=-1:
            sec_pro_file=lines[i].split()[0]
        if lines[i].find('nselt:')!=-1:
            out_elements=lines[i].split()[0]
            out_elements=int(out_elements)
    sec_pro_dir=os.path.join(BModes_path,sec_pro_file.strip("'"))
    #sec_pro_dir=sec_pro_file.strip("'")
    f= open(sec_pro_dir, "r")
    sec_pro_baseline=f.readlines()
    f.close()
    # create new section property data
    # get the number of stations
    for i in range(len(sec_pro_baseline)):
        if sec_pro_baseline[i].find('n_secs:')!=-1:
            Num_sec=sec_pro_baseline[i].split()[0]
    # extract the data
    Num_sec=int(Num_sec)
    sec_pro_org=np.array([])
    for i in range(Num_sec):
        trans=sec_pro_baseline[5+i].split()
        transs=np.array([])
        for j in range(len(trans)):
            transs=np.append(transs,float(trans[j]))
        sec_pro_org=np.append(sec_pro_org,transs,axis=0)
    sec_pro_org=sec_pro_org.reshape(Num_sec,len(trans))
    # create new section properties
    # changed Bmodel columes in sec_pro_org:1-9: str_tw	tw_iner	mass_den	flp_iner	
    # edge_iner	flp_stff	edge_stff	tor_stff	axial_stff
    sec_pro_new=sec_pro_org
    sec_pro_new[:,1]=ElastoBldNodes[:,2]
    sec_pro_new[:,2]=ElastoBldNodes[:,2]
    sec_pro_new[:,3]=ElastoBldNodes[:,3]
    sec_pro_new[:,4]=ElastoBldNodes[:,9]
    sec_pro_new[:,5]=ElastoBldNodes[:,10]
    sec_pro_new[:,6]=ElastoBldNodes[:,4]
    sec_pro_new[:,7]=ElastoBldNodes[:,5]
    sec_pro_new[:,8]=ElastoBldNodes[:,6]
    sec_pro_new[:,9]=ElastoBldNodes[:,7]
    
    # rewrite the distributed properties
    # the fisrt 5 lines not changed:sec_pro_dir
    with open(sec_pro_dir, 'w') as sec_file:
        for i in range(5):
            sec_file.write(sec_pro_baseline[i])
        for i in range(sec_pro_new.shape[0]):
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,0]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,1]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,2]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,3]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,4]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,5]))
            sec_file.write("{0:16.2f}".format(sec_pro_new[i,6]))
            sec_file.write("{0:16.2f}".format(sec_pro_new[i,7]))
            sec_file.write("{0:16.2f}".format(sec_pro_new[i,8]))
            sec_file.write("{0:16.2f}".format(sec_pro_new[i,9]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,10]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,11]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,12]))
            sec_file.write('\n')
        sec_file.write('\n')
        sec_file.write('**Note: If the above data represents TOWER properties, the following are overwritten:\n')
        sec_file.write('str_tw is set to zero\n')
        sec_file.write('tw_iner is set to zero\n')
        sec_file.write('cg_offst is set to zero\n')
        sec_file.write('sc_offst is set to zero\n')
        sec_file.write('tc_offst is set to zero\n')
        sec_file.write('edge_iner is set equal to flp_iner\n')
        sec_file.write(' edge_stff is set equal to flp_stff\n')
        
    #rerun the BModel simulation
    subprocess.run(["/home/seager/Downloads/CCD_controller/Source/Modetracking/BModes-master/install/bin/bmodes", BModes_dir])
    
    # Extract the bending modes from output file
    # get output file path
    BModes_out_dir=os.path.join(BModes_path,'DTU10MWBlade.out')
    # open and extract the data
    #sec_pro_dir=os.path.join(BModes_path,sec_pro_file.strip("'"))
    fout= open(BModes_out_dir, "r")
    Out_baseline=fout.readlines()
    fout.close()
    # create new section property data
    # get the number of stations
    loc_data=np.array([])   # all modes location
    for i in range(len(Out_baseline)):
        if Out_baseline[i].find('Mode No.')!=-1:
            loc_data=np.append(loc_data,int(i))
    # extract the data: out_elements+1 stations
    NaFre=np.array([])
    Modes=np.array([])
    
    #for i in range(len(loc_data)): # now only extract the first three modes
    for i in range(3):
        trans=Out_baseline[int(loc_data[i])].split()                # for extracting natural frequency
        NaFre=np.append(NaFre,float(trans[6]))                      # Natural frequency of each mode
        ModeMatrix=np.array([])
        for j in range(out_elements+1):                             # for each line
            transd=Out_baseline[int(loc_data[i])+4+j].split()
            transs=np.array([])
            for jj in range(len(transd)):                           # for each num elements
                transs=np.append(transs,float(transd[jj]))
            ModeMatrix=np.append(ModeMatrix,transs,axis=0)
        ModeMatrix=ModeMatrix.reshape(out_elements+1,len(transd))   # Reshape to the matrix form
        # for extracting the mode
        if i==0:
            Modes=np.append(Modes,ModeMatrix[:,1])    # Default: the first mode is the 1st flapwise
        if i==1:
            Modes=np.append(Modes,ModeMatrix[:,3])    # Default: the first mode is the 1st flapwise
        if i==2:
            Modes=np.append(Modes,ModeMatrix[:,1])
    Modes=Modes.reshape(3,out_elements+1)
    Modes=np.c_[ModeMatrix[:,0],Modes.transpose()]                  #combine station and mode shape
    #%% plot the results
    # fig, axs = plt.subplots(1, 3,sharey=True,dpi=600)
    # #fig.subplots_adjust(left=-1)
    # axs[0].plot(Modes[0,:],ModeMatrix[:,0])
    # #axs[0].set_xlim(0, 2)
    # axs[0].set_xlabel('Magnitudes')
    # axs[0].set_ylabel('Length scale')
    # axs[0].grid(True)
    # axs[0].set_title('1st Flapwise')
    
    # axs[1].plot(Modes[1,:],ModeMatrix[:,0])
    # #axs[1].set_xlim(0, 2)
    # axs[1].set_xlabel('Magnitudes')
    # axs[1].set_ylabel('Length scale')
    # axs[1].grid(True)
    # axs[1].set_title('1st edgewise')
    
    # axs[2].plot(Modes[2,:],ModeMatrix[:,0])
    # #axs[2].set_xlim(0, 2)
    # axs[2].set_xlabel('Magnitudes')
    # axs[2].set_ylabel('Length scale')
    # axs[2].grid(True)
    # axs[2].set_title('2nd Flapwise')
    #%%
    return NaFre, Modes