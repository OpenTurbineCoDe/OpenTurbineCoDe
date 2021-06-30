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

form_class = uic.loadUiType("Config.ui")[0]  # Load the UI


class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self,  parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        # Bind the event handlers to the buttons
        self.pushButton.clicked.connect(self.sendToHPC)

	# Set placeholders
        self.lineEdit_7.setText("11.4")

    def showSolverSetup(self):
        print("The user have selected "+str(self.comboBox.currentText()))
        if self.comboBox.currentText() == "AeroDyn (BEM)":
            self.stackedWidget.setCurrentIndex(1)
            self.lineEdit_2.setText("0 0.5 20")
        if self.comboBox.currentText() == "OpenFOAM (ALM)":
            self.stackedWidget.setCurrentIndex(0)
            self.lineEdit_2.setText("0 0.5 20")

    def sendToHPC(self):
        subprocess.run(["scp", "-r", self.lineEdit_12.text() ,self.lineEdit_13.text()+"@"+self.lineEdit_14.text()+":"+self.lineEdit_15.text()])
        subprocess.run(["rm", "-r",  self.ALMFolder+"/rpm*"])

def run():
    app = QtWidgets.QApplication(sys.argv)
    myWindow = Mapper()
    myWindow.show()
    app.exec_()

run()
