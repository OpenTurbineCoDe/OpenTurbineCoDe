# ================================================
# External python imports
# ================================================

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import time

from openturbinecode.aerostructural.aerostruct_wrapper import aerostruct_Wrapper
import openturbinecode.utils.io as io

class Aerostructural:
    def __init__(self, path_to_case, turb_data=None, models=None, plotonly=False, optimize=False):

        self.turb_data = turb_data
        self.models = models
        self.path_to_case = path_to_case

        self.setDefaultValues()

        self.plotonly = plotonly
        self.optimize = optimize      

    # ==================== GENERAL FUNCTIONS ==========================================    
    def setDefaultValues(self):

        # Initialization of attributes
        if self.turb_data and self.models:
            #Will read directly from turb_data, so nothing to do here
            pass
        else:
            #pre-load a turbine
            path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
            path_to_TMP = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
            turb_yaml = path_to_TMP + os.sep + "./Madsen2019_10.yaml"
            self.turb_data = io.load_yaml(turb_yaml)

        self.case_tag = "DTU_10MW" #TODO: this should be read from turbdata!

        Nel = 7 #number of stations spanwise
        # Nel = len(self.turb_data["components"]["blade"]["outer_shape_bem"]["twist"]["values"])

        # geometric parameters - default scaling
        #TODO: read from models
        self.twist = [0.0] * Nel  # Hardcoding vals and number of DVs now
        self.chord = [1.0] * Nel
        self.span = 1.0
        self.precone = 1.0
        self.thickness = [1.0] * Nel

        # global parameters
        self.fidelity = "MACH"  #TODO: read from models
        self.mesh_level = "3" #TODO: read from models

        #parameters for sweep:
        # self.tsrlist = np.array([9.6]) #TODO: read from models
        # self.Vlist = np.array([8.]) #TODO: read from models
        # self.pitchlist = np.array([0.]) #TODO: read from models
        self.tsrlist = np.array([7.81]) #TODO: read from models
        self.Vlist = np.array([8.]) #TODO: read from models
        self.pitchlist = np.array([0.]) #TODO: read from models

        # Optimization
        self.torqueWeight = 0.0
        self.massWeight = 1.0
        self.convergencetolerance = 1e-4
        self.maxiters = 500

        #results
        self.torque = np.nan*self.Vlist
        self.thrust = np.nan*self.Vlist
        self.cp     = np.nan*self.Vlist


        self.Username = "xd101"
        self.Server   = "amarel.rutgers.edu"
        self.HPCPath  = "/scratch/xd101/Subroutine-ROSCODemo"

        self.CaseToHPC = self.path_to_case

            


    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================

    def Run(self):

        T = 273.25 #TODO: environment turb data give speend of sound instead
        rho = self.turb_data["environment"]["air_density"]
        R0 = self.turb_data["components"]["hub"]["diameter"] / 2.
        R = self.turb_data["assembly"]["rotor_diameter"] / 2.
        Nblade =  self.turb_data["assembly"]["number_of_blades"]

        options = {} #TODO:  fill that with whatever is needed...

        options["path_to_case"] = self.path_to_case
        options["case_tag"] = self.case_tag
        options["fidelity"] = self.fidelity

        options["spanDir"] = "y" #TODO: this should come from turbine definition
        options["rotsign"] = 1 #TODO: this should come from turbine definition
        options["hifimesh"] = self.mesh_level
        # options["output"] = "..."

        options["plotonly"] = self.plotonly

        torque, thrust, cp = aerostruct_Wrapper(self.tsrlist, self.Vlist, self.pitchlist, T, rho, R0, R, Nblade, options, self.optimize)
        
        self.torque = np.array(torque)
        self.thrust = np.array(thrust)
        self.cp     = np.array(cp)


    def PlotCp(self):
        plt.ion()
        #TODO: call a proper postpro function, common with aero_compute_standalone
        # f, ax = plt.subplots(figsize=(10, 7.5)) #(8, 3.2)
        f = plt.figure(num=1,figsize=(10, 7.5)) #(8, 3.2)
    
        plt.plot(self.Vlist, self.cp, label=self.fidelity, marker="+")

        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
        plt.ylabel(r"$C_p$", fontsize=16)
        plt.grid()
        plt.tick_params(axis="both", labelsize=16)
        plt.legend(fontsize=16)
        f.tight_layout()

        plt.show(block=True)

    def PlotThrust(self):
        plt.ion()

        #TODO: call a proper postpro function, common with aero_compute_standalone
        # f, ax = plt.subplots(figsize=(10, 7.5)) #(8, 3.2)
        f = plt.figure(num=2,figsize=(10, 7.5)) #(8, 3.2)
    
        plt.plot(self.Vlist, self.thrust / 1.e6, label=self.fidelity, marker="+")

        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
        plt.ylabel(r"Thrust [MW]", fontsize=16)
        plt.grid()
        plt.tick_params(axis="both", labelsize=16)
        plt.legend(fontsize=16)
        f.tight_layout()

        plt.show(block=True)

    def PlotTorque(self):
        plt.ion()

        #TODO: call a proper postpro function, common with aero_compute_standalone
        # f, ax = plt.subplots(figsize=(10, 7.5)) 
        f = plt.figure(num=3,figsize=(10, 7.5)) #(8, 3.2)
    
        plt.plot(self.Vlist, self.torque / 1.e6, label=self.fidelity, marker="+")

        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
        plt.ylabel(r"Torque [MNm]", fontsize=16)
        plt.grid()
        plt.tick_params(axis="both", labelsize=16)
        plt.legend(fontsize=16)
        f.tight_layout()

        plt.show(block=True)

    #  ========================== DATA HANDLING ========================== #

    def SendToHPC(self, folder):
        # Send to HPC for running
        print(f"Sending the content of {folder} to HPC...")
        time.sleep(3)
        # subprocess.run(["scp", orig, dest])
        print("Transfer complete")

    def HPCload(self):
        # Load retults from HPC
        print("Retrieving from HPC")
        # subprocess.run(["scp", orig, dest])
        print("Download complete")

if __name__=='__main__':

    path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
    path_to_case = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
    # path_to_case = os.getcwd() + os.sep + "Madsen2019" + os.sep 

    plotonly = False 
    myAeroStruct = Aerostructural(path_to_case, plotonly=plotonly,optimize=True)
    myAeroStruct.setDefaultValues()
    myAeroStruct.Run()
    myAeroStruct.PlotCp()
