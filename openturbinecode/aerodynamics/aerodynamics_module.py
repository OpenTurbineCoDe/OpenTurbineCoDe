

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from openturbinecode.aerodynamics.aero_wrapper import aero_Wrapper
import openturbinecode.utils.io as io

class Aerodynamics:
    def __init__(self, path_to_case, turb_data=None, models=None):
        
        self.turb_data = turb_data
        self.models = models
        self.path_to_case = path_to_case

        self.setDefaultValues()

              
    # ==================== GENERAL FUNCTIONS ==========================================
        
    def setDefaultValues(self):

        # Initialization of attributes
        if self.turb_data and self.models:
            #Will read directly from turb_data, so nothing to do here
            pass
        else:
            #TODO : temp - pre - load a turbine
            turb_yaml = self.path_to_case + os.sep + "./Madsen2019_10.yaml"
            self.turb_data = io.load_yaml(turb_yaml)
            
        from types import SimpleNamespace
        self.args = SimpleNamespace()
        self.args.configuration = "DTU_10MW"
            
        self.fidelity = "AeroDyn"  #TODO: read from models

        #parameters for sweep:
        self.tsrlist = np.array([9.6]) #TODO: read from models
        self.Vlist = np.array([8.]) #TODO: read from models

        #results
        self.torque = np.nan*self.Vlist
        self.thrust = np.nan*self.Vlist
        self.cp     = np.nan*self.Vlist


        # self.Username = "xd101"
        # self.Server   = "amarel.rutgers.edu"
        # self.HPCPath  = "/scratch/xd101/Subroutine-ROSCODemo"
            


    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================

    def Run(self):

        T = 273.25 #TODO: environment turb data give speend of sound instead
        rho = self.turb_data["environment"]["air_density"]
        R0 = self.turb_data["components"]["hub"]["diameter"] / 2.
        R = self.turb_data["assembly"]["rotor_diameter"] / 2.
        Nblade =  self.turb_data["assembly"]["number_of_blades"]

        options = {} #TODO:  fill that with whatever is needed...

        options["spanDir"] = "y"
        options["rotsign"] = 1
        # options["hifimesh"] = args.hifimesh
        # options["output"] = args.output
        # options["plotonly"] = args.plotonly


        torque, thrust, cp = aero_Wrapper(self.args, self.tsrlist, self.Vlist, T, rho, R0, R, Nblade, self.fidelity, options, self.path_to_case)
        
        self.torque = np.array(torque)
        self.thrust = np.array(thrust)
        self.cp     = np.array(cp)


    def PlotCp(self):
        #TODO: call a proper postpro function, common with aero_compute_standalone
        f, ax = plt.subplots(figsize=(10, 7.5)) #(8, 3.2)
    
        plt.plot(self.Vlist, self.cp, label='Results', marker="+")

        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
        plt.ylabel(r"$C_p$", fontsize=16)
        plt.grid()
        plt.tick_params(axis="both", labelsize=16)
        plt.legend(fontsize=16)
        f.tight_layout()

        plt.show()

    def PlotThrust(self):
        #TODO: call a proper postpro function, common with aero_compute_standalone
        f, ax = plt.subplots(figsize=(10, 7.5)) #(8, 3.2)
    
        plt.plot(self.Vlist, self.thrust / 1.e6, label='Results', marker="+")

        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
        plt.ylabel(r"Thrust [MW]", fontsize=16)
        plt.grid()
        plt.tick_params(axis="both", labelsize=16)
        plt.legend(fontsize=16)
        f.tight_layout()

        plt.show()


if __name__=='__main__':

    cwd = os.getcwd()
    myAero = Aerodynamics(cwd)
    myAero.setDefaultValues()
    myAero.Run()
    myAero.PlotCp()
