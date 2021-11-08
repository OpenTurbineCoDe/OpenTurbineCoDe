#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 14:54:16 2021
Created by Xinaping Du (xianping.du@gmail.com), Rutgers University.

This scriot is a wrapper for connecting the DTU10MW TACS model with the controller GUI
"""

# ==============================================================================
#       Import modules
# ==============================================================================
import yaml 
import numpy as np

try:
    from baseclasses import StructProblem
except ImportError as err:
    _has_baseclasses = False
else:
    _has_baseclasses = True

try:
    from tacs_orig import functions
except ImportError as err:
    _has_tacs = False
else:
    _has_tacs = True

#from mpi4py import MPI
from openturbinecode.controls.tacs_setup import setup_DTU10MW

# ==============================================================================
#       Initialize TACS
# ==============================================================================
class TACSParams:
    def __init__(self,Tacsfile,thicknesses):
        # thicknesses: a list contain 9 scale factors for the 9 stations
        self.thicknesses = thicknesses
        self.ThickScaling()
        self.bdffile = Tacsfile
        self.FEASolver = setup_DTU10MW.setup(self.bdffile,self.ts)
    def ThickScaling(self):
        # Scaling to mm
        self.ts = [float(d)*0.001 for d in self.thicknesses]
        # scaling to a specified vector at each station
        # ts11 = [42,46,40,35,28,25,18,12,10]  # leadings
        # ts1=[float(d)*0.001 for d in ts11]
        # ts21 = [38,60,78,82,82,76,60,42,20]  # caps
        # ts2=[float(d)*0.001 for d in ts21]
        # ts31 = [40,70,80,70,66,58,40,30,18]  # trailing
        # ts3=[float(d)*0.001 for d in ts31]
        # # to = ts3   # Assume training = Web c
        # # distributed thicknesses
        # tsn1 = [42,46,40,35,28,25,18,12,10] # the nose thickness distribution along the span at 9 stations
        # tsn=[float(d)*0.001 for d in tsn1]
        # # ts = [ts1,ts2,ts3]  # leading->trailing
        # tw1 = [64,60,58,50,38,28,20,16,10]  # web
        # tw=[float(d)*0.001 for d in tw1]
        # self.tsn = np.multiply(tsn, self.thicknesses).tolist()
        # self.ts1 = np.multiply(ts1, self.thicknesses).tolist()
        # self.ts2 = np.multiply(ts2, self.thicknesses).tolist()
        # self.ts3 = np.multiply(ts3, self.thicknesses).tolist()
        # self.ts = [self.ts1,self.ts2,self.ts3]
        # self.tw = np.multiply(tw, self.thicknesses).tolist()
        # self.to = self.ts3
    
    # define structural analysis function
    def StructuralAnalysis(self, evalFunclist):
        FEASolver = self.FEASolver
        # sp = StructProblem("aeroload", loadFile="force_allwalls_L3.txt", evalFuncs = FEASolver.functionList.keys())
        sp = StructProblem("aeroload", evalFuncs = FEASolver.functionList.keys())
        # Add inertial (gravity) loads
        FEASolver.addInertialLoad(sp)
        
        # Add tip load
        FEASolver.addPointLoads(sp,[0,0,80],[[100000.,0,0]],[[0,0,0]])
        
        FEASolver(sp)
        # Evaluate the functions and save data to 'funcs'
        funcs = {}
        FEASolver.evalFunctions(sp, funcs)
        
        # assgin response for return
        response = {}
        for func in evalFunclist:
            funcName = sp.name+'_'+func
            response[func] = funcs[funcName]
        # Evaluate the functions sensitivity and save data to 'funcsSens'
        funcsSens = {}
        FEASolver.evalFunctionsSens(sp, funcsSens)
        
        # Sensitivity of response to variables
        response_dot = {}
        for func in evalFunclist:
            funcName = sp.name+'_'+func
            response_dot[func] = funcsSens[funcName]['struct']
        return response, response_dot  
    
    def Frequencyanalysis(self,N):
        FEASolver=self.FEASolver
        sigma = 200
        M = FEASolver.structure.createFEMat(FEASolver.TACS.TACSAssembler.ND_ORDER)
        K = FEASolver.structure.createFEMat(FEASolver.TACS.TACSAssembler.ND_ORDER)
        
        # create preconditioner
        PCFillLevel = 1000
        PCFillRatio = 20
        isReorderSchur = 1
        PC = FEASolver.TACS.PcScMat(K, PCFillLevel, PCFillRatio, isReorderSchur)
        
        # create Krylov subspace
        subSpaceSize = 100
        nRestarts = 100
        isFlexible = 1
        KSM = FEASolver.TACS.GMRES(K, PC, subSpaceSize, nRestarts, isFlexible)
        
        # eigenpairs to compute
        maxEigVecs = N
        self.nEigVals = N
        eigTol = 1e-12
        
        # create eigen solver
        self.freq = FEASolver.TACS.TACSFrequencyAnalysis(FEASolver.structure, 0, sigma, M, K, KSM, maxEigVecs, self.nEigVals, eigTol)
        
        # solve
        monitor = FEASolver.TACS.KSMPrintStdout("GMRES", 0, 1)
        self.freq.solve(monitor)
        
    def Modeextractiion(self):
        # modeNum, the orders of the interesting modes
        FEASolver=self.FEASolver
        #% extract eigenvalues
        freqValue = []
        Mode=np.array([])
        evec = FEASolver.structure.createVec()
        for i in range(self.nEigVals):
            eigVal = self.freq.extractEigenvector(i, evec)
            transmode=np.array([])
            for j in range(evec.getSize()):  # estract eigen vectors
                transmode=np.append(transmode,evec.getValue(j))
            Mode=np.append(Mode,transmode)
            FEASolver.structure.setVariables(0, evec)
            freqValue.append(np.sqrt(np.real(eigVal)[0]) / (2*np.pi))  # to Hz
        Mode=Mode.reshape([i+1,j+1])  # the modes
        # Process the modes
        # Mode_X=Mode[modeNum-1, np.arange(0,len(Mode[0,:]), 6)]
        # Mode_Y=Mode[modeNum-1, np.arange(1,len(Mode[0,:]), 6)]
        # Mode_Z=Mode[modeNum-1, np.arange(2,len(Mode[0,:]), 6)]
        # NormT=np.sqrt(Mode_X**2+Mode_Y**2+Mode_Z**2)  # norm
        # Mode_XN=Mode_X/max(NormT)
        # Mode_YN=Mode_Y/max(NormT)
        # Mode_ZN=Mode_Z/max(NormT)
        
        # freqValueN=freqValue[modeNum-1]
        # ModeN=np.array([Mode_XN,Mode_YN,Mode_ZN]).T
        return freqValue
    def extractMassstiffness(self):
        # Extract the mass and stiffness properties from the tacs solver
        FEASolver=self.FEASolver
        # Add Functions
        FEASolver.addFunction('mass', functions.StructuralMass)
        
        # Structural problem
        evalFuncs = ['mass']
        sp = StructProblem(name='blade', evalFuncs=evalFuncs)
 
        # Solve state
        FEASolver(sp)
        
        # Evaluate functions
        funcs = {}
        FEASolver.evalFunctions(sp, funcs)
        bldeMass = funcs['blade_mass']
        
        funcsSens = {}
        FEASolver.evalFunctionsSens(sp, funcsSens)
        sens_Mass2Thick = funcsSens['blade_mass']['struct']
        return bldeMass, sens_Mass2Thick
#%%
if __name__=="__main__":
    # initialize
    #%%
    Thicks = [42,46,40,35,28,25,18,12,10] # scaling factor
    # TacsFile = 'tacs_setup/DTU_10MW_RWT_blade3D_rotated_Single.bdf'
    TacsFile = 'tacs_setup/DTU_10MW_RWT_blade3D_rotated_Single.bdf'
    evalFunclist = ['LSkinKSFailure','USkinKSFailure','TotalMass']
    var = [30.0] #np.arange(Thicks[0]*0.5,Thicks[0]*1.5,1)
    Response = {}
    Response_d = {}
    for i in range(len(var)):
        Thicks[0] = var[i]
        TACSsolver = TACSParams(TacsFile, Thicks)
        FunRes, FunRes_d = TACSsolver.StructuralAnalysis(evalFunclist)
        Response['VarThick'+str(i)] = FunRes
        Response_d['VarThick'+str(i)] = FunRes_d
    #%% plot
    pltRes = []
    pltRes_d = []
    for i in range(len(var)):
        tempres = []
        temtes_d = []
        for j in range(3):
            tempres.append(Response['VarThick'+str(i)][evalFunclist[j]])
            temtes_d.append(Response_d['VarThick'+str(i)][evalFunclist[j]][0])
        pltRes.append(tempres)
        pltRes_d.append(temtes_d)
        
    import matplotlib.pyplot as plt
    pltRes = np.array(pltRes)
    pltRes_d = np.array(pltRes_d)
    
    plt.figure(1,dpi=300,figsize=[8,4])
    for i in range(3):
        plt.subplot(2,3,i+1)
        plt.plot(var,pltRes[:,i],'k-s')
        plt.xlabel('T1 (mm)')
        plt.ylabel(evalFunclist[i])
    units = ['mm^{-1}','mm^{-1}','kg/mm']
    for i in range(3):
        plt.subplot(2,3,i+4)
        plt.plot(var,pltRes_d[:,i],'k-s')
        plt.xlabel('T1 (mm)')
        plt.ylabel(r"$\delta {}({})$".format(evalFunclist[i], units[i]))

    plt.tight_layout()
    # plt.savefig('/home/seager/Desktop/ForQ6Presentation/Res-Sens_T1.png', bbox_inches='tight')
    #%%
    # N=9
    # TACSsolver.Frequencyanalysis(N) # N: number of modes for computation
    # freqValueN = TACSsolver.Modeextractiion()
    # bldeMass, sens_Mass2Thick = TACSsolver.extractMassstiffness()

    
    
    
    
