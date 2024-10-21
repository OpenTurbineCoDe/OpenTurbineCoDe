import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import logging

from pathlib import Path

# Conditional imports
try:
    from PyQt5 import QtCore, QtGui, uic, QtWidgets  # noqa: F401
    from PyQt5.QtWidgets import QFileDialog  # noqa: F401
except ImportError as err:
    logging.error(f"Error importing PyQt5: {err}")
    pass

try:
    import pandas as pd  # noqa: F401
except ImportError as err:
    logging.error(f"Error importing pandas: {err}")
    _has_pandas = False
else:
    _has_pandas = True

try:
    import openmdao.api as om
except ImportError as err:
    logging.error(f"Error importing openmdao: {err}")
    _has_openmdao = False
else:
    _has_openmdao = True

from openturbinecode.controls.TACSDynParams import TACSParams
from openturbinecode.structure.Opt_Struct import StructMDAOom
# import openturbinecode.structure.structure_module as stru
import openturbinecode.structure.structure_module as stru

form_class = uic.loadUiType(
    Path(__file__).parent / "structure_gui.ui")[0]  # Load the UI


class Mapper(QtWidgets.QMainWindow, form_class):
    def __init__(self, myStru, parent=None, withMasterGUI=False):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.myStru = myStru  # make the control module available

        # =================== INITIALIZE FIELD VALUES ==============================
        self.myStru.setDefaultValues()
        self.writeToUI()

        if withMasterGUI:
            pass

        # =================== CONNECT BUTTONS AND ACTIONS ==============================
        # activate the different UI based on solvers
        self.Solver.activated.connect(self.StructralSolverUI)
        # Load Model
        self.LoadModel.clicked.connect(self.caller_LoadModel)
        # Local run and plot
        self.LocalRun.clicked.connect(self.caller_LocalRun)
        self.Plot.clicked.connect(self.caller_Plot)
        # Contraint default definition
        self.Cst.activated.connect(self.SetContraintdefault)
        # Optimization run
        self.Optimization.clicked.connect(self.caller_Optimization)

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
        # Optimization
        self.Iterations.setText(str(self.myStru.Iterations))
        self.Tolerane.setText(str(self.myStru.Tolerane))

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
        # response
        self.myStru.BeamResponse = self.BeamResponse.currentText()
        self.myStru.TACSResponse = self.TACSResponse.currentText()
        # Optimization
        self.myStru.Contraints = self.Cst.currentText()
        self.myStru.ContraintSymbol = self.Cst_s.currentText()
        self.myStru.ContraintValue = self.Cst_v.text()
        self.myStru.Optimizer = self.Optimizer.currentText()
        self.myStru.Display = self.Display.currentText()
        self.myStru.Iterations = self.Iterations.text()
        self.myStru.Tolerane = self.Tolerane.text()

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
            #            self.myStru.workingmodel == self.myStru.DTU10MWBeamDyn                    # should from yaml
            # TG 7/21 should be 1 equals sign
            self.myStru.workingmodel = self.myStru.DTU10MWBeamDyn
            print("DTU10MW BeamDyn model loaded from library for Parametric sweep: " +
                  self.myStru.workingmodel)
        if self.myStru.Solver == "BeamDyn" and self.myStru.Modelselection == "NREL5MW":
            #            self.myStru.workingmodel == self.myStru.NREL5MWBeamDyn                     # should from yaml
            # TG 7/21 should be 1 equals sign
            self.myStru.workingmodel = self.myStru.NREL5MWBeamDyn
            print("NREL5MW BeamDyn model loaded from library for Parametric sweep: " +
                  self.myStru.workingmodel)
        if self.myStru.Solver == "TACS" and self.myStru.Modelselection == "DTU10MW":
            #            self.myStru.workingmodel == self.myStru.DTU10MWTACS                    # should from yaml
            # TG 7/21 should be 1 equals sign
            self.myStru.workingmodel = self.myStru.DTU10MWTACS
            print("DTU10MW TACS model loaded from library for Parametric sweep: " +
                  self.myStru.workingmodel)
        if self.myStru.Solver == "TACS" and self.myStru.Modelselection == "NREL5MW":
            raise ValueError("Model Mot implemented yet implemented for TACS!")
        if self.myStru.Modelselection == "User_Model":
            raise ValueError("Function not yet implemented!")

    def caller_LocalRun(self):
        self.myStru.setDefaultValues()
        self.readFromUI()
        if self.myStru.Solver == "BeamDyn":
            if self.RB12.isChecked():
                sweep = np.arange(float(self.myStru.TipLoadxL), float(
                    self.myStru.TipLoadxU), float(self.myStru.TipLoadxSTP))
                # L, U, and STP are the lower, upper, and step values for the sweep input in the GUI.
                # Numpy.arange creates an array between L and U evenly spaced by STP.
                # The lower value is included in this range, but the upper value is not.
                for i in range(len(sweep)):
                    self.myStru.TipLoadxCV = sweep[i]
                    self.myStru.RunModelUpdate_Beamdyn()
                    self.myStru.LocalRun()
                    self.myStru.postprocessBeamDyn()
                self.myStru.TipLoadxCV = self.myStru.TipLoadx
            if self.RB22.isChecked():
                sweep = np.arange(float(self.myStru.DistrLoadxL), float(
                    self.myStru.DistrLoadxU), float(self.myStru.DistrLoadxSTP))
                for i in range(len(sweep)):
                    self.myStru.DistrLoadxCV = sweep[i]
                    self.myStru.RunModelUpdate_Beamdyn()
                    self.myStru.LocalRun()
                    self.myStru.postprocessBeamDyn()
                self.myStru.DistrLoadxCV = self.myStru.DistrLoadx
            if self.RB32.isChecked():
                sweep = np.arange(float(self.myStru.TwstSclFL), float(
                    self.myStru.TwstSclFU), float(self.myStru.TwstSclFSTP))
                for i in range(len(sweep)):
                    self.myStru.TwstSclFCV = sweep[i]
                    self.myStru.RunModelUpdate_Beamdyn()
                    self.myStru.LocalRun()
                    self.myStru.postprocessBeamDyn()
                self.myStru.TwstSclFCV = self.myStru.TwstSclF
        # TACS running updated
        if self.myStru.Solver == "TACS":
            T = self.myStru.T
            self.Response = []
            if str(self.myStru.TACSResponse) == "KSFailure":
                ResItem = ["USkinKSFailure"]
            if str(self.myStru.TACSResponse) == "Mass_bld":
                ResItem = ["TotalMass"]
            if self.RB42.isChecked():
                sweep = np.arange(float(self.myStru.ThickSclF1L), float(
                    self.myStru.ThickSclF1U), float(self.myStru.ThickSclF1STP))
                for i in range(len(sweep)):
                    self.myStru.thickness = []
                    self.myStru.ThickSclF1CV = sweep[i]
                    ones = np.ones(3)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF1CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF2CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF3CV)
                    TACS = TACSParams(self.myStru.DTU10MWTACS,
                                      self.myStru.thickness*np.array(T))
                    Res, Res_dot = TACS.StructuralAnalysis(ResItem)
                    self.Response.append(Res[ResItem[0]])
                self.myStru.ThickSclF1CV = self.myStru.ThickSclF1
            if self.RB52.isChecked():
                sweep = np.arange(float(self.myStru.ThickSclF2L), float(
                    self.myStru.ThickSclF2U), float(self.myStru.ThickSclF2STP))
                for i in range(len(sweep)):
                    self.myStru.thickness = []
                    self.myStru.ThickSclF2CV = sweep[i]
                    ones = np.ones(3)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF1CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF2CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF3CV)
                    TACS = TACSParams(self.myStru.DTU10MWTACS,
                                      self.myStru.thickness*np.array(T))
                    Res, Res_dot = TACS.StructuralAnalysis(ResItem)
                    self.Response.append(Res[ResItem[0]])
                self.myStru.ThickSclF2CV = self.myStru.ThickSclF2
            if self.RB62.isChecked():
                sweep = np.arange(float(self.myStru.ThickSclF3L), float(
                    self.myStru.ThickSclF3U), float(self.myStru.ThickSclF3STP))
                for i in range(len(sweep)):
                    self.myStru.thickness = []
                    self.myStru.ThickSclF3CV = sweep[i]
                    ones = np.ones(3)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF1CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF2CV)
                    self.myStru.thickness.extend(ones*self.myStru.ThickSclF3CV)
                    TACS = TACSParams(self.myStru.DTU10MWTACS,
                                      self.myStru.thickness*np.array(T))
                    Res, Res_dot = TACS.StructuralAnalysis(ResItem)
                    self.Response.append(Res[ResItem[0]])
                self.myStru.ThickSclF3CV = self.myStru.ThickSclF3
        self.myStru.sweep = sweep

    def caller_Plot(self):
        self.readFromUI()
        if self.myStru.Solver == "BeamDyn":
            # plot
            # TG 7/21 Creates new figure so there can be multiple simultaneous plots.
            plt.figure()
            if self.myStru.BeamResponse == "RootFxr_max":
                plt.plot(self.myStru.sweep, self.myStru.RootFxr_max, 'r-s')
                response_units = " (N)"  # TG 7/21
            if self.myStru.BeamResponse == "RootFyr_max":
                plt.plot(self.myStru.sweep, self.myStru.RootFyr_max, 'r-s')
                response_units = " (N)"  # TG 7/21
            if self.myStru.BeamResponse == "RootMxr_max":
                plt.plot(self.myStru.sweep, self.myStru.RootMxr_max, 'r-s')
                response_units = " (N-m)"  # TG 7/21
            if self.myStru.BeamResponse == "RootMyr_max":
                plt.plot(self.myStru.sweep, self.myStru.RootMyr_max, 'r-s')
                response_units = " (N-m)"  # TG 7/21
            if self.myStru.BeamResponse == "TipTDxr_max":
                plt.plot(self.myStru.sweep, self.myStru.TipTDxr_max, 'r-s')
                response_units = " (m)"  # TG 7/21
            if self.myStru.BeamResponse == "TipTDyr_max":
                plt.plot(self.myStru.sweep, self.myStru.TipTDyr_max, 'r-s')
                response_units = " (m)"  # TG 7/21
            sweeptype = "Tip_Load_x (N)" if self.RB12.isChecked(
            ) else "Distributed_Load_x (N/m)" if self.RB22.isChecked() else "Twist_Scale_Factor"  # TG 7/21

            plt.xlabel(sweeptype)  # TG 7/21
            plt.ylabel(self.myStru.BeamResponse + response_units)  # TG 7/21
            plt.show()
        # TACS plot
        if self.myStru.Solver == "TACS":
            plt.plot(self.myStru.sweep, self.Response, 'r-s')
            plt.show()

    def SetContraintdefault(self):
        self.readFromUI()
        constraint = str(self.myStru.Contraints)
        print("Current Constraint:"+constraint)
        if constraint == "TACS_KSFailure":
            self.Cst_v.setText(str(self.myStru.ContraintValueKSF))
        if constraint == "TACS_Mass_bld":
            self.Cst_v.setText(str(self.myStru.ContraintValueBldM))

    def caller_Optimization(self):
        self.myStru.setDefaultValues()
        self.readFromUI()
        if self.myStru.Solver == "TACS":
            prob = om.Problem()
            MDAOObj = StructMDAOom()
            prob.model.add_subsystem('p', MDAOObj)
            # Default thickness values along the span
            T = self.myStru.T
            # Tacs parameterization for blade
            if self.RB43.isChecked():
                # Update first segment
                prob.model.add_design_var('p.Thick1', lower=float(
                    self.myStru.ThickSclF1L)*T[0], upper=float(self.myStru.ThickSclF1U)*T[0])
                prob.model.add_design_var('p.Thick2', lower=float(
                    self.myStru.ThickSclF1L)*T[1], upper=float(self.myStru.ThickSclF1U)*T[1])
                prob.model.add_design_var('p.Thick3', lower=float(
                    self.myStru.ThickSclF1L)*T[2], upper=float(self.myStru.ThickSclF1U)*T[2])
            if self.RB53.isChecked():
                # Update second segment
                prob.model.add_design_var('p.Thick4', lower=float(
                    self.myStru.ThickSclF2L)*T[3], upper=float(self.myStru.ThickSclF2U)*T[3])
                prob.model.add_design_var('p.Thick5', lower=float(
                    self.myStru.ThickSclF2L)*T[4], upper=float(self.myStru.ThickSclF2U)*T[4])
                prob.model.add_design_var('p.Thick6', lower=float(
                    self.myStru.ThickSclF2L)*T[5], upper=float(self.myStru.ThickSclF2U)*T[5])
            if self.RB63.isChecked():
                # Update third segment
                prob.model.add_design_var('p.Thick7', lower=float(
                    self.myStru.ThickSclF3L)*T[6], upper=float(self.myStru.ThickSclF3U)*T[6])
                prob.model.add_design_var('p.Thick8', lower=float(
                    self.myStru.ThickSclF3L)*T[7], upper=float(self.myStru.ThickSclF3U)*T[7])
                prob.model.add_design_var('p.Thick9', lower=float(
                    self.myStru.ThickSclF3L)*T[8], upper=float(self.myStru.ThickSclF3U)*T[8])

            if self.myStru.TACSResponse == "KSFailure":
                prob.model.add_objective('p.USkinKSFailure')
            if self.myStru.TACSResponse == "Mass_bld":
                prob.model.add_objective('p.Mass')
            # Constraint
            if self.Cst.currentText() == "TACS_KSFailure" and self.Cst_s.currentText() == "<=":
                prob.model.add_constraint(
                    'p.USkinKSFailure', upper=float(self.myStru.ContraintValue))
            if self.Cst.currentText() == "TACS_Mass_bld" and self.Cst_s.currentText() == "<=":
                prob.model.add_constraint(
                    'p.Mass', upper=float(self.myStru.ContraintValue))

            # Driver setup
            driver = prob.driver = om.ScipyOptimizeDriver(
                optimizer=self.myStru.Optimizer, tol=float(self.myStru.Tolerane))
            driver.options['maxiter'] = int(self.myStru.Iterations)
            if self.myStru.Display == "True":
                driver.options['disp'] = True
            else:
                driver.options['disp'] = False

            driver.recording_options['includes'] = ['*']
            driver.recording_options['record_objectives'] = True
            driver.recording_options['record_constraints'] = True
            driver.recording_options['record_desvars'] = True
            driver.recording_options['record_inputs'] = True
            driver.recording_options['record_outputs'] = True
            driver.recording_options['record_residuals'] = True

            recorder = om.SqliteRecorder("cases.sql")
            driver.add_recorder(recorder)

            prob.setup()
            prob.run_driver()
            # Extract retuls
            desvar_nd = prob.driver.desvar_nd
            nd_obj = prob.driver.obj_nd
            print('Optimal design:'+desvar_nd)
            print('Optimal response:'+nd_obj)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    path_to_root = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))))
    path_to_case = path_to_root + os.sep + "models" + \
        os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep
    # path_to_case = os.getcwd() + os.sep + "Madsen2019" + os.sep

    # empty control object
    myStru = stru.Structural(path_to_case)

    myWindow = Mapper(myStru)
    myWindow.show()
    app.exec_()
