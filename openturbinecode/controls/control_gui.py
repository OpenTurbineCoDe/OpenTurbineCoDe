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
import numpy as np

#import openturbinecode.controls.control_module as ctrl
import control_module as ctrl

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
        self.FidelitySelection.activated.connect(self.FidelitySelectionUI)
        self.ModelSelection.activated.connect(self.ModelSelectionUI)
        # General
        self.LoadUsrModel.clicked.connect(self.LoadInherentMod)
        self.toolButton_8.clicked.connect(self.Setuserfile)
        self.LoadUsFile.clicked.connect(self.Loaduserfile)
        # Parametric Sweep
        self.toolButton_6.clicked.connect(self.setyamlfile)
        self.Loadyaml.clicked.connect(self.loadyamlfile)
        #self.ControlTune.clicked.connect(self.caller_ControlTune)
        #self.SetOutDir.clicked.connect(self.SetOutputDir)
        #self.WritoutModel.clicked.connect(self.caller_Writeout)
        self.PushRun.clicked.connect(self.caller_LocalRun)
        self.Postplot.clicked.connect(self.caller_Postplot)
        self.SendToHPC_2.clicked.connect(self.caller_SendToHPCf)
        self.LoadResults_2.clicked.connect(self.caller_HPCloadf)
        # Constraints
        self.C1.activated.connect(self.C1set)
        self.C2.activated.connect(self.C2set)
        # Optimization
        self.PushRunCCD.clicked.connect(self.caller_RunCCD)

    # ======== Functions to fill the UI, or to retrieve info from the UI =====
    def writeToUI(self):
        # Set system parameters radio button defaults
        self.RB111.setChecked(True)
        self.RB121.setChecked(True)
        self.RB131.setChecked(True)
        self.RB211.setChecked(True)
        self.RB221.setChecked(True)
        self.RB231.setChecked(True)
        
        # set the system parameters for openfast
        self.CHD1.setText(str(self.myCtrl.ChordF))
        self.CHD2.setText(str(self.myCtrl.ChordFL))
        self.CHD3.setText(str(self.myCtrl.ChordFU))
        self.CHD4.setText(str(self.myCtrl.ChordFSTP))
        self.Thick1.setText(str(self.myCtrl.ThickF))
        self.Thick2.setText(str(self.myCtrl.ThickFL))
        self.Thick3.setText(str(self.myCtrl.ThickFU))
        self.Thick4.setText(str(self.myCtrl.ThickFSTP))
        self.TILT1.setText(str(self.myCtrl.TiltAngle))
        self.TILT2.setText(str(self.myCtrl.TiltAngleL))
        self.TILT3.setText(str(self.myCtrl.TiltAngleU))
        self.TILT4.setText(str(self.myCtrl.TiltAngleSTP))
        
        # set the system parameters for TACS based
        self.FlpK1.setText(str(self.myCtrl.BldFpK))
        self.FlpK2.setText(str(self.myCtrl.BldFpKL))
        self.FlpK3.setText(str(self.myCtrl.BldFpKU))
        self.FlpK4.setText(str(self.myCtrl.BldFpKSTP))
        self.ThickL1.setText(str(self.myCtrl.ThickL))
        self.ThickL2.setText(str(self.myCtrl.ThickLL))
        self.ThickL3.setText(str(self.myCtrl.ThickLU))
        self.ThickL4.setText(str(self.myCtrl.ThickLSTP))
        self.RtIner1.setText(str(self.myCtrl.RtInertia))
        self.RtIner2.setText(str(self.myCtrl.RtInertiaL))
        self.RtIner3.setText(str(self.myCtrl.RtInertiaU))
        self.RtIner4.setText(str(self.myCtrl.RtInertiaSTP))
        # Set radio default for control parameters
        self.RB41.setChecked(True)
        self.RB51.setChecked(True)
        self.RB61.setChecked(True)
        self.RB71.setChecked(True)
        self.RB81.setChecked(True)
        
        #Set interface values for control
        self.OMEGAR21.setText(str(self.myCtrl.ROSCOR2Omega))
        self.OMEGAR22.setText(str(self.myCtrl.ROSCOR2OmegaL))
        self.OMEGAR23.setText(str(self.myCtrl.ROSCOR2OmegaU))
        self.OMEGAR24.setText(str(self.myCtrl.ROSCOR2OmegaSTP))
        self.ZETAR21.setText(str(self.myCtrl.ROSCOR2Zeta))
        self.ZETAR22.setText(str(self.myCtrl.ROSCOR2ZetaL))
        self.ZETAR23.setText(str(self.myCtrl.ROSCOR2ZetaU))
        self.ZETAR24.setText(str(self.myCtrl.ROSCOR2ZetaSTP))
        self.OMEGAR31.setText(str(self.myCtrl.ROSCOR3Omega))
        self.OMEGAR32.setText(str(self.myCtrl.ROSCOR3OmegaL))
        self.OMEGAR33.setText(str(self.myCtrl.ROSCOR3OmegaU))
        self.OMEGAR34.setText(str(self.myCtrl.ROSCOR3OmegaSTP))
        self.ZETAR31.setText(str(self.myCtrl.ROSCOR3Zeta))
        self.ZETAR32.setText(str(self.myCtrl.ROSCOR3ZetaL))
        self.ZETAR33.setText(str(self.myCtrl.ROSCOR3ZetaU))
        self.ZETAR34.setText(str(self.myCtrl.ROSCOR3ZetaSTP))
        self.PLATK1.setText(str(self.myCtrl.PlatformKp))
        self.PLATK2.setText(str(self.myCtrl.PlatformKpL))
        self.PLATK3.setText(str(self.myCtrl.PlatformKpU))
        self.PLATK4.setText(str(self.myCtrl.PlatformKpSTP))
        # Run Simulation
        self.DLCV.setText(str(self.myCtrl.DLCV))
        # Run on HPC
        self.lineEdit_27.setText(self.myCtrl.Username)
        self.lineEdit_26.setText(self.myCtrl.Server)
        self.lineEdit_25.setText(self.myCtrl.HPCPath)
        # Constraints: using 0.0 and will initiate later
        self.CV1.setText(str(0.0))
        self.CV2.setText(str(0.0))
        # Optimization
        self.Iterations.setText(str(self.myCtrl.Iterations))
        self.Tolerane.setText(str(self.myCtrl.Tolerane))
        
    def readFromUI(self):
        #Get user inputs data
        self.myCtrl.Modelfidelity   = self.FidelitySelection.currentText() #no.text function
        self.myCtrl.ModelSelected   = self.ModelSelection.currentText() 
        # system: FAST
        self.myCtrl.ChordF          = self.CHD1.text()
        self.myCtrl.ChordFL         = self.CHD2.text()
        self.myCtrl.ChordFU         = self.CHD3.text()
        self.myCtrl.ChordFSTP       = self.CHD4.text()
        
        self.myCtrl.ThickF          = self.Thick1.text()
        self.myCtrl.ThickFL         = self.Thick2.text()
        self.myCtrl.ThickFU         = self.Thick3.text()
        self.myCtrl.ThickFSTP       = self.Thick4.text()
        
        self.myCtrl.TiltAngle       = self.TILT1.text()
        self.myCtrl.TiltAngleL      = self.TILT2.text() # (deg)
        self.myCtrl.TiltAngleU      = self.TILT3.text() # (deg)
        self.myCtrl.TiltAngleSTP    = self.TILT4.text() # (deg)
        
        # system: TACS based ROM
        self.myCtrl.BldFpK          = self.FlpK1.text() # N/m
        self.myCtrl.BldFpKL         = self.FlpK2.text()
        self.myCtrl.BldFpKR         = self.FlpK3.text()
        self.myCtrl.BldFpKSTP       = self.FlpK4.text()
        
        self.myCtrl.ThickL          = self.ThickL1.text()
        self.myCtrl.ThickLL         = self.ThickL2.text()
        self.myCtrl.ThickLU         = self.ThickL3.text()
        self.myCtrl.ThickLSTP       = self.ThickL4.text()
        
        self.myCtrl.RtInertia       = self.RtIner1.text() # kg*m^2
        self.myCtrl.RtInertiaL      = self.RtIner2.text() 
        self.myCtrl.RtInertiaU      = self.RtIner3.text()
        self.myCtrl.RtInertiaSTP    = self.RtIner4.text()
        
        # Controller
        self.myCtrl.Controller      = self.comboBox_10.currentText() 
        #set default text for general parameters
        self.myCtrl.ROSCOR2Omega    = self.OMEGAR21.text()
        self.myCtrl.ROSCOR2OmegaL   = self.OMEGAR22.text()
        self.myCtrl.ROSCOR2OmegaU   = self.OMEGAR23.text()
        self.myCtrl.ROSCOR2OmegaSTP = self.OMEGAR24.text()
        
        self.myCtrl.ROSCOR2Zeta     = self.ZETAR21.text()
        self.myCtrl.ROSCOR2ZetaL    = self.ZETAR22.text()
        self.myCtrl.ROSCOR2ZetaU    = self.ZETAR23.text()
        self.myCtrl.ROSCOR2ZetaSTP  = self.ZETAR24.text()
        
        self.myCtrl.ROSCOR3Omega    = self.OMEGAR31.text()
        self.myCtrl.ROSCOR3OmegaL   = self.OMEGAR32.text()
        self.myCtrl.ROSCOR3OmegaU   = self.OMEGAR33.text()
        self.myCtrl.ROSCOR3OmegaSTP = self.OMEGAR34.text()
        
        self.myCtrl.ROSCOR3Zeta     = self.ZETAR31.text()
        self.myCtrl.ROSCOR3ZetaL    = self.ZETAR32.text()
        self.myCtrl.ROSCOR3ZetaU    = self.ZETAR33.text()
        self.myCtrl.ROSCOR3ZetaSTP  = self.ZETAR34.text()
        
        self.myCtrl.PlatformKp      = self.PLATK1.text()
        self.myCtrl.PlatformKpL     = self.PLATK2.text()
        self.myCtrl.PlatformKpU     = self.PLATK3.text()
        self.myCtrl.PlatformKpSTP   = self.PLATK4.text()
        # DLC case
        self.myCtrl.DLCs            = self.DLCs.currentText() 
        self.myCtrl.DLCV            = self.DLCV.text()
        # Constraints
        self.myCtrl.C1              = self.C1.currentText() 
        self.myCtrl.CS1             = self.CS1.currentText() 
        self.myCtrl.CV1             = self.CV1.text()
        self.myCtrl.C2              = self.C2.currentText() 
        self.myCtrl.CS2             = self.CS2.currentText() 
        self.myCtrl.CV2             = self.CV2.text()
        # Objective
        self.myCtrl.Objective       = self.Objective.currentText()
        # Yaml file
        self.myCtrl.YamlFile             = self.Yamlefile.text()
        # self.output=""
        self.myCtrl.Username        = "xd101"
        self.myCtrl.Server          = "amarel.rutgers.edu"
        self.myCtrl.HPCPath         = "/scratch/xd101/Subroutine-ROSCODemo"
        
        # Optimization configuration
        self.myCtrl.Optimizer       = self.Optimizer.currentText()
        self.myCtrl.Display         = self.Display.currentText() 
        self.myCtrl.Iterations      = self.Iterations.text()
        self.myCtrl.Tolerane        = self.Tolerane.text()

       
    def FidelitySelectionUI(self):
        self.readFromUI()
        fidelity = str(self.myCtrl.Modelfidelity)
        print("Current model type:"+fidelity)
        if fidelity == "OpenFAST":
            self.StackedSysIo.setCurrentIndex(0)          
        else:
            self.StackedSysIo.setCurrentIndex(1)  
            
    def ModelSelectionUI(self):
        self.readFromUI()
        model = str(self.myCtrl.ModelSelected)
        print("Current model:"+model)
        if model == "User_Model":
            self.StackedFIleIO.setCurrentIndex(0)
        else:
            self.StackedFIleIO.setCurrentIndex(1)
            
    def LoadInherentMod(self):
        self.readFromUI()
        if self.myCtrl.ModelSelected == "DTU10MW(Local)" and self.myCtrl.Modelfidelity == "OpenFAST":
            self.myCtrl.workingmodelOpenFAST == self.myCtrl.DTU10MWOpenFAST                    # should from yaml         
            print("DTU10MW OpenFAST model loaded from library for CCD: "+ self.myCtrl.workingmodelOpenFAST)
        if self.myCtrl.ModelSelected == "DTU10MW(Local)" and self.myCtrl.Modelfidelity == "ROM_OpenFAST":
            self.myCtrl.workingmodelTACS == self.myCtrl.DTU10MWTACS
            self.myCtrl.workingmodelOpenFAST == self.myCtrl.DTU10MWOpenFAST                              
            print("DTU10MW OpenFAST model loaded from library for ROM  and ROM-based CCD: "+self.myCtrl.workingmodelOpenFAST)
        if self.myCtrl.ModelSelected == "DTU10MW(Local)" and self.myCtrl.Modelfidelity == "ROM_TACS+OpenFAST":
            self.myCtrl.workingmodel == self.myCtrl.DTU10MWTACS  
            print("DTU10MW TACS model and OpenFAST model are loaded from library for ROM and ROM-based CCD: "+ self.myCtrl.workingmodelTACS+" and "+self.myCtrl.workingmodelOpenFAST)                            
        if self.myCtrl.ModelSelected == "User_Model" and self.myCtrl.Modelfidelity == "ROM_TACS+OpenFAST":
            print("ERROR: This model is not available now.")
        if self.myCtrl.ModelSelected == "External_model":
            pass # not implemented: function for receiving model path from other module
        
    def Setuserfile(self):
        self.readFromUI()
        (filePath, fileType) = QtWidgets.QFileDialog.getOpenFileName()
        self.lineEdit_55.setText(str(filePath))
        
    def Loaduserfile(self):
        self.readFromUI()
        self.myCtrl.workingmodelOpenFAST=str(self.lineEdit_55.text())
        print("Loaded file  "+self.myCtrl.workingmodelOpenFAST)
    
    def setyamlfile(self):   #load the control parameters txt file
        self.readFromUI()
        (filePath, fileType) = QtWidgets.QFileDialog.getOpenFileName()
        self.Yamlefile.setText(filePath)
        print("Yaml file selected: "+str(filePath))
        
    def loadyamlfile(self):   #load the control parameters txt file
        self.readFromUI()
        print("Yaml file loaded: "+self.myCtrl.YamlFile)

    # # ============== Caller functions: gather params from the GUI and calls specific function ==================
    def caller_LocalRun(self):
        self.readFromUI()
        if self.myCtrl.Modelfidelity == "OpenFAST":
            # FAST running
            if self.RB112.isChecked():
                sweep = np.arange(float(self.myCtrl.ChordFL),float(self.myCtrl.ChordFU),float(self.myCtrl.ChordFSTP))
                for i in range(len(sweep)):
                    self.myCtrl.ChordFCV = sweep[i]
                    self.myCtrl.RunModelUpdate_OpenFAST()
                    self.myCtrl.LocalRun()
                    self.myCtrl.postprocessOpenFAST()
                self.myCtrl.ChordFCV = self.myCtrl.ChordF
                
            if self.RB122.isChecked():
                sweep = np.arange(float(self.myCtrl.ThickFL),float(self.myCtrl.ThickFU),float(self.myCtrl.ThickFSTP))
                for i in range(len(sweep)):
                    self.myCtrl.ThickFCV = sweep[i]
                    self.myCtrl.RunModelUpdate_OpenFAST()
                    self.myCtrl.LocalRun()
                    self.myCtrl.postprocessOpenFAST()
                self.myCtrl.ThickFCV = self.myCtrl.ThickF
                
            if self.RB132.isChecked():
                sweep = np.arange(float(self.myCtrl.TiltAngleL),float(self.myCtrl.TiltAngleU),float(self.myCtrl.TiltAngleSTP))
                for i in range(len(sweep)):
                    self.myCtrl.TiltAngleCV = sweep[i]
                    self.myCtrl.RunModelUpdate_OpenFAST()
                    self.myCtrl.LocalRun()
                    self.myCtrl.postprocessOpenFAST()
                self.myCtrl.TiltAngleCV = self.myCtrl.TiltAngle
              # Control parameters 
            if self.RB42.isChecked():
                sweep = np.arange(float(self.myCtrl.ROSCOR2OmegaL),float(self.myCtrl.ROSCOR2OmegaU),float(self.myCtrl.ROSCOR2OmegaSTP))
                for i in range(len(sweep)):
                    self.myCtrl.ROSCOR2OmegaCV = sweep[i]
                    self.myCtrl.RunModelUpdate_OpenFAST()
                    self.myCtrl.RunRoscoTune()
                    self.myCtrl.Writeout()
                    self.myCtrl.LocalRun()
                    self.myCtrl.postprocessOpenFAST()
                self.myCtrl.ROSCOR2OmegaCV = self.myCtrl.ROSCOR2Omega
                    
            if self.RB52.isChecked():
                sweep = np.arange(float(self.myCtrl.ROSCOR2ZetaL),float(self.myCtrl.ROSCOR2ZetaU),float(self.myCtrl.ROSCOR2ZetaSTP))
                for i in range(len(sweep)):
                    self.myCtrl.ROSCOR2ZetaCV = sweep[i]
                    self.myCtrl.RunModelUpdate_OpenFAST()
                    self.myCtrl.RunRoscoTune()
                    self.myCtrl.Writeout()
                    self.myCtrl.LocalRun()
                    self.myCtrl.postprocessOpenFAST()
                self.myCtrl.ROSCOR2ZetaCV = self.myCtrl.ROSCOR2Zeta
                
            if self.RB62.isChecked():
                sweep = np.arange(float(self.myCtrl.ROSCOR3OmegaL),float(self.myCtrl.ROSCOR3OmegaU),float(self.myCtrl.ROSCOR3OmegaSTP))
                for i in range(len(sweep)):
                    self.myCtrl.ROSCOR3OmegaCV = sweep[i]
                    self.myCtrl.RunModelUpdate_OpenFAST()
                    self.myCtrl.RunRoscoTune()
                    self.myCtrl.Writeout()
                    self.myCtrl.LocalRun()
                    self.myCtrl.postprocessOpenFAST()
                self.myCtrl.ROSCOR3OmegaCV = self.myCtrl.ROSCOR3Omega
                
            if self.RB72.isChecked():
                sweep = np.arange(float(self.myCtrl.ROSCOR3ZetaL),float(self.myCtrl.ROSCOR3ZetaU),float(self.myCtrl.ROSCOR3ZetaSTP))
                for i in range(len(sweep)):
                    self.myCtrl.ROSCOR3ZetaCV = sweep[i]
                    self.myCtrl.RunModelUpdate_OpenFAST()
                    self.myCtrl.RunRoscoTune()
                    self.myCtrl.Writeout()
                    self.myCtrl.LocalRun()
                    self.myCtrl.postprocessOpenFAST()
                self.myCtrl.ROSCOR3ZetaCV = self.myCtrl.ROSCOR3Zeta
                
        if "HF" in self.myCtrl.Modelfidelity:
            # FOR ROM based model running and control tuning
            if self.RB212.isChecked():
                pass
            if self.RB222.isChecked():
                pass
            if self.RB232.isChecked():
                pass
            if self.RB42.isChecked():
                pass
            if self.RB52.isChecked():
                pass
            if self.RB62.isChecked():
                pass
            if self.RB72.isChecked():
                pass

        self.myCtrl.sweep = sweep
    def caller_Postplot(self):
        self.readFromUI()
        #self.myCtrl.postprocessOpenFAST()
        if self.myCtrl.Objective == "RotThrust_max":
             plt.plot(self.myCtrl.sweep,self.myCtrl.Ft_max,'r-s')
        else:
             plt.plot(self.myCtrl.sweep,self.myCtrl.Tq_max,'r-s')  
        plt.show()
       
    def caller_SendToHPCf(self):
        #read parameters if needed
        self.readFromUI()
        self.myCtrl.SendToHPCf()
        
    def caller_HPCloadf(self):
        #read parameters if needed
        self.readFromUI()
        self.myCtrl.HPCloadf()
    def C1set(self):
        self.readFromUI()
        if self.myCtrl.C1 == "Mr":
            self.CV1.setText(str(self.myCtrl.Constraint_Mr))
        if self.myCtrl.C1 == "DEL_Mbr":
            self.CV1.setText(str(self.myCtrl.Constraint_DEL_Mbr))
        if self.myCtrl.C1 == "DEL_Mtwr":
            self.CV1.setText(str(self.myCtrl.Constraint_DEL_Mtwr))
        if self.myCtrl.C1 == "DEL_Fbr":
            self.CV1.setText(str(self.myCtrl.Constraint_DEL_Fbr))
        if self.myCtrl.C1 == "DEL_Ftwr":
            self.CV1.setText(str(self.myCtrl.Constraint_DEL_Ftwr))
        if self.myCtrl.C1 == "None":
            self.CV1.setText(str(" "))
    def C2set(self):
        self.readFromUI()
        if self.myCtrl.C2 == "Mr":
            self.CV2.setText(str(self.myCtrl.Constraint_Mr))
        if self.myCtrl.C2 == "DEL_Mbr":
            self.CV2.setText(str(self.myCtrl.Constraint_DEL_Mbr))
        if self.myCtrl.C2 == "DEL_Mtwr":
            self.CV2.setText(str(self.myCtrl.Constraint_DEL_Mtwr))
        if self.myCtrl.C2 == "DEL_Fbr":
            self.CV2.setText(str(self.myCtrl.Constraint_DEL_Fbr))
        if self.myCtrl.C2 == "DEL_Ftwr":
            self.CV2.setText(str(self.myCtrl.Constraint_DEL_Ftwr))
        if self.myCtrl.C2 == "None":
            self.CV2.setText(str(" "))
        
    def caller_RunCCD(self):
        #read parameters if needed
        #Finishing this week to implement the CCD and clean the CCD framework simple version
        self.myCtrl.RunCCD()


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    path_to_case = "./"
    
    #empty control object
    myCtrl = ctrl.Control(path_to_case)

    myWindow = Mapper(myCtrl)
    myWindow.show()
    app.exec_()

