# This script was created and developed by Xianing Du, Rutgers University, xianping.du@gmail.com, 07-11-2021
# It is created for the control module of OpenTurbineCoDe.
# Functions are implemented for both the coding and GUI calling.
# Also, the CCD module can also be called but not merged in this script for a clear classification of codes.

import yaml 
import os
this_dir            = os.path.dirname(__file__) 
# Import ROSCO_toolbox modules 
from ROSCO_toolbox import controller as ROSCO_controller
from ROSCO_toolbox import turbine as ROSCO_turbine
from ROSCO_toolbox.utilities import write_DISCON
from pyFAST.input_output import FASTInputFile,FASTOutputFile
from TACSDynParams import TACSParams
#from Gen_Ctables import writCtables
from scipy.optimize import curve_fit
import openmdao.api as om
import numpy as np
import subprocess
from datetime import date
# import matlab.engine
# my codes
#from BladeMode import fun_mode_tracking   # self cuntion
#from fastpost import multipostprocessing   # self cuntion



class Control:
    def __init__(self, path_to_case, turb_data=None, models=None):
        
        self.turb_data          = turb_data
        self.models             = models
        self.path_to_case       = path_to_case
        self.DTU10MWOpenFAST    = "DTU10MWAero15/DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_Baseline.fst"
        self.DTU10MWTACS        = "tacs_setup/DTU_10MW_RWT_blade3D_rotated_Single.bdf"
        self.NREL5MWOpenFAST    = "./"
        self.workingmodel       = 'DTU10MWAero15/DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_Baseline.fst'

        self.setDefaultValues()
        
    # ==================== GENERAL FUNCTIONS ==========================================
        
    def setDefaultValues(self):

        # Initialization of attributes
        if self.turb_data and self.models:
            #use turbine data and model data passed as argument to initialize this object
            #... TODO
            pass
        else:
            #set default text for general parameters
            self.ROSCOR2Omega = 0.2
            self.ROSCOR2Zeta  = 0.7
            self.ROSCOR3Omega = 0.3
            self.ROSCOR3Zeta  = 0.7
            self.PlatformKp   = 0.0
            self.DLCVelocity = 11.4
            # Parametric sweep in GUI
            # self.yaml=""
            # self.output=""
            self.Username = "xd101"
            self.Server   = "amarel.rutgers.edu"
            self.HPCPath  = "/scratch/xd101/Subroutine-ROSCODemo"
            # Optimization
            self.ChordStations = [0,0.5,1.0]
            self.TwistStations = [0,0.5,1.0]
            self.ThickStations = [0,0.5,1.0]
            self.Limits        = [[[0,-0.5,-0.5],[0,-0.5,-0.5],[0,-0.5,-0.5]],[[0,0.5,0.5],[0,0.5,0.5],[0,0.5,0.5]]]
            
            # Optimization configuration
            self.Iterations     = 10
            self.Tolerane       = 1e-6

            #self.YamlFile=""
            #self.ControlSelection = ""


    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================

    def RunRoscoTune(self):   # Tune the rosco controller
        # self.YamlFile       = kwargs['YamlFile']
        self.yaml                   = yaml.safe_load(open(self.YamlFile))
        #---------------------------------- Using the ROSCO_toolbox--------------------------------#
        self.controller_params      = self.yaml['controller_params']
        self.path_params            = self.yaml['path_params']
        
        self.turbine_params         = self.yaml['turbine_params']
        self.turbine                     = ROSCO_turbine.Turbine(self.turbine_params)
        self.path_params            = self.yaml['path_params']
        self.FASTfile           = self.path_params['FAST_InputFile']
        # Load Turbine
        self.turbine.load_from_fast(self.FASTfile,self.path_params['FAST_directory'], \
                rot_source = 'txt',txt_filename = self.path_params['rotor_performance_filename'])

        # The yamal file do not need to be rewrite, Just using the data ro tune the controller
        # Instantiate controller tuning and tune controller
        self.controller             = ROSCO_controller.Controller(self.controller_params)
        # define design varaibles
        self.controller.omega_vs    = float(self.ROSCOR2Omega)
        self.controller.zeta_vs     = float(self.ROSCOR2Zeta)
        self.controller.omega_pc    = float(self.ROSCOR3Omega)
        self.controller.zeta_pc     = float(self.ROSCOR3Zeta)
        # self.controller.zeta_pc     = self.ROSCOR3Zeta
        # tune controller
        self.controller.tune_controller(self.turbine)

    def RunRoscoTune_Adv(self):
        pass
        TACSParams(self.YamlFile,self.ThickStations)
        TACSParams.Frequencyanalysis(3)
        bldeMass, sens_Mass2Thick=TACSParams.extractMassstiffness()
        #eng = matlab.engine.start_matlab() #Start an engine
        #eng.RunRoscoTune_Adv(bldeMass)
        
    
    def Writeout(self):
        # Write parameter input file
        self.FASTmodelPath=os.path.join(self.path_params['FAST_directory'], self.path_params['FAST_InputFile'])
        WorkFast_file=FASTInputFile(self.FASTmodelPath)
        Servo_filename_new  = os.path.join(self.path_params['FAST_directory'],WorkFast_file['ServoFile'].strip('"')) 
        Servo_file_new=FASTInputFile(Servo_filename_new)
        Discon_filename_new  = os.path.join(self.path_params['FAST_directory'],Servo_file_new['DLL_InFile'].strip('"'))
        
        param_file = Discon_filename_new   
        write_DISCON(self.turbine,self.controller,param_file=param_file, txt_filename=os.path.join(this_dir,self.path_params['rotor_performance_filename']))
        
    
    
    def LocalRun(self):
        # Local run the case for parametric study
        print("Running:" + self.workingmodel)
        subprocess.run(["openfast", self.workingmodel])
        
    def RunCCD(self):
        print('abc')
        # Collect information
        # construct the OPT path
        # CCD based on AutoCCD
        # Show to progress bar
        #self.progressBar.setValue(idx/nTotal*100)  #used in the CCD function


    def SendToHPCf(self):
        # Send to HPC for running
        subprocess.run(["scp", self.path_params['FAST_directory']+'DISCON.IN',self.Username+"@"+self.Server+":"+self.HPCPath+'/5MW_Land_BD_DLL_WTurb/Rosco_tuning'])
        
    def HPCloadf(self):
        # Load retults from HPC
        subprocess.run(["scp", self.Username +"@"+self.Server +":"+self.HPCPath+"/5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.out", 'HPC/'])
        
        
        

# if __name__=='__main__':
#     pass

