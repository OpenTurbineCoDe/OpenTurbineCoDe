#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 18:13:04 2021
This script is used to be the mainbody of DTU10MW blade optimization for demonstration only.
@author: Xianping Du, Rutgers, xianping.du@rutgers.edu
"""
import os
import numpy as np
import openmdao.api as om
from openturbinecode.controls.TACSDynParams import TACSParams


class StructMDAOom(om.ExternalCodeComp):
    def setup(self):
        # setup the thickness scaling factors along span
        self.add_input('Thick1', val=42.0)
        self.add_input('Thick2', val=46.0)
        self.add_input('Thick3', val=40.0)
        self.add_input('Thick4', val=35.0)
        self.add_input('Thick5', val=28.0)
        self.add_input('Thick6', val=25.0)
        self.add_input('Thick7', val=18.0)
        self.add_input('Thick8', val=12.0)
        self.add_input('Thick9', val=10.0)
        # define output
        self.add_output('Mass', val=300856.25)
        # self.add_output('LSkinKSFailure', val=0.0)
        self.add_output('USkinKSFailure', val=0.2918)
        # Evaluated functions for putput
        self.evalFunclist = ['USkinKSFailure', 'TotalMass']

        self.path_to_root = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))
        self.TacsFile = self.path_to_root + \
            "/controls/tacs_setup/DTU_10MW_RWT_blade3D_rotated_Single.bdf"
        # file check
        self.options['external_input_files'] = [self.TacsFile]

    def setup_partials(self):
        # derivative calculation method
        # self.declare_partials(of='*', wrt='*')
        self.declare_partials(of='*', wrt='*', method='fd')

    def compute(self, inputs, outputs):
        # Thicknesses
        v_t1 = inputs['Thick1']
        v_t2 = inputs['Thick2']
        v_t3 = inputs['Thick3']
        v_t4 = inputs['Thick4']
        v_t5 = inputs['Thick5']
        v_t6 = inputs['Thick6']
        v_t7 = inputs['Thick7']
        v_t8 = inputs['Thick8']
        v_t9 = inputs['Thick9']
        # DV definition
        Thicks = np.array(
            [v_t1, v_t2, v_t3, v_t4, v_t5, v_t6, v_t7, v_t8, v_t9])
        # setup solver
        TACSsolver = TACSParams(self.TacsFile, Thicks)
        FunRes, FunRes_d = TACSsolver.StructuralAnalysis(self.evalFunclist)
        self.derivative = FunRes_d
        # Assgind feedback
        outputs['USkinKSFailure'] = FunRes[self.evalFunclist[0]]
        outputs['Mass'] = FunRes[self.evalFunclist[1]]


if __name__ == '__main__':
    # import sys
    prob = om.Problem()
    prob.model.add_subsystem('p', StructMDAOom())
    # Define DVs
    prob.model.add_design_var('p.Thick1', lower=21., upper=63.)
    prob.model.add_design_var('p.Thick2', lower=23., upper=69.)
    prob.model.add_design_var('p.Thick3', lower=20., upper=60.)
    prob.model.add_design_var('p.Thick4', lower=18., upper=53.)
    prob.model.add_design_var('p.Thick5', lower=14., upper=42.)
    prob.model.add_design_var('p.Thick6', lower=12., upper=48.)
    prob.model.add_design_var('p.Thick7', lower=9., upper=27.)
    prob.model.add_design_var('p.Thick8', lower=6., upper=18.)
    prob.model.add_design_var('p.Thick9', lower=5., upper=15.)
    # Contrained Uskin KS failure
    prob.model.add_constraint('p.USkinKSFailure', upper=0.4)
    # Define objective: min mass
    prob.model.add_objective('p.Mass')
    # SciPy optimizer
    driver = prob.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-9)
    driver.options['maxiter'] = 20
    driver.options['disp'] = True
    # Options of optimizers
    driver.recording_options['includes'] = ['*']
    driver.recording_options['record_objectives'] = True
    driver.recording_options['record_constraints'] = True
    driver.recording_options['record_desvars'] = True
    driver.recording_options['record_inputs'] = True
    driver.recording_options['record_outputs'] = True
    driver.recording_options['record_residuals'] = True
    # Recorder definition
    recorder = om.SqliteRecorder("cases.sql")
    driver.add_recorder(recorder)
    # Problem setup and run driver
    prob.setup()
    prob.run_driver()
    prob.cleanup()
    # Read recorder
    cr = om.CaseReader("cases.sql")
    driver_cases = cr.list_cases('driver')
    last_case = cr.get_case(driver_cases[-1])
    print("Optimal Solutions:\n")
    print(last_case)
