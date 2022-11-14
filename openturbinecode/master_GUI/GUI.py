# Config program using PyQt5

import sys
import os
import matplotlib.pyplot as plt
# import shutil, tempfile, math, string
# import numpy as np
# import subprocess
import ast

#conditional imports
try:
    from PyQt5 import QtCore, QtGui, uic, QtWidgets
    from PyQt5.QtWidgets import QFileDialog
except ImportError as err:
    pass

from openturbinecode.aerodynamics import aerodynamics_gui as aero
from openturbinecode.structure import structure_gui as struc
from openturbinecode.aerostructural import aerostructural_gui as aerostruct
from openturbinecode.controls import control_gui as ctrl
from openturbinecode.geometry import geometry_gui as geom


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
        
        #=====  DEFAULTS ===============================================

        self.pathToMadsen = self.OTCD.path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep + "Madsen2019_10.yaml"

        #=====  MAIN OPTIONS ===============================================
        #self.OTCD.MessageBox = self.textBrowser
        self.OTCD.QtWidgets = QtWidgets
        
        self.Main_set_PathToCaseButton.clicked.connect(self.set_path_to_case)

        self.preload_button.clicked.connect(self.load_case)

        self.Main_set_SaveCaseButton.clicked.connect(self.save_all_options)

        self.toolButton.clicked.connect(self.openWorkingDir)


        self.Main_DLC_genButton.clicked.connect(self.caller_generateDLC)

        #=====  GEOMETRY ===============================================
        self.geometry_ui = geom.Mapper(self.OTCD.myGeom,parent=self,withMasterGUI=True)
        self.Master_tabs.addTab(self.geometry_ui,"Geometry")
        #=====  MESHING ===============================================
        
        #...

        #=====  AERODYNAMICS ===============================================
        
        self.aero_ui = aero.Mapper(self.OTCD.myAero,parent=self,withMasterGUI=True)
        self.Master_tabs.addTab(self.aero_ui,"Aerodynamics")

        #=====  STRUCTURE ===============================================
        
        self.struc_ui = struc.Mapper(self.OTCD.myStruc,parent=self,withMasterGUI=True)
        self.Master_tabs.addTab(self.struc_ui,"Structure")

        #=====  AERO-STRUCTURE ===============================================
        
        # aerostructGUI_ui = asGui.Mapper(OTCD=self.OTCD,parent=self)
        # self.SampleModule.addTab(aerostructGUI_ui,"Aerostructural")
        self.aerostructGUI_ui = aerostruct.Mapper(self.OTCD.myAeroStruct,parent=self, withMasterGUI=True)
        self.Master_tabs.addTab(self.aerostructGUI_ui,"AeroStructure")

        #=====  CCD ===============================================
        
        self.control_ui = ctrl.Mapper(self.OTCD.myCtrl,parent=self,withMasterGUI=True)
        self.Master_tabs.addTab(self.control_ui,"CCD")

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
        if "DLC" in self.OTCD.modeling_options["OpenTurbineCoDe"] and "DLC_list" in self.OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]: 
            self.disp_DLC_options()

        if self.OTCD.turb_data:
            self.disp_main_params()
        

    #=====  MAIN OPTIONS ===============================================

    #set the case path
    def openWorkingDir(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(self, "Set Working Directory", " ", QtWidgets.QFileDialog.ShowDirsOnly)
        print("You have selected " + "\033[4m" + dir_ + "\033[0m" + " as the working directory")
        self.Main_set_PathToCase.setText(dir_)

    def set_path_to_case(self):
        path = self.Main_set_PathToCase.text()
        self.OTCD.setPathToCase( path )
        #UPDATE UI:
        self.aero_ui.str_pathToCase.setText(path)
        #TODO: do the same for all standalone GUIs?
        

    def load_case(self):

        #TODO: select the right path depending on the case_list combobox. As there is only 1 option there for now, let's just hardcode it.
        path = self.pathToMadsen

        self.OTCD.turb_yaml = path
        self.OTCD.load_turbine_case()
        self.disp_case()

        #update standalone GUIs
        self.aero_ui.writeToUI()
        # self.aerostruct_ui.writeToUI() #does not seem to be needed here...
        self.geometry_ui.writeToUI()


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

        DLC_list = ast.literal_eval(self.Main_DLC_listDlc.text()) if self.Main_DLC_listDlc.text() else []
        # [float(dlc) for dlc in self.Main_DLC_listDlc.text().split(',')]
        n_ws     = float(self.Main_DLC_nws.text()) if self.Main_DLC_nws.text() else 0.
        n_seeds  = float(self.Main_DLC_nseeds.text()) if self.Main_DLC_nseeds.text() else 0.
        Tmax     = float(self.Main_DLC_TMax.text()) if self.Main_DLC_TMax.text() else 0.
        Vrated   = float(self.Main_DLC_VRated.text()) if self.Main_DLC_VRated.text() else 0.
        
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
