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
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog

import openturbinecode.aerodynamics.aerodynamics_module as aero

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) +os.sep+ "Config.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myAero, parent=None, withMasterGUI=False):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.myAero = myAero 
              
        # =================== INITIALIZE FIELD VALUES ==============================
        self.myAero.setDefaultValues()
        self.writeToUI()

        # =================== FORCE INTERNAL VALUES WHEN RUNNING WITH MASTER ==============================
        if withMasterGUI:
            #TODO
            pass

        # =================== CONNECT BUTTONS AND ACTIONS ==============================
        # Bind the event handlers to the buttons using a function
        
        self.loadRotor.clicked.connect(self.load_case)

        self.runAerodyn.clicked.connect(self.caller_Run)
        self.plot_cp.clicked.connect(self.myAero.PlotCp)
        self.plot_thrust.clicked.connect(self.myAero.PlotThrust)               
        self.plot_torque.clicked.connect(self.myAero.PlotTorque)               
        
        

    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

    def writeToUI(self):

        #Set interface values
        # model list
        # self.rotorPath.setText(self.myAero.path_to_case)

        self.windSpeed.setText(', '.join([str(el) for el in self.myAero.Vlist]))
        self.TSR.setText(', '.join([str(el) for el in self.myAero.tsrlist]))
        # self.pitchAngle.setText(str(self.myAero.pitchlist))

        # self.solver_list.setCurrentIndex( XX ) self.myAero.fidelity

    def readFromUI(self):
        #Get user inputs data
        # self.myAero.XXX = self.model_list.currentText()
        # self.myAero.path_to_case = self.rotorPath.text()

        self.myAero.Vlist = np.array( ast.literal_eval(self.windSpeed.text()) )
        self.myAero.tsrlist = np.array( ast.literal_eval(self.TSR.text()) )
        # self.myAero.pitchlist = np.array( ast.literal_eval(self.pitchAngle.text()) )

        self.myAero.fidelity = self.solver_list.currentText()
        self.myAero.mesh_level = self.mesh_list.currentText()

    # ============== Caller functions: gather params from the GUI and calls specific function ==================

    def load_case(self):
        pass
        #TODO

    def caller_Run(self):
        #read params from the GUI
        self.readFromUI()

        #execute function through the control object
        self.myAero.Run()




if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("--plotonly", action='store_true', help="Do not compute anything")
    args = parser.parse_args()

    path_to_case = os.getcwd() + "/models/DTU_10MW/Madsen2019"
    
    #empty aero object
    myAero = aero.Aerodynamics(path_to_case, plotonly=args.plotonly)

    myWindow = Mapper(myAero)
    myWindow.show()
    app.exec_()

