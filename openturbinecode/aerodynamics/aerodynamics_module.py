

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from openturbinecode.aerodynamics.aero_wrapper import aero_Wrapper
import openturbinecode.utils.io as io

class Aerodynamics:
    def __init__(self, path_to_case, turb_data=None, models=None, plotonly=False):
        
        self.turb_data = turb_data
        self.models = models
        self.path_to_case = path_to_case

        self.setDefaultValues()

        self.caseToRun = []

        self.plotonly = plotonly
              
    # ==================== GENERAL FUNCTIONS ==========================================
        
    def setDefaultValues(self):

        path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))

        # Initialization of attributes
        if self.turb_data and self.models:
            #Will read directly from turb_data, so nothing to do here
            pass
        else:
            #pre-load a turbine
            path_to_TMP = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
            turb_yaml = path_to_TMP + os.sep + "Madsen2019_10.yaml"
            self.reload_turbdata(turb_yaml)
            
        self.case_tag = "DTU_10MW"
            
        # global parameters
        self.fidelity = "AeroDyn"
        self.DLC = 0 #TODO: read from models
        self.selectDLC(self.DLC)
        self.mesh_level = "2" #TODO: read from models

        #parameters for sweep:
        self.tsrlist = np.array([9.34,7.81,7.81,7.47]) #TODO: read from models
        self.Vlist = np.array([6.,8.,10.,12.]) #TODO: read from models
        self.pitchlist = np.array([0.,0.,0.,0.]) #TODO: read from models
        self.bladeRlist = np.array([1.,1.,1.,1.]) #TODO: read from models

        #results
        self.torque = np.nan*self.Vlist
        self.thrust = np.nan*self.Vlist
        self.cp     = np.nan*self.Vlist

        #predefined list of velocities for precomputed DLCs
        self.Vdlc = np.array([6.,8.,10.,12.]) #np.array(range(5,16)) 
        #self.DLCtag = "iea10MW"    #Commented out by TG 8/15
        self.DLCtag = "iea10mw"    #TG 8/15. Files have lowercase mw
        self.path_to_wind = path_to_root + os.sep + "models" + os.sep + "defaults" + os.sep + "pregenerated_DLCs"
        
        # self.Username = "xd101"
        # self.Server   = "amarel.rutgers.edu"
        # self.HPCPath  = "/scratch/xd101/Subroutine-ROSCODemo"
            
    def setPathToCase(self,path_to_case):    
        self.path_to_case = path_to_case

    def selectDLC(self,DLCtype):
        if DLCtype == 0:
            self.DLC = DLCtype
            if self.fidelity == "OpenFAST":
                self.fidelity = "AeroDyn" 
        if DLCtype > 0 :
            self.DLC = DLCtype
            self.fidelity = "OpenFAST" #override
            # set velocities to the preset values from precomputed DLCs
            self.Vlist = self.Vdlc
        elif DLCtype < 0 :
            #TODO: set DLC to the internal value !
            #TODO: adapt fidelity if needed!
            print("CAUTION: the use of DLC computed from the main tab is not yet available!")

    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================

    def reload_turbdata(self,path):
        try:
            self.turb_data = io.load_yaml(path)
        except FileNotFoundError:
            print("CAUTION: file not found at "+path)
        except IsADirectoryError:
            print("CAUTION: I did not find a yaml file at "+path)

    def Run(self):

        T = 273.25 
        rho = self.turb_data["environment"]["air_density"]
        R0 = self.turb_data["components"]["hub"]["diameter"] / 2.
        R = self.turb_data["assembly"]["rotor_diameter"] / 2.
        Nblade =  self.turb_data["assembly"]["number_of_blades"]

        options = {}

        options["path_to_case"] = self.path_to_case
        options["case_tag"] = self.case_tag
        options["fidelity"] = self.fidelity

        options["spanDir"] = "y" 
        options["rotsign"] = 1 
        options["hifimesh"] = self.mesh_level
        # options["output"] = "..."

        options["plotonly"] = self.plotonly

        options["DLC"] = {}
        options["DLC"]["type"] = self.DLC
        options["DLC"]["DLCtag"] = self.DLCtag
        options["DLC"]["path_to_wind"] = self.path_to_wind

        options["withFlexibility"] = False

        try:
            torque, thrust, cp = aero_Wrapper(self.tsrlist, self.Vlist, self.pitchlist, T, rho, R0, R, Nblade, options, Rlist=self.bladeRlist)
        except KeyboardInterrupt:
            print("interrupted run...")
            torque = np.nan*self.Vlist
            thrust = np.nan*self.Vlist
            cp = np.nan*self.Vlist

        self.torque = np.array(torque)
        self.thrust = np.array(thrust)
        self.cp     = np.array(cp)


    def PlotCp(self):
        plt.ion()
        f = plt.figure(num=1,figsize=(10, 7.5)) #(8, 3.2)
    
        plt.plot(self.Vlist, self.cp, label=self.fidelity, marker="+")

        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
        plt.ylabel(r"$C_p$", fontsize=16)
        plt.grid()
        plt.tick_params(axis="both", labelsize=16)
        plt.legend(fontsize=16)
        f.tight_layout()

        plt.show()

    def PlotThrust(self):
        
        plt.ion()
        f = plt.figure(num=2,figsize=(10, 7.5)) #(8, 3.2)
    
        plt.plot(self.Vlist, self.thrust / 1.e6, label=self.fidelity, marker="+")

        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
        plt.ylabel(r"Thrust [MW]", fontsize=16)
        plt.grid()
        plt.tick_params(axis="both", labelsize=16)
        plt.legend(fontsize=16)
        f.tight_layout()

        plt.show()

    def PlotTorque(self):
        plt.ion()
        f = plt.figure(num=3,figsize=(10, 7.5)) #(8, 3.2)
    
        plt.plot(self.Vlist, self.torque / 1.e6, label=self.fidelity, marker="+")

        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
        plt.ylabel(r"Torque [MNm]", fontsize=16)
        plt.grid()
        plt.tick_params(axis="both", labelsize=16)
        plt.legend(fontsize=16)
        f.tight_layout()

        plt.show()

if __name__=='__main__':

    cwd = os.getcwd()

    path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
    path_to_case = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
    # path_to_case = os.getcwd() + os.sep + "Madsen2019" + os.sep 

    myAero = Aerodynamics(path_to_case)

    myAero.setDefaultValues()
    myAero.Run()
    myAero.PlotCp()
