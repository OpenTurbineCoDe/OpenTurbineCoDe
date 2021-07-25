import sys
import os
import matplotlib.pyplot as plt
import numpy as np 
import subprocess
import scp
import pandas as pd

import openturbinecode.meshing.surf_mesher_PGL as pgl
import openturbinecode.utils.io as io

# def afid_to_afpos(afid,aflist):
#     return afpos
class Geometry:
    def __init__(self, path_to_case, turb_data=None, models=None):
        self.turb_data = turb_data
        self.models = models
        self.path_to_case = path_to_case
        self.path_to_root = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))

        self.setDefaultValues()
              
    # ==================== GENERAL FUNCTIONS ==========================================
        
    def setDefaultValues(self):

        ## default settings for BB3D
        self.BB3DExe = "/home/kz/Desktop/BB3D/make_blade" #TODO: move this to the config.json file
        self.salomeExe = "/home/kz/SALOME-9.7.0-UB18.04-SRC/salome"

        # TODO: These two should go with turbine settings
        self.spar = [0.15, 0.55]
        self.lofts = 2

        ## End of BB3D default settings

        self.afNum = 0
        self.AFID = []
        self.AFlist = []

        # Initialization of attributes
        if self.turb_data and self.models:
            #use turbine data and model data passed as argument to initialize this object
            #... TODO

            self.setPGLdata()
        else:
            #generate our internal structure a minima #TODO: create a function for this
            self.turb_data = {}

            self.turb_data["assembly"] = {"rotor_diameter": 0. }
            
            self.turb_data["components"] = {
                "hub": { "diameter": 0. },
                "blade": {"outer_shape_bem": {
                    "chord": {"grid" : [], "values" : [] },
                    "twist": {"values" : [] },
                    "rthick": {"values" : [] },
                    "pitch_axis": {"values" : [] },
                    "airfoil_position": {"grid": [], "values": [] },
            }}} 

            self.turb_data["airfoils"] = {}

            #TODO:
            # self.setPGLdata()

    def setPathToCase(self,path_to_case):    
        self.path_to_case = path_to_case
        #TODO: adapt anything after this?

    def setPGLdata(self,updateADIF=True):
            r_nodes = self.turb_data["components"]["blade"]["outer_shape_bem"]["chord"]["grid"]

            r_af = self.turb_data["components"]["blade"]["outer_shape_bem"]["airfoil_position"]["grid"]
            i_af = range(len(r_af))
            label_af = self.turb_data["components"]["blade"]["outer_shape_bem"]["airfoil_position"]["labels"]

            self.afNum = len(label_af)
            
            #translating af ids for aerodyn file #TODO: this is not very elegant
            self.AFlist = [ str(int(np.round(np.interp(r,r_af,i_af)))) for r in r_nodes ]
            # self.AFID = [label_af[int(i)] for i in self.AFlist]
            if updateADIF:
                self.AFID = label_af 

    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================
    def Geo_loadPredefinedTurbine(self, comboBox, lineEdit, toolButton, widget):
        # TODO: When selecting predefined turbiens, also set the airfoil types 
        if comboBox.currentText() == "DTU 10 MW":
            self.AFID = []
            toolButton.setEnabled(False)
            widget.setEnabled(False)
            lineEdit.setText( self.path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "AeroDyn_Reduced" + os.sep + "blade.dat") #TODO: we should refer to Madsen2019 aerodyn file
            self.AFID = [self.path_to_root + os.sep + "openturbinecode" + os.sep + "geometry" + os.sep + "lib_airfoils" + os.sep + "cylinder.dat", 
                         self.path_to_root + os.sep + "openturbinecode" + os.sep + "geometry" + os.sep + "lib_airfoils" + os.sep + "ffaw3600.dat",
                         self.path_to_root + os.sep + "openturbinecode" + os.sep + "geometry" + os.sep + "lib_airfoils" + os.sep + "ffaw3480.dat",
                         self.path_to_root + os.sep + "openturbinecode" + os.sep + "geometry" + os.sep + "lib_airfoils" + os.sep + "ffaw3360.dat",
                         self.path_to_root + os.sep + "openturbinecode" + os.sep + "geometry" + os.sep + "lib_airfoils" + os.sep + "ffaw3301.dat",
                         self.path_to_root + os.sep + "openturbinecode" + os.sep + "geometry" + os.sep + "lib_airfoils" + os.sep + "ffaw3241.dat"
                         ]

            path_to_TMP = self.path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep 
            turb_yaml = path_to_TMP + os.sep + "Madsen2019_10.yaml"
            self.turb_data = io.load_yaml(turb_yaml)
            self.setPGLdata(updateADIF=False)


        elif comboBox.currentText() == "NREL Phase VI":
            widget.setEnabled(False)
            toolButton.setEnabled(False)
            lineEdit.setText(os.path.dirname( os.path.realpath(__file__) )+os.sep +"../../models/NREL_PhaseVI_UAE/original/AeroDyn/NREL_PhaseVI_UAE_ADBlade.dat")
            #TODO:
            # path_to_TMP = self.path_to_root + os.sep + "models" + os.sep + "NREL_PhaseVI_UAE" + os.sep + "original" + os.sep 
            # turb_yaml = path_to_TMP + os.sep + "Madsen2019_10.yaml"
            # self.turb_data = io.load_yaml(turb_yaml)
            # self.setPGLdata(updateADIF=False)

        elif comboBox.currentText() == "NREL 5 MW":
            widget.setEnabled(False)
            toolButton.setEnabled(False)
            #TODO: add NREL 5 MW
            print("Not available yet.")
        elif comboBox.currentText() == "Load External":
            widget.setEnabled(True)
            toolButton.setEnabled(True)


    def loadGeom(self, fn, table, QtWidgets, comboBox, comboBox2):
        #print("I should execute: subprocess.run(\"openfast \" + " + args +")")
        # TODO: add FileNotFound error treatment so that the GUI does not abort if so
        with open(fn, 'r') as f:
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            content = [x.strip().split()[0:] for x in f]
        
        # translate the AeroDyn formatted info into our internal data structure
        
        #TODO: these two should be specified independently!!
        R = float(content[-1][0])   # This is rotor diameter
        R0 = float(content[0][0])   # This is hub diameter
        self.turb_data["components"]["hub"]["diameter"] = 2 * R0
        self.turb_data["assembly"]["rotor_diameter"] = 2 * R

        self.turb_data["components"]["blade"]["outer_shape_bem"]["chord"]["grid"]   = [(float(el[0])-R0)/(R-R0) for el in content]
        # reference_axis y...
        # reference_axis z...
        self.turb_data["components"]["blade"]["outer_shape_bem"]["twist"]["values"] = [float(el[4]) * np.pi / 180 for el in content]
        self.turb_data["components"]["blade"]["outer_shape_bem"]["chord"]["values"] = [float(el[5]) for el in content]
        self.turb_data["components"]["blade"]["outer_shape_bem"]["pitch_axis"]["values"] = .25 * np.ones(len(content)) # this info is not contained in AeroDyn files


        self.AFlist = [el[6] for el in content] 
        self.turb_data["components"]["blade"]["outer_shape_bem"]["airfoil_position"]["grid"] = self.turb_data["components"]["blade"]["outer_shape_bem"]["chord"]["grid"] 
        self.turb_data["components"]["blade"]["outer_shape_bem"]["airfoil_position"]["labels"] = self.AFlist #TODO: should actually be the string of that airfoil...

        # set the items in comboBox according to the airfoil numbers
        # currently using the data in the original aerodyn file
        # TODO: read data from the table to allow edits
        self.afNum = int(content[-1][-1])
        
        # Since AFID has been set for predefined turbines (see function Geo_loadPredefinedTurbine). Initialize AFID only when "Load External"
        if comboBox2.currentText() == "Load External":
            self.AFID = ["" for x in range(self.afNum)]    # initial AFID to store airfoil ID

    def openFileDialogue(self, fn, QtWidgets):
        fn_ = QtWidgets.QFileDialog.getOpenFileName(None, "Open AeroDyn blade file", "", "(*)")[0]
        fn.setText(str(fn_))

    def Geo_outputFormat(self, comboBox, stackedWidget):
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

    def Geo_setGrey(self, toolButton, comboBox, lineEdit, comboBox2, pushButton):
        if comboBox.currentText() != "External":
            toolButton.setEnabled(False)       
            pushButton.setEnabled(True)     
        else:
            toolButton.setEnabled(True)
            pushButton.setEnabled(False)
            lineEdit.setText(" ")

    #TODO: use os.listdir to list all airfoil coord files dynamically. Should be done in main option, possibly using a refresh button
    def Geo_loadAFCoord(self, comboBox1, comboBox2, lineEdit, comboBox3):
        if comboBox3.currentText() == "Load External":
            lineEdit.setText(os.path.dirname( os.path.realpath(__file__) ) + os.sep + "lib_airfoils" + os.sep + comboBox2.currentText() + '.dat')
            print('AF ID ' + comboBox1.currentText() + ': ' + comboBox2.currentText())
            self.AFID[int(comboBox1.currentText())-1] = lineEdit.text() 
            #TODO: read airfoil coordinates and populate self.turb_data["aifroils"]
            self.turb_data["components"]["blade"]["outer_shape_bem"]["airfoil_position"]["labels"] = self.AFlist
            print(self.AFID[0])
        
    def Geo_loadExternalAF(self, toolButton, lineEdit, QtWidgets, comboBox2, comboBox3):
        if comboBox3.currentText() == "Load External":
            fn_ = QtWidgets.QFileDialog.getOpenFileName(None, "Open airfoil coordinate file", "", "(*)")[0]
            lineEdit.setText(str(fn_))
            self.AFID[int(comboBox2.currentText())-1] = lineEdit.text() 
            self.turb_data["components"]["blade"]["outer_shape_bem"]["airfoil_position"]["labels"] = self.AFlist
            #TODO: read airfoil coordinates and populate self.turb_data["aifroils"]
            print('AF ID ' + comboBox2.currentText() + ': ' + lineEdit.text())

    # ==================== AERODYN - SALOME GEOM ==========================================
    
    def Geo_generateGeom(self, comboBox, table, table2, lineEdit, lineEdit_4, lineEdit_2, radioButton):
        if comboBox.currentText() == "AeroDyn blade file":
            self.Geo_generateAeroDyn(table)

        elif comboBox.currentText() == "turbinesFoam file":
            self.Geo_generateTurbinesFoam(table)

        elif comboBox.currentText() == "BB3D":
            self.Geo_runBB3D(table, table2, lineEdit)

        elif comboBox.currentText() == "PGL":
            self.Geo_runPGL(table)

        elif comboBox.currentText() == "Salome":
            self.Geo_runSalome(lineEdit_4, lineEdit_2, radioButton)

    # SUB-FUNCTIONS for Geo_generateGeom

    def Geo_generateAeroDyn(self, table):
        print("Generating AeroDyn blade file")
        # TODO: replace file name and location
        bl = open('/home/kz/Desktop/AeroDynBL.dat', 'w')
        bl.write("------- AERODYN v15.04.* BLADE DEFINITION INPUT FILE ------------------------------------- \n")
        bl.write("Description line for this file -- file corresponds to inputs in Test01_UAE_AeroDyn.dat \n") # TODO: change description
        bl.write("======  Blade Properties ================================================================= \n")
        bl.write("   " + str(table.rowCount()-1) + "              NumBlNds           - Number of blade nodes used in the analysis (-) \n")
        bl.write("  BlSpn     BlCrvAC    BlSwpAC    BlCrvAng    BlTwist    BlChord    BlAFID \n")
        bl.write("  (m)       (m)        (m)        (deg)       (deg)      (m)        (-) \n")
        for row in range(0, table.rowCount()):
            bl.write(str(table.item(row, 0).text()) + "\t 0 \t 0 \t 0 \t" + str(table.item(row, 1).text()) + "\t" + str(table.item(row, 2).text()) + "\t" + str(table.item(row, 3).text()) + "\n")
        print("Done writing AeroDyn blade file. The file is stored at /home/kz/Desktop/AeroDynBL.dat")
        bl.close()

    def Geo_generateTurbinesFoam(self, table):
        print("Generate turbinesFoam file")
        # TODO: replace file name and location
        bl = open('/home/kz/Desktop/turbFoam.dat', 'w')
        af = open('/home/kz/Desktop/AF.dat', 'w')
        for row in range(0, table.rowCount()):
            bl.write("(0 \t " + str(table.item(row, 0).text()) + "\t 0 \t" + str(table.item(row, 1).text()) + "\t 0.25 \t" + str(table.item(row, 2).text()) + ")\n")
            af.write(str(table.item(row,3).text())+'\n')
        print("Done writing turbinesFoam blade file. The file is stored at /home/kz/Desktop/turbFoam.dat and AF.dat")

    
    #=====  PGL FUNCTIONS ===============================================
    
    def Geo_runPGL(self, table):
        print("run PGL")
        self.call_writePGLinputs()
        self.call_generateSurfMesh()
        
    #write all the geometry files required by PGL, from global turbine data 
    def call_writePGLinputs(self):
        if self.models and self.models["OpenTurbineCoDe"]:
            planform_file = self.models["OpenTurbineCoDe"]["Meshing"]["Aero"]["PGL"]["planform_file"]
        else:
            planform_file = 'planform.dat'
        pgl.writePGLinputs(self.turb_data, self.path_to_case, planform_file)
    
    #generate and write aerodynamic surface mesh with PGL
    def call_generateSurfMesh(self):
        R = self.turb_data["assembly"]["rotor_diameter"] / 2.
        R0 = self.turb_data["components"]["hub"]["diameter"] / 2.
        
        #determine the blending parameter, basically corresponding to the relative thickness of each airfoil
        
        afs = self.turb_data["airfoils"]
        blend_var = np.zeros(len(afs))
        airfoil_list = []
        i = 0
        for af in afs:
            blend_var[i] = af["relative_thickness"]
            airfoil_list.append(af["name"])
            i+=1
            
        print(airfoil_list)
        print(blend_var)

        #Call the function:
        if self.models and self.models["OpenTurbineCoDe"]:
            mesh_file = self.modeling_options["OpenTurbineCoDe"]["Meshing"]["Aero"]["PGL"]["meshName"]
            planform_file = self.modeling_options["OpenTurbineCoDe"]["Meshing"]["Aero"]["PGL"]["planform_file"]
        else:
            mesh_file = '2Dmesh'
            planform_file = 'planform.dat'
        pgl.generateSurfMesh(R0, R, self.path_to_case, planform_file, airfoil_list, blend_var, mesh_file)


    # ==================== BB3D GEOM ==========================================
    ## BB3D stuff begins from here    
    def Geo_setLofts(self, lineEdit, table, QtWidgets):
        self.lofts = int(lineEdit.text())
        if self.lofts > 1:
            table.setEnabled(True)
            table.setRowCount(self.lofts)
            for row in range(self.lofts):
                table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row+1)))
        else:
            table.setEnabled(False)

    def Geo_setBB3DExe(self, lineEdit):
        self.BB3DExe = lineEdit.text()
        print("BB3D is located at " + self.BB3DExe)

    def Geo_setSpar(self, lineEdit):
        spar_ = lineEdit.text().split(" ")[0:]
        self.spar = [float(i) for i in spar_]

    def Geo_openBB3DExe(self, fn, QtWidgets):
        fn_ = QtWidgets.QFileDialog.getOpenFileName(None, "Open BB3D executable", "", "(*)")[0]
        fn.setText(str(fn_))


    def Geo_runBB3D(self, table, table2, lineEdit):
        print("Generating BB3D input file")
        # initialize loft distribution with 1
        loft = [1 for ii in range(table.rowCount())]
        # if loft number is higher than 1, form loft distribution according to table2
        if self.lofts > 1:
            loft[0:int(table2.item(0,1).text())-1] = [1 for ii in range(int(table2.item(0,1).text())-1)]
            for ii in range(1,self.lofts):
                loft_ = table2.item(ii,0).text()
                endSec1 = int(table2.item(ii-1,1).text())
                endSec2 = int(table2.item(ii,1).text())
                for jj in range(endSec1,endSec2):
                    loft[jj] = int(loft_)
            print(loft)
            print(type(loft[1]))
            print(type(loft[-1]))
                
        bl = open('/home/kz/Desktop/workingFolder/blade.dat', 'w')
        bl.write(str(table.rowCount()) + " ## Number of blade sections \n")
        bl.write(str(self.lofts) + " ## Number of lofts \n")
        bl.write(str(len(self.spar)) + " ## Number of spars \n")
        for row in range(0, table.rowCount()):
            afid = table.item(row,3).text()
            bl.write(str(row+1) + "\t" + self.AFID[int(afid)-1] + "\n")
            # print(self.AFID[int(afid)-1])
        bl.write("#NODE 	 RNODES 	  TWIST 	  DRNODES 	 CHORD 	  AEROCENT 	 AEROORIG  	 LOFT  \n")
        for row in range(0, table.rowCount()):      

            bl.write(str(row+1) + "\t" + str(table.item(row,0).text())+ "\t" + str(table.item(row, 2).text()) + "\t  0 \t " + str(table.item(row, 1).text()) + "\t 0.125 \t 0.25 \t " + str(loft[row]) +  "\n")
        bl.write("#SPAR PERCENTAGE \n")
        for i in range(len(self.spar)):
            bl.write(str(self.spar[i])+"\n")

        print("Run BB3D")
        workingFolder = "/home/kz/Desktop/workingFolder"
        os.chdir(workingFolder)
        print(os.system("pwd"))
        subprocess.Popen([self.BB3DExe, "/home/kz/Desktop/workingFolder/blade.dat"])
        #os.system(self.BB3DExe + " " + "/home/kz/Desktop/blade.dat")

    ## BB3D stuff ends at here    

    def Geo_getSalome(self, lineEdit, QtWidgets):
        self.salomeExe = QtWidgets.QFileDialog.getOpenFileName(None, "Open Salome Executable", "", "(*)")[0]
        lineEdit.setText(str(self.salomeExe))

    def Geo_getIGES(self, lineEdit, QtWidgets):
        fn_ = QtWidgets.QFileDialog.getOpenFileName(None, "Load iges file", "", "(*)")[0]
        lineEdit.setText(str(fn_))

    def Geo_runSalome(self, lineEdit_4, lineEdit_2, radioButton):
        print("Run Salome")
        salome_ = lineEdit_4.text()
        geom_ = lineEdit_2.text()
        workingFolder = "/home/kz/Desktop/workingFolder"
        os.chdir(workingFolder)    
        with open(self.path_to_root+"/openturbinecode/geometry/salomeMacro/DTU10_1spar.py", "r") as fin:
            with open("script.py", "w") as fout:
                for line in fin:
                    fout.write(line.replace('???', geom_))
        if radioButton.isChecked():
            subprocess.Popen([salome_, "script.py"]) 
        else:      
            subprocess.Popen([salome_, "-t", "script.py"]) 

# if __name__=='__main__':
#     pass

