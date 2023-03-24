#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code is developed for the OpenFAST based control co-design.
Created on Sun Feb 28 16:42:41 2021
@author: Xianping Du, rutgers University, xianping.du@rutgers.edu
"""
#------------------------------------- INITIALIZATION ----------------------------------#

import yaml 
import os
this_dir            = os.path.dirname(__file__) 

# Import ROSCO_toolbox modules 
try:
    from ROSCO_toolbox import controller as ROSCO_controller
    from ROSCO_toolbox import turbine as ROSCO_turbine
    from ROSCO_toolbox.utilities import write_DISCON
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

#from Gen_Ctables import writCtables
from scipy.optimize import curve_fit
import openmdao.api as om
import numpy as np
import subprocess
from datetime import date

# my codes
from .BladeMode import fun_mode_tracking   # self cuntion
from .fastpost import multipostprocessing   # self cuntion
from ..utils import utilities as ut #TG 2/23 added to use Aerodyn path

#%% Initialize parameter dictionaries
class TurbineMorph:
    def __init__(self, **obj):
        # Release yaml
        self.path_to_root       =  os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.yamlfile           = obj['yamlfile']
        self.yaml               = yaml.safe_load(open(self.yamlfile))
        self.path_params        = self.yaml['path_params']
        self.turbine_params     = self.yaml['turbine_params']
        self.controller_params  = self.yaml['controller_params']
        self.BModes_params      = self.yaml['BModes_params']
        self.Bldmass_params     = self.yaml['Bld_mass']
        self.config             = ut.read_config() #TG 2/23 added to use Aerodyn path

        
        #FAST directory
        self.path_to_root       = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.path               = self.path_to_root + os.sep + "controls" + os.sep + self.path_params['FAST_directory']
        # Baseline model 
        self.BaselineFast_file  = FASTInputFile(self.path + os.sep + self.yaml['path_params']['FAST_Baselinefile']) 
        # All working FAST files
        self.WorkFast_file      = obj['WorkFast_file']
        
    def SplinMorph(self, xc, yc, xy):
        xcp             = xc* (max(xy[:,0]) - min(xy[:,0])) + min(xy[:,0])            
        ycp             = yc                                 
        x               = xy[:,0]                                 
        prob            = om.Problem()
        akima_option    = {'delta_x': 0.1}
        comp            = om.SplineComp(method = 'akima', x_cp_val = xcp, x_interp_val = x,
                                            interp_options = akima_option)
        prob.model.add_subsystem('akima1', comp)
        comp.add_spline(y_cp_name = 'ycp', y_interp_name = 'y_val', y_cp_val = ycp)
        prob.setup(force_alloc_complex = True)
        prob.run_model()
        y = prob.get_val('akima1.y_val')
        yt = y
        return(yt.T)

    def aeroelastomorph(self, xc, yc, xt, yt):
        '''
        For the morphing of aerpdyn properties: twist and chord distribution
        xc: normalized control points locations in length for chord morph
        yc: normalized control points locations in y for chord morph
        xt: normalized control points locations in length for chord morph
        yt: normalized control points locations in y for chord morph

        '''
        Fast_file                   = self.BaselineFast_file

        Aero_filename               = os.path.join(self.path,Fast_file['AeroFile'].strip('"')) 
        Aero_file                   = FASTInputFile(Aero_filename)

        AeroBld_filename            = os.path.join(self.path,Aero_file['ADBlFile(1)'].strip('"')) 
        AeroBld_file                = FASTInputFile(AeroBld_filename)
        AeroBldNodes                = AeroBld_file['BldAeroNodes']

        # Morphing twist
        AeroTwstOrg                 = AeroBldNodes[:,[0,4]]  
        y                           = self.SplinMorph(xc,yc,AeroTwstOrg)
        AeroTwstVarunit             = y[:,0];  
        AeroTwstVarunit[0:4]        = np.zeros(4) 
        # Assign back
        AeroTwstVar                 = AeroTwstVarunit*AeroTwstOrg[:,1];   
        AeroBldNodes[:,4]           = AeroTwstOrg[:,1]+AeroTwstVar; 

        # Morphing chord
        AeroChordOrg                = AeroBldNodes[:,[0,5]]                                              
        y                           = self.SplinMorph(xt,yt,AeroChordOrg)
        AeroChordVarunit            = y[:,0];                                                        
        AeroChordVarunit[0:4]       = np.zeros(4)                                               
        # Assign back
        AeroChordVar                = AeroChordVarunit*AeroChordOrg[:,1];                                
        AeroBldNodes[:,5]           = AeroChordOrg[:,1]+AeroChordVar;   
        
        AeroBld_file['BldAeroNodes']=AeroBldNodes
        # Write out
        WorkFast_file               = FASTInputFile(self.WorkFast_file)
        Aero_filename_new           = os.path.join(self.path,WorkFast_file['AeroFile'].strip('"'))
        Aero_file_new               = FASTInputFile(Aero_filename_new)
        AeroBld_filename_new        = os.path.join(self.path,Aero_file_new['ADBlFile(1)'].strip('"'))
        AeroBld_file.write(AeroBld_filename_new)
        
        return AeroTwstVar, AeroBldNodes, AeroChordVarunit
                  
    def elastodynmorph(self, AeroTwstVar, AeroBldNodes, AeroChordVarunit):
        '''
        Change the Elastodyn, Calculate CP-Ct_Cd table and the J of rotor
        AeroTwstVar, AeroBldNodes, AeroChordVarunit
        Arrrays return from aeroelastomorph().
        '''
        Fast_file                   = self.BaselineFast_file
        Elasto_filename             = os.path.join(self.path, Fast_file['EDFile'].strip('"')) 
        Elasto_file                 = FASTInputFile(Elasto_filename)
        
        ElastoBld_filename          = os.path.join(self.path, Elasto_file['BldFile(1)'].strip('"')) 
        ElastoBld_file              = FASTInputFile(ElastoBld_filename)
        ElastoBldNodes              = ElastoBld_file['BldProp']  # distributed properties
        
        # Structurla twist
        xxc                         = ElastoBldNodes[:,0] * (max(AeroBldNodes[:,0]) - min(AeroBldNodes[:,0])) + min(AeroBldNodes[:,0])  
        yyc                         = np.interp(xxc,AeroBldNodes[:,0], AeroTwstVar)
        # Assign back
        ElastoBldNodes[:,2]         = ElastoBldNodes[:,2] + yyc
        
        # Structurla stiffness and mass properties
        yyc                         = np.interp(xxc, AeroBldNodes[:,0], AeroChordVarunit)
        #mass scaling
        StrutMassDist               = ElastoBldNodes[:,3] 
        StrutMassVar                = StrutMassDist * yyc;   
        StrutMassDist               = StrutMassDist + StrutMassVar;
        # Stiffness
        StrutFlpstiffDist           = ElastoBldNodes[:,4]   
        StrutFlpstiffDist           = StrutFlpstiffDist * np.power(1 + yyc, 3);  
        StrutEdgstiffDist           = ElastoBldNodes[:,5]   
        StrutEdgstiffDist           = StrutEdgstiffDist * np.power(1 + yyc, 3);
        
        # Assign back
        ElastoBldNodes[:,3]         = StrutMassDist
        ElastoBldNodes[:,4]         = StrutFlpstiffDist
        ElastoBldNodes[:,5]         = StrutEdgstiffDist
        ElastoBld_file['BldProp']   = ElastoBldNodes
        
        # Write out
        WorkFast_file               = FASTInputFile(self.WorkFast_file)
        Elasto_filename_new         = os.path.join(self.path, WorkFast_file['EDFile'].strip('"')) 

        Elasto_file_new             = FASTInputFile(Elasto_filename_new)
        ElastoBld_filename_new      = os.path.join(self.path, Elasto_file_new['BldFile(1)'].strip('"'))
        ElastoBld_file.write(ElastoBld_filename_new)   #write to Elastodyn file
        newElastoBldNodes           = ElastoBldNodes
        
        return newElastoBldNodes
        
    def bmodetrack(self, newElastoBldNodes):
        '''
        Mode tracking by eigen analysis
        newElastoBldNodes:
        New Elastodyn distribution properties from elastodynmorph() after morphing.
        '''
        WorkFast_file               = FASTInputFile(self.WorkFast_file)
        Elasto_filename_new         = os.path.join(self.path,WorkFast_file['EDFile'].strip('"')) 
        Elasto_file_new             = FASTInputFile(Elasto_filename_new)
        ElastoBld_filename_new      = os.path.join(self.path,Elasto_file_new['BldFile(1)'].strip('"'))
        ElastoBld_file              = FASTInputFile(ElastoBld_filename_new)
        # Mode tracking
        #BModes_path                = self.BModes_params['BModes_directory']   #TG 2/26 switched to universal path
        BModes_path                 = self.path + os.sep + self.BModes_params['BModes_directory'] #TG 2/26 switched to universal path
        BModes_file                 = self.BModes_params['BModes_InputFile']
        #BModes_exe                 = self.BModes_params['BModes_exe']   #TG 2/26 switched to config path
        BModes_exe                  = self.config['lofi']["path_to_bmodes"]  #TG 2/26 switched to config path
        ElastoBldNodes              = newElastoBldNodes
        frequency, modes            = fun_mode_tracking(ElastoBldNodes, BModes_path, BModes_file, BModes_exe)
        #% normalize
        modes_N                     = modes
        modes_N[:,1]                = modes[:,1] / modes[len(modes[:,1])-1, 1]
        modes_N[:,2]                = modes[:,2] / modes[len(modes[:,2])-1, 2]
        modes_N[:,3]                = modes[:,3] / modes[len(modes[:,2])-1, 3]
        
        # Coefficients: fitting polynomial
        def polyfun(x,a,b,c,d,e):
            return a*x**2+b*x**3+c*x**4+d*x**5+e*x**6
        poptflp1, pcovflp1          = curve_fit(polyfun, modes_N[:,0], modes_N[:,1])
        poptedg1, pcovedg1          = curve_fit(polyfun, modes_N[:,0], modes_N[:,2])
        poptflp2, pcovflp2          = curve_fit(polyfun, modes_N[:,0], modes_N[:,3])
        # Normalization
        poptflp1                    = poptflp1 / sum(poptflp1)
        poptedg1                    = poptedg1 / sum(poptedg1)
        poptflp2                    = poptflp2 / sum(poptflp2)
        # Assign back: 1st flap
        ElastoBld_file['BldFl1Sh(2)']   = poptflp1[0]    
        ElastoBld_file['BldFl1Sh(3)']   = poptflp1[1]   
        ElastoBld_file['BldFl1Sh(4)']   = poptflp1[2]   
        ElastoBld_file['BldFl1Sh(5)']   = poptflp1[3]  
        ElastoBld_file['BldFl1Sh(6)']   = poptflp1[4]   
        # 1st edge wise mode
        ElastoBld_file['BldEdgSh(2)']   = poptedg1[0]  
        ElastoBld_file['BldEdgSh(3)']   = poptedg1[1]   
        ElastoBld_file['BldEdgSh(4)']   = poptedg1[2]   
        ElastoBld_file['BldEdgSh(5)']   = poptedg1[3]   
        ElastoBld_file['BldEdgSh(6)']   = poptedg1[4]   
        # 2nd flap wise mode
        ElastoBld_file['BldFl2Sh(2)']   = poptflp2[0]   
        ElastoBld_file['BldFl2Sh(3)']   = poptflp2[1]    
        ElastoBld_file['BldFl2Sh(4)']   = poptflp2[2]    
        ElastoBld_file['BldFl2Sh(5)']   = poptflp2[3]   
        ElastoBld_file['BldFl2Sh(6)']   = poptflp2[4]   
        
        # Write out
        WorkFast_file                   = FASTInputFile(self.WorkFast_file)
        Elasto_filename_new             = os.path.join(self.path,WorkFast_file['EDFile'].strip('"')) 
        Elasto_file_new                 = FASTInputFile(Elasto_filename_new)
        ElastoBld_filename_new          = os.path.join(self.path,Elasto_file_new['BldFile(1)'].strip('"'))
        ElastoBld_file.write(ElastoBld_filename_new)
        
        return frequency

    def Ctablegen(self):
        '''
        CP-CT-Cq table generation
        '''
        # Stand-alone aerodyn
        Single_aero_DrivFil = self.path + os.sep + self.path_params['Single_aero_DrivFil']
        Single_aero_Driver  = self.path_params['Single_aero_Driver']
        Single_aero_OutFil  = self.path + os.sep+self.path_params['Single_aero_OutFil']
        AerodynSADrv_file   = FASTInputFile(Single_aero_DrivFil)
        
        # Defalut beta and lambda vectors
        beta_tab            = np.linspace(-1.0,24.75,104) #This can be changed to make testing faster -TG
        lambda_tab          = np.linspace(3.0,14.75,48)   #This can be changed to make testing faster -TG
        v_tab               = 11.4
        pi                  = 3.1415926
        aerodyn_stepSA      = 0.01
        aerodyn_casetime    = 0.1
        RotRadius           = self.Bldmass_params['RotRadius']

        # The following was commented out by Hesam:
        # Cp=np.array([])
        # Cq=np.array([])
        # Ct=np.array([])
        # for i in range(len(lambda_tab)):
        #     Rotspeedrpm    = 60 * (lambda_tab[i] * v_tab) / (RotRadius * 2 * pi)
        #     Cases_SAAerodyn= np.array([])
        #     for j in range(len(beta_tab)):
        #         Cases_SAAerodyn             = np.append(Cases_SAAerodyn, [v_tab, 0.0, Rotspeedrpm, beta_tab[j], 0.0, aerodyn_stepSA, aerodyn_casetime], axis=0)
        #     Cases_SAAerodyn                 = Cases_SAAerodyn.reshape((j+1, 7))
        #     AerodynSADrv_file['Cases']      = Cases_SAAerodyn
        #     AerodynSADrv_file['NumCases']   = j+1
        #     AerodynSADrv_file.write(Single_aero_DrivFil)
        #     # Aerodyn Simulation
        #     subprocess.run([Single_aero_Driver, Single_aero_DrivFil])
        #     # Extract
        #     AerodynSA_out                   = FASTOutputFile(Single_aero_OutFil).toDataFrame()
        #     AerodynSA_out                   = AerodynSA_out.to_numpy()
        #     locs                            = (np.arange(j+1)) * 10 + 6
        #     Cp                              = np.append(Cp, AerodynSA_out[locs,6], axis=0)
        #     Cq                              = np.append(Cq, AerodynSA_out[locs,7], axis=0)
        #     Ct                              = np.append(Ct, AerodynSA_out[locs,8], axis=0)

        # Cp = Cp.reshape((i+1, j+1))
        # Cq = Cq.reshape((i+1, j+1))
        # Ct = Ct.reshape((i+1, j+1))
        
        #New from Hesam
        Cp = np.zeros([len(lambda_tab), len(beta_tab)])
        Cq = np.zeros([len(lambda_tab), len(beta_tab)])
        Ct = np.zeros([len(lambda_tab), len(beta_tab)])

        for i in range(len(lambda_tab)):
            Rotspeedrpm = 60 * (lambda_tab[i] * v_tab) / (RotRadius * 2 * pi)
            Cases_SAAerodyn = np.array([])
            for j in range(len(beta_tab)):
                Cases_SAAerodyn = np.append(Cases_SAAerodyn, [
                                            v_tab, 0.0, Rotspeedrpm, beta_tab[j], 0.0, aerodyn_stepSA, aerodyn_casetime], axis=0)
            Cases_SAAerodyn = Cases_SAAerodyn.reshape((j+1, 7))
            AerodynSADrv_file['Cases'] = Cases_SAAerodyn
            AerodynSADrv_file['NumCases'] = j+1
            AerodynSADrv_file.write(Single_aero_DrivFil)
            # Aerodyn Simulation
            #subprocess.run([Single_aero_Driver, Single_aero_DrivFil])  #TG 2/23 Commented out to use config.json Aerodyn path 
            subprocess.run([self.config['lofi']["path_to_aerodyn"], Single_aero_DrivFil]) #TG 2/26 Commented to use config.json Aerodyn path 
            # Extract
            for j in range(len(beta_tab)):
                AerodynSA_out = FASTOutputFile(
                    Single_aero_OutFil+"."+str(j+1)+"."+"out").toDataFrame()
                AerodynSA_out = AerodynSA_out.to_numpy()
                Cp[i, j] = np.mean(AerodynSA_out[:, 1])
                Cq[i, j] = np.mean(AerodynSA_out[:, 2])
                Ct[i, j] = np.mean(AerodynSA_out[:, 3])
                #End new from Hesam

        # Write out
        self.textfile = self.path+os.sep+self.path_params['rotor_performance_filename']
        with open(self.textfile, 'w') as input_file:
            input_file.write('# ----- Rotor performance tables for the DTU_10MW_RWT wind turbine -----\n')
            input_file.write('# ------------ Written on {} using the AutoCCD developed by XP DU ------------\n'.format(date.today()))
            input_file.write(' \n')
            input_file.write('# Pitch angle vector - x axis (matrix columns) (deg)\n')
            for i in range(len(beta_tab)):
                input_file.write("{0:10.2f}".format(beta_tab[i]))
            input_file.write(' \n')
            input_file.write('# TSR vector - y axis (matrix rows) (-)\n')
            for i in range(len(lambda_tab)):
                input_file.write("{0:10.2f}".format(lambda_tab[i]))
            input_file.write(' \n')
            input_file.write('# Wind speed vector - z axis (m/s)\n')
            input_file.write("{0:10.2f}".format(v_tab))
            input_file.write(' \n')
            input_file.write(' \n')
            input_file.write('# Power coefficient \n')
            input_file.write(' \n')
            for i in range(len(lambda_tab)):
                for j in range(len(beta_tab)):
                    input_file.write("{0:10.6f}".format(Cp[i,j]))
                input_file.write('\n')
            input_file.write(' \n')
            input_file.write(' \n')
            input_file.write('# Thrust coefficient \n')
            input_file.write(' \n')
            for i in range(len(lambda_tab)):
                for j in range(len(beta_tab)):
                    #input_file.write("{0:10.6f}".format(Cq[i, j])) #HS 3/6
                    input_file.write("{0:10.6f}".format(Ct[i, j])) #HS 3/6
                input_file.write('\n')
            input_file.write(' \n')
            input_file.write(' \n')
            input_file.write('# Torque coefficient \n')
            input_file.write(' \n')
            for i in range(len(lambda_tab)):
                for j in range(len(beta_tab)):
                    #input_file.write("{0:10.6f}".format(Ct[i, j])) #HS 3/6
                    input_file.write("{0:10.6f}".format(Cq[i, j])) #HS 3/6
                input_file.write('\n')
            input_file.write(' \n')

    def MassCal(self, newElastoBldNodes):
        '''
        Calculate the new mass properties based on the 'newElastoBldNodes'
        '''
        InertiaBld_ref      = self.Bldmass_params['Bldinertia_ref']   
        InertiaRot_ref      = self.turbine_params['rotor_inertia']      
        LenBld              = self.Bldmass_params['LenBld'] 
        ElastoBldNodes      = newElastoBldNodes
        # Initialize the mass and innertia variables
        MassBld             = 0.0
        InertiaBld          = 0.0
        DistDens_New        = np.concatenate([[0.0], ElastoBldNodes[:,0], [ElastoBldNodes[-1,0]]])
        for i in range(len(ElastoBldNodes[:, 0])):
            Len_BldSeg      = (DistDens_New[i+2] - DistDens_New[i]) / 2
            BldMassSeg      = LenBld * Len_BldSeg * ElastoBldNodes[i,3]
            MassBld         = MassBld + BldMassSeg
            InertiaBld      = InertiaBld + 0.5 * BldMassSeg * ((LenBld * (ElastoBldNodes[i,0] - 0.5 * Len_BldSeg))**2 + (LenBld * (ElastoBldNodes[i,0] + 0.5 * Len_BldSeg))**2)  
        # Update yaml
        rotor_inertia       = 3 * InertiaBld + (InertiaRot_ref - 3 * InertiaBld_ref)
        self.rotor_inertia  = rotor_inertia
        
        return MassBld, InertiaBld, rotor_inertia
    
    def controlupdate(self, frequency, vc):
        '''
        Update the controller using ROSCP_toolbox and new infromation due to morphing.
        frequency:
            New natural frequencies of baldes
        vc:
            The four control variables, natural frequency and damping ratio in region 2 and 3, respetively.
        '''
        controller_params       = self.controller_params
        turbine                 = ROSCO_turbine.Turbine(self.turbine_params)
        # New rotor inertia
        turbine.rotor_inertia   = self.rotor_inertia
        
        # Load Turbine
        turbine.load_from_fast(self.WorkFast_file, self.path, rot_source='txt', txt_filename = self.textfile)

        # Flap tuning if necessary
        if controller_params['Flp_Mode']:
            turbine.load_blade_info()
        # Determined based on Cp table: default Cp.max() 0.470403 in ROSCO repo
        turbine.v_rated             = turbine.v_rated * ((0.4536946 / turbine.Cp_table.max())**(1. / 3))     
        turbine.rated_rotor_speed   = turbine.v_rated * turbine.TSR_operational / turbine.TipRad
        turbine.bld_edgewise_freq   = frequency[1] * 6.28
        turbine.bld_flapwise_freq   = frequency[0] * 6.28
        # ROSCO tuning
        controller                  = ROSCO_controller.Controller(controller_params)
        # Define design varaibles
        controller.omega_vs         = vc[0]
        controller.zeta_vs          = vc[1]
        controller.omega_pc         = vc[2]
        controller.zeta_pc          = vc[3]
        # Tune controller
        controller.tune_controller(turbine)
        
        # Write parameter input file
        WorkFast_file               = FASTInputFile(self.WorkFast_file)
        Servo_filename_new          = os.path.join(self.path,WorkFast_file['ServoFile'].strip('"')) 
        Servo_file_new              = FASTInputFile(Servo_filename_new)
        Discon_filename_new         = os.path.join(self.path,Servo_file_new['DLL_InFile'].strip('"'))
        
        param_file                  = Discon_filename_new   
        write_DISCON(turbine, controller, param_file = param_file, txt_filename = os.path.join(self.path, self.path_params['rotor_performance_filename']))

if __name__ == "__main__":
    # Welcome
    print('AUTOCCD Framework Developed by Xianping Du, Rutgers University, xianping.du@gmail.com')
    # yaml file
    yamlfile                    = 'DTU10MW.yaml'
    WorkFast_file               = []
    for i in range(22):
        case                    = 'DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_v' + str(i+4) + '.fst' 
        WorkFast_file.append(case)
    # DLC6.1
    WorkFast_file.append('DTU_10MW_NAUTILUS_GoM_A15_DLC6.1_v37.5.fst')
    inputfile                   = 'fastbat.py'
    
    # Define variables
    xc                          = np.array([0,0.1,0.2,0.4,0.7,1.0])              
    v_chd                       = np.array([0.0,0.0,0.3,0.1,-0.2,-0.1])           
    xt                          = np.array([0,0.1,0.2,0.4,0.7,1.0])                
    v_twst                      = np.array([0.0,0.0,0.2,0.3,-0.3,-0.1])            
    # Control Parameter
    vc                          = [0.2,0.7,0.3,0.7]
    
    TurbineMorphs               = TurbineMorph(yamlfile = yamlfile, WorkFast_file = WorkFast_file)
    # Aero morphing
    AeroTwstVar, AeroBldNodes, AeroChordVarunit = TurbineMorphs.aeroelastomorph(xc, v_chd, xt, v_twst)
    # Structural update
    newElastoBldNodes               = TurbineMorphs.elastodynmorph(AeroTwstVar, AeroBldNodes, AeroChordVarunit)
    frequency                       = TurbineMorphs.bmodetrack(newElastoBldNodes)
    # Controller update
    TurbineMorphs.Ctablegen()
    BladMass,BldInertia,RotInertia  = TurbineMorphs.MassCal(newElastoBldNodes)
    TurbineMorphs.controlupdate(frequency,vc)
    # OpenFAST running
    subprocess.run(['python3', inputfile])
    # Postprocessing
    AEP, DEL, UltiStrength          = multipostprocessing(filepath = 'DTU10MWAero15/Baseline_Results/')
   