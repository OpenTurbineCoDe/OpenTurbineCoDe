

import sys
import os
import numpy as np
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
        self.tsrlist = np.array([9.6])
        self.Vlist = np.array([8.])


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


        aero_Wrapper(self.args, self.tsrlist, self.Vlist, T, rho, R0, R, Nblade, self.fidelity, options, self.path_to_case)
        


if __name__=='__main__':

    myAero = Aerodynamics("/Users/dg/Documents/BYU/devel/OpenTurbineCoDe/OpenTurbineCoDe/examples/01_Aerodynamics_demoGUI/")
    myAero.setDefaultValues()
    myAero.Run()
