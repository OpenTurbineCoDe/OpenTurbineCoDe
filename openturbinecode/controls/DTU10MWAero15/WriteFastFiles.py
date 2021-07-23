#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 23 23:10:41 2021

@author: seager
"""
from multiprocess import Pool
import subprocess

try:
    from pyFAST.input_output import FASTInputFile,FASTOutputFile
except ImportError as err:
    _has_pyfast = False
else:
    _has_pyfast = True

import numpy as np
   #%%
for i in range(21):
    fastfile="DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_v"+str(i+5)+".fst"
    subprocess.run(["cp","DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_v4.fst",fastfile])
    fastfile=FASTInputFile(fastfile)
    fastfile['InflowFile']='"InflowWinds/InflowWind_NTW_DLC1.2_v'+str(i+5)+'.dat"'
    fastfile.write()
#%% Write the time step
for i in range(22):
    fastfile="DTU10MWAero15/DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_v"+str(i+4)+".fst"
    fastfile=FASTInputFile(fastfile)
    fastfile['TMax']=650
    fastfile['DT']=0.025
    fastfile['DT_Out']=0.05
    fastfile.write()   
#%% run fast file in parallel
def openfastrun(x):
    fastfile="DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_v"+str(x)+".fst"
    subprocess.run(["openfast",fastfile])
    

N=25    # number of cases
cases=np.arange(4,N+1,1)

ncore=4
with Pool(ncore) as pool:
    pool.map(openfastrun,[x for x in cases])
    
pool.close()