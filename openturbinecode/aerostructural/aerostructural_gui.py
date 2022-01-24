# ================================================
# External python imports
# ================================================

import sys
import os

# import matplotlib.pyplot as plt
import numpy as np
import ast
import argparse

# import subprocess

# conditional imports
try:
    from PyQt5 import QtCore, QtGui, uic, QtWidgets  # noqa
    from PyQt5.QtWidgets import QFileDialog  # noqa
except ImportError as err:  # noqa
    pass

import openturbinecode.aerostructural.aerostructural_module as aerostruct

form_class = uic.loadUiType(os.path.dirname(os.path.realpath(__file__)) + os.sep + "Config.ui")[0]  # Load the UI


class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myAeroStruct, parent=None, withMasterGUI=False):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.myAeroStruct = myAeroStruct

        # =================== INITIALIZE FIELD VALUES ==============================
        # self.myAeroStruct.setDefaultValues()  # redundant, it's done on init
        self.writeToUI()

        # =================== FORCE INTERNAL VALUES WHEN RUNNING WITH MASTER ==============================
        if withMasterGUI:
            self.lineEdit_5.setEnabled(False)

            self.pushButton_14.setEnabled(False)

            self.comboBox.setEnabled(False)
            self.comboBox.setItemText(0, "internal")

        # =================== CONNECT BUTTONS AND ACTIONS ==============================
        # Bind the event handlers to the buttons using a function

        # TODO: connect buttons:
        # # self.loadRotor.clicked.connect(self.load_case)
        self.RunAnalysis.clicked.connect(self.caller_Run)
        self.RunOptimization.clicked.connect(self.caller_Opt)
        # self.plot_cp.clicked.connect(self.myAeroStructPlotCp)
        # self.plot_thrust.clicked.connect(self.myAeroStructPlotThrust)
        # self.plot_torque.clicked.connect(self.myAeroStructPlotTorque)
        self.Push_sendtoHPC.clicked.connect(self.caller_SendToHPC)

    # ============== Functions to fill the UI, or to retrieve info from the UI ==========================

    def writeToUI(self):

        # Set interface values
        # model list
        # self.rotorPath.setText(self.myAeroStruct.path_to_case)

        # self.windSpeed.setText(', '.join([str(el) for el in self.myAeroStruct.Vlist]))
        # self.TSR.setText(', '.join([str(el) for el in self.myAeroStruct.tsrlist]))
        self.input_pitchAngle.setText(", ".join([str(el) for el in self.myAeroStruct.pitchlist]))
        self.input_twist.setText(", ".join([str(el) for el in self.myAeroStruct.analysis_input["twist"]]))
        self.input_chord.setText(", ".join([str(el) for el in self.myAeroStruct.analysis_input["chord"]]))
        self.input_thickness.setText(", ".join([str(el) for el in self.myAeroStruct.analysis_input["thickness"]]))
        self.input_sweep.setText(", ".join([str(el) for el in self.myAeroStruct.analysis_input["sweep"]]))
        self.input_span.setText(str(self.myAeroStruct.analysis_input["span"]))

        self.output_torque.setChecked(self.myAeroStruct.analysis_output["torque"])
        self.output_thrust.setChecked(self.myAeroStruct.analysis_output["thrust"])
        self.output_bending.setChecked(self.myAeroStruct.analysis_output["bending"])
        self.output_mass.setChecked(self.myAeroStruct.analysis_output["mass"])
        self.output_stress.setChecked(self.myAeroStruct.analysis_output["stress"])
        self.output_liftdistr.setChecked(self.myAeroStruct.analysis_output["lift_distr"])

        self.DV_twist.setChecked(self.myAeroStruct.opt_dvs["twist"])
        self.DV_thickness.setChecked(self.myAeroStruct.opt_dvs["thickness"])
        self.DV_chord.setChecked(self.myAeroStruct.opt_dvs["chord"])
        self.DV_sweep.setChecked(self.myAeroStruct.opt_dvs["sweep"])
        self.DV_structThick.setChecked(self.myAeroStruct.opt_dvs["structThick"])

        self.con_stress.setChecked(self.myAeroStruct.opt_constraints["stress"])
        self.con_displ.setChecked(self.myAeroStruct.opt_constraints["displ"])
        self.con_thrust.setChecked(self.myAeroStruct.opt_constraints["thrust"])

        self.obj_torque.setChecked(self.myAeroStruct.opt_obj["torque"])
        self.obj_mass.setChecked(self.myAeroStruct.opt_obj["mass"])
        self.weight_Torque.setText(str(self.myAeroStruct.torqueWeight))
        self.weight_Mass.setText(str(self.myAeroStruct.massWeight))
        self.conv_tol.setText(str(self.myAeroStruct.convergencetolerance))
        self.max_iters.setText(str(self.myAeroStruct.maxiters))

        self.Wind_V.setText(str(self.myAeroStruct.Vlist))
        self.rpm.setText(str(self.myAeroStruct.rpmlist))

        self.whichHPC.setText(str(self.myAeroStruct.CaseToHPC))

    def readFromUI(self):
        # Get user inputs data
        # TODO: injecting attributes in a class is technically very bad, might want to think about an alternative soon
        # self.myAeroStruct.XXX = self.model_list.currentText()
        # self.myAeroStruct.path_to_case = self.rotorPath.text()

        self.myAeroStruct.fidelity = str(self.Fidelity_selection.currentText())

        self.myAeroStruct.pitchlist = np.array(ast.literal_eval(self.input_pitchAngle.text()))

        self.myAeroStruct.Vlist = np.array(ast.literal_eval(self.Wind_V.text()))
        self.myAeroStruct.rpmlist = np.array(ast.literal_eval(self.rpm.text()))

        self.myAeroStruct.opt_obj = {
            "torque": True if self.obj_torque.checkState() == 2 else False,
            "mass": True if self.obj_mass.checkState() == 2 else False,
            "torqueWeight": np.float(ast.literal_eval(self.weight_Torque.text())),
            "massWeight": np.float(ast.literal_eval(self.weight_Mass.text())),
        }

        self.myAeroStruct.analysis_input = {
            "twist": np.array(ast.literal_eval(self.input_twist.text())),
            "chord": np.array(ast.literal_eval(self.input_chord.text())),
            "thickness": np.array(ast.literal_eval(self.input_thickness.text())),
            "sweep": np.array(ast.literal_eval(self.input_sweep.text())),
            "span": np.array(ast.literal_eval(self.input_span.text())),
        }

        self.myAeroStruct.analysis_output = {
            "torque": True if self.output_torque.checkState() == 2 else False,
            "thrust": True if self.output_thrust.checkState() == 2 else False,
            "bending": True if self.output_bending.checkState() == 2 else False,
            "mass": True if self.output_mass.checkState() == 2 else False,
            "stress": True if self.output_stress.checkState() == 2 else False,
            "lift_distr": True if self.output_liftdistr.checkState() == 2 else False,
        }
        self.myAeroStruct.opt_dvs = {
            "twist": True if self.DV_twist.checkState() == 2 else False,
            "thickness": True if self.DV_thickness.checkState() == 2 else False,
            "chord": True if self.DV_chord.checkState() == 2 else False,
            "sweep": True if self.DV_sweep.checkState() == 2 else False,
            "structThick": True if self.DV_structThick.checkState() == 2 else False,
        }
        self.myAeroStruct.opt_constraints = {
            "stress": True if self.con_stress.checkState() == 2 else False,
            "displ": True if self.con_displ.checkState() == 2 else False,
            "thrust": True if self.con_thrust.checkState() == 2 else False,
        }

        self.myAeroStruct.opt_options = {
            "max_iters": np.float(ast.literal_eval(self.max_iters.text())),
            "optimizer": str(self.optimizer_selection.currentText()),
            "tol": np.float(ast.literal_eval(self.conv_tol.text())),
        }  # optimizer options

        # --- Data Handling ---
        self.myAeroStruct.caseToHpc = self.whichHPC.text()

    # --- Executing analysis/optimization (calling OTCD) ---

    def caller_Run(self):
        # read params from the GUI
        self.readFromUI()

        # execute function through the control object
        self.myAeroStruct.Run()

    def caller_Opt(self):
        # read params from the GUI
        self.readFromUI()

        self.myAeroStruct.optimize = True

        # execute function through the control object
        self.myAeroStruct.Run()

    def caller_SendToHPC(self):
        # read params from the GUI
        self.readFromUI()

        self.myAeroStruct.SendToHPC(self.myAeroStruct.caseToHpc)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("--plotonly", action="store_true", help="Do not compute anything")
    args = parser.parse_args()

    path_to_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    path_to_case = path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep

    myAeroStruct = aerostruct.Aerostructural(path_to_case, plotonly=args.plotonly)

    myWindow = Mapper(myAeroStruct)
    myWindow.show()
    app.exec_()
