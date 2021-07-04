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

form_class = uic.loadUiType("ConfigControl_v3.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self,  parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
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
        
        
        #set placeholder default text for parametric sweep
        self.lineEdit_32.setText("0.2")
        self.lineEdit_31.setText("0.7")
        self.lineEdit_35.setText("0.3")
        self.lineEdit_36.setText("0.7")
        self.lineEdit_27.setText("xd101")
        self.lineEdit_26.setText("amarel.rutgers.edu")
        self.lineEdit_24.setText("/scratch/xd101/Subroutine-ROSCODemo")
        #Get user inputs
        self.Baselinemodel=self.ModelSelection.text()
        
    def setyamlWorkingDir(self):   #load the control parameters txt file
        #self.ctrldir = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.yamlfilePath = QtWidgets.QFileDialog.getOpenFileName()
        self.lineEdit_17.setText(str(self.yamlfilePath))

    def RunRoscoTune(self):
        # Tune the ROsco controller and also tune the simulink model
        fname1 = open(self.lineEdit_17.text(), 'r')  #newline='\r\n'
        fname = open(self.lineEdit_16.text()+'/Rosco_tuning/DISCON.IN', 'w')
        for x in list(range(0,22)):
            fname.write(fname1.readline())
        fname.write(self.lineEdit_7.text() + '       ! F_LPFDamping	 - Damping coefficient [used only when F_FilterType = 2] \n')
        fname.write(self.lineEdit_6.text() + '       ! F_NotchCornerFreq  - Natural frequency of the notch filter, [rad/s] \n')
        fname1.readline();fname1.readline();
        for x in list(range(1,8)):
            fname.write(fname1.readline())
        fname.write(self.lineEdit_3.currentText() + '       ! PC_GS_angles	 - Gain-schedule table: pitch angles \n')
        fname.write(self.lineEdit_4.currentText() + '       ! PC_GS_KP	 - Gain-schedule table: pitch controller kp gains \n')
        fname.write(self.lineEdit_5.currentText() + '       ! PC_GS_KI	 - Gain-schedule table: pitch controller ki gains \n')
        fname1.readline();fname1.readline();fname1.readline();
        for x in list(range(1,29)):
            fname.write(fname1.readline())
        fname.write(self.lineEdit.text() + '       ! VS_KP  - Proportional gain for generator PI torque controller [1/(rad/s) Nm]. \n')
        fname.write(self.lineEdit_2.text() + '       ! VS_KI  - Integral gain for generator PI torque controller [1/rad Nm]. \n')
        fname1.readline();fname1.readline();
        for x in fname1:
            fname.write(x)       
        fname.close()

    
    def LocalRun(self):
        subprocess.run(["openfast", self.lineEdit_16.text()+"/5MW_Land_BD_DLL_WTurb.fst"])
        #os.chdir("testCase")
        #subprocess.run(["pimpleFoam"])
        #os.chdir("..")
        
    def SendToHPCf(self):
        subprocess.run(["scp", self.lineEdit_16.text()+'/Rosco_tuning/DISCON.IN',self.lineEdit_13.text()+"@"+self.lineEdit_14.text()+":"+self.lineEdit_15.text()+'/5MW_Land_BD_DLL_WTurb/Rosco_tuning'])
        
    def HPCloadf(self):
        subprocess.run(["scp", self.lineEdit_13.text()+"@"+self.lineEdit_14.text()+":"+self.lineEdit_15.text()+"/5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.out",self.lineEdit_16.text()])
        
    def RunCCD(self):
        print('abc')
        # Collect information
        # construct the OPT path
        # CCD based on AutoCCD
        # Show to progress bar
        #self.progressBar.setValue(idx/nTotal*100)  #used in the CCD function

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = Mapper()
    myWindow.show()
    app.exec_()

