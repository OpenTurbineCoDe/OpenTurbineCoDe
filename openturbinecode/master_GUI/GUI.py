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
    def __init__(self,  OTCD_, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # This is the OpenTurbineCode object. You can access all the functions defined in main by calling `self.OTCD.myfunction()`
        self.OTCD = OTCD_
        
        
        # The following code maps the action handlers with the main.py functionalities.
        # ------>> PLEASE WRITE CODE UNDER YOUR ASSOCIATED SECTION <<---------
        # You can get inspiration from sample code below, or other resources/tutorials on Qt stuff.
        
        #=====  MAIN OPTIONS ===============================================
        
        #...

        self.Main_DLC_genButton.clicked.connect(self.caller_generateDLC)

        #=====  GEOMETRY ===============================================
        
        #...

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

        # ===================================
        # FILL THE GUI WITH PRELOADED DATA:
        # ===================================
        self.disp_Case()



    #*******************************************************************
    #************** CALLER FUNCTIONS               *********************
    #*******************************************************************


    #=====  MAIN OPTIONS ===============================================

    #set the case path
    def caller_loadCase(self):
        pass 
    
    # unpack all options and fill the UI
    def disp_Case(self):

        DLC_list = []

        if "DLC" in self.OTCD.modeling_options["OpenTurbineCoDe"]: 
            DLC_list = self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["DLC_list"]
            n_ws     = self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["n_ws"]    
            n_seeds  = self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["n_seeds"] 
            TMax     = self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["TMax"]    
            Vrated   = 0

        if self.OTCD.turb_data:
            # ...
            Vrated   = self.OTCD.turb_data["control"]["supervisory"]["Vrated"]

        #update parameters with the current texts in the fields
        if "DLC" in self.OTCD.modeling_options["OpenTurbineCoDe"]: 
            self.disp_DLC_options(DLC_list, n_ws, n_seeds , TMax    , Vrated  )

    #...

    # action to generate DLC
    def caller_generateDLC(self):
        self.save_DLC_options()
        self.OTCD.call_generateDLC()

    # from UI to internal DLC options
    def save_DLC_options(self):
        DLC_list = [float(dlc) for dlc in self.Main_DLC_listDlc.text().split(',')]
        n_ws     = float(self.Main_DLC_nws.text())
        n_seeds  = float(self.Main_DLC_nseeds.text())
        Tmax     = float(self.Main_DLC_TMax.text())
        Vrated   = float(self.Main_DLC_VRated.text())
        
        self.OTCD.update_DLCoptions(DLC_list, n_ws    , n_seeds , Tmax    , Vrated  ) 

    # from internal DLC options to UI
    def disp_DLC_options(self, DLC_list, n_ws, n_seeds, Tmax, Vrated ):
        # Prepare DLC list as str
        DLC_str = ""
        for dlc in DLC_list:
            DLC_str += str(dlc) + ", "
        
        self.Main_DLC_listDlc.setText(DLC_str)
        self.Main_DLC_nws.setText(str(n_ws))
        self.Main_DLC_nseeds.setText(str(n_seeds))
        self.Main_DLC_TMax.setText(str(Tmax))
        self.Main_DLC_VRated.setText(str(Vrated))

    #...

    def save_all_options(self):
        # ................... DLCs ...................
        self.save_DLC_options()



def run(OTCD):
    app = QtWidgets.QApplication(sys.argv)
    myWindow = OTCD_GUI(OTCD)
    myWindow.show()
    app.exec_()
