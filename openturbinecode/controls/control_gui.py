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
        self.toolButton_6.clicked.connect(self.setyamlfile)
        self.Loadyaml.clicked.connect(self.loadyamlfile)
        self.ControlTune.clicked.connect(self.caller_ControlTune)
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
        
    def readFromUI(self):
        #Get user inputs data
        self.myCtrl.ModelSelected = ast.literal_eval(self.ModelSelection.currentText()) #no.text function
        # Control params
        self.myCtrl.ROSCOR2Omega = ast.literal_eval(self.lineEdit_32.text())
        self.myCtrl.ROSCOR2Zeta = ast.literal_eval(self.lineEdit_31.text())
        self.myCtrl.ROSCOR3Omega = ast.literal_eval(self.lineEdit_35.text())
        self.myCtrl.ROSCOR3Zeta = ast.literal_eval(self.lineEdit_36.text())
        self.myCtrl.PlatformKp = ast.literal_eval(self.lineEdit_37.text())

        # Run Simulation
        self.myCtrl.Controller = ast.literal_eval(self.comboBox_10.currentText()) #no.text function
        self.myCtrl.DLC = ast.literal_eval(self.comboBox.currentText()) #no.text function
        self.myCtrl.DLCVelocity = ast.literal_eval(self.lineEdit_52.text())
        # Run on HPC
        self.myCtrl.Username = self.lineEdit_27.text()
        self.myCtrl.Server = self.lineEdit_26.text()
        self.myCtrl.HPCPath =self.lineEdit_25.text()
        # Parameterization OpenFAST
        self.myCtrl.ChordStations = ast.literal_eval(self.lineEdit_29.text())
        self.myCtrl.TwistStations = ast.literal_eval(self.lineEdit_45.text())
        self.myCtrl.ThickStations = ast.literal_eval(self.lineEdit_40.text())
        self.myCtrl.Limits = ast.literal_eval(self.lineEdit_30.text())
        self.myCtrl.Objective = ast.literal_eval(self.comboBox_4.currentText())
        # Optimization
        self.myCtrl.Optimizer = ast.literal_eval(self.comboBox_2.currentText()) 
        self.myCtrl.Iterations = ast.literal_eval(self.lineEdit_23.text())
        self.myCtrl.Display = ast.literal_eval(self.comboBox_6.currentText()) 
        self.myCtrl.Tolerane = ast.literal_eval(self.lineEdit_28.text())


    def ModelSelectionUI(self):
        self.readFromUI()
        print("Current model:"+str(self.myCtrl.ModelSelected))
        if self.comboBox.currentText() == "User-specified Model":
            self.StackedFIleIO.setCurrentIndex(1)
        else:
            self.StackedFIleIO.setCurrentIndex(0)
            
    def LoadInherentMod(self):
        self.readFromUI()
        if self.myCtrl.ModelSelected == "LF_OpenFAST_DTU10MW (Local)":
            self.myCtrl.workingmodel == "DTU10MW/"                               # path for DTU10MW model
        if self.myCtrl.ModelSelected == "LF_OpenFAST_NREL5MW (Local)":
            self.myCtrl.workingmodel == "DTU10MW/"                               # path for DTU10MW model
        if self.myCtrl.ModelSelected == "HF_TACS_DTU10MW (Local)":
            self.myCtrl.workingmodel == "DTU10MW/"                               # path for DTU10MW model
        if self.myCtrl.ModelSelected == "HF_TACS_NREL5MW (Local) (Not available Now)":
            print("ERROR: This model is not available now.")
        if self.myCtrl.ModelSelected == "External_model":
            pass # not implemented: function for receiving model path from other module
        
    def Setuserfile(self):
        self.readFromUI()
        (filePath, fileType) = QtWidgets.QFileDialog.getOpenFileName()
        self.lineEdit_55.setText(str(filePath))
        
    def Loaduserfile(self):
        self.readFromUI()
        self.myCtrl.workingmodel=ast.literal_eval(self.lineEdit_55.text())
        print("Loaded file  "+self.myCtrl.workingmodel)
    
        
    def setyamlfile(self):   #load the control parameters txt file
        self.readFromUI()
        (filePath, fileType) = QtWidgets.QFileDialog.getOpenFileName()
        self.lineEdit_53.setText(filePath)
        print("Yaml file selected: "+filePath)
        
    def loadyamlfile(self):   #load the control parameters txt file
        self.myCtrl.YamlFile=filePath
        print("Yaml file loaded: "+filePath)

    # ============== Caller functions: gather params from the GUI and calls specific function ==================
    def caller_ControlTune(self):
        self.readFromUI()
        #if 
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

