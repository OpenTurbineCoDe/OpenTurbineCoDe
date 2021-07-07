# ================================================
# External python imports
# ================================================

import sys
import os
import matplotlib.pyplot as plt
import shutil, tempfile, math, numpy, string
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import subprocess

form_class = uic.loadUiType(os.path.dirname( os.path.realpath(__file__) ) +os.sep+ "Config.ui")[0]  # Load the UI

class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, OTCD,  parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
              
    # --- Setting default values ---

    # --- Reading input values ---

    # --- Executing analysis/optimization (calling OTCD) ---
    
if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = Mapper()
    myWindow.show()
    app.exec_()

