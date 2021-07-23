#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 16:18:23 2021

@author: seager
"""
import os

try:
    import ROSCO_toolbox.ofTools.fast_io.output_processing as fp
except ImportError as err:
    _has_rosco = False
else:
    _has_rosco = True

try:
    from pCrunch import Analysis
except ImportError:
    _has_pcrunch = False
else:
    _has_pcrunch = True

import numpy as np
#%%
 # postprocessing mutiple openfast simulations
def multipostprocessing(outputfile):
    #filepath: e.g., DTU10MWAero15/
    this_dir            = os.path.dirname(__file__) 
    #%% Initialize processing classes
    # postprocessing for calculating the average power for each wind input
    numbin=22
    # weibull distribution calculated probabilities under 'cdf' or 'pdf'
    pr_bin=[]
    for i in range(numbin):
        #p1=Analysis.Power_Production().prob_WindDist(windspeed=i+3.5,disttype='cdf')
        p=Analysis.Power_Production().prob_WindDist(windspeed=i+4,disttype='pdf')
        pr_bin.append(p)  #weibul distribution
    #%% Collect the fast outputs
    fastoutfiles = outputfile
    fastposts=fp.output_processing()
    fastoutputs=fastposts.load_fast_out(filenames=fastoutfiles)    
    #%% Mean power of each input
    P_bin=[]
    for i in range(22):
        pwr=fastoutputs[i]['GenPwr'].mean()
        P_bin.append(pwr)
    #%% AEP calculation
    P_ave=0
    for i in range(numbin):
        P_ave += pr_bin[i]*P_bin[i]
    AEP=8760*P_ave
    #%% Calculate the mean DEL: blade root M abd F; Tower root M and F;
    chan_infos=[['RootFxb1',4],['RootFyb1',4],['RootMxb1',4],['RootMyb1',4],['TwrBsFxt',4],['TwrBsFyt',4],['TwrBsMxt',4],['TwrBsMyt',4]]
    panalyze=Analysis.Loads_Analysis()
    # load DEL vector
    localDel=panalyze.get_DEL(fast_data=fastoutputs,chan_info=chan_infos, binNum=100, t=600)
    # weibull weighted DEL
    DEL_aveBrFx=0
    DEL_aveBrFy=0
    DEL_aveBrMx=0
    DEL_aveBrMy=0
    DEL_aveTrFx=0
    DEL_aveTrFy=0
    DEL_aveTrMx=0
    DEL_aveTrMy=0
    for i in range(numbin):
        DEL_aveBrFx += pr_bin[i]*localDel['RootFxb1'][i]
        DEL_aveBrFy += pr_bin[i]*localDel['RootFyb1'][i]
        DEL_aveBrMx += pr_bin[i]*localDel['RootMxb1'][i]
        DEL_aveBrMy += pr_bin[i]*localDel['RootMyb1'][i]
        DEL_aveTrFx += pr_bin[i]*localDel['TwrBsFxt'][i]
        DEL_aveTrFy += pr_bin[i]*localDel['TwrBsFyt'][i]
        DEL_aveTrMx += pr_bin[i]*localDel['TwrBsMxt'][i]
        DEL_aveTrMy += pr_bin[i]*localDel['TwrBsMyt'][i]
    # Combine X and Y
    DEL_aveBrF=np.sqrt(DEL_aveBrFx**2+DEL_aveBrFy**2)
    DEL_aveBrM=np.sqrt(DEL_aveBrMx**2+DEL_aveBrMy**2)
    DEL_aveTrF=np.sqrt(DEL_aveTrFx**2+DEL_aveTrFy**2)
    DEL_aveTrM=np.sqrt(DEL_aveTrMx**2+DEL_aveTrMy**2)
    #%% Ultimate strength on these four
    fastposts=fp.output_processing()
    caseUltiStren = os.path.join(this_dir,filepath,'DTU_10MW_NAUTILUS_GoM_A15_DLC6.1_v37.5.out') 
    fastoutput_ulti=fastposts.load_fast_out(filenames=caseUltiStren,tmin=50, tmax=650)
    BrF=np.sqrt(fastoutput_ulti[0]['RootFxb1']**2+fastoutput_ulti[0]['RootFyb1']**2).max()
    BrM=np.sqrt(fastoutput_ulti[0]['RootMxb1']**2+fastoutput_ulti[0]['RootMyb1']**2).max()
    TrF=np.sqrt(fastoutput_ulti[0]['TwrBsFxt']**2+fastoutput_ulti[0]['TwrBsFyt']**2).max()
    TrM=np.sqrt(fastoutput_ulti[0]['TwrBsMxt']**2+fastoutput_ulti[0]['TwrBsMyt']**2).max()
    #%%
    return AEP, [DEL_aveBrF,DEL_aveBrM,DEL_aveTrF,DEL_aveTrM],[BrF,BrM,TrF,TrM]

    