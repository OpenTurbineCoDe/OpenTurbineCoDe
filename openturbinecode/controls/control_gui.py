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
        # Model selection
        self.ModelSelection.activated.connect(self.ModelSelection)
        # Parametric Sweep
        self.ModelSelection.activated.connect(self.Setuserfile)
        self.toolButton_8.clicked.connect(self.Setuserfile)
        self.toolButton_6.clicked.connect(self.setyamlWorkingDir)
        self.ControlTune.clicked.connect(self.caller_RunRoscoTune)
        self.WritoutModel.clicked.connect(self.caller_Writeout)
        self.PushRun.clicked.connect(self.caller_LocalRun)
        self.SendToHPC_2.clicked.connect(self.caller_SendToHPCf)
        self.LoadResults_2.clicked.connect(self.caller_HPCloadf)
        # Optimization
        self.PushRunCCD.clicked.connect(self.caller_RunCCD)

        

    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

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
        # Get user inputs data
        
        # self.myCtrl.Baselinemodel = ast.literal_eval(self.ModelSelection.text()) #no.text function
        self.myCtrl.ROSCOR2Omega = ast.literal_eval(self.lineEdit_32.text())
        self.myCtrl.ROSCOR2Zeta = ast.literal_eval(self.lineEdit_31.text())
        self.myCtrl.ROSCOR3Omega = ast.literal_eval(self.lineEdit_35.text())
        self.myCtrl.ROSCOR3Zeta = ast.literal_eval(self.lineEdit_36.text())
        self.myCtrl.PlatformKp = ast.literal_eval(self.lineEdit_37.text())
        # self.myCtrl.ControlSelection = ast.literal_eval(self.comboBox_3.text()) #no.text function
        # Run Simulation
        # self.myCtrl.DLC = ast.literal_eval(self.comboBox.text()) #no.text function
        self.myCtrl.DLCVelocity = ast.literal_eval(self.lineEdit_52.text())
        # Run on HPC
        self.myCtrl.Username = self.lineEdit_27.text()
        self.myCtrl.Server = self.lineEdit_26.text()
        self.myCtrl.HPCPath =self.lineEdit_24.text()
        # Parameterization OpenFAST
        self.myCtrl.FSChordStations = ast.literal_eval(self.lineEdit_29.text())
        self.myCtrl.FSTwistStations = ast.literal_eval(self.lineEdit_45.text())
        self.myCtrl.FSThickStations = ast.literal_eval(self.lineEdit_40.text())
        self.myCtrl.FSLimits = ast.literal_eval(self.lineEdit_30.text())
        # self.myCtrl.FSObjective = ast.literal_eval(self.comboBox_4.text()) #no.text function
        # Parameterization TACS
        self.myCtrl.TSChordStations = ast.literal_eval(self.lineEdit_43.text())
        self.myCtrl.TSTwistStations = ast.literal_eval(self.lineEdit_46.text())
        self.myCtrl.TSThickStations = ast.literal_eval(self.lineEdit_42.text())
        self.myCtrl.TSLimits = ast.literal_eval(self.lineEdit_41.text())
        # self.myCtrl.TSObjective = ast.literal_eval(self.comboBox_5.text()) #no.text function
        # Optimization
        # self.myCtrl.Optimizer = ast.literal_eval(self.comboBox_2.text()) #no.text function
        self.myCtrl.Iterations = ast.literal_eval(self.lineEdit_23.text())
        # self.myCtrl.Display = ast.literal_eval(self.comboBox_6.text()) #no.text function
        self.myCtrl.Tolerane = ast.literal_eval(self.lineEdit_28.text())

    def ModelSelection(self):
        print("Current model:"+str(self.ModelSelection.currentText()))
        if self.comboBox.currentText() == "User Model":
            self.StackedFIleIO.setCurrentIndex(1)
        else:
            self.StackedFIleIO.setCurrentIndex(0)
        
    def setyamlWorkingDir(self):   #load the control parameters txt file
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
        
    def caller_LocalRun(self):
        #read params from the GUI (TENTATIVELY USING VELOCITY FIELD FOR THE DEMO):
        folder = self.lineEdit_39.text()
        #alternativly, re-read the entire GUI information if you define the readFromUI function:
        # self.readFromUI()

        #execute function through the control object
        self.myCtrl.LocalRun( folder + "/5MW_Land_BD_DLL_WTurb.fst")

    def caller_RunCCD(self):
        #read parameters if needed
        #...
        # self.readFromUI()
        #Call the function:
        self.myCtrl.RunCCD()

        
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


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    path_to_case = "./"
    
    #empty control object
    myCtrl = ctrl.Control(path_to_case)

    myWindow = Mapper(myCtrl)
    myWindow.show()
    app.exec_()

