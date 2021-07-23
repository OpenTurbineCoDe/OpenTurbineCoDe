#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code is developed for the OpenFAST based control co-design.
Created on Sun Feb 28 16:42:41 2021
@author: Xianping Du (xianping.du@gmail.com)
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
#%% Initialize parameter dictionaries
class TurbineMorph:
    def __init__(self,**obj):
        # Release yaml parameters
        self.yamlfile = obj['yamlfile']
        self.yaml = yaml.safe_load(open(self.yamlfile))
        self.path_params = self.yaml['path_params']
        self.turbine_params = self.yaml['turbine_params']
        self.controller_params = self.yaml['controller_params']
        self.BModes_params = self.yaml['BModes_params']
        self.Bldmass_params = self.yaml['Bld_mass']
        
        #FAST directory
        self.path = self.path_params['FAST_directory']
        # Baseline model for providing baseline plant parameters
        self.BaselineFast_file = FASTInputFile(self.yaml['path_params']['FAST_Baselinefile']) 
        # All working FAST files for evaluating all cases, constraints, and objectives
        self.WorkFast_file = os.path.join(self.path,obj['WorkFast_file'])
        
    #%%#######################################Scaling function############################
    def SplinMorph(self,xc,yc, xy):
        xcp = xc* (max(xy[:,0])-min(xy[:,0]))+min(xy[:,0])             #scale to blade length; 
        ycp = yc                                 #variation dist between [-0.5 0.5]
        x = xy[:,0]                                 #airfoil distribution
        prob = om.Problem()
        akima_option = {'delta_x': 0.1}
        comp = om.SplineComp(method='akima', x_cp_val=xcp, x_interp_val=x,
                             interp_options=akima_option)
        prob.model.add_subsystem('akima1', comp)
        comp.add_spline(y_cp_name='ycp', y_interp_name='y_val', y_cp_val=ycp)
        prob.setup(force_alloc_complex=True)
        prob.run_model()
        y=prob.get_val('akima1.y_val')
        yt=y
        return(yt.T)

