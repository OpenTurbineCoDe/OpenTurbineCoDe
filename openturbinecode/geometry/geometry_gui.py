import sys
import os
import ast
import matplotlib.pyplot as plt
import shutil, tempfile, math, string
import numpy as np
import subprocess
import scp

#conditional imports
try:
    from PyQt5 import QtCore, QtGui, uic, QtWidgets
    from PyQt5.QtWidgets import QFileDialog
except ImportError as err:
    pass

try:
    import pandas as pd
except ImportError as err:
    _has_pandas = False
else:
    _has_pandas = True

import openturbinecode.geometry.geometry_module as geom

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) + os.sep + "geom.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myGeom, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.myGeom = myGeom #make the control module available
              
        # =================== INITIALIZE FIELD VALUES ==============================
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
        self.Geo_pushButton_3.clicked.connect(self.caller_Geo_getSalome)
        self.Geo_pushButton.clicked.connect(self.caller_Geo_getIGES)
        self.Geo_pushButton_4.clicked.connect(self.caller_Geo_loadAFCoord)
        self.Geo_Button2.clicked.connect(self.caller_Geo_generateGeom)
        self.Geo_pushButton_2.clicked.connect(self.caller_Geo_setLofts)
        self.Geo_pushButton_5.clicked.connect(self.caller_Geo_setSpar)
        self.Geo_comboBox_4.activated.connect(self.caller_Geo_loadPredefinedTurbine)
        self.Geo_toolButton2.clicked.connect(self.caller_Geo_openBB3DExe)
        self.Geo_lineEdit_6.setText(self.myGeom.BB3DExe)
        self.Geo_lineEdit_3.setText(str(self.myGeom.lofts))
        self.Geo_lineEdit_5.setText(str(self.myGeom.spar[0])+" "+str(self.myGeom.spar[1]))
        self.Geo_pushButton_6.clicked.connect(self.caller_Geo_setBB3DExe)
        self.Geo_lineEdit_4.setText(self.myGeom.salomeExe)
        self.Geo_lineEdit_2.setText("")


        self.Geo_LineEdit1.setText(self.myGeom.path_to_case + os.sep + "AeroDynCase" + os.sep + "blade.dat")
    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

    def writeToUI(self):
        #Set interface values
        
        # Moved this line out of this function, otherwise it would set the same path even if another file is loaded
        # self.Geo_LineEdit1.setText(self.myGeom.path_to_case + os.sep + "AeroDynCase" + os.sep + "blade.dat")

        if self.myGeom.turb_data:
            R0 = self.myGeom.turb_data["components"]["hub"]["diameter"] / 2
            R  = self.myGeom.turb_data["assembly"]["rotor_diameter"] / 2

            r =  self.myGeom.turb_data["components"]["blade"]["outer_shape_bem"]["chord"]["grid"]  
            chord = self.myGeom.turb_data["components"]["blade"]["outer_shape_bem"]["chord"]["values"]
            twist = self.myGeom.turb_data["components"]["blade"]["outer_shape_bem"]["twist"]["values"]

            table = self.Geo_Table1
            table.setRowCount(len(r))
            for i in range(len(r)):
                table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(r[i] * (R-R0) + R0 )))
                table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(chord[i])))
                table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(twist[i] * 180. / np.pi)))
                table.setItem(i, 3, QtWidgets.QTableWidgetItem(self.myGeom.AFlist[i]))

            self.Geo_comboBox_2.clear() # clear the items in comboBox, otherwise the items adds up everywrite it executes
            for i in range(0, self.myGeom.afNum):
                self.Geo_comboBox_2.addItem(str(i+1))

    def readFromUI(self):
        #Get user inputs data
        self.myGeom.AeroDynFileName = self.Geo_LineEdit1.text() #no.text function

        #TODO: FILL IN INTERNAL STRUCTURE WITH DATA IN THE TABLE!!

  
    # ============== Caller functions: gather params from the GUI and calls specific function ==================
    def caller_Geo_loadPredefinedTurbine(self):
        self.myGeom.Geo_loadPredefinedTurbine(self.Geo_comboBox_4, self.Geo_LineEdit1, self.Geo_toolButton1, self.Geo_widget)

    def caller_loadGeom(self):
        self.readFromUI()
        self.myGeom.loadGeom(self.myGeom.AeroDynFileName, self.Geo_Table1, QtWidgets, self.Geo_comboBox_2, self.Geo_comboBox_4)
        self.writeToUI()
    
    def caller_openFileDialogue(self):
        self.readFromUI()
        self.myGeom.openFileDialogue(self.Geo_LineEdit1, QtWidgets)
        
    def caller_Geo_outputFormat(self):
        self.myGeom.Geo_outputFormat(self.Geo_comboBox, self.Geo_stackedWidget)

    def caller_Geo_setGrey(self):
        self.myGeom.Geo_setGrey(self.Geo_toolButton, self.Geo_comboBox_3, self.Geo_lineEdit, self.Geo_comboBox_2, self.Geo_pushButton_4)

    #TODO: underlying codes for saving airfoil shapes 
    def caller_Geo_loadAFCoord(self):
        self.myGeom.Geo_loadAFCoord(self.Geo_comboBox_2, self.Geo_comboBox_3, self.Geo_lineEdit, self.Geo_comboBox_4)

    def caller_Geo_loadExternalAF(self):
        self.myGeom.Geo_loadExternalAF(self.Geo_toolButton, self.Geo_lineEdit, QtWidgets, self.Geo_comboBox_2, self.Geo_comboBox_4)

    def caller_Geo_openBB3DExe(self):
        self.myGeom.Geo_openBB3DExe(self.Geo_lineEdit_6, QtWidgets)

    def caller_Geo_setBB3DExe(self):
        self.myGeom.Geo_setBB3DExe(self.Geo_lineEdit_6)





    def caller_Geo_generateGeom(self):
        self.readFromUI()
        self.myGeom.Geo_generateGeom(self.Geo_comboBox, self.Geo_Table1, self.Geo_Table2, self.Geo_lineEdit_3, self.Geo_lineEdit_4, self.Geo_lineEdit_2, self.Geo_radioButton)

    def caller_Geo_setLofts(self):
        self.myGeom.Geo_setLofts(self.Geo_lineEdit_3, self.Geo_Table2, QtWidgets)

    def caller_Geo_setSpar(self):
        self.myGeom.Geo_setSpar(self.Geo_lineEdit_5)

    ## Salome stuffs
    def caller_Geo_runSalome(self):
        self.myGeom.Geo_setSalome(self.Geo_lineEdit_4, self.Geo_lineEdit_2, self.Geo_radioButton)

    def caller_Geo_getSalome(self):
        self.myGeom.Geo_getSalome(self.Geo_lineEdit_4, QtWidgets)

    def caller_Geo_getIGES(self):
        self.myGeom.Geo_getIGES(self.Geo_lineEdit_2, QtWidgets)


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
    path_to_case = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
    # path_to_case = os.getcwd() + os.sep + "Madsen2019" + os.sep 
    
    #empty geometry object
    myGeom = geom.Geometry(path_to_case)

    myWindow = Mapper(myGeom)
    myWindow.show()
    app.exec_()

