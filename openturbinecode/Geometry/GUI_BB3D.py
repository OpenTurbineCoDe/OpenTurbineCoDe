# Config program using PyQt5

import sys
import os
import matplotlib.pyplot as plt
import shutil, tempfile, math, numpy, string
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import subprocess
import pyqtgraph as pg
import scp

form_class = uic.loadUiType("GUI_BB3D.ui")[0]  # Load the UI


class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self,  parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        # Bind the event handlers to the buttons
        self.pushButton.clicked.connect(self.generateFileSimple)
        self.pushButton_2.clicked.connect(self.runBB3D)
        self.pushButton_3.clicked.connect(self.salome)
        self.pushButton_4.clicked.connect(self.salomeDebug)
        self.pushButton_5.clicked.connect(self.saveTo)
        self.radioButton.toggled.connect(self.lineEdit_6.setDisabled)
        self.radioButton.toggled.connect(self.lineEdit_7.setDisabled)
        self.radioButton_2.toggled.connect(self.comboBox.setDisabled)
        self.radioButton_2.toggled.connect(self.lineEdit_7.setDisabled)
        self.radioButton_3.toggled.connect(self.comboBox.setDisabled)
        self.radioButton_3.toggled.connect(self.lineEdit_6.setDisabled)
        self.pushButton_6.clicked.connect(self.loadAeroDyn)

	# Set placeholders
        self.lineEdit.setText("100")
        self.lineEdit_2.setText("10")
        self.lineEdit_3.setText("0.01")
        self.lineEdit_5.setText("0.15 0.5")
        self.lineEdit_4.setText("0")
        self.lineEdit_6.setText("0015")
        self.lineEdit_7.setText("Enter file location")
        self.lineEdit_8.setText("0.1")
        self.lineEdit_20.setText("/home/kz/Desktop/BB3D")
        self.lineEdit_21.setText("/home/kz/Desktop/BB3D/AeroDynCase/blade.dat")

    def loadBlade(self):
        fName = self.lineEdit_5.text()
        with open('AeroDynCase/blade.dat', 'r') as f:
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
        content = [x.strip().split()[0:] for x in f]
        
    def generateFileSimple(self):
        spar = self.lineEdit_5.text().split()
        
        if self.radioButton.isChecked():
            with open('Demo/data.dat', 'w') as fn:
                fn.write(str(2) + " ## Number of blade sections" + '\n')
                fn.write("1 ## Number of lofts" + '\n')
                fn.write(str(len(spar)) + " ## Number of spars" + '\n')
                fn.write("1 \t" + self.comboBox.currentText() + '.dat' + '\n')
                fn.write("2 \t" + self.comboBox.currentText() + '.dat' + '\n')
                fn.write("#NODE \t RNODES \t  TWIST \t  DRNODES \t CHORD \t  AEROCENT \t AEROORIG  \t LOFT  " + '\n')
                fn.write("1 \t 0 \t 0 \t 0 " + self.lineEdit_2.text() + "\t 0.125	\t 0.25	\t 1	" + '\n')
                fn.write("2 \t " + self.lineEdit.text() + '\t' + self.lineEdit_4.text() + '\t' + str(0) + '\t' + str(float(self.lineEdit_2.text())-float(self.lineEdit.text())*float(self.lineEdit_3.text())) + "\t 0.125 \t	0.25	\t 1	" + '\n' )
                fn.write("#SPAR PERCENTAGE" + '\n')
                for x in spar:
                    fn.write(x + '\n')
        elif self.radioButton_2.isChecked():
            nacaName = "naca"+self.lineEdit_6.text()+".dat"
            os.system("python3 naca.py -p"+self.lineEdit_6.text()+">Demo/"+nacaName)
            #subprocess.run(["python3", "naca.py", "-p", self.lineEdit_6.text()]) > ">Demo/"+nacaName
            with open('Demo/data.dat', 'w') as fn:
                fn.write(str(2) + " ## Number of blade sections" + '\n')
                fn.write("1 ## Number of lofts" + '\n')
                fn.write(str(len(spar)) + " ## Number of spars" + '\n')
                fn.write("1 \t" + "naca"+self.lineEdit_6.text() + '.dat' + '\n')
                fn.write("2 \t" + "naca"+self.lineEdit_6.text() + '.dat' + '\n')
                fn.write("#NODE \t RNODES \t  TWIST \t  DRNODES \t CHORD \t  AEROCENT \t AEROORIG  \t LOFT  " + '\n')
                fn.write("1 \t 0 \t 0 \t 0 " + self.lineEdit_2.text() + "\t 0.125	\t 0.25	\t 1	" + '\n')
                fn.write("2 \t " + self.lineEdit.text() + '\t' + self.lineEdit_4.text() + '\t' + str(0) + '\t' + str(float(self.lineEdit_2.text())-float(self.lineEdit.text())*float(self.lineEdit_3.text())) + "\t 0.125 \t	0.25	\t 1	" + '\n' )
                fn.write("#SPAR PERCENTAGE" + '\n')
                for x in spar:
                    fn.write(x + '\n')     
        elif self.radioButton_3.isChecked():
            fileName = self.lineEdit_7.text().split('/')[-1]
            shutil.copyfile(self.lineEdit_7.text(), "Demo/"+fileName)
            with open('Demo/data.dat', 'w') as fn:
                fn.write(str(2) + " ## Number of blade sections" + '\n')
                fn.write("1 ## Number of lofts" + '\n')
                fn.write(str(len(spar)) + " ## Number of spars" + '\n')
                fn.write("1 \t" + fileName + '\n')
                fn.write("2 \t" + fileName + '\n')
                fn.write("#NODE \t RNODES \t  TWIST \t  DRNODES \t CHORD \t  AEROCENT \t AEROORIG  \t LOFT  " + '\n')
                fn.write("1 \t 0 \t 0 \t 0 " + self.lineEdit_2.text() + "\t 0.125	\t 0.25	\t 1	" + '\n')
                fn.write("2 \t " + self.lineEdit.text() + '\t' + self.lineEdit_4.text() + '\t' + str(0) + '\t' + str(float(self.lineEdit_2.text())-float(self.lineEdit.text())*float(self.lineEdit_3.text())) + "\t 0.125 \t	0.25	\t 1	" + '\n' )
                fn.write("#SPAR PERCENTAGE" + '\n')
                for x in spar:
                    fn.write(x + '\n')

    def salome(self):
        spar = self.lineEdit_5.text().split()
        gridSize = self.lineEdit_8.text()
        if len(spar) == 1:
            fin = open("salomeMeshing1Spar_org.py", "rt")
            fout = open("salomeMeshing1Spar.py", "wt")
            for line in fin:
                fout.write(line.replace('????', gridSize))
            fin.close()
            fout.close()
            os.system("/home/kz/salome_meca/appli_V2017.0.2/salome -t salomeMeshing1Spar.py")              

        elif len(spar) == 2:
            fin = open("salomeMeshing2Spar_org.py", "rt")
            fout = open("salomeMeshing2Spar.py", "wt")
            for line in fin:
                fout.write(line.replace('????', gridSize))
            fin.close()
            fout.close()
            os.system("/home/kz/salome_meca/appli_V2017.0.2/salome -t salomeMeshing2Spar.py")   
        else:
            print("Error! Spars can not be more than 3")

    def salomeDebug(self):
        spar = self.lineEdit_5.text().split()
        gridSize = self.lineEdit_8.text()
        if len(spar) == 1:
            fin = open("salomeMeshing1Spar_org.py", "rt")
            fout = open("salomeMeshing1Spar.py", "wt")
            for line in fin:
                fout.write(line.replace('????', gridSize))
            fin.close()
            fout.close()
            os.system("/home/kz/salome_meca/appli_V2017.0.2/salome salomeMeshing1Spar.py")              

        elif len(spar) == 2:
            fin = open("salomeMeshing2Spar_org.py", "rt")
            fout = open("salomeMeshing2Spar.py", "wt")
            for line in fin:
                fout.write(line.replace('????', gridSize))
            fin.close()
            fout.close()
            os.system("/home/kz/salome_meca/appli_V2017.0.2/salome salomeMeshing2Spar.py")   
        else:
            print("Error! Spars can not be more than 3")

    def runBB3D(self): 
        os.chdir('Demo')
        os.system('./make_blade')
        os.chdir('..')

    def saveTo(self): 
        saveLoc = self.lineEdit_20.text()
        os.system("cp Mesh_Simple2.cgns "+saveLoc)

    def loadAeroDyn(self):
        with open(self.lineEdit_21.text(), 'r') as f:
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            next(f)
            content = [x.strip().split()[0:] for x in f]
        NoSec = len(content)
        self.tableWidget.setRowCount(NoSec)
        for i in range(0, NoSec-1):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(content[i][0]))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(content[i][4]))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(content[i][5]))
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(content[i][6]))
            self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(str(0.125)))
            self.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem(str(0.25)))
            self.tableWidget.setItem(i, 6, QtWidgets.QTableWidgetItem(content[i][6]))


def run():
    app = QtWidgets.QApplication(sys.argv)
    myWindow = Mapper()
    myWindow.show()
    app.exec_()

run()