#%%######################################FAST input read,scaling, and write ###################
    def aeroelastomorph(self,xc,yc,xt,yt):
        #xc: normalized control points locations in length for chord morph
        #yc: normalized control points locations in y for chord morph
        #xt: normalized control points locations in length for chord morph
        #yt: normalized control points locations in y for chord morph
        # baseline fast model
        Fast_file=self.BaselineFast_file

        Aero_filename  = os.path.join(self.path,Fast_file['AeroFile'].strip('"')) 
        Aero_file=FASTInputFile(Aero_filename)
        #changing the model
        #Aero_file.write(Aero_filename)
        
        AeroBld_filename  = os.path.join(self.path,Aero_file['ADBlFile(1)'].strip('"')) 
        AeroBld_file=FASTInputFile(AeroBld_filename)
        AeroBldNodes=AeroBld_file['BldAeroNodes']

        ##Morphing the twist
        AeroTwstOrg=AeroBldNodes[:,[0,4]]   #station locations and the twist distribution
        y=self.SplinMorph(xc,yc,AeroTwstOrg)
        AeroTwstVarunit=y[:,0];   # the morphed location within [-0.5,0.5]
        AeroTwstVarunit[0:4]=np.zeros(4) # force the blade root not did not changed
        #assign to the FAST data: aero Twist
        AeroTwstVar=AeroTwstVarunit*AeroTwstOrg[:,1];   # variation from original
        AeroBldNodes[:,4]=AeroTwstOrg[:,1]+AeroTwstVar;  # scale to the blade scale and assign to original data strucutre
        #AeroTwstVar=AeroTwstVar        # Twist varied from the baseline
        
        ##Morphing the chord
        AeroChordOrg=AeroBldNodes[:,[0,5]]                                              #station locations and the twist distribution
        y=self.SplinMorph(xt,yt,AeroChordOrg)
        AeroChordVarunit=y[:,0];                                                        # the morphed location within [-0.5,0.5]
        AeroChordVarunit[0:4]=np.zeros(4)                                               # for the root not changed
        #assign to the FAST data: Chord
        AeroChordVar=AeroChordVarunit*AeroChordOrg[:,1];                                # Scaling: variation from original
        AeroBldNodes[:,5]=AeroChordOrg[:,1]+AeroChordVar;   
        #AeroBldNodes=AeroBldNodes                      # bladnode distribution changed
        #AeroChordVarunit=AeroChordVarunit              # Chord unit variation from the baseline  
        
        AeroBld_file['BldAeroNodes']=AeroBldNodes
        #########################Write the aerodyn blade file back
        #changing the model by write out
        WorkFast_file=FASTInputFile(self.WorkFast_file)
        Aero_filename_new  = os.path.join(self.path,WorkFast_file['AeroFile'].strip('"'))
        #Aero_file.write(Aero_filename_new)  #write the  aerodyn file: may not need since no change made here
        Aero_file_new=FASTInputFile(Aero_filename_new)
        AeroBld_filename_new  = os.path.join(self.path,Aero_file_new['ADBlFile(1)'].strip('"'))
        AeroBld_file.write(AeroBld_filename_new)  #write the aerodyn blade file: required
        return AeroTwstVar, AeroBldNodes, AeroChordVarunit
        #%%            
    def elastodynmorph(self,AeroTwstVar,AeroBldNodes,AeroChordVarunit):
        #####################change the structural models accrodingly:################
        # Currently, we did use the Elastodyn for structure because the DTU10MW beamdyn model can not couple with openFAST model
        #In addition, the parameters for control trunin is also required to be calculated,
        # that is, the CP-Ct_Cd table and the J of rotor (basic+blade*scaling)
        
        #def beandynmorph(self): # a placeholder for beamdyn scaling
        Fast_file=self.BaselineFast_file
        #% Elastodyn model (practical)
        Elasto_filename  = os.path.join(self.path,Fast_file['EDFile'].strip('"')) 
        Elasto_file=FASTInputFile(Elasto_filename)
        # changing the model
        
        ElastoBld_filename  = os.path.join(self.path,Elasto_file['BldFile(1)'].strip('"')) 
        ElastoBld_file=FASTInputFile(ElastoBld_filename)
        ElastoBldNodes=ElastoBld_file['BldProp']  # distributed properties
        
        ##############3#Structurla twist distribution#################################
        #changes to the blade length properties
        # interpolate the AeroTwstVar at each strucTwst location
        xxc=ElastoBldNodes[:,0]* (max(AeroBldNodes[:,0])-min(AeroBldNodes[:,0]))+min(AeroBldNodes[:,0])  #scale elastodyn stations (0 1) to blade length
        yyc=np.interp(xxc,AeroBldNodes[:,0],AeroTwstVar)    #interpolate the change of twist at the elasto blade station locations
        # change the elastodyn distribution
        ElastoBldNodes[:,2]=ElastoBldNodes[:,2]+yyc
        
        ###############Structurla stiffness and mass properties scaling###########################
        # we assume the chord and airfoil thickness are scaled equally
        # assume no composite shell thickness scaling
        # Convert Aero- chord to structural chord stations
        # interpolate the chord scaling to the lengh scale of Elastodyn
        # diffrent from twist, the mass and stiffness is caling but not adding from original,
        # so the unit aero chord varaition is used.
        yyc=np.interp(xxc,AeroBldNodes[:,0],AeroChordVarunit)    #interpolate the change of chord at the elasto blade station locations
        #mass scaling
        StrutMassDist=ElastoBldNodes[:,3]   # Mass distribution
        StrutMassVar=StrutMassDist*yyc;   # only the chord scaling affect the mass
        StrutMassDist=StrutMassDist+StrutMassVar;
        #stiffness scaling: stiffness was scaled to: S_chord^3*S_thick (no S_thick here)
        #flapwise
        StrutFlpstiffDist=ElastoBldNodes[:,4]   # flapwise stiffness distribution
        StrutFlpstiffDist=StrutFlpstiffDist*np.power(1+yyc,3);   # only the chord scaling affect the mass
        #edgewise
        StrutEdgstiffDist=ElastoBldNodes[:,5]   # edgewise stiffness distribution
        StrutEdgstiffDist=StrutEdgstiffDist*np.power(1+yyc,3);   # only the chord scaling affect the mass
        
        # write back
        ElastoBldNodes[:,3]=StrutMassDist
        ElastoBldNodes[:,4]=StrutFlpstiffDist
        ElastoBldNodes[:,5]=StrutEdgstiffDist
        
        ElastoBld_file['BldProp']=ElastoBldNodes    #write to change the original data
        # wrie wrokign directory
        WorkFast_file=FASTInputFile(self.WorkFast_file)
        Elasto_filename_new  = os.path.join(self.path,WorkFast_file['EDFile'].strip('"')) 
        # Elasto_file.write(Elasto_filename_new)  # check if the data in elastodyn file was changed
        Elasto_file_new=FASTInputFile(Elasto_filename_new)
        ElastoBld_filename_new  = os.path.join(self.path,Elasto_file_new['BldFile(1)'].strip('"'))
        ElastoBld_file.write(ElastoBld_filename_new)   #write to Elastodyn file
        
        newElastoBldNodes=ElastoBldNodes
        return newElastoBldNodes
        
        #%% ############################################mode shape parameters###########
    def bmodetrack(self,newElastoBldNodes):
        # Initialize the Elasto file
        WorkFast_file=FASTInputFile(self.WorkFast_file)
        Elasto_filename_new  = os.path.join(self.path,WorkFast_file['EDFile'].strip('"')) 
        # Elasto_file.write(Elasto_filename_new)  # check if the data in elastodyn file was changed
        Elasto_file_new=FASTInputFile(Elasto_filename_new)
        ElastoBld_filename_new  = os.path.join(self.path,Elasto_file_new['BldFile(1)'].strip('"'))
        ElastoBld_file=FASTInputFile(ElastoBld_filename_new)
        #ElastoBld_file.write(ElastoBld_filename_new)   #write to Elastodyn file
        #%% mode tracking
        BModes_path=self.BModes_params['BModes_directory']
        BModes_file=self.BModes_params['BModes_InputFile']
        ElastoBldNodes=newElastoBldNodes   # the new elastodyn distribution
        frequency, modes=fun_mode_tracking(ElastoBldNodes,BModes_path,BModes_file)   # the three modes returned: 1st flap, 2nd flap, 1st edge
        #% normalize
        modes_N=modes
        modes_N[:,1]=modes[:,1]/modes[len(modes[:,1])-1,1]
        modes_N[:,2]=modes[:,2]/modes[len(modes[:,2])-1,2]
        modes_N[:,3]=modes[:,3]/modes[len(modes[:,2])-1,3]
        
        # coefficients: fitting polynomial
        def polyfun(x,a,b,c,d,e):
            return a*x**2+b*x**3+c*x**4+d*x**5+e*x**6
        poptflp1, pcovflp1 = curve_fit(polyfun, modes_N[:,0], modes_N[:,1])
        poptedg1, pcovedg1 = curve_fit(polyfun, modes_N[:,0], modes_N[:,2])
        poptflp2, pcovflp2 = curve_fit(polyfun, modes_N[:,0], modes_N[:,3])
        # normalize coefficients
        poptflp1=poptflp1/sum(poptflp1)
        poptedg1=poptedg1/sum(poptedg1)
        poptflp2=poptflp2/sum(poptflp2)
        #%% Assigned the calculated polynomial coefficient to elastodyn
        # 1st flap wise mode
        ElastoBld_file['BldFl1Sh(2)']=poptflp1[0]   #coeff of x^2 
        ElastoBld_file['BldFl1Sh(3)']=poptflp1[1]   #coeff of x^3 
        ElastoBld_file['BldFl1Sh(4)']=poptflp1[2]   #coeff of x^4 
        ElastoBld_file['BldFl1Sh(5)']=poptflp1[3]   #coeff of x^5 
        ElastoBld_file['BldFl1Sh(6)']=poptflp1[4]   #coeff of x^6 
        # 1st edge wise mode
        ElastoBld_file['BldEdgSh(2)']=poptedg1[0]   #coeff of x^2 
        ElastoBld_file['BldEdgSh(3)']=poptedg1[1]   #coeff of x^3 
        ElastoBld_file['BldEdgSh(4)']=poptedg1[2]   #coeff of x^4 
        ElastoBld_file['BldEdgSh(5)']=poptedg1[3]   #coeff of x^5 
        ElastoBld_file['BldEdgSh(6)']=poptedg1[4]   #coeff of x^6 
        # 2nd flap wise mode
        ElastoBld_file['BldFl2Sh(2)']=poptflp2[0]   #coeff of x^2 
        ElastoBld_file['BldFl2Sh(3)']=poptflp2[1]   #coeff of x^3 
        ElastoBld_file['BldFl2Sh(4)']=poptflp2[2]   #coeff of x^4 
        ElastoBld_file['BldFl2Sh(5)']=poptflp2[3]   #coeff of x^5 
        ElastoBld_file['BldFl2Sh(6)']=poptflp2[4]   #coeff of x^6 
        
        # wrie wrokign directory
        WorkFast_file=FASTInputFile(self.WorkFast_file)
        Elasto_filename_new  = os.path.join(self.path,WorkFast_file['EDFile'].strip('"')) 
        Elasto_file_new=FASTInputFile(Elasto_filename_new)
        ElastoBld_filename_new  = os.path.join(self.path,Elasto_file_new['BldFile(1)'].strip('"'))
        ElastoBld_file.write(ElastoBld_filename_new)   #write to Elastodyn blade file
        return frequency
        #%%
    def Ctablegen(self):
        #########################CP-CT-Cq table generation (write for OpenFAST sim)###
        # Maybe, using a initialize function to initialize this model if surrogate
        # Currrently, stand alone aerodyn simulations are affordable using 0.1s for each case:
        #% stand-alone aerodyn
        Single_aero_DrivFil=self.path_params['Single_aero_DrivFil']
        Single_aero_Driver=self.path_params['Single_aero_Driver']
        Single_aero_OutFil=self.path_params['Single_aero_OutFil']
        
        AerodynSADrv_file=FASTInputFile(Single_aero_DrivFil)
        #% defalut beta and lambda vectors
        beta_tab=np.linspace(-1.0,24.75,104)  # series beta
        lambda_tab=np.linspace(3.0,14.75,48)   # series lambda
        v_tab=11.4   # Not rated velocity: velocity used for simulation: default is 11.4 m/s (default rated for DTU10 MW)
        pi=3.1415926
        aerodyn_stepSA=0.01
        aerodyn_casetime=0.1
        RotRadius=self.Bldmass_params['RotRadius'] #self.Bldmass_params['RotRadius']
        #% accumulate the cases
        Cp=np.array([])
        Cq=np.array([])
        Ct=np.array([])
        for i in range(len(lambda_tab)):
            Rotspeedrpm=60*(lambda_tab[i]*v_tab)/(RotRadius*2*pi)
            Cases_SAAerodyn=np.array([])
            for j in range(len(beta_tab)): 
                # items: [WndSpeed  ShearExp  RotSpd Pitch   Yaw  dT  Tmax]
                Cases_SAAerodyn=np.append(Cases_SAAerodyn,[v_tab, 0.0,Rotspeedrpm,beta_tab[j],0.0,aerodyn_stepSA,aerodyn_casetime],axis=0)
            Cases_SAAerodyn=Cases_SAAerodyn.reshape((j+1,7))
            AerodynSADrv_file['Cases']=Cases_SAAerodyn
            AerodynSADrv_file['NumCases']=j+1
            AerodynSADrv_file.write(Single_aero_DrivFil)
            #rerun the aerodyn simulation
            subprocess.run([Single_aero_Driver, Single_aero_DrivFil])
            # extract the data
            AerodynSA_out=FASTOutputFile(Single_aero_OutFil).toDataFrame()
            AerodynSA_out=AerodynSA_out.to_numpy()
            locs=(np.arange(j+1))*10+6
            Cp=np.append(Cp,AerodynSA_out[locs,6],axis=0)   #Cp
            Cq=np.append(Cq,AerodynSA_out[locs,7],axis=0)   #Cq
            Ct=np.append(Ct,AerodynSA_out[locs,8],axis=0)   #Ct
        
        Cp=Cp.reshape((i+1,j+1))
        Cq=Cq.reshape((i+1,j+1))
        Ct=Ct.reshape((i+1,j+1))
        #write out
        #% self.yamlfile
        textfile=self.path_params['rotor_performance_filename']
        with open(textfile, 'w') as input_file:
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
                    input_file.write("{0:10.6f}".format(Cq[i,j]))
                input_file.write('\n')
            input_file.write(' \n')
            input_file.write(' \n')
            input_file.write('# Torque coefficient \n')
            input_file.write(' \n')
            for i in range(len(lambda_tab)):
                for j in range(len(beta_tab)):
                    input_file.write("{0:10.6f}".format(Ct[i,j]))
                input_file.write('\n')
            input_file.write(' \n')
        #%%
    def MassCal(self,newElastoBldNodes):
        InertiaBld_ref=self.Bldmass_params['Bldinertia_ref']          #(kg*m^2)
        InertiaRot_ref=self.turbine_params['rotor_inertia']        #(kg*m^2)
        LenBld=self.Bldmass_params['LenBld'] 
        
        ElastoBldNodes=newElastoBldNodes
        #initialize the mass and innertia variables
        MassBld=0.0
        InertiaBld=0.0
        DistDens_New=np.concatenate([[0.0],ElastoBldNodes[:,0],[ElastoBldNodes[-1,0]]])
        for i in range(len(ElastoBldNodes[:,0])):
            Len_BldSeg=(DistDens_New[i+2]-DistDens_New[i])/2
            BldMassSeg=LenBld*Len_BldSeg*ElastoBldNodes[i,3]
            MassBld=MassBld+BldMassSeg
            InertiaBld=InertiaBld+0.5*BldMassSeg*((LenBld*(ElastoBldNodes[i,0]-0.5*Len_BldSeg))**2+(LenBld*(ElastoBldNodes[i,0]+0.5*Len_BldSeg))**2)  # inertia
        # update yaml: only turbine parameters are rewriten since no control strategy changed
        rotor_inertia = 3*InertiaBld+(InertiaRot_ref-3*InertiaBld_ref) # update the parameters
        self.rotor_inertia=rotor_inertia
        return MassBld, InertiaBld, rotor_inertia
    def controlupdate(self,frequency,vc):
        #######################################New parameters generation to update Yaml###################
        #% calculate the mass
        # segment mass: calculated by seen each station as the center of each segment
        # inertia: calculated inertia of each segment by seen it as the sum of two subsegments
        # varied from the center of each mass segment
        #---------------------------------- Using the ROSCO_toolbox--------------------------------#
        controller_params=self.controller_params
        turbine         = ROSCO_turbine.Turbine(self.turbine_params)
        # New rotor inertia
        turbine.rotor_inertia = self.rotor_inertia
        
        # Load Turbine
        turbine.load_from_fast(self.WorkFast_file,self.path_params['FAST_directory'], \
                rot_source='txt',txt_filename=self.path_params['rotor_performance_filename'])

            
        # Flap tuning if necessary
        if controller_params['Flp_Mode']:
            turbine.load_blade_info()
        # determined based on Cp table: default Cp.max() 0.470403 in ROSCO repo
        turbine.v_rated           =  turbine.v_rated*((0.4536946/turbine.Cp_table.max())**(1./3))           # Rated wind speed
        turbine.rated_rotor_speed =  turbine.v_rated*turbine.TSR_operational/turbine.TipRad           # Rated rotor speed
        turbine.bld_edgewise_freq = frequency[1]*6.28
        turbine.bld_flapwise_freq = frequency[0]*6.28

        # The yamal file do not need to be rewrite, Just using the data ro tune the controller
        # Instantiate controller tuning and tune controller
        controller      = ROSCO_controller.Controller(controller_params)
        # define design varaibles
        controller.omega_vs = vc[0]
        controller.zeta_vs  = vc[1]
        controller.omega_pc = vc[2]
        controller.zeta_pc  = vc[3]
        # tune controller
        controller.tune_controller(turbine)
        
        # Write parameter input file
        WorkFast_file=FASTInputFile(self.WorkFast_file)
        Servo_filename_new  = os.path.join(self.path,WorkFast_file['ServoFile'].strip('"')) 
        Servo_file_new=FASTInputFile(Servo_filename_new)
        Discon_filename_new  = os.path.join(self.path,Servo_file_new['DLL_InFile'].strip('"'))
        
        param_file = Discon_filename_new   
        write_DISCON(turbine,controller,param_file=param_file, txt_filename=os.path.join(this_dir,self.path_params['rotor_performance_filename']))
        
        

