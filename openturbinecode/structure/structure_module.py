import sys
import os
import matplotlib.pyplot as plt
import shutil, tempfile, math, string
import numpy as np
import subprocess
import scp

#conditional imports
try:
    from PyQt5 import QtCore, QtGui, uic, QtWidgets
    from PyQt5.QtWidgets import QFileDialog
except ImportError as err:
    pass

try:
    from pyFAST.input_output import FASTInputFile,FASTOutputFile
except ImportError as err:
    _has_pyfast = False
else:
    _has_pyfast = True

# try:
#     from TACSDynParams import TACSParams
# except ImportError as err:
#     _has_tacs = False
# else:
    # _has_tacs = True
    
import openturbinecode.utils.io as io
import openturbinecode.utils.utilities as ut

#%%
class Structural:
    def __init__(self, path_to_case, turb_data=None, models=None):
        self.turb_data = turb_data
        self.models = models
        self.path_to_case = path_to_case
        self.DTU10MWBeamDyn    = "BeamDyn/DTU10MW/DTU10MW_driver.inp"
        self.DTU10MWTACS        = "../controls/tacs_setup/DTU_10MW_RWT_blade3D_rotated_Single.bdf"
        self.NREL5MWBeamDyn   = "BeamDyn/NREL5MW/NREL5MW_driver.inp"
        self.workingmodel      = self.DTU10MWBeamDyn

        self.setDefaultValues()
              
    # ==================== GENERAL FUNCTIONS ==========================================
        
    def setDefaultValues(self):

        # Initialization of attributes
        if self.turb_data and self.models:
            #use turbine data and model data passed as argument to initialize this object
            #... TODO
            pass
        else:
            #pre-load a turbine
            path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
            path_to_TMP = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
            turb_yaml = path_to_TMP + os.sep + "./Madsen2019_10.yaml"
            self.turb_data = io.load_yaml(turb_yaml)

        #TODO: read the parameters inside turb_yaml to fill all the following variables (if approprate):

        # system: BeamDyn
        self.TipLoadx = self.TipLoadxCV = 1.0
        self.TipLoadxL = 0.5
        self.TipLoadxU = 1.5
        self.TipLoadxSTP = 0.5
        
        self.DistrLoadx = self.DistrLoadxCV = 1.0
        self.DistrLoadxL = 0.5
        self.DistrLoadxU = 1.5
        self.DistrLoadxSTP = 0.5
        
        self.TwstSclF = self.TwstSclFCV = 1. # (deg)
        self.TwstSclFL = 0.5 # (deg)
        self.TwstSclFU = 1.5 # (deg)
        self.TwstSclFSTP = 0.5 # (deg)
        # system: TACS
        self.ThickSclF1 = self.ThickSclF1CV = 1.0
        self.ThickSclF1L = 0.5
        self.ThickSclF1U = 1.5
        self.ThickSclF1STP = 0.5
        
        self.ThickSclF2 = self.ThickSclF2CV = 1.0
        self.ThickSclF2L = 0.5
        self.ThickSclF2U = 1.5
        self.ThickSclF2STP = 0.5
        
        self.ThickSclF3 = self.ThickSclF3CV = 1.0
        self.ThickSclF3L = 0.5
        self.ThickSclF3U = 1.5
        self.ThickSclF3STP = 0.5
        
        # HPC
        self.Username = "xd101"
        self.Server   = "amarel.rutgers.edu"
        self.HPCPath  = "/scratch/xd101/Subroutine-Structural"
        # response
        self.RootFxr_max = []
        self.RootFyr_max = []
        self.RootMxr_max = []
        self.RootMyr_max = []
        self.TipTDxr_max = []
        self.TipTDyr_max = []
            

    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================

    def RunModelUpdate_Beamdyn(self):
        # 
        print("New design synthesis:" + self.workingmodel)
        BeamFile                       = FASTInputFile(self.workingmodel)
        PrimaryPath                    = os.path.join(os.path.split(self.workingmodel)[0],BeamFile["InputFile"].strip('"'))
        PrimaryFile                    = FASTInputFile(PrimaryPath)
        # DistFilPath                  = os.path.join(os.path.split(PrimaryPath)[0],PrimaryFile["BldFile"].strip('"'))
        # DistFile                     = FASTInputFile(PrimaryPath)
        #
        BeamFile["TipLoad(1)"]         = self.TipLoadxCV
        #
        BeamFile["DistrLoad(1)"]       = self.DistrLoadxCV
        #
        PrimaryFile["MemberGeom"][:,3] = PrimaryFile["MemberGeom"][:,3] * float(self.TwstSclFCV)
        # Write out
        BeamFile.write()     
        PrimaryFile.write() 
        
    def LocalRun(self):
        # local run
        print("Running:" + self.workingmodel)
        conf = ut.read_config()
        bd_driver = conf["lofi"]["path_to_beamdyn"]
        subprocess.run([bd_driver, self.workingmodel])

    def postprocessBeamDyn(self):
        Beamout = FASTOutputFile(os.path.splitext(self.workingmodel)[0]+".out").toDataFrame()
        Beamouts=Beamout.to_numpy()
        self.RootFxr_max.append(Beamouts[1].max())
        self.RootFyr_max.append(Beamouts[2].max())
        self.RootMxr_max.append(Beamouts[3].max())
        self.RootMyr_max.append(Beamouts[4].max())
        self.TipTDxr_max.append(Beamouts[5].max())
        self.TipTDyr_max.append(Beamouts[6].max())


    def sendToHPC(self, lineEdit, lineEdit2, lineEdit3):
        subprocess.run(["scp", "-r", lineEdit.text() ,lineEdit2.text()+"@"+lineEdit2.text()+":"+lineEdit3.text()])
        subprocess.run(["rm", "-r",  self.ALMFolder+"/rpm*"])

# if __name__=='__main__':
#     pass

