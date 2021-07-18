#!/usr/bin/env python3

"""
OpenTurbineCoDe standalone run file for aerodynamic solving

authors: Denis-Gabriel Caprace, Marco Mangano
"""

# ================================================
# External python imports
# ================================================
import argparse
import numpy as np
import os
import sys
from mpi4py import MPI
import matplotlib.pyplot as plt

import openturbinecode.aerodynamics.aero_wrapper as OTCDaw
import openturbinecode.utils.OTCDparser as OTCDparser
import openturbinecode.utils.utilities as ut

# ================================================
# Input arguments
# ================================================
baseDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + os.sep  #path to OTCD root

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="Output directory (relative to case files)", type=str, default="outputs")
parser.add_argument("--configuration", help="WT Configuration", type=str, default="NREL_PhaseVI_UAE", choices=["NREL_PhaseVI_UAE","DTU_10MW"])
    #-> meant to disappear when the hardcoded parameters will instead be passed in a case file
parser.add_argument("--fidelities", help="fidelities to be included [AeroDyn, (OpenFAST,) ADflow, (turbinesFoam)]", type=str, default=["AeroDyn","ADflow"], nargs="+")
parser.add_argument("--path_to_case", help="path where the case files are and where we will dump outputs", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'case_aero_standalone' ))
parser.add_argument("--hifimesh", help="CFD mesh level - [0,1,2,3,4]", type=int, default=2)
parser.add_argument("--V", help="Inflow wind speed", type=float, default=[7.0], nargs="+")
parser.add_argument("--tsrlist", help="Prescribed tip speed ratio", type=float, default=[5.42], nargs="+")
parser.add_argument("--restart", help="Name of the restart file", type=str, default=None)
parser.add_argument("--plotonly", action='store_true', help="Skip the computations (outputs must be present in folders)")
parser.add_argument("--withADres", action='store_true', help="Look for external AeroDyn results and plot them")
parser.add_argument("--withEllipsys", action='store_true', help="Look for EllipSys3D results and plot them")
args = parser.parse_args()

path_to_case = args.path_to_case

# =============================================================
# Initialize output case folder
# =============================================================
if not os.path.exists(path_to_case):
    print("ERROR: The case folder\n"+path_to_case+"\ndoes not exist. Please consider copy/pasting one of the cases provided in ./models")
    sys.exit(1)
    #ideally, we should check that we also have aerodyn files etc...

# =============================================================
# Parse the parser data
# =============================================================

if isinstance(args.V,list): #sweeping tsr with constant vel
    tsrlist = np.array(args.tsrlist)
    Vlist = np.ones(np.shape(tsrlist))*args.V
elif isinstance(args.tsrlist,list): #sweeping vel with constant tsr
    Vlist = np.array(args.V)
    tsrlist = np.ones(np.shape(Vlist)) *args.tsrlist
else:
    if len(args.V) != len(args.tsrlist):
        print("ERROR: V and tsrlist must have the same size")
        exit(1)
    Vlist = np.array(args.V)
    tsrlist = np.array(args.tsrlist)

# TODO: add the ability to specify blade pitch

# Vlist = np.array([5.,6.,7.,8.,9.,10.,12.,15.,20.])
# tsrlist = np.array([7.58,6.32,5.42,4.74,4.21,3.78,3.16,2.53,1.90])

pitchlist = np.nan*Vlist

# =============================================================
# Turbine data
# =============================================================

# TODO: mode all these hardcoded values to a json file, consider using WindIO onthology.

T = 284.15  # [Kelvin].Eqv to 11C.
rho = 1.225

# Setting the correct reference system and blade span for the selected configuration
if args.configuration == "NREL_PhaseVI_UAE":
    Tag = "UAE"
    spanDir = "z"
    R = 5.029
    R0 = 0.508  # spanwise location of the root [m]
    Nblade = 2
    rotsign = -1 #trigonometric sign of the rotor revolution along axis x
    xvals = tsrlist #x axis values for the plots
elif args.configuration == "DTU_10MW":
    Tag = "DTU10MW"
    spanDir = "y"
    R = 89.166
    R0 = 2.8
    Nblade = 3
    rotsign = 1
    xvals = Vlist

omlist = tsrlist * Vlist / R #absolute value of the rotation rate
rpmlist = omlist / (2 * np.pi) * 60

