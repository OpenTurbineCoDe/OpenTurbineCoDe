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
        
        self.Main_set_PathToCaseButton.clicked.connect(self.set_path_to_case)

        self.Main_set_SaveCaseButton.clicked.connect(self.save_all_options)

        #...

        self.Main_DLC_genButton.clicked.connect(self.caller_generateDLC)

        #=====  GEOMETRY ===============================================
        self.Geo_LineEdit1.setText("/home/kz/Desktop/Geometry/AeroDynCase/blade.dat")
        self.OTCD.AeroDynBladeFileName = self.Geo_LineEdit1  
        self.OTCD.Geom_Table1 = self.Geo_Table1
        self.Geo_Button1.clicked.connect(self.OTCD.loadGeom)
        self.Geo_Button1.setToolTip('Load blade geometry from an AeroDyn file')
        self.Geo_toolButton1.clicked.connect(self.OTCD.openFileDialogue)
        self.Geo_toolButton1.setToolTip('Click here to select AeroDyn blade file')
 




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
        self.disp_case()



    #*******************************************************************
    #************** CALLER FUNCTIONS               *********************
    #*******************************************************************


    #=====  GENERAL FUNCTIONS, USED FOR THE ENTIRE GUI ===============================================

    # unpack all options and fill the UI
    def disp_case(self):

        #display path to case
        self.Main_set_PathToCase.setText(self.OTCD.path_to_case)

        #update parameters with the current texts in the fields
        if "DLC" in self.OTCD.modeling_options["OpenTurbineCoDe"]: 
            self.disp_DLC_options()

        if self.OTCD.turb_data:
            self.disp_main_params()
        

    #=====  MAIN OPTIONS ===============================================

    #set the case path
    def set_path_to_case(self):
        self.OTCD.path_to_case = self.Main_set_PathToCase.text()
        
        # Shall we do the following then ?
        # # reload turbine data
        # self.OTCD.load_turbine_case()


    def save_MainParams_options(self):
        PRated    = float(self.Main_para_PRated.text())
        nblade    = float(self.Main_para_nblade.text())
        D         = float(self.Main_para_D.text())
        HubD      = float(self.Main_para_HubD.text())
        HubHeight = float(self.Main_para_HubHeight.text())
        Vin       = float(self.Main_para_Vin.text())
        Vout      = float(self.Main_para_Vout.text())
        Overhang  = float(self.Main_para_Overhang.text())
        Tilt      = float(self.Main_para_Tilt.text())
        Precone   = float(self.Main_para_Precone.text())
        # Prebend = float(self.Main_para_Prebend.text())
        
        self.OTCD.update_MainParams(PRated, nblade, D, HubD, HubHeight, Vin, Vout, Overhang, Tilt, Precone)

    # from UI to internal DLC options
    def disp_main_params(self):
        self.Main_para_PRated.setText( str( self.OTCD.turb_data["assembly"]["rated_power"] ))
        self.Main_para_nblade.setText( str( self.OTCD.turb_data["assembly"]["number_of_blades"] ))
        self.Main_para_D.setText( str( self.OTCD.turb_data["assembly"]["rotor_diameter"] ))
        self.Main_para_HubHeight.setText( str( self.OTCD.turb_data["assembly"]["hub_height"] ))
        
        self.Main_para_HubD.setText( str( self.OTCD.turb_data["components"]["hub"]["diameter"] ))
        self.Main_para_Precone.setText( str( self.OTCD.turb_data["components"]["hub"]["cone_angle"] ))
        self.Main_para_Overhang.setText( str( self.OTCD.turb_data["components"]["nacelle"]["outer_shape_bem"]["overhang"] ))
        self.Main_para_Tilt.setText( str( self.OTCD.turb_data["components"]["nacelle"]["outer_shape_bem"]["uptilt_angle"] ))

        self.Main_para_Vin.setText( str( self.OTCD.turb_data["control"]["supervisory"]["Vin"] ))
        self.Main_para_Vout.setText( str( self.OTCD.turb_data["control"]["supervisory"]["Vout"] ))

    #...

    #Collect all informations in the GUI, write them in our data structure, and then write yaml files
    def save_all_options(self):
        self.set_path_to_case()

        # ................... Main turbine params ..................
        self.save_MainParams_options()

        # ................... DLCs ...................
        self.save_DLC_options()

        # ------------------- write the yaml ---------------------------
        self.OTCD.save_turbine_case()
        #TODO: should also save modeling options!


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
    def disp_DLC_options(self):
        
        DLC_list = []
        DLC_list = self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["DLC_list"]
        n_ws     = self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["n_ws"]    
        n_seeds  = self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["n_seeds"] 
        TMax     = self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["TMax"]    
        Vrated   = 0

        if self.OTCD.turb_data:
            Vrated   = self.OTCD.turb_data["control"]["supervisory"]["Vrated"]

        # Prepare DLC list as str
        DLC_str = ""
        for dlc in DLC_list:
            DLC_str += str(dlc) + ", "
        if DLC_str:
            DLC_str = DLC_str[0:-3] # remove the last ", "
        
        self.Main_DLC_listDlc.setText(DLC_str)
        self.Main_DLC_nws.setText(str(n_ws))
        self.Main_DLC_nseeds.setText(str(n_seeds))
        self.Main_DLC_TMax.setText(str(TMax))
        self.Main_DLC_VRated.setText(str(Vrated))

    #...




def run(OTCD):
    app = QtWidgets.QApplication(sys.argv)
    myWindow = OTCD_GUI(OTCD)
    myWindow.show()
    app.exec_()
