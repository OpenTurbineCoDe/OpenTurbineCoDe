import sys
import os
import ast
import matplotlib.pyplot as plt
import shutil, tempfile, math, string
import subprocess
import scp
import numpy as np

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

from openturbinecode.controls.TACSDynParams import TACSParams

# import openturbinecode.structure.structure_module as stru
import openturbinecode.structure.structure_module as stru

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) + os.sep + "structure_gui.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myStru, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.myStru = myStru #make the control module available
              
        # =================== INITIALIZE FIELD VALUES ==============================
        self.myStru.setDefaultValues()
        self.writeToUI()

        # =================== CONNECT BUTTONS AND ACTIONS ==============================
        # activate the different UI based on solvers
        self.Solver.activated.connect(self.StructralSolverUI)
        # Load Model
        self.LoadModel.clicked.connect(self.caller_LoadModel)
        # BeamDyn run
        self.LocalRunBeamDyn.clicked.connect(self.caller_LocalRunBeamDyn)
        self.BeamDynPlot.clicked.connect(self.caller_BeamDynPlot)
        
        # TACS run
        self.LocalRunTACS.clicked.connect(self.caller_LocalRunTACS)
        self.TACSPlot.clicked.connect(self.caller_TACSPlot)
        self.SendTCAStoHPC.clicked.connect(self.caller_SendToHPCf)
        self.LoadtoLocal.clicked.connect(self.caller_HPCloadf)
        
        
    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

    def writeToUI(self):
        # set default raio button
        self.RB11.setChecked(True)
        self.RB21.setChecked(True)
        self.RB31.setChecked(True)
        self.RB41.setChecked(True)
        self.RB51.setChecked(True)
        self.RB61.setChecked(True)
        # Update the values for beamdyn
        self.TipLoad_x1.setText(str(self.myStru.TipLoadx))
        self.TipLoad_x2.setText(str(self.myStru.TipLoadxL))
        self.TipLoad_x3.setText(str(self.myStru.TipLoadxU))
        self.TipLoad_x4.setText(str(self.myStru.TipLoadxSTP))
        
        self.DistrLoad_x1.setText(str(self.myStru.DistrLoadx))
        self.DistrLoad_x2.setText(str(self.myStru.DistrLoadxL))
        self.DistrLoad_x3.setText(str(self.myStru.DistrLoadxU))
        self.DistrLoad_x4.setText(str(self.myStru.DistrLoadxSTP))
        
        self.TwstF1.setText(str(self.myStru.TwstSclF))
        self.TwstF2.setText(str(self.myStru.TwstSclFL))
        self.TwstF3.setText(str(self.myStru.TwstSclFU))
        self.TwstF4.setText(str(self.myStru.TwstSclFSTP))
        # Update the values for tacs
        self.TF1.setText(str(self.myStru.ThickSclF1))
        self.TF2.setText(str(self.myStru.ThickSclF1L))
        self.TF3.setText(str(self.myStru.ThickSclF1U))
        self.TF4.setText(str(self.myStru.ThickSclF1STP))
        
        self.TFF1.setText(str(self.myStru.ThickSclF2))
        self.TFF2.setText(str(self.myStru.ThickSclF2L))
        self.TFF3.setText(str(self.myStru.ThickSclF2U))
        self.TFF4.setText(str(self.myStru.ThickSclF2STP))
        
        self.TFFF1.setText(str(self.myStru.ThickSclF3))
        self.TFFF2.setText(str(self.myStru.ThickSclF3L))
        self.TFFF3.setText(str(self.myStru.ThickSclF3U))
        self.TFFF4.setText(str(self.myStru.ThickSclF3STP))
         # Set HPC parameters
        self.Username.setText(str(self.myStru.Username))
        self.server.setText(str(self.myStru.Server))
        self.Dir.setText(str(self.myStru.HPCPath))

    def readFromUI(self):
        # set solver and model
        self.myStru.Solver = self.Solver.currentText()
        self.myStru.Modelselection = self.Modelselection.currentText()
        
        # system: BeamDyn
        self.myStru.TipLoadx = self.TipLoad_x1.text()
        self.myStru.TipLoadxL = self.TipLoad_x2.text()
        self.myStru.TipLoadxU = self.TipLoad_x3.text()
        self.myStru.TipLoadxSTP = self.TipLoad_x4.text()
        
        self.myStru.DistrLoadx = self.DistrLoad_x1.text()
        self.myStru.DistrLoadxL = self.DistrLoad_x2.text()
        self.myStru.DistrLoadxU = self.DistrLoad_x3.text()
        self.myStru.DistrLoadxSTP = self.DistrLoad_x4.text()
        
        self.myStru.TwstSclF = self.TwstF1.text()
        self.myStru.TwstSclFL = self.TwstF2.text()
        self.myStru.TwstSclFU = self.TwstF3.text()
        self.myStru.TwstSclFSTP = self.TwstF4.text()
        # system: TACS
        self.myStru.ThickSclF1 = self.TF1.text()
        self.myStru.ThickSclF1L = self.TF2.text()
        self.myStru.ThickSclF1U = self.TF3.text()
        self.myStru.ThickSclF1STP = self.TF4.text()
        
        self.myStru.ThickSclF2 = self.TFF1.text()
        self.myStru.ThickSclF2L = self.TFF2.text()
        self.myStru.ThickSclF2U = self.TFF3.text()
        self.myStru.ThickSclF2STP = self.TFF4.text()
        
        self.myStru.ThickSclF3 = self.TFFF1.text()
        self.myStru.ThickSclF3L = self.TFFF2.text()
        self.myStru.ThickSclF3U = self.TFFF3.text()
        self.myStru.ThickSclF3STP = self.TFFF4.text()
        #
        self.myStru.BeamResponse = self.BeamResponse.currentText()
        self.myStru.TACSResponse = self.TACSResponse.currentText()
        # HPC parameters
        # self.output=""
        self.myStru.Username        = str(self.Username.text())
        self.myStru.Server          = str(self.server.text())
        self.myStru.HPCPath         = str(self.Dir.text())

  
    # ============== Caller functions: gather params from the GUI and calls specific function ==================
    def StructralSolverUI(self):
        self.readFromUI()
        fidelity = str(self.myStru.Solver)
        print("Current Solver:"+fidelity)
        if fidelity == "BeamDyn":
            self.SolverOptionsIO.setCurrentIndex(1)          
        else:
            self.SolverOptionsIO.setCurrentIndex(0) 
    
    def caller_LoadModel(self):
        self.readFromUI()
        if self.myStru.Solver == "BeamDyn" and self.myStru.Modelselection == "DTU10MW":
            self.myStru.workingmodel == self.myStru.DTU10MWBeamDyn                    # should from yaml         
            print("DTU10MW BeamDyn model loaded from library for Paraetric sweep: "+ self.myStru.workingmodel)
        if self.myStru.Solver == "BeamDyn" and self.myStru.Modelselection == "NREL5MW":
            self.myStru.workingmodel == self.myStru.NREL5MWBeamDyn                    # should from yaml         
            print("NREL5MW BeamDyn model loaded from library for Paraetric sweep: "+ self.myStru.workingmodel)
        if self.myStru.Solver == "TACS" and self.myStru.Modelselection == "DTU10MW":
            self.myStru.workingmodel == self.myStru.DTU10MWTACS                    # should from yaml         
            print("DTU10MW TACS model loaded from library for Paraetric sweep of eigen analysis: "+ self.myStru.workingmodel) 
        if self.myStru.Solver == "TACS" and self.myStru.Modelselection == "NREL5MW":
            raise ValueError("Model Mot implemented yet implemented for TACS!")
        if self.myStru.Modelselection == "User_Model":
            raise ValueError("Function not yet implemented!")
        
    def caller_LocalRunBeamDyn(self):
        self.readFromUI()
        if  self.myStru.Solver == "BeamDyn":
            if self.RB12.isChecked():
                    sweep = np.arange(float(self.myStru.TipLoadxL),float(self.myStru.TipLoadxU),float(self.myStru.TipLoadxSTP))
                    for i in range(len(sweep)):
                        self.myStru.TipLoadxCV = sweep[i]
                        self.myStru.RunModelUpdate_Beamdyn()
                        self.myStru.LocalRun()
                        self.myStru.postprocessBeamDyn()
                    self.myStru.TipLoadxCV = self.myStru.TipLoadx
            if self.RB22.isChecked():
                    sweep = np.arange(float(self.myStru.DistrLoadxL),float(self.myStru.DistrLoadxU),float(self.myStru.DistrLoadxSTP))
                    for i in range(len(sweep)):
                        self.myStru.DistrLoadxCV = sweep[i]
                        self.myStru.RunModelUpdate_Beamdyn()
                        self.myStru.LocalRun()
                        self.myStru.postprocessBeamDyn()
                    self.myStru.DistrLoadxCV = self.myStru.DistrLoadx
            if self.RB32.isChecked():
                    sweep = np.arange(float(self.myStru.TwstSclFL),float(self.myStru.TwstSclFU),float(self.myStru.TwstSclFSTP))
                    for i in range(len(sweep)):
                        self.myStru.TwstSclFCV = sweep[i]
                        self.myStru.RunModelUpdate_Beamdyn()
                        self.myStru.LocalRun()
                        self.myStru.postprocessBeamDyn()
                    self.myStru.TwstSclFCV = self.myStru.TwstSclF
        self.myStru.sweep = sweep    
    
    def caller_BeamDynPlot(self):
        self.readFromUI()
        # plot
        if self.myStru.BeamResponse == "RootFxr_max":
             plt.plot(self.myStru.sweep,self.myStru.RootFxr_max,'r-s')
        if self.myStru.BeamResponse == "RootFyr_max":
             plt.plot(self.myStru.sweep,self.myStru.RootFyr_max,'r-s')
        if self.myStru.BeamResponse == "RootMxr_max":
             plt.plot(self.myStru.sweep,self.myStru.RootMxr_max,'r-s')
        if self.myStru.BeamResponse == "RootMyr_max":
             plt.plot(self.myStru.sweep,self.myStru.RootMyr_max,'r-s')
        if self.myStru.BeamResponse == "TipTDxr_max":
             plt.plot(self.myStru.sweep,self.myStru.TipTDxr_max,'r-s')
        if self.myStru.BeamResponse == "TipTDyr_max":
             plt.plot(self.myStru.sweep,self.myStru.TipTDyr_max,'r-s')   
        plt.show()
    
    def caller_LocalRunTACS(self):
        if  self.myStru.Solver == "TACS":
            self.frequency = []
            if self.RB42.isChecked():
                sweep = np.arange(float(self.myStru.ThickSclF1L),float(self.myStru.ThickSclF1U),float(self.myStru.ThickSclF1STP))
                for i in range(len(sweep)):
                    self.myStru.thickness = []
                    self.myStru.ThickSclF1CV = sweep[i]
                    ones= np.ones(3)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF1CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF2CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF3CV)
                    TACS = TACSParams(self.myStru.DTU10MWTACS,self.myStru.thickness)
                    TACS.Frequencyanalysis(9)
                    frequency= TACS.Modeextractiion()
                    self.frequency.append(frequency)
                self.myStru.ThickSclF1CV = self.myStru.ThickSclF1
            if self.RB52.isChecked():
                sweep = np.arange(float(self.myStru.ThickSclF2L),float(self.myStru.ThickSclF2U),float(self.myStru.ThickSclF2STP))
                for i in range(len(sweep)):
                    self.myStru.thickness = []
                    self.myStru.ThickSclF2CV = sweep[i]
                    ones= np.ones(3)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF1CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF2CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF3CV)
                    TACS = TACSParams(self.myStru.DTU10MWTACS,self.myStru.thickness)
                    TACS.Frequencyanalysis(9)
                    frequency = TACS.Modeextractiion()
                    self.frequency.append(frequency)
                self.myStru.ThickSclF2CV = self.myStru.ThickSclF2
            if self.RB62.isChecked():
                sweep = np.arange(float(self.myStru.ThickSclF3L),float(self.myStru.ThickSclF3U),float(self.myStru.ThickSclF3STP))
                for i in range(len(sweep)):
                    self.myStru.thickness = []
                    self.myStru.ThickSclF3CV = sweep[i]
                    ones= np.ones(3)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF1CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF2CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF3CV)
                    TACS = TACSParams(self.myStru.DTU10MWTACS,self.myStru.thickness)
                    TACS.Frequencyanalysis(9)
                    frequency = TACS.Modeextractiion()
                    self.frequency.append(frequency)
                self.myStru.ThickSclF3CV = self.myStru.ThickSclF3
        self.myStru.sweep = sweep 
    def caller_TACSPlot(self):
        self.readFromUI()
        # plot
        frequency = []
        if self.myStru.TACSResponse == "NaturalFrequency1":
            for i in self.frequency:
                frequency.append(i[0])
            plt.plot(self.myStru.sweep,frequency,'r-s')
        if self.myStru.TACSResponse == "NaturalFrequency2":
            for i in self.frequency:
                frequency.append(i[1])
            plt.plot(self.myStru.sweep,frequency,'r-s')
        if self.myStru.TACSResponse == "NaturalFrequency3":
            for i in self.frequency:
                frequency.append(i[2])
            plt.plot(self.myStru.sweep,frequency,'r-s')   
        plt.show()
    
    def caller_SendToHPCf(self):
        pass
    
    def caller_HPCloadf(self):
        pass
    
        
        
if __name__=='__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    
    path_to_root =  os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
    path_to_case = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
    # path_to_case = os.getcwd() + os.sep + "Madsen2019" + os.sep 
    
    #empty control object
    myStru = stru.Structural(path_to_case)

    myWindow = Mapper(myStru)
    myWindow.show()
    app.exec_()