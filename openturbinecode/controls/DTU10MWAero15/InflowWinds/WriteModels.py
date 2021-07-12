#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 23 22:41:36 2021

@author: seager
"""
import subprocess
from pyFAST.input_output import FASTInputFile,FASTOutputFile

for i in range(21):
    inflowfile="InflowWind_NTW_DLC1.2_v"+str(i+5)+".dat"
    subprocess.run(["cp","InflowWind_NTW_DLC1.2_v4.dat",inflowfile])
    windfile=FASTInputFile(inflowfile)
    windfile['FileName_BTS']='"DLCs/DTU10_NTW_DLC1.2_v'+str(i+5)+'.bts"'
    windfile.write()