areaRef = np.pi*R**2

# TODO: Are these the spanwise stations used for OpenFast computations?
# DG: yes, and all this should be factored out and passed in a cfg or json file
nodeidxs = np.array([1, 9, 29, 35, 48, 68, 75, 85, 92])
nodeR = nodeidxs/100.*(R-R0) + R0



# =============================================================
# External data
# =============================================================

if args.configuration == "NREL_PhaseVI_UAE":

    #hardcoded for now, for the results in the corresponding folder
    ADext_tsr = np.array([7.58, 6.32, 5.42, 4.74, 4.21, 3.78, 3.16, 2.53, 1.90])
    ADext_vel = np.array([5.,6.,7.,8.,9.,10.,12.,15.,20.])

  #  for use with the limited range (ltd, see `suffixes` below)
  #  ADext_vel = np.array([7.,8.,9.,10.])
  #  ADext_tsr = np.array([5.42, 4.74, 4.21, 3.78])
    ADext_xvals = ADext_tsr

elif args.configuration == "DTU_10MW":

    #hardcoded for now, for the results in the corresponding folder
    ADext_tsr = np.array([14.01, 9.34, 7.81, 7.81, 7.81, 7.81, 7.47, 5.98, 3.59])
    ADext_vel = np.array([4.,6.,8.,9.,10.,11.,12.,15.,25.])
    ADext_xvals = ADext_vel

else:
    raise ValueError("unknown configuration")


# =============================================================
# Extra CFD data from EllipSys3D
# =============================================================

extraFolder = "EllipSys3D"

if extraFolder and args.withEllipsys:
    if args.configuration == "NREL_PhaseVI_UAE":
        extraFile = "LSStorque.csv" #low speed shaft torque. This file contains inflow vel in the first column, and torques in the second one.

        extraData = np.genfromtxt(os.path.join(path_to_case, extraFolder, extraFile), delimiter=';')
        extraV = extraData[:,0] #np.array([7.,10.,13.,15.,20.,25.])
        extraOm = omlist[0]
        extraTSR = extraOm * R / extraData[:,0]
        extraQ = extraData[:,1]
        extraCp = ut.WT_performance(extraV, R, areaRef, rho, extraTSR, extraQ)
        extraCp = extraCp[0]

        extraQ = extraQ[0:2]
        extraCp = extraCp[0:2]
        extraX = extraTSR[0:2]
        print(extraQ)
        
    elif args.configuration == "DTU_10MW":
        extraFile = "QEll.csv" 

        extraData = np.genfromtxt(os.path.join(path_to_case, extraFolder, extraFile), delimiter=';')
        extraV = extraData[:,0]
        extraOm = np.array([.63, .63, .70, .88, .96, 1.01, 1.01, 1.01])
        extraTSR = extraOm * R / extraData[:,0]
        extraQ = extraData[:,1]
        extraCp = ut.WT_performance(extraV, R, areaRef, rho, extraTSR, extraQ)
        extraCp = extraCp[0]

        extraX = extraV

# #hardcoded data, just for comparison
# if extraFolder and args.withEllipsys:
#     if args.configuration == "NREL_PhaseVI_UAE":
#         extraTSR2 = [7.58,5.42,4.21]
#         extraV2  = [5.,7.,9.]
#         extraQ2 = 2*np.array([173.4194, 465.9139, 821.3795])
#         extraCp2 = WT_performance(np.array(extraV2), R, areaRef, rho, np.array(extraTSR2), extraQ2) 
#         extraCp2 = extraCp2[0]
#         extraX2 = extraTSR2
#     elif args.configuration == "DTU_10MW" and args.variant == "Madsen2019":
#         extraFile = "QADflow.csv" 
#         extraData = np.genfromtxt(os.path.join(path_to_case, extraFolder, extraFile), delimiter=';')
#         extraV2 = extraData[:,0]
#         extraOm = np.array([.63, .63, .70, .88, .96, 1.01, 1.01, 1.01])
#         extraTSR2 = extraOm * R / extraData[:,0]
#         extraQ2 = extraData[:,1]
#         extraCp2 = WT_performance(np.array(extraV2), R, areaRef, rho, np.array(extraTSR2), extraQ2) 
#         extraCp2 = extraCp2[0]
#         extraX2 = extraV2



