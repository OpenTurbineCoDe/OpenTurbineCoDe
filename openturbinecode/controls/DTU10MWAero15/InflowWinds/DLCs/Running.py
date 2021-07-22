#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 23 21:14:25 2021

@author: seager
"""
import subprocess
#from multiprocess import Pool
#import numpy as np

for i in range(22):
    turbfile="DTU10_NTW_DLC1.2_v"+str(i+4)+".inp"
    subprocess.run(["turbsim",turbfile])
    
