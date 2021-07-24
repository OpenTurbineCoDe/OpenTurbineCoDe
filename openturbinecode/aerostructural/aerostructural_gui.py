# ================================================
# External python imports
# ================================================

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import ast
import argparse
import subprocess

#conditional imports
try:
    from PyQt5 import QtCore, QtGui, uic, QtWidgets
    from PyQt5.QtWidgets import QFileDialog
except ImportError as err:
    pass

import openturbinecode.aerostructural.aerostructural_module as aerostruct

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) +os.sep+ "Config.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myAeroStruct,  parent=None, withMasterGUI=False):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.myAeroStruct = myAeroStruct 
              
        # =================== INITIALIZE FIELD VALUES ==============================
        self.myAeroStruct.setDefaultValues()
        self.writeToUI()

        # =================== FORCE INTERNAL VALUES WHEN RUNNING WITH MASTER ==============================
        if withMasterGUI:
            #TODO
            pass

        # =================== CONNECT BUTTONS AND ACTIONS ==============================
        # Bind the event handlers to the buttons using a function
        
        #TODO: connect buttons:
        # # self.loadRotor.clicked.connect(self.load_case)
        self.RunAnalysis.clicked.connect(self.caller_Run)
        self.RunOptimization.clicked.connect(self.caller_Opt)
        # self.plot_cp.clicked.connect(self.myAeroStructPlotCp)
        # self.plot_thrust.clicked.connect(self.myAeroStructPlotThrust)               
        # self.plot_torque.clicked.connect(self.myAeroStructPlotTorque)
        self.Push_sendtoHPC.clicked.connect(self.caller_SendToHPC)               
        
        
    # --- Setting default values ---

    # --- Reading input values ---

    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

    def writeToUI(self):

        #Set interface values
        # model list
        # self.rotorPath.setText(self.myAeroStruct.path_to_case)

        # self.windSpeed.setText(', '.join([str(el) for el in self.myAeroStruct.Vlist]))
        # self.TSR.setText(', '.join([str(el) for el in self.myAeroStruct.tsrlist]))
        self.pitchAngle.setText(', '.join([str(el) for el in self.myAeroStruct.pitchlist]))
        self.twist.setText(', '.join([str(el) for el in self.myAeroStruct.twist]))
        self.chord.setText(', '.join([str(el) for el in self.myAeroStruct.chord]))
        self.span.setText(str(self.myAeroStruct.span))
        self.precone.setText(str(self.myAeroStruct.precone))
        self.thickness.setText(', '.join([str(el) for el in self.myAeroStruct.thickness]))
        self.whichHPC.setText(str(self.myAeroStruct.CaseToHPC))
        self.Objective_Torque.setText(str(self.myAeroStruct.torqueWeight))
        self.Objective_Mass.setText(str(self.myAeroStruct.massWeight))
        self.conv_tol.setText(str(self.myAeroStruct.convergencetolerance))
        self.max_iters.setText(str(self.myAeroStruct.maxiters))
        self.Wind_V.setText(str(self.myAeroStruct.Vlist))
        self.rpm.setText(str(self.myAeroStruct.rpmlist))

    def readFromUI(self):
        #Get user inputs data
        # TODO: injecting attributes in a class is technically very bad, might want to think about an alternative soon
        # self.myAeroStruct.XXX = self.model_list.currentText()
        # self.myAeroStruct.path_to_case = self.rotorPath.text()

        # self.myAeroStruct.Vlist = np.array( ast.literal_eval(self.windSpeed.text()) )
        # self.myAeroStruct.tsrlist = np.array( ast.literal_eval(self.TSR.text()) )
        # self.myAeroStruct.pitchlist = np.array( ast.literal_eval(self.pitchAngle.text()) )

        # self.myAeroStruct.fidelity = self.solver_list.currentText()
        # self.myAeroStruct.mesh_level = self.mesh_list.currentText()

        self.myAeroStruct.fidelity = str(self.Fidelity_selection.currentText())
        self.myAeroStruct.pitchlist = np.array( ast.literal_eval(self.pitchAngle.text()) )
        self.myAeroStruct.twist = np.array( ast.literal_eval(self.twist.text()) )
        self.myAeroStruct.chord = np.array( ast.literal_eval(self.chord.text()) )
        self.myAeroStruct.span = np.array( ast.literal_eval(self.span.text()) )
        self.myAeroStruct.precone = np.array( ast.literal_eval(self.precone.text()) )
        self.myAeroStruct.thickness = np.array( ast.literal_eval(self.thickness.text()) )

        # --- Data Handling ---
        self.myAeroStruct.caseToHpc = self.whichHPC.text()



    # --- Executing analysis/optimization (calling OTCD) ---

    def caller_Run(self):
        #read params from the GUI
        self.readFromUI()

        #execute function through the control object
        self.myAeroStruct.Run()

    def caller_Opt(self):
        #read params from the GUI
        self.readFromUI()

        self.myAeroStruct.optimize = True

        #execute function through the control object
        self.myAeroStruct.Run()


    def caller_SendToHPC(self):
        #read params from the GUI
        self.readFromUI()

        self.myAeroStruct.SendToHPC(self.myAeroStruct.caseToHpc)
        
    

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("--plotonly", action='store_true', help="Do not compute anything")
    args = parser.parse_args()

    path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
    path_to_case = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
    # path_to_case = os.getcwd() + os.sep + "Madsen2019" + os.sep 

    #empty aero object
    myAeroStruct = aerostruct.Aerostructural(path_to_case, plotonly=args.plotonly)

    myWindow = Mapper(myAeroStruct)
    myWindow.show()
    app.exec_()

