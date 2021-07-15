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
        self.Geo_comboBox.activated.connect(self.caller_Geo_outputFormat)
        self.Geo_comboBox_3.activated.connect(self.caller_Geo_setGrey)
        self.Geo_toolButton.clicked.connect(self.caller_Geo_loadExternalAF)
        self.Geo_pushButton_3.clicked.connect(self.caller_Geo_setSalome)
        self.Geo_pushButton_4.clicked.connect(self.caller_Geo_loadAFCoord)
        self.Geo_Button2.clicked.connect(self.caller_Geo_generateGeom)
        self.Geo_pushButton_2.clicked.connect(self.caller_Geo_setLofts)
        self.Geo_pushButton_5.clicked.connect(self.caller_Geo_setSpar)
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
        self.myGeom.loadGeom(self.myGeom.AeroDynFileName, self.Geo_Table1, QtWidgets, self.Geo_comboBox_2)
    
    def caller_openFileDialogue(self):
        self.readFromUI()
        self.myGeom.openFileDialogue(self.Geo_LineEdit1, QtWidgets)
        
    def caller_Geo_outputFormat(self):
        self.myGeom.Geo_outputFormat(self.Geo_comboBox, self.Geo_stackedWidget)

    def caller_Geo_setGrey(self):
        self.myGeom.Geo_setGrey(self.Geo_toolButton, self.Geo_comboBox_3, self.Geo_lineEdit, self.Geo_comboBox_2, self.Geo_pushButton_4)

    #TODO: underlying codes for saving airfoil shapes 
    def caller_Geo_loadAFCoord(self):
        self.myGeom.Geo_loadAFCoord(self.Geo_comboBox_2, self.Geo_comboBox_3, self.Geo_lineEdit)

    def caller_Geo_loadExternalAF(self):
        self.myGeom.Geo_loadExternalAF(self.Geo_toolButton, self.Geo_lineEdit, QtWidgets, self.Geo_comboBox_2)

    
    def caller_Geo_openSalomeD(self):
        self.myGeom.Geo_openSalomeD(self.Geo_comboBox, self.Geo_radioButton, Geo_Button2)

    def caller_Geo_setSalome(self):
        self.myGeom.Geo_setSalome(self.Geo_lineEdit_4, QtWidgets)

    def caller_Geo_generateGeom(self):
        self.myGeom.Geo_generateGeom(self.Geo_comboBox, self.Geo_Table1, self.Geo_Table2, self.Geo_lineEdit_3)

    def caller_Geo_setLofts(self):
        self.myGeom.Geo_setLofts(self.Geo_lineEdit_3, self.Geo_Table2, QtWidgets)

    def caller_Geo_setSpar(self):
        self.myGeom.Geo_setSpar(self.Geo_lineEdit_5)


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    path_to_case = "./"
    
    #empty geometry object
    myGeom = geom.Geometry(path_to_case)

    myWindow = Mapper(myGeom)
    myWindow.show()
    app.exec_()