## if running this file directly
if __name__ == "__main__":
    # Welcome
    print('AUTOCCD Framework Developed by Xianping Du, Rutgers University, xianping.du@gmail.com')
    ## Files
    # yaml file
    yamlfile = 'DTU10MW.yaml'
    
    WorkFast_file=[]
    for i in range(22):
        case='DTU_10MW_NAUTILUS_GoM_A15_DLC1.2_v'+str(i+4)+'.fst'  # Working openFAST model
        WorkFast_file.append(case)
    # Additional case for extreme condition
    WorkFast_file.append('DTU_10MW_NAUTILUS_GoM_A15_DLC6.1_v37.5.fst')
    inputfile = 'fastbat.py'
    
    # Define variables: chord morph
    xc = np.array([0,0.1,0.2,0.4,0.7,1.0])                # distribute the control points
    v_chd = np.array([0.0,0.0,0.3,0.1,-0.2,-0.1])            # no change on the first 0.1 scale due to the root cylinder
    # Define variables: twist morph
    xt = np.array([0,0.1,0.2,0.4,0.7,1.0])                 # distribute the control points
    v_twst = np.array([0.0,0.0,0.2,0.3,-0.3,-0.1])             # no change on the first 0.1 scale due to the root cylinder
    # Control Parameter
    vc = [0.2,0.7,0.3,0.7]
    
    TurbineMorphs=TurbineMorph(yamlfile = yamlfile, WorkFast_file = WorkFast_file)
    # Aero morphing
    AeroTwstVar, AeroBldNodes, AeroChordVarunit=TurbineMorphs.aeroelastomorph(xc,v_chd,xt,v_twst)
    #%%
    # structural update: elasto twist-mass-distributuion; structural mass and stiffness update;
    newElastoBldNodes=TurbineMorphs.elastodynmorph(AeroTwstVar,AeroBldNodes,AeroChordVarunit)
    frequency=TurbineMorphs.bmodetrack(newElastoBldNodes)
    # controller update: cp table, controller tunning
    TurbineMorphs.Ctablegen()
    BladMass,BldInertia,RotInertia = TurbineMorphs.MassCal(newElastoBldNodes)
    TurbineMorphs.controlupdate(frequency,vc)
    # openfast runnin
    # super().compute(inputs, outputs)    # run the running code to run all fast models in parallel
    subprocess.run(['python3', inputfile])
    # read all output files
    AEP,DEL,UltiStrength=multipostprocessing(filepath='DTU10MWAero15/Baseline_Results/')   # Specify the working directory   
   