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
        

    # ==================== MODULE-SPECIFIC FUNCTIONS ==========================================
    def loadGeom(self, fn, table, QtWidgets, comboBox):
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
        for i in range(0, NoSec):
            table.setItem(i, 0, QtWidgets.QTableWidgetItem(content[i][0]))
            table.setItem(i, 1, QtWidgets.QTableWidgetItem(content[i][4]))
            table.setItem(i, 2, QtWidgets.QTableWidgetItem(content[i][5]))
            table.setItem(i, 3, QtWidgets.QTableWidgetItem(content[i][6]))
        # set the items in comboBox according to the airfoil numbers
        # currently using the data in the original aerodyn file
        # TODO: read data from the table to allow edits
        self.afNum = content[-1][-1]
        for i in range(0, int(self.afNum)):
            comboBox.addItem(str(i+1))
        self.AFID = ["" for x in range(int(self.afNum))]    # initial AFID to store airfoil ID

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
    def Geo_loadAFCoord(self, comboBox1, comboBox2, lineEdit):
        lineEdit.setText(os.path.dirname( os.path.realpath(__file__) ) + os.sep + "lib_airfoils" + os.sep + comboBox2.currentText() + '.dat')
        print('AF ID ' + comboBox1.currentText() + ': ' + comboBox2.currentText())
        self.AFID[int(comboBox1.currentText())-1] = lineEdit.text() 
        print(self.AFID[0])
        
    def Geo_loadExternalAF(self, toolButton, lineEdit, QtWidgets, comboBox2):
        fn_ = QtWidgets.QFileDialog.getOpenFileName(None, "Open airfoil coordinate file", "", "(*)")[0]
        lineEdit.setText(str(fn_))
        self.AFID[int(comboBox2.currentText())-1] = lineEdit.text() 
        print('AF ID ' + comboBox2.currentText() + ': ' + lineEdit.text())

    def Geo_openSalomeD(self, comboBox, radioButton, button):
        if comboBox.currentText() == 'Salome' and radioButton.isChecked():
            #TODO: replace by input from GUI
            os.system("/home/kz/salome_meca/appli_V2017.0.2/salome")   
    
    def Geo_setSalome(self, lineEdit, QtWidgets):
        salome_ = QtWidgets.QFileDialog.getOpenFileName(None, "Open Salome executable", "", "(*)")[0]
        lineEdit.setText(salome_)

    def Geo_generateGeom(self, comboBox, table, table2, lineEdit):
        if comboBox.currentText() == "AeroDyn blade file":
            self.Geo_generateAeroDyn(table)

        elif comboBox.currentText() == "turbinesFoam file":
            self.Geo_generateTurbinesFoam(table)

        elif comboBox.currentText() == "BB3D":
            self.Geo_runBB3D(table, table2, lineEdit)

        elif comboBox.currentText() == "PGL":
            self.Geo_runPGL(table)

        elif comboBox.currentText() == "Salome":
            self.Geo_runSalome(table)

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

    def Geo_runPGL(self, table):
        print("run PGL")

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

    def Geo_setSpar(self, lineEdit):
        spar_ = lineEdit.text().split(" ")[0:]
        self.spar = [float(i) for i in spar_]

    def Geo_runBB3D(self, table, table2, lineEdit):
        print("Generating BB3D input file")
        bl = open('/home/kz/Desktop/blade.dat', 'w')
        bl.write(str(table.rowCount()) + " ## Number of blade sections \n")
        bl.write(str(self.lofts) + " ## Number of lofts \n")
        bl.write(str(len(self.spar)) + "## Number of spars \n")
        for row in range(0, table.rowCount()):
            afid = table.item(row,3).text()
            bl.write(str(row+1) + "\t" + self.AFID[int(afid)-1] + "\n")
        bl.write("#NODE 	 RNODES 	  TWIST 	  DRNODES 	 CHORD 	  AEROCENT 	 AEROORIG  	 LOFT  \n")
        for row in range(0, table.rowCount()):
            #TODO:  1. change loft distribution according to table in bb3d
            bl.write(str(row+1) + "\t" + str(table.item(row,0).text())+ "\t" + str(table.item(row, 2).text()) + "\t  0 \t " + str(table.item(row, 1).text()) + "\t 0.125 \t 0.25 \t " + "1" +  "\n")
        bl.write("#SPAR PERCENTAGE \n")
        for i in range(len(self.spar)):
            bl.write(str(self.spar[i])+"\n")

        print("Run BB3D")
        os.system('/home/kz/Desktop/make_blade')
        
        # Codes to run BB3D 
        # The executable is pre-compiled and will be copied to the case folder

    ## BB3D stuff ends at here    


    def Geo_runSalome(self, table):
        print("Launch Salome")

# if __name__=='__main__':
#     pass

