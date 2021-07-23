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
import numpy as np
import argparse

#conditional imports
try:
    from PyQt5 import QtCore, QtGui, uic, QtWidgets
    from PyQt5.QtWidgets import QFileDialog
except ImportError as err:
    pass


import openturbinecode.aerodynamics.aerodynamics_module as aero

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) +os.sep+ "Config.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myAero, parent=None, withMasterGUI=False):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))    

        self.myAero = myAero 

        self.pathToRotor = ""
        self.pathToMadsen = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep + "Madsen2019_10.yaml"

        # =================== INITIALIZE FIELD VALUES ==============================
        self.myAero.setDefaultValues()
        self.writeToUI()

        # =================== FORCE INTERNAL VALUES WHEN RUNNING WITH MASTER ==============================
        if withMasterGUI:
            self.str_pathToCase.setEnabled(False)

            self.model_list.setEnabled(False)

            self.loadRotor.setEnabled(False)
            self.model_list.setItemText(0, "internal") 
            self.DLC_list.setEnabled(False)
            self.DLC_list.setItemText(0, "internal") 
        
        self.str_pathToRotor.setEnabled(False)            
        self.browseButtonRotor.setEnabled(False)
            

        # =================== CONNECT BUTTONS AND ACTIONS ==============================
        # Bind the event handlers to the buttons using a function
        
        self.loadRotor.clicked.connect(self.load_case)

        self.model_list.activated.connect(self.GrayOutRotor)

        self.browseButtonRotor.clicked.connect(self.set_pathToRotor)

        self.setFolderStruct_button.clicked.connect(self.caller_setFolderStructure)
        self.runAerodyn.clicked.connect(self.caller_Run)
        self.plot_cp.clicked.connect(self.myAero.PlotCp)
        self.plot_thrust.clicked.connect(self.myAero.PlotThrust)               
        self.plot_torque.clicked.connect(self.myAero.PlotTorque)               
        
        

    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

    def writeToUI(self):

        self.str_pathToCase.setText(self.myAero.path_to_case)
        self.str_pathToRotor.setText(self.pathToRotor)

        #Set interface values
        # model list
        # self.rotorPath.setText(self.myAero.path_to_case)

        self.windSpeed.setText(', '.join([str(el) for el in self.myAero.Vlist]))
        self.TSR.setText(', '.join([str(el) for el in self.myAero.tsrlist]))
        self.pitchAngle.setText(', '.join([str(el) for el in self.myAero.pitchlist]))
        self.bladeRadius.setText(', '.join([str(el) for el in self.myAero.bladeRlist]))

        # self.solver_list.setCurrentIndex( XX ) self.myAero.fidelity

    def readFromUI(self):
        self.myAero.setPathToCase(self.str_pathToCase.text())
        
        if self.model_list.currentText() == 'DTU 10 MW': 
            self.pathToRotor = self.pathToMadsen
        # elif ...:
        #     pass
        else:
            self.pathToRotor = self.str_pathToRotor.text()

        #Get user inputs data
        # self.myAero.XXX = self.model_list.currentText()
        # self.myAero.path_to_case = self.rotorPath.text()

        self.myAero.Vlist = np.array( ast.literal_eval(self.windSpeed.text()) )
        self.myAero.tsrlist = np.array( ast.literal_eval(self.TSR.text()) )
        self.myAero.pitchlist = np.array( ast.literal_eval(self.pitchAngle.text()) )
        self.myAero.bladeRlist = np.array( ast.literal_eval(self.bladeRadius.text()) )

        self.myAero.fidelity = self.solver_list.currentText()
        self.myAero.mesh_level = self.mesh_list.currentText()

    # ============== Caller functions: gather params from the GUI and calls specific function ==================

    def load_case(self):
        #read params from the GUI and then load data
        self.readFromUI()
        print("loading "+ self.pathToRotor)
        self.myAero.reload_turbdata(self.pathToRotor)
    
    def caller_setFolderStructure(self):
        self.readFromUI()
        print("Setting folders in "+ self.myAero.path_to_case)
        self.myAero.setFolderStructure()


    def caller_Run(self):
        #read params from the GUI
        self.readFromUI()

        #execute function through the control object
        self.myAero.Run()

    # ============== Purely GUI functions ===========================
    def set_pathToRotor(self):
        (filePath, _) = QtWidgets.QFileDialog.getOpenFileName()
        self.pathToRotor = filePath
        self.writeToUI()

    def GrayOutRotor(self):
        if self.model_list.currentText() == "external":
            self.str_pathToRotor.setEnabled(True)
            self.browseButtonRotor.setEnabled(True)
        else:
            self.str_pathToRotor.setEnabled(False)            
            self.browseButtonRotor.setEnabled(False)


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("--plotonly", action='store_true', help="Do not compute anything")
    args = parser.parse_args()

    path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
    path_to_case = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
    # path_to_case = os.getcwd() + os.sep + "Madsen2019" + os.sep 
    
    #empty aero object
    myAero = aero.Aerodynamics(path_to_case, plotonly=args.plotonly)

    myWindow = Mapper(myAero)
    myWindow.show()
    app.exec_()

