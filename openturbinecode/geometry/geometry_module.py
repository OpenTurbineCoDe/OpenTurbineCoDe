import sys
import os
import matplotlib.pyplot as plt
import numpy
import subprocess
import scp
import pandas as pd

class Geometry:
    def __init__(self, path_to_case, turb_data=None, models=None):
        
        self.turb_data = turb_data
        self.models = models
        self.path_to_case = path_to_case

        self.setDefaultValues()
              
    # ==================== GENERAL FUNCTIONS ==========================================
        
    def setDefaultValues(self):

        # Initialization of attributes
        if self.turb_data and self.models:
            #use turbine data and model data passed as argument to initialize this object
            #... TODO
            pass
        else:


            #set placeholder default text for parametric sweep
            self.ROSCOR2Omega = 0.2
            self.ROSCOR2Zeta  = 0.7
            self.ROSCOR3Omega = 0.3
            self.ROSCOR3Zeta  = 0.7
            self.PlatformP1   = 0.7
            self.PlatformP2   = 0.7            

    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================
    def loadGeom(self, fn, table, QtWidgets):
        #print("I should execute: subprocess.run(\"openfast \" + " + args +")")
        with open(fn, 'r') as f:
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            content = [x.strip().split()[0:] for x in f]
        NoSec = len(content)
        table.setRowCount(NoSec)
        for i in range(0, NoSec-1):
            table.setItem(i, 0, QtWidgets.QTableWidgetItem(content[i][0]))
            table.setItem(i, 1, QtWidgets.QTableWidgetItem(content[i][4]))
            table.setItem(i, 2, QtWidgets.QTableWidgetItem(content[i][5]))
            table.setItem(i, 3, QtWidgets.QTableWidgetItem(content[i][6]))
            table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(0.125)))
            table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(0.25)))

    def openFileDialogue(self, fn, QtWidgets):
        solverFolder, _filter = str(QtWidgets.QFileDialog.getOpenFileName(None, "Open AeroDyn blade file", '.', "(*)"))
        fn.setText(self.solverFolder)

    def Geo_showSolvers(self, comboBox, stackedWidget):
        if comboBox.currentText() == "AeroDyn blade file":
            stackedWidget.setCurrentIndex(0)
        elif comboBox.currentText() == "turbinesFoam file":
            stackedWidget.setCurrentIndex(1)
        elif comboBox.currentText() == "BB3D":
            stackedWidget.setCurrentIndex(2)
        elif comboBox.currentText() == "PGL":
            stackedWidget.setCurrentIndex(3)
        elif comboBox.currentText() == "Salome":
            stackedWidget.setCurrentIndex(4)               
        

# if __name__=='__main__':
#     pass