# =============================================================
# Packing options
# =============================================================
options = {}

options["path_to_case"] = path_to_case
options["case_tag"] = args.configuration

options["spanDir"] = spanDir
options["rotsign"] = rotsign
options["hifimesh"] = args.hifimesh
options["output"] = args.output
options["plotonly"] = args.plotonly

# ================================================
# High-Fidelity runs with ADflow
# ================================================
if 'ADflow' in args.fidelities:
    options["fidelity"] = "ADflow"
    hifi_torque, hifi_thrust, hifi_cp = OTCDaw.aero_Wrapper(tsrlist, Vlist, pitchlist, T, rho, R0, R, Nblade, options)
    
# ================================================
# Low-Fidelity runs with OpenFAST
# ================================================
if 'OpenFAST' in args.fidelities:
    options["fidelity"] = "OpenFAST"
    lofi_torque, lofi_thrust, lofi_cp = OTCDaw.aero_Wrapper(tsrlist, Vlist, pitchlist, T, rho, R0, R, Nblade, options)

# ================================================
# Low-Fidelity runs with AeroDyn 
# ================================================
if 'AeroDyn' in args.fidelities:
    options["fidelity"] = "AeroDyn"
    AD_torque, AD_thrust, AD_cp = OTCDaw.aero_Wrapper(tsrlist, Vlist, pitchlist, T, rho, R0, R, Nblade, options)

# ================================================
# Medium fidelity
# ================================================
if 'turbinesFoam' in args.fidelities:
    options["fidelity"] = "turbinesFoam"
    foam_torque, foam_thrust, foam_cp = OTCDaw.aero_Wrapper(tsrlist, Vlist, pitchlist, T, rho, R0, R, Nblade, options)

# ================================================
# External Low-Fidelity data 
# CAUTION: the wrapper does not execute AeroDyn:
#   Data should be obtained independently.
# ================================================
#suffixes = ["_ltd"]
suffixes = [""]
ADext_torque = np.zeros([len(ADext_vel),len(suffixes)])
ADext_thrust = np.zeros([len(ADext_vel),len(suffixes)])
ADext_cp = np.zeros([len(ADext_vel),len(suffixes)])
outputDirectory = os.path.join(path_to_case, "AeroDyn", args.output)
if args.withADres:
    if MPI.COMM_WORLD.rank == 0:
        for i in range(len(ADext_vel)):  # Looping over a range of input tip speed ratios
            tsr = ADext_tsr[i]
            Vel = ADext_vel[i]
            for j in range(len(suffixes)):  
                # Caution: the naming of the files assumes that they are numbered in the same order as the list of velocity you provide in ADext_vel
                outputFile = os.path.join(outputDirectory + suffixes[j], f"{Tag:s}.{i+1:d}.out")

                #postprocessing output files
                thrust, torque, power, fN, fT = OTCDparser.OFparse(outputFile,nodeR)

                cp, pwr, rpm, om, tip_speed = ut.WT_performance(Vel, R, np.pi*R**2, rho, tsr, torque)

                ADext_torque[i,j] = torque
                ADext_thrust[i,j] = thrust
                ADext_cp[i,j] = cp


# ================================================
# Plotting the results
# ================================================

globaloutputs = os.path.join(path_to_case, args.output)

