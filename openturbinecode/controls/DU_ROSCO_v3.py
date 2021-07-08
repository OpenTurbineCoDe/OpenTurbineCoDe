# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 14:12:35 2020
# The CCD GUI for the framework
@author: Xianping Du (xianping.du@gmail.com)
"""
# Config program using PyQt5

import sys
import os
import matplotlib.pyplot as plt
import shutil, tempfile, math, numpy, string
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import subprocess
import scp
import pandas as pd

import openturbinecode.main as main

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) +os.sep+ "ConfigControl_v3.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, OTCD, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.OTCD = OTCD #make the framework available
              
        #set placeholder default text for parametric sweep
        self.lineEdit_32.setText("0.2")
        self.lineEdit_31.setText("0.7")
        self.lineEdit_35.setText("0.3")
        self.lineEdit_36.setText("0.7")
        #self.lineEdit_37.setText("0.7")
        #self.lineEdit_38.setText("0.7")
        self.lineEdit_39.setText("11.4")
        self.lineEdit_27.setText("xd101")
        self.lineEdit_26.setText("amarel.rutgers.edu")
        self.lineEdit_24.setText("/scratch/xd101/Subroutine-ROSCODemo")
        # Optimization: FAST
        self.lineEdit_29.setText("[0,0.5,1.0]")
        self.lineEdit_45.setText("[0,0.5,1.0]")
        self.lineEdit_40.setText("[0 0.5,1.0]")
        self.lineEdit_30.setText("[[[0,-0.5,-0.5],[0,-0.5,-0.5],[0,-0.5,-0.5]],[[0,0.5,0.5],[0,0.5,0.5],[0,0.5,0.5]]]")
        # Optimization: TACS
        self.lineEdit_43.setText("[0,0.5,1.0]")
        self.lineEdit_46.setText("[0,0.5,1.0]")
        self.lineEdit_42.setText("[0 0.5,1.0]")
        self.lineEdit_41.setText("[[[0,-0.5,-0.5],[0,-0.5,-0.5],[0,-0.5,-0.5]],[[0,0.5,0.5],[0,0.5,0.5],[0,0.5,0.5]]]")
        # Optimization configuration
        self.lineEdit_23.setText("10")
        self.lineEdit_28.setText("1e-6")
    
        #Get user inputs data
        # self.Baselinemodel = self.ModelSelection.text() #no text function
        self.ROSCOR2Omega = self.lineEdit_32.text()
        self.ROSCOR2Zeta = self.lineEdit_31.text()
        self.ROSCOR3Omega = self.lineEdit_35.text()
        self.ROSCOR3Zeta = self.lineEdit_36.text()
        self.PlatformP1 = self.lineEdit_37.text()
        self.PlatformP2 = self.lineEdit_38.text()
        #self.SimulinkP1 = self.lineEdit_.text()
        #self.SimulinkP2 = self.lineEdit_.text()
        # self.ControlSelection = self.comboBox_3.text() #no text function
        # Run Simulation
        # self.DLC = self.comboBox.text() #no text function
        self.DLCVelocity = self.lineEdit_39.text()
        # Run on HPC
        self.Username = self.lineEdit_27.text()
        self.Server = self.lineEdit_26.text()
        self.HPCPath = self.lineEdit_24.text()
        # Parameterization OpenFAST
        self.FSChordStations = self.lineEdit_29.text()
        self.FSTwistStations = self.lineEdit_45.text()
        self.FSThickStations = self.lineEdit_40.text()
        self.FSLimits = self.lineEdit_30.text()
        # self.FSObjective = self.comboBox_4.text() #no text function
        # Parameterization TACS
        self.TSChordStations = self.lineEdit_43.text()
        self.TSTwistStations = self.lineEdit_46.text()
        self.TSThickStations = self.lineEdit_42.text()
        self.TSLimits = self.lineEdit_41.text()
        # self.TSObjective = self.comboBox_5.text() #no text function
        # Optimization
        # self.Optimizer = self.comboBox_2.text() #no text function
        self.Iterations = self.lineEdit_23.text()
        # self.Display = self.comboBox_6.text() #no text function
        self.Tolerane = self.lineEdit_28.text()
        
        # Bind the event handlers to the buttons using a function
        # Parametric Sweep
        self.toolButton_6.clicked.connect(self.setyamlWorkingDir)
        self.ControlTune.clicked.connect(self.RunRoscoTune)
        self.PushRun.clicked.connect(self.LocalRun)
        #self.saveButton.clicked.connect(self.saveFileDialog)
        self.SendToHPC_2.clicked.connect(self.SendToHPCf)
        self.LoadResults_2.clicked.connect(self.HPCloadf)
        #self.QMessageBox .clicked.connect(self.Message)
        # Optimization
        self.PushRunCCD.clicked.connect(self.RunCCD)

        # ---- TEST BUTTON ---
        self.test_framework.clicked.connect(self.OTCD.sample_hello_world)
        
    
    def setyamlWorkingDir(self):   #load the control parameters txt file
        #self.ctrldir = str(QtWidgets.QFileDialog.getExistingDirectory())
        (filePath, fileType) = QtWidgets.QFileDialog.getOpenFileName()
        self.lineEdit_25.setText(str(filePath))
        self.YamlFile=filePath

    # ============== Caller functions: gather params from the GUI and calls specific function ==================
    def RunRoscoTune(self):
        #TODO: call functions through the OTCD object

        # Function to tune the controller and write to specific lcation in yaml
        if self.ControlSelection == "ROSCO":
            self.YamlFile
            # ROSCO tunning
        elif self.ControlSelection == "Legacy":
            # Only applicable to simulink
            self.YamlFile
            function(SimulinkLegacyTUning)
        else:
            raise TypeError("Controller should be specified.")
            self.textBrowser.append(str("TypeError: Controller should be specified."))
            
    def LocalRun(self):
        
        #read params from the GUI (TENTATIVELY USING VELOCITY FIELD FOR THE DEMO):
        folder = self.lineEdit_39.text()

        #execute function through the OTCD object
        self.OTCD.ctrl_LocalRun( folder + "/5MW_Land_BD_DLL_WTurb.fst")


    def RunCCD(self):
        print('abc')
        # Collect information
        # construct the OPT path
        # CCD based on AutoCCD
        # Show to progress bar
        #self.progressBar.setValue(idx/nTotal*100)  #used in the CCD function
        
    # ============== Functions that we will only need in the GUI, so we do not need to have them explicitely in the control module =================
    def SendToHPCf(self):
        # Send to HPC for running
        subprocess.run(["scp", self.lineEdit_16.text()+'/Rosco_tuning/DISCON.IN',self.lineEdit_13.text()+"@"+self.lineEdit_14.text()+":"+self.lineEdit_15.text()+'/5MW_Land_BD_DLL_WTurb/Rosco_tuning'])
        
    def HPCloadf(self):
        # Load retults from HPC
        subprocess.run(["scp", self.lineEdit_13.text()+"@"+self.lineEdit_14.text()+":"+self.lineEdit_15.text()+"/5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.out",self.lineEdit_16.text()])
        


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    fakeArgs =  {}
    OTCD = main.OpenTurbineCoDe(fakeArgs)

    myWindow = Mapper(OTCD)
    myWindow.show()
    app.exec_()

