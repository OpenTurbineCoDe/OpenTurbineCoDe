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
        # Parametric Sweep
        self.toolButton_8.clicked.connect(self.Setuserfile)
        self.toolButton_6.clicked.connect(self.setyamlWorkingDir)
        self.ControlTune.clicked.connect(self.caller_RunRoscoTune)
        self.WritoutModel.clicked.connect(self.caller_Writeout)
        self.PushRun.clicked.connect(self.caller_LocalRun)
        self.SendToHPC_2.clicked.connect(self.caller_SendToHPCf)
        self.LoadResults_2.clicked.connect(self.caller_HPCloadf)
        #self.QMessageBox .clicked.connect(self.Message)
        # Optimization
        self.PushRunCCD.clicked.connect(self.caller_RunCCD)

        

    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

    def writeToUI(self):

        #Set interface values
        # self.ModelSelection.setText(str(self.myCtrl.Baselinemodel)) #no text function
        self.lineEdit_32.setText(str(self.myCtrl.ROSCOR2Omega))
        self.lineEdit_31.setText(str(self.myCtrl.ROSCOR2Zeta))
        self.lineEdit_35.setText(str(self.myCtrl.ROSCOR3Omega))
        self.lineEdit_36.setText(str(self.myCtrl.ROSCOR3Zeta))
        self.lineEdit_37.setText(str(self.myCtrl.PlatformP1))
        #self.SimulinkP1 = ast.literal_eval(self.lineEdit_.text
        #self.SimulinkP2 = ast.literal_eval(self.lineEdit_.text
        # self.comboBox_3.setText(str(self.myCtrl.ControlSelection)) #no text function
        # Run Simulation
        # self.comboBox.setText(str(self.myCtrl.DLC)) #no text function
        self.lineEdit_52.setText(str(self.myCtrl.DLCVelocity))
        # Run on HPC
        self.lineEdit_27.setText(self.myCtrl.Username)
        self.lineEdit_26.setText(self.myCtrl.Server)
        self.lineEdit_25.setText(self.myCtrl.HPCPath)
        # Parameterization OpenFAST
        self.lineEdit_29.setText(str(self.myCtrl.FSChordStations))
        self.lineEdit_45.setText(str(self.myCtrl.FSTwistStations))
        self.lineEdit_40.setText(str(self.myCtrl.FSThickStations))
        self.lineEdit_30.setText(str(self.myCtrl.FSLimits))
        # self.comboBox_4.setText(str(self.myCtrl.FSObjective)) #no text function
        # Parameterization TACS
        # self.comboBox_5.setText(str(self.myCtrl.TSObjective)) #no text function
        # Optimization
        # self.comboBox_2.setText(str(self.myCtrl.Optimizer)) #no text function
        self.lineEdit_23.setText(str(self.myCtrl.Iterations))
        # self.comboBox_6.setText(str(self.myCtrl.Display)) #no text function
        self.lineEdit_28.setText(str(self.myCtrl.Tolerane))

        self.lineEdit_25.setText(self.myCtrl.YamlFile)



    def readFromUI(self):
        #Get user inputs data
        # self.myCtrl.Baselinemodel = ast.literal_eval(self.ModelSelection.text()) #no.text function
        self.myCtrl.ROSCOR2Omega = ast.literal_eval(self.lineEdit_32.text())
        self.myCtrl.ROSCOR2Zeta = ast.literal_eval(self.lineEdit_31.text())
        self.myCtrl.ROSCOR3Omega = ast.literal_eval(self.lineEdit_35.text())
        self.myCtrl.ROSCOR3Zeta = ast.literal_eval(self.lineEdit_36.text())
        self.myCtrl.PlatformP1 = ast.literal_eval(self.lineEdit_37.text())
        self.myCtrl.PlatformP2 = ast.literal_eval(self.lineEdit_38.text())
        #self.SimulinkP1 = ast.literal_eval(self.lineEdit_.text())
        #self.SimulinkP2 = ast.literal_eval(self.lineEdit_.text())
        # self.myCtrl.ControlSelection = ast.literal_eval(self.comboBox_3.text()) #no.text function
        # Run Simulation
        # self.myCtrl.DLC = ast.literal_eval(self.comboBox.text()) #no.text function
        self.myCtrl.DLCVelocity = ast.literal_eval(self.lineEdit_39.text())
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