if MPI.COMM_WORLD.rank == 0:
    if not os.path.exists(globaloutputs):
        os.mkdir(globaloutputs)

    # print(hifi_torque)
    # print(lofi_torque)
    # print(hifi_cp)
    # print(lofi_cp)
    # print(ADext_torque)
    # print(ADext_cp)

    #pull experimental data if they exist (only for UAE actually)
    exp_folder = os.path.join(path_to_case, "experiment")
    Eq = np.zeros(np.shape(tsrlist))*np.nan
    Et = np.zeros(np.shape(tsrlist))*np.nan
    Ep = np.zeros(np.shape(tsrlist))*np.nan
    Ecp = np.zeros(np.shape(tsrlist))*np.nan
    Eqs = np.zeros(np.shape(tsrlist))*np.nan
    Ets = np.zeros(np.shape(tsrlist))*np.nan
    Eps = np.zeros(np.shape(tsrlist))*np.nan
    Ecps = np.zeros(np.shape(tsrlist))*np.nan
    if os.path.exists(exp_folder):
        for i in range(len(Vlist)):  # Looping over a range of input tip speed ratios
            tsr = tsrlist[i]
            Vel = Vlist[i]
            Et[i], Eq[i], Ep[i], Ets[i], Eqs[i], Eps[i] = OTCDparser.UAEHparse(os.path.join(exp_folder,"uae6.z07.00.h%02.0f00000.hd1"%Vel))
            Ecp[i], pwr, rpm, om, tip_speed = ut.WT_performance(Vel, R, np.pi*R**2, rho, tsr, Eq[i])
            Ecps[i], pwr, rpm, om, tip_speed = ut.WT_performance(Vel, R, np.pi*R**2, rho, tsr, Eqs[i])

    f, ax = plt.subplots(figsize=(10, 7.5)) #(8, 3.2)
    if 'ADflow' in args.fidelities:
        plt.plot(xvals, hifi_cp, label="ADflow", marker="x", color=(1., 0, 0))
    if 'OpenFAST' in args.fidelities:        
        plt.plot(xvals, lofi_cp, label='OpenFAST', marker="o")
    if 'AeroDyn' in args.fidelities:
        plt.plot(xvals, AD_cp, label='AeroDyn', marker="+")
    #TODO: turbinegfaom
    if args.withADres:
        plt.plot(ADext_xvals, ADext_cp, label='AeroDyn ext', marker="s")
    if extraFolder and args.withEllipsys:
        # plt.plot(extraX, extraCp, label=extraFolder, marker="^",markersize=12, linestyle='', color=(0, 0.5, 0))
        plt.plot(extraX, extraCp, label=extraFolder, marker="^", markersize=8, color=(0, 0.5, 0))
        
        # plt.plot(extraX2, extraCp2, label="ADflow", marker="+")       
        
    if not np.isnan(sum(Eq)):
        plt.errorbar(xvals, Ecp, yerr=Ecps, color='black', label='experiment', marker="D")
    # ax.set_xlim(0, -40)
    # plt.title("Power coefficient", fontsize=18)
    if args.configuration == "NREL_PhaseVI_UAE":
        plt.xlabel(r"TSR", fontsize=16)
    else:
        plt.xlabel(r"$V \: [m/s]$", fontsize=16)
    plt.ylabel(r"$C_p$", fontsize=16)
    plt.grid()
    plt.tick_params(axis="both", labelsize=16)
    plt.legend(fontsize=16)
    # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(N, N_list)
    f.tight_layout()
    plt.savefig(f"{globaloutputs}/Cp.pdf")


    f, ax = plt.subplots(figsize=(10, 7.5))
    if 'ADflow' in args.fidelities:
        plt.plot(xvals, hifi_torque, label="ADflow", marker="x", color=(0.5, 0, 0))
    if 'OpenFAST' in args.fidelities:        
        plt.plot(xvals, lofi_torque, label='OpenFAST', marker="o")
    if 'AeroDyn' in args.fidelities:
        plt.plot(xvals, AD_torque, label='AeroDyn', marker="+")
    #TODO: turbinegfaom
    if args.withADres:
        plt.plot(ADext_xvals, ADext_torque, label='AeroDyn ext', marker="s")
    if extraFolder and args.withEllipsys:
        plt.plot(extraX, extraQ, label=extraFolder, marker="^")

        # plt.plot(extraX2, extraQ2, label="ADflow L0", marker="+")
    if not np.isnan(sum(Eq)):
        plt.errorbar(xvals, Eq, yerr=Eqs, color='black', label='Expe', marker="D")
    # ax.set_xlim(0, -40)
    plt.title("Torque", fontsize=18)
    if args.configuration == "NREL_PhaseVI_UAE":
        plt.xlabel(r"TSR", fontsize=16)
    else:
        plt.xlabel(r"$V$", fontsize=16)
    plt.ylabel(r"$Q \: [Nm]$", fontsize=16)
    plt.grid()
    plt.tick_params(axis="both", labelsize=16)
    plt.legend(fontsize=16)
    # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(N, N_list)
    f.tight_layout()
    plt.savefig(f"{globaloutputs}/Q.pdf")

    plt.show()

#    export_data=
#    numpy.savetxt("data.csv", export_data, delimiter=",")
