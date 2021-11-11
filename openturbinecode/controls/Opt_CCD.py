#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 18:13:04 2021
For the OpenFAST based CCD.
@author: Xianping Du, rutgers University, xianping.du@rutgers.edu
"""
import os
import sys
#-------------------------------- LOAD INPUT PARAMETERS ---------------------------------#
# Change this for your turbine
#this_dir            = os.path.dirname(__file__) 

import yaml 
import numpy as np
# Import ROSCO_toolbox modules 
try:
    from ROSCO_toolbox import controller as ROSCO_controller
    from ROSCO_toolbox import turbine as ROSCO_turbine
    from ROSCO_toolbox.utilities import  write_DISCON
except ImportError as err:
    _has_rosco = False
else:
    _has_rosco = True

try:
    from pyFAST.input_output import FASTInputFile,FASTOutputFile
except ImportError as err:
    _has_pyfast = False
else:
    _has_pyfast = True

# """
# Definition of a decorator to be used on every function that requires the sprcific module
# """
# def requires_pyfast(function):
#     def check_requirement(*args,**kwargs):
#         if not _has_pyfast:
#             raise ImportError("pyfast is required to do this.")
#         function(*args,*kwargs)
#     return check_requirement


# my function
from .control_module import Control
from .AutoRosco import TurbineMorph
#import openMDAO
import openmdao.api as om
#%%
#---------------------------------- DO THE FUN STUFF ------------------------------------#

class ControlMDAOom(om.ExternalCodeComp):
    def setup(self):
        # setup the baseline openfast model also
        # openfast chord
        self.add_input('Chd_c', val=0.0)
        # openfast aero twist
        self.add_input('Twst_c', val=0.0)
        # control module
        self.add_input('omega_vs', val=0.2)
        self.add_input('zeta_vs', val=0.7)
        self.add_input('omega_pc', val=0.3)
        self.add_input('zeta_pc', val=0.7)
        
        # define constraint and objectives
        self.add_output('RotThrust_max', val=0.0)  
        self.add_output('RotTorq_max', val=0.0) 
        #self.add_output('WeAEP_Mass', val=0.0) 
        self.path_to_root       = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.yamlfile           = self.path_to_root+"/controls/OTCD_DTU10MW.yaml"
        self.WorkFast_file      = self.path_to_root+"/controls/DTU10MWAero15/DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_Baseline.fst"
        self.WorkFast_fileloc   = self.path_to_root+"/controls/DTU10MWAero15/DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_Baseline.fst"
        # providing these is optional; the component will verify that any input
        # files exist before execution and that the output files exist after.
        self.options['external_input_files']    = [self.yamlfile]
        
        
        self.options['command']                 = ["openfast", self.WorkFast_fileloc] #need to be defined: python wrapper is good

    def setup_partials(self):
        # this external code does not provide derivatives, use finite difference
        self.declare_partials(of='*', wrt='*', method='fd', form='forward',step=0.005)

    def compute(self, inputs, outputs):
        # chord
        v_p     = inputs['Chd_c']
        # twist
        v_t     = inputs['Twst_c']
        
        v_c1    = inputs['omega_vs']
        v_c2    = inputs['zeta_vs']
        v_c3    = inputs['omega_pc']
        v_c4    = inputs['zeta_pc']
        # Section 1: aero update
        xc      = np.array([0,0.1,0.25,0.4,0.55,0.7,0.85,1.0]) 
        v_chd   = np.array([0.0,0.0,v_p,v_p,v_p,v_p,v_p,v_p])
        xt      = xt = np.array([0,0.1,0.25,0.4,0.55,0.7,0.85,1.0]) 
        v_twst  = np.array([0.0,0.0,v_t,v_t,v_t,v_t,v_t,v_t])
        # vc: control variables
        vc      = [v_c1,v_c2,v_c3,v_c4]
        #%%
        # Aeromorphing
        # AeroTwstVar: Twist varaition from original
        # AeroBldNodes: aerodyn node distribution table
        # AeroChordVarunit: scaling factor for chord distribution to calculate mass and stiffness properties
        TurbineMorphs                               = TurbineMorph(yamlfile = self.yamlfile, WorkFast_file = self.WorkFast_file)
        AeroTwstVar, AeroBldNodes, AeroChordVarunit = TurbineMorphs.aeroelastomorph(xc, v_chd, xt, v_twst)
        #%%
        # Structural update: elasto twist-mass-distributuion; structural mass and stiffness update;
        newElastoBldNodes                           = TurbineMorphs.elastodynmorph(AeroTwstVar, AeroBldNodes, AeroChordVarunit)
        frequency                                   = TurbineMorphs.bmodetrack(newElastoBldNodes)
        # Controller update
        TurbineMorphs.Ctablegen()  
        BladMass, BldInertia, RotInertia            = TurbineMorphs.MassCal(newElastoBldNodes)
        TurbineMorphs.controlupdate(frequency, vc)
        # openfast running
        super().compute(inputs, outputs)
        
        FASTout                                     = FASTOutputFile(os.path.splitext(self.WorkFast_fileloc)[0]+".out").toDataFrame()
        FASTouts                                    = FASTout.to_numpy()
        # Assigning the DEL 
        outputs['RotThrust_max']                    = FASTouts[69].max()
        outputs['RotTorq_max']                      = FASTouts[70].max()
        print('################# \n'+'Response: RotTorq_max='+str(FASTouts[70].max())+'\n'+'##################')

if __name__ == '__main__':
    # import sys
    prob = om.Problem()

    prob.model.add_subsystem('p', ControlMDAOom())
    
    # OpenFAST aero- chord
    prob.model.add_design_var('p.Chd_c',    lower = -0.5, upper = 0.5)
    # OpenFAST aero- twist
    prob.model.add_design_var('p.Twst_c',   lower = -0.5, upper = 0.5)
    # Control 
    prob.model.add_design_var('p.omega_vs', lower = 0.1,  upper = 0.5)
    prob.model.add_design_var('p.zeta_vs',  lower = 0.4,  upper = 1.0)
    prob.model.add_design_var('p.omega_pc', lower = 0.1,  upper = 0.5)
    prob.model.add_design_var('p.zeta_pc',  lower = 0.4,  upper = 1.0)
    # Contrained DEL with respect to baseline DTU10 MW model (kN, kN-m)
    prob.model.add_constraint('p.RotThrust_max', upper = 655530.8)
    
    prob.model.add_objective('p.RotTorq_max')

    # find optimal solution with SciPy optimize
    driver = prob.driver = om.ScipyOptimizeDriver(optimizer = 'SLSQP', tol = 0.01)
    driver.options['maxiter'] = 20
    driver.options['disp']    = True
    
    driver.recording_options['includes']            = ['*']
    driver.recording_options['record_objectives']   = True
    driver.recording_options['record_constraints']  = True
    driver.recording_options['record_desvars']      = True
    driver.recording_options['record_inputs']       = True
    driver.recording_options['record_outputs']      = True
    driver.recording_options['record_residuals']    = True
    
    recorder = om.SqliteRecorder("cases.sql")
    driver.add_recorder(recorder)

    prob.setup()
    prob.run_driver()
    
    # output display
    prob.cleanup()
    cr              = om.CaseReader("cases.sql")
    driver_cases    = cr.list_cases('driver')
    #%%
    last_case       = cr.get_case(driver_cases[-1])
    print("Optimal Solutions" + last_case)
    
    
    
    
    