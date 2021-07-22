# This script was created and developed by Xianing Du, Rutgers University, xianping.du@gmail.com, 07-11-2021
# It is created for the control module of OpenTurbineCoDe.
# Functions are implemented for both the coding and GUI calling.
# Also, the CCD module can also be called but not merged in this script for a clear classification of codes.

import yaml 
import os
import math
this_dir            = os.path.dirname(__file__) 
# Import ROSCO_toolbox modules 
from ROSCO_toolbox import controller as ROSCO_controller
from ROSCO_toolbox import turbine as ROSCO_turbine
from ROSCO_toolbox.utilities import write_DISCON
from pyFAST.input_output import FASTInputFile,FASTOutputFile
from .TACSDynParams import TACSParams
#from Gen_Ctables import writCtables
from scipy.optimize import curve_fit
import openmdao.api as om
import numpy as np
import subprocess
from datetime import date
import pandas as pd


#%%

class Control:
    def __init__(self, path_to_case, turb_data=None, models=None):
        
        self.turb_data          = turb_data
        self.models             = models
        self.path_to_case       = path_to_case
        self.YamlFile           = "OTCD_DTU10MW.yaml"
        self.DTU10MWOpenFAST    = "DTU10MWAero15/DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_Baseline.fst"
        self.DTU10MWTACS        = "tacs_setup/DTU_10MW_RWT_blade3D_rotated_Single.bdf"
        self.NREL5MWOpenFAST    = ""
        self.workingmodelOpenFAST       = self.DTU10MWOpenFAST
        self.workingmodelTACS       = self.DTU10MWTACS

        self.setDefaultValues()
        
    # ==================== GENERAL FUNCTIONS ==========================================
        
    def setDefaultValues(self):

        # Initialization of attributes
        if self.turb_data and self.models:
            #use turbine data and model data passed as argument to initialize this object
            #... TODO
            pass
        else:
            # system: FAST
            self.ChordF = self.ChordFCV = 0.0 # Also define a current value variable for model update
            self.ChordFL = -0.5
            self.ChordFU = 0.5
            self.ChordFSTP = 0.5
            
            self.ThickF = self.ThickFCV = 0.0
            self.ThickFL = -0.5
            self.ThickFU = 0.5
            self.ThickFSTP = 0.5
            
            self.TiltAngle = self.TiltAngleCV = -5 # (deg)
            self.TiltAngleL = -8. # (deg)
            self.TiltAngleU = -2. # (deg)
            self.TiltAngleSTP = 3. # (deg)
            
            # system: TACS based ROM
            self.BldFpK = self.BldFpKCV = 806463. # N/m
            self.BldFpKL = 706463.
            self.BldFpKU = 906463.
            self.BldFpKSTP = 100000.
            
            self.ThickL = self.ThickLCV = 1814541.
            self.ThickLL = 1614541.
            self.ThickLU = 2014541.
            self.ThickLSTP = 200000.
            
            self.RtInertia = self.RtInertiaCV = 156348032. # kg*m^2
            self.RtInertiaL = 136348032. 
            self.RtInertiaU = 176348032.
            self.RtInertiaSTP = 20000000.
            
            #set default text for general parameters
            self.ROSCOR2Omega = self.ROSCOR2OmegaCV = 0.2
            self.ROSCOR2OmegaL = 0.1
            self.ROSCOR2OmegaU = 0.3
            self.ROSCOR2OmegaSTP = 0.1
            
            self.ROSCOR2Zeta  = self.ROSCOR2ZetaCV = 0.7
            self.ROSCOR2ZetaL  = 0.5
            self.ROSCOR2ZetaU  = 0.9
            self.ROSCOR2ZetaSTP  = 0.2
            
            self.ROSCOR3Omega = self.ROSCOR3OmegaCV = 0.3
            self.ROSCOR3OmegaL = 0.2
            self.ROSCOR3OmegaU = 0.4
            self.ROSCOR3OmegaSTP = 0.1
            
            self.ROSCOR3Zeta  = self.ROSCOR3ZetaCV = 0.7
            self.ROSCOR3ZetaL  = 0.5
            self.ROSCOR3ZetaU  = 0.9
            self.ROSCOR3ZetaSTP  = 0.2
            
            self.PlatformKp   = self.PlatformKpCV = 0.0
            self.PlatformKpL   = 0.0
            self.PlatformKpU   = 0.0
            self.PlatformKpSTP   = 0.0
            
            self.DLCV = 11.4
            # Parametric sweep in GUI
            # self.yaml=""
            # self.output=""
            self.Username = "xd101"
            self.Server   = "amarel.rutgers.edu"
            self.HPCPath  = "/scratch/xd101/Subroutine-ROSCODemo"
            # Optimization constraints: baseline model values
            self.Constraint_Mr             = 41738.8      # rotor mass kg
            self.Constraint_DEL_Mbr        = 399250.1
            self.Constraint_DEL_Mtwr       = 1055163.2
            self.Constraint_DEL_Fbr        = 7234.7
            self.Constraint_DEL_Ftwr       = 19152.7
            
            # Optimization configuration
            self.Iterations     = 10
            self.Tolerane       = 1e-6

            # Set objectives
            self.AEP = []
            self.Ft_max = []
            self.Tq_max = []


    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================
    def RunModelUpdate_OpenFAST(self):
        self.yaml                   = yaml.safe_load(open(self.YamlFile))
        self.path_params            = self.yaml['path_params']
        self.Path                   = self.path_params['FAST_directory']
        FASTFile                    = FASTInputFile(self.workingmodelOpenFAST)
        Elastodynpath               = os.path.join(self.Path,FASTFile['EDFile'].strip('"'))
        ElastoFile                  = FASTInputFile(Elastodynpath)
        ElastoFile['ShftTilt']      = self.TiltAngleCV
        ElastoFile.write()
        # wind write out
        InflowFilePath              = os.path.join(self.Path,FASTFile['InflowFile'].strip('"'))
        InflowFile                  = FASTInputFile(InflowFilePath)
        if self.DLCs == "Uniform_wind":
            InflowFile['WindType']      = 1
            InflowFile['HWindSpeed']      = self.DLCV
            InflowFile.write()
        if self.DLCs == "DLC 1.1" or self.DLCs == "DLC 1.2":
            InflowFile['WindType']      = 3
            windfile = "DTU10_NTW_DLC1.2_v"+str(math.ceil(float(self.DLCV)))+".bts"
            InflowFile['FileName_BTS']      = os.path.join(os.path.split(InflowFile['FileName_BTS'])[0],windfile)
            InflowFile.write()
        else:
            pass

    def RunRoscoTune(self):   # Tune the rosco controller
        # self.YamlFile       = kwargs['YamlFile']
        #---------------------------------- Using the ROSCO_toolbox--------------------------------#
        self.controller_params      = self.yaml['controller_params']
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
        self.controller.omega_vs    = self.ROSCOR2OmegaCV
        self.controller.zeta_vs     = self.ROSCOR2ZetaCV
        self.controller.omega_pc    = self.ROSCOR3OmegaCV
        self.controller.zeta_pc     = self.ROSCOR3ZetaCV
        # self.controller.Kp     = self.ROSCOR3Zeta
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
        print("Running:" + self.workingmodelOpenFAST)
        subprocess.run(["openfast", self.workingmodelOpenFAST])
    def postprocessOpenFAST(self):
        FASTout = FASTOutputFile(os.path.splitext(self.workingmodelOpenFAST)[0]+".out").toDataFrame()
        FASTouts=FASTout.to_numpy()
        self.Ft_max.append(FASTouts[69].max())
        self.Tq_max.append(FASTouts[70].max())
    def RunCCD(self):
        pass
    def SendToHPCf(self):
        # Send to HPC for running
        subprocess.run(["scp", self.path_params['FAST_directory']+'DISCON.IN',self.Username+"@"+self.Server+":"+self.HPCPath+'/5MW_Land_BD_DLL_WTurb/Rosco_tuning'])
        
    def HPCloadf(self):
        # Load retults from HPC
        subprocess.run(["scp", self.Username +"@"+self.Server +":"+self.HPCPath+"/5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.out", 'HPC/'])
    # for control    
        
        

# if __name__=='__main__':
#     pass

