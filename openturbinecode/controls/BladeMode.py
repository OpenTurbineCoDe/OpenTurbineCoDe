#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 15:55:09 2021

@author: Xianping Du, rutgers University, xianping.du@rutgers.edu
"""
import os
import numpy as np
import subprocess
import matplotlib.pyplot as plt 
#%%
def fun_mode_tracking(ElastoBldNodes,BModes_path,BModes_file,BModes_exe):
    #%%
    BModes_dir = os.path.join(BModes_path,BModes_file)
    with open(BModes_dir, 'r') as BMFile:
        lines = BMFile.readlines()
    for i in range(len(lines)):
        if 'sec_props_file' in lines[i]:
            sec_pro_file = lines[i].split()[0]
        if 'nselt:' in lines[i]:
            out_elements = lines[i].split()[0]
            out_elements = int(out_elements)
    sec_pro_dir = sec_pro_file.strip("'")
    f = open(sec_pro_dir, "r")
    sec_pro_baseline = f.readlines()
    f.close()
    # create new section property data: define new number of stations
    Num_sec = len(ElastoBldNodes)
    # create new section properties
    # Rewrite BModes columes in sequence
    sec_pro_new      = np.zeros([len(ElastoBldNodes),13])
    sec_pro_new[:,0] = ElastoBldNodes[:,0]
    sec_pro_new[:,1] = ElastoBldNodes[:,2]
    sec_pro_new[:,2] = ElastoBldNodes[:,2]
    sec_pro_new[:,3] = ElastoBldNodes[:,3]
    sec_pro_new[:,4] = ElastoBldNodes[:,9]
    sec_pro_new[:,5] = ElastoBldNodes[:,10]
    sec_pro_new[:,6] = ElastoBldNodes[:,4]
    sec_pro_new[:,7] = ElastoBldNodes[:,5]
    sec_pro_new[:,8] = ElastoBldNodes[:,6]
    sec_pro_new[:,9] = ElastoBldNodes[:,7]
    
    # rewrite the distributed files
    with open(sec_pro_dir, 'w') as sec_file:
        for i in range(5):
            if 'n_secs:' in sec_pro_baseline[i]:
                StLine              = sec_pro_baseline[i].split()
                StLine[0]           = str(Num_sec)
                sec_pro_baseline[i] = StLine[0]+'    '+StLine[1]+'    '+' '.join(StLine[2:])+'\n'
            sec_file.write(sec_pro_baseline[i])
        for i in range(sec_pro_new.shape[0]):
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,0]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,1]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,2]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,3]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,4]))
            sec_file.write("{0:10.2f}".format(sec_pro_new[i,5]))
            sec_file.write("{0:20.2f}".format(sec_pro_new[i,6]))
            sec_file.write("{0:20.2f}".format(sec_pro_new[i,7]))
            sec_file.write("{0:20.2f}".format(sec_pro_new[i,8]))
            sec_file.write("{0:20.2f}".format(sec_pro_new[i,9]))
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
        
    #rerun the BModel simulation; "/home/seager/Downloads/CCD_controller/Source/Modetracking/BModes-master/install/bin/bmodes"
    subprocess.run([BModes_exe, BModes_dir])
    # Extract the bending modes from output file
    # get output file path
    BModes_out_dir = os.path.join(BModes_path, os. path. splitext(BModes_file)[0]+'.out')
    # open and extract the data
    fout = open(BModes_out_dir, "r")
    Out_baseline = fout.readlines()
    fout.close()
    # create new section property data
    # get the number of stations
    loc_data = np.array([])   # all modes location
    for i in range(len(Out_baseline)):
        if 'Mode No.' in Out_baseline[i]:
            loc_data = np.append(loc_data,int(i))
    # extract the data: out_elements+1 stations
    NaFre = np.array([])
    Modes = np.array([])
    
    # only extract the first three modes
    for i in range(3):
        trans       = Out_baseline[int(loc_data[i])].split()                # for extracting natural frequency
        NaFre       = np.append(NaFre,float(trans[6]))                      # Natural frequency of each mode
        ModeMatrix  = np.array([])
        for j in range(out_elements+1):                                     # for each line
            transd = Out_baseline[int(loc_data[i])+4+j].split()
            transs = np.array([])
            for jj in range(len(transd)):                                   # for each num elements
                transs = np.append(transs,float(transd[jj]))
            ModeMatrix = np.append(ModeMatrix,transs,axis=0)
        ModeMatrix     = ModeMatrix.reshape(out_elements+1,len(transd))     # Reshape to the matrix form
        # for extracting the mode
        if i==0:
            Modes = np.append(Modes,ModeMatrix[:,1])                        # Default: the first mode is the 1st flapwise
        if i==1:
            Modes = np.append(Modes,ModeMatrix[:,3])                        # Default: the first mode is the 1st flapwise
        if i==2:
            Modes = np.append(Modes,ModeMatrix[:,1])
    Modes = Modes.reshape(3,out_elements+1)
    Modes = np.c_[ModeMatrix[:,0],Modes.transpose()]                  # Combine station and mode shape
    
    return NaFre, Modes