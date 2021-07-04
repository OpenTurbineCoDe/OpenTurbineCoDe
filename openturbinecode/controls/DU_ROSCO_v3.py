# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 14:12:35 2020

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

form_class = uic.loadUiType("ConfigRosco_v3.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self,  parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        # Bind the event handlers to the buttons using a function
        self.toolButton_2.clicked.connect(self.setyamlWorkingDir)
        self.saveButton.clicked.connect(self.saveFileDialog)
        self.runButton.clicked.connect(self.runexample)
        self.SendToHPC.clicked.connect(self.SendToHPCf)
        #self.HPCRun_2.clicked.connect(self.HPCloginf)
        #self.HPCRun.clicked.connect(self.HPCRunf)
        self.LoadResults.clicked.connect(self.HPCloadf)
        self.Plotresults.clicked.connect(self.Plotresultsf)
        
        
        #set placeholder
        self.lineEdit.setText("-1028.5")
        self.lineEdit_2.setText("-185.79")
        self.lineEdit_6.setText("0.4499")
        self.lineEdit_7.setText("0.0")
        self.lineEdit_13.setText("xd101")
        self.lineEdit_14.setText("amarel.rutgers.edu")
        self.lineEdit_15.setText("/scratch/xd101/Subroutine-ROSCODemo")
        self.Responses.setText("GenPwr")
        self.lineEdit_16.setText("/home/seager/Desktop/APAR_E/GUI/Control/5MW_Land_BD_DLL_WTurb")
        self.lineEdit_17.setText("/home/seager/Desktop/APAR_E/GUI/Control/5MW_Land_BD_DLL_WTurb/Rosco_tuning/DISCON1.IN")
    
    def openFileDialogue(self):  #working directory of the model
        self.modelFolder = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.lineEdit_16.setText(self.modelFolder)
        
    def setyamlWorkingDir(self):   #load the control parameters txt file
        #self.ctrldir = str(QtWidgets.QFileDialog.getExistingDirectory())
        (filePath, fileType) = QtWidgets.QFileDialog.getOpenFileName()
        self.lineEdit_17.setText(str(filePath))

    def saveFileDialog(self):
        #fname1 = open('./5MW_Land_BD_DLL_WTurb/Rosco_tuning/DISCON1.IN', 'r')  #newline='\r\n'
        #fname = open('./5MW_Land_BD_DLL_WTurb/Rosco_tuning/DISCON.IN', 'w')
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

    
    def runexample(self):
        subprocess.run(["openfast", self.lineEdit_16.text()+"/5MW_Land_BD_DLL_WTurb.fst"])
        #os.chdir("testCase")
        #subprocess.run(["pimpleFoam"])
        #os.chdir("..")
        
    def SendToHPCf(self):
        subprocess.run(["scp", self.lineEdit_16.text()+'/Rosco_tuning/DISCON.IN',self.lineEdit_13.text()+"@"+self.lineEdit_14.text()+":"+self.lineEdit_15.text()+'/5MW_Land_BD_DLL_WTurb/Rosco_tuning'])
        
    #def HPCloginf(self):
        #subprocess.run(["ssh", self.lineEdit_13.text()+"@"+self.lineEdit_14.text()])
        
    #def HPCRunf(self):
        #subprocess.run(["ssh", self.lineEdit_13.text()+"@"+self.lineEdit_14.text()])
        #subprocess.run(["/home/xd101/Downloads/openfast/install/bin/openfast","./5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.fst"])
        
    def HPCloadf(self):
        subprocess.run(["scp", self.lineEdit_13.text()+"@"+self.lineEdit_14.text()+":"+self.lineEdit_15.text()+"/5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.out",self.lineEdit_16.text()])
        
    def Plotresultsf(self):
        result = numpy.loadtxt("./5MW_Land_BD_DLL_WTurb/5MW_Land_BD_DLL_WTurb.out", skiprows=8)   
        plt.plot(result[:,0], result[:,62])
        plt.xlabel('Time (s)', fontsize=16)
        plt.ylabel('Generator Power (kW)', fontsize=16)
        plt.show()

app = QtWidgets.QApplication(sys.argv)
myWindow = Mapper()
myWindow.show()
app.exec_()

