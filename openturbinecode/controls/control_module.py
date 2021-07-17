

import sys
import os
# import matplotlib.pyplot as plt
import numpy
import subprocess
import scp
import pandas as pd



class Control:
    def __init__(self, path_to_case, turb_data=None, models=None):
        
        self.turb_data = turb_data
        self.models = models
        self.path_to_case = path_to_case

        self.setDefaultValues()


              
    # ==================== GENERAL FUNCTIONS ==========================================
        
    def setDefaultValues(self):

        # Initialization of attributes
        if self.turb_data and self.models:
            #use turbine data and model data passed as argument to initialize this object
            #... TODO
            pass
        else:
            pass

        #set placeholder default text for parametric sweep
        self.ROSCOR2Omega = 0.2
        self.ROSCOR2Zeta  = 0.7
        self.ROSCOR3Omega = 0.3
        self.ROSCOR3Zeta  = 0.7
        self.PlatformP1   = 0.7
        self.PlatformP2   = 0.7
        
        self.DLCVelocity = 11.4
        self.Username = "xd101"
        self.Server   = "amarel.rutgers.edu"
        self.HPCPath  = "/scratch/xd101/Subroutine-ROSCODemo"
        # Optimization: FAST
        self.FSChordStations = [0,0.5,1.0]
        self.FSTwistStations = [0,0.5,1.0]
        self.FSThickStations = [0,0.5,1.0]
        self.FSLimits        = [[[0,-0.5,-0.5],[0,-0.5,-0.5],[0,-0.5,-0.5]],[[0,0.5,0.5],[0,0.5,0.5],[0,0.5,0.5]]]
        # Optimization: TACS
        self.TSChordStations = [0,0.5,1.0]
        self.TSTwistStations = [0,0.5,1.0]
        self.TSThickStations = [0,0.5,1.0]
        self.TSLimits        = [[[0,-0.5,-0.5],[0,-0.5,-0.5],[0,-0.5,-0.5]],[[0,0.5,0.5],[0,0.5,0.5],[0,0.5,0.5]]]
        # Optimization configuration
        self.Iterations     = 10
        self.Tolerane       = 1e-6

        self.YamlFile=""
        self.ControlSelection = ""


    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================

    def RunRoscoTune(self):
        # Function to tune the controller and write to specific lcation in yaml
        if self.ControlSelection == "ROSCO":
            self.YamlFile
            # ROSCO tunning
        elif self.ControlSelection == "Legacy":
            # Only applicable to simulink
            self.YamlFile
            function(SimulinkLegacyTUning)
        else:
            raise TypeError("Controller should be specified.")
            self.textBrowser.append(str("TypeError: Controller should be specified."))
            
    def LocalRun(self, args):
        # Local run the case for parametric study

        print("I should execute: subprocess.run(\"openfast \" + " + args +")")
        # subprocess.run("openfast " + args)
        
    def RunCCD(self):
        print('abc')
        # Collect information
        # construct the OPT path
        # CCD based on AutoCCD
        # Show to progress bar
        #self.progressBar.setValue(idx/nTotal*100)  #used in the CCD function


    def SendToHPCf(self, orig):
        # Send to HPC for running
        subprocess.run(["scp", orig+'/Rosco_tuning/DISCON.IN',self.Username +"@"+self.Server +":"+self.HPCPath+'/5MW_Land_BD_DLL_WTurb/Rosco_tuning'])
        
    def HPCloadf(self, dest):
        # Load retults from HPC
        subprocess.run(["scp", self.Username +"@"+self.Server +":"+self.HPCPath+"/5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.out", dest])
        
        
        

# if __name__=='__main__':
#     pass

