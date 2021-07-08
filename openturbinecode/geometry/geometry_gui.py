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

import openturbinecode.geometry.geometry_module as geom

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) + os.sep + "geom.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myGeom, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.myGeom = myGeom #make the control module available
              
        # =================== INITIALIZE FIELD VALUES ==============================
        self.myGeom.setDefaultValues()
        self.writeToUI()

        # =================== CONNECT BUTTONS AND ACTIONS ==============================
        # Bind the event handlers to the buttons using a function
        self.Geo_Button1.clicked.connect(self.caller_loadGeom)
        self.Geo_Button1.setToolTip('Load blade geometry from an AeroDyn file')
        self.Geo_toolButton1.clicked.connect(self.caller_openFileDialogue)
        self.Geo_toolButton1.setToolTip('Click here to select AeroDyn blade file')
        self.Geo_comboBox.activated.connect(self.caller_Geo_showSolvers)

    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

    def writeToUI(self):
        #Set interface values
        self.Geo_LineEdit1.setText("/home/kz/Desktop/Geometry/AeroDynCase/blade.dat")

    def readFromUI(self):
        #Get user inputs data
        self.myGeom.AeroDynFileName = self.Geo_LineEdit1.text() #no.text function
  
    # ============== Caller functions: gather params from the GUI and calls specific function ==================
    def caller_loadGeom(self):
        self.readFromUI()
        file = self.Geo_LineEdit1.text()  
        table = self.Geo_Table1
        #qwidgets_ = QtWidgets
        self.myGeom.loadGeom(file, table, QtWidgets)

    def caller_openFileDialogue(self):
        file = self.Geo_LineEdit1.text()  
        self.myGeom.openFileDialogue(file, QtWidgets)
        
    def caller_Geo_showSolvers(self):
        comboBox = self.Geo_comboBox
        stackedWidget = self.Geo_stackedWidget
        self.myGeom.Geo_showSolvers(comboBox, stackedWidget)


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    path_to_case = "./"
    
    #empty geometry object
    myGeom = geom.Geometry(path_to_case)

    myWindow = Mapper(myGeom)
    myWindow.show()
    app.exec_()

