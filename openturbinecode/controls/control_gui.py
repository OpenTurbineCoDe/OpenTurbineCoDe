# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 14:12:35 2020
# The CCD GUI for the framework
@author: Xianping Du (xianping.du@gmail.com)
"""
# Config program using PyQt5

import sys
import os
import ast
import matplotlib.pyplot as plt
import shutil, tempfile, math, numpy, string
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import subprocess
import scp
import pandas as pd

import openturbinecode.controls.control_module as ctrl

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) +os.sep+ "ConfigControl_v3.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myCtrl, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.myCtrl = myCtrl #make the control module available
              
        # =================== INITIALIZE FIELD VALUES ==============================
        self.myCtrl.setDefaultValues()
        self.writeToUI()
        

        # =================== CONNECT BUTTONS AND ACTIONS ==============================
        # Bind the event handlers to the buttons using a function
        # determine the model selection interface
        self.ModelSelection.activated.connect(self.ModelSelectionUI)
        # General
        self.LoadUsrModel.clicked.connect(self.LoadInherentMod)
        self.toolButton_8.activated.connect(self.Setuserfile)
        self.LoadUsFile.clicked.connect(self.Loaduserfile)
        # Parametric Sweep
        self.toolButton_6.clicked.connect(self.caller_setyamlWorkingDir)
        self.ControlTune.clicked.connect(self.caller_RunRoscoTune)
        self.SetOutDir.clicked.connect(self.caller_SetOutputDir)
        self.WritoutModel.clicked.connect(self.caller_Writeout)
        self.PushRun.clicked.connect(self.caller_LocalRun)
        self.SendToHPC_2.clicked.connect(self.caller_SendToHPCf)
        self.LoadResults_2.clicked.connect(self.caller_HPCloadf)
        # Optimization
        self.PushRunCCD.clicked.connect(self.caller_RunCCD)

    # ======== Functions to fill the UI, or to retrieve info from the UI =====
    def writeToUI(self):
        #Set interface values
        self.lineEdit_32.setText(str(self.myCtrl.ROSCOR2Omega))
        self.lineEdit_31.setText(str(self.myCtrl.ROSCOR2Zeta))
        self.lineEdit_35.setText(str(self.myCtrl.ROSCOR3Omega))
        self.lineEdit_36.setText(str(self.myCtrl.ROSCOR3Zeta))
        self.lineEdit_37.setText(str(self.myCtrl.PlatformKp))
        # Run Simulation
        self.lineEdit_52.setText(str(self.myCtrl.DLCVelocity))
        # Run on HPC
        self.lineEdit_27.setText(self.myCtrl.Username)
        self.lineEdit_26.setText(self.myCtrl.Server)
        self.lineEdit_25.setText(self.myCtrl.HPCPath)
        # Parameterization
        self.lineEdit_29.setText(str(self.myCtrl.ChordStations))
        self.lineEdit_45.setText(str(self.myCtrl.TwistStations))
        self.lineEdit_40.setText(str(self.myCtrl.ThickStations))
        self.lineEdit_30.setText(str(self.myCtrl.Limits))
        # Optimization
        self.lineEdit_23.setText(str(self.myCtrl.Iterations))
        self.lineEdit_28.setText(str(self.myCtrl.Tolerane))


    def ModelSelectionUI(self):
        print("Current model:"+str(self.myCtrl.ModelSelected))
        if self.comboBox.currentText() == "User Model":
            self.StackedFIleIO.setCurrentIndex(1)
        else:
            self.StackedFIleIO.setCurrentIndex(0)
            
    def LoadInherentMod(self):
        
    def Setuserfile(self):
        pass
        
    def Loaduserfile(self):
        pass
    
        
    def caller_setyamlWorkingDir(self):   #load the control parameters txt file
        #self.ctrldir = str(QtWidgets.QFileDialog.getExistingDirectory())
        (filePath, fileType) = QtWidgets.QFileDialog.getOpenFileName()
        self.lineEdit_25.setText(filePath)
        self.myCtrl.YamlFile=filePath

    # ============== Caller functions: gather params from the GUI and calls specific function ==================
    def caller_RunRoscoTune(self):
        #read parameters if needed
        #...
        #alternativly, re-read the entire GUI information if you define the readFromUI function:
        # self.readFromUI()

        #Call the function:
        self.myCtrl.RunRoscoTune()
        
    def caller_SetOutputDir(self):
        
    def caller_Writeout(self):
        

        
    def caller_LocalRun(self):
        #read params from the GUI (TENTATIVELY USING VELOCITY FIELD FOR THE DEMO):
        folder = self.lineEdit_39.text()
        #alternativly, re-read the entire GUI information if you define the readFromUI function:
        # self.readFromUI()

        #execute function through the control object
        self.myCtrl.LocalRun( folder + "/5MW_Land_BD_DLL_WTurb.fst")
    
    def caller_SendToHPCf(self):
        #read parameters if needed
        self.readFromUI()
        orig = "dummy" #TODO
        
        #Call the function:
        self.myCtrl.SendToHPCf(self,orig)
        
    def caller_HPCloadf(self):
        #read parameters if needed
        self.readFromUI()
        orig = "dummy" #TODO
        
        #Call the function:
        self.myCtrl.HPCloadf(self,orig)
        
    def caller_RunCCD(self):
        #read parameters if needed
        #...
        # self.readFromUI()
        #Call the function:
        self.myCtrl.RunCCD()


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    path_to_case = "./"
    
    #empty control object
    myCtrl = ctrl.Control(path_to_case)

    myWindow = Mapper(myCtrl)
    myWindow.show()
    app.exec_()

