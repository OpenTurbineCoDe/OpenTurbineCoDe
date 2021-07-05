# Config program using PyQt5

import sys
import os
import matplotlib.pyplot as plt
import shutil, tempfile, math, numpy, string
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import subprocess
import pyqtgraph as pg

#NOTE : for now, we dynamically load the UI file so that it's easier for everybody to work in parallel.
#       Later, we should replace this by a static load when everybody is done editing the GUI.
#       See also https://realpython.com/qt-designer-python/
UIrepresentation = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) + os.sep + "Config.ui")[0]  # Load the UI


class OTCD_GUI(QtWidgets.QMainWindow, UIrepresentation):

    #=====  GEOMETRY CALLER FUNCTIONS  =====================================   
    #def call_Geo_loadGeom(self):
    #    self.OTCD.loadGeom(self.fName)
    


    def __init__(self,  OTCD_, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # This is the OpenTurbineCode object. You can access all the functions defined in main by calling `self.OTCD.myfunction()`
        self.OTCD = OTCD_
        
        
        # The following code maps the action handlers with the main.py functionalities.
        # ------>> PLEASE WRITE CODE UNDER YOUR ASSOCIATED SECTION <<---------
        # You can get inspiration from sample code below, or other resources/tutorials on Qt stuff.
        
        #=====  MAIN OPTIONS ===============================================
        self.OTCD.MessageBox = self.textBrowser
        self.OTCD.QtWidgets = QtWidgets
        
        #...

        #=====  GEOMETRY ===============================================
        self.Geo_LineEdit1.setText("/home/kz/Desktop/Geometry/AeroDynCase/blade.dat")
        self.OTCD.AeroDynBladeFileName = self.Geo_LineEdit1  
        self.OTCD.Geom_Table = self.Geo_Table
        self.Geo_Button1.clicked.connect(self.OTCD.loadGeom)
        self.Geo_Button1.setToolTip('Load blade geometry from an AeroDyn file')
        self.toolButton1.clicked.connect(self.OTCD.openFileDialogue)
        self.toolButton1.setToolTip('Please click here to select AeroDyn blade file')

        #=====  MESHING ===============================================
        
        #...

        #=====  AERODYNAMICS ===============================================
        
        #...

        #=====  STRUCTURE ===============================================
        
        #...

        #=====  AERO-STrUCTURE ===============================================
        
        #...

        #=====  CCD ===============================================
        
        #...

        #=====  SAMPLE MODULE ===============================================
        
        self.sample_button1.clicked.connect(self.OTCD.sample_hello_world)

        # ===================================
        # SAMPLE CODE:
        # ===================================

        # Bind the event handlers to the buttons
        # self.pushButton.clicked.connect(self.sendToHPC)

        # Set placeholders
        # self.lineEdit_7.setText("11.4")

        # def showSolverSetup(self):
        #     print("The user have selected "+str(self.comboBox.currentText()))
        #     if self.comboBox.currentText() == "AeroDyn (BEM)":
        #         self.stackedWidget.setCurrentIndex(1)
        #         self.lineEdit_2.setText("0 0.5 20")
        #     if self.comboBox.currentText() == "OpenFOAM (ALM)":
        #         self.stackedWidget.setCurrentIndex(0)
        #         self.lineEdit_2.setText("0 0.5 20")

        # def sendToHPC(self):
        #     subprocess.run(["scp", "-r", self.lineEdit_12.text() ,self.lineEdit_13.text()+"@"+self.lineEdit_14.text()+":"+self.lineEdit_15.text()])
        #     subprocess.run(["rm", "-r",  self.ALMFolder+"/rpm*"])

def run(OTCD):
    app = QtWidgets.QApplication(sys.argv)
    myWindow = OTCD_GUI(OTCD)
    myWindow.show()
    app.exec_()
