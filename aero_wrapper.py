# ================================================
# External python imports
# ================================================
import argparse
import numpy as np
import os
import sys
import json
from mpi4py import MPI
import matplotlib.pyplot as plt

sys.path.insert(1, './scripts')
from OTCDparser import OFparse, UAEHparse, getLiftDistribution

# ================================================
# Input arguments
# ================================================

parser = argparse.ArgumentParser()
parser.add_argument("--output", help="Output directory (relative to case files)", type=str, default="outputs")
parser.add_argument("--configuration", help="WT Configuration", type=str, default="NREL_PhaseVI_UAE", choices=["NREL_PhaseVI_UAE","DTU_10MW"])
parser.add_argument("--variant", help="variant of the configuration", type=str, default="original")
parser.add_argument("--hifimesh", help="CFD mesh level - [0,1,2,3,4]", type=int, default=3)
parser.add_argument("--V", help="Inflow wind speed", type=float, default=[7.0], nargs="+")
parser.add_argument("--tsrlist", help="Prescribed tip speed ratio", type=float, default=[5.42], nargs="+")
parser.add_argument("--restart", help="Name of the restart file", type=str, default=None)
parser.add_argument("--plotonly", action='store_true', help="Skip the computations (outputs must be present in folders)")
parser.add_argument("--withADres", action='store_true', help="Look for AeroDyn-only results and plot them")
parser.add_argument("--withEllipsys", action='store_true', help="Look for EllipSys3D results and plot them")
args = parser.parse_args()

baseDir = os.path.dirname(os.path.abspath(__file__))
path_to_case = os.path.join(baseDir, args.configuration, args.variant)

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
        printf("ERROR: V and tsrlist must have the same size")
        exit(1)
    Vlist = np.array(args.V)
    tsrlist = np.array(args.tsrlist)

# TODO: add the ability to specify blade pitch

# Vlist = np.array([5.,6.,7.,8.,9.,10.,12.,15.,20.])
# tsrlist = np.array([7.58,6.32,5.42,4.74,4.21,3.78,3.16,2.53,1.90])

# =============================================================
# Parse additional config input file(s)
# =============================================================

with open('config.json') as file:
  config = json.load(file)

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
# File names for the lofi analysis
# =============================================================

if args.configuration == "NREL_PhaseVI_UAE":

    fstFile = "20kWturbine.fst"
    outFile = "20kWturbine.out"
    EDfile = "20kWEDexp.dat"
    IWfile = "20kW_InflowWind.dat"

    #TODO: define standard names and look for the proper file instead of hardcoding it
    fileList = [IWfile,
        "20kWADBlade.dat",
        "20kWAD15.dat",
        "20kWED_Tower.dat",
        "20kWEDBlade_experiment.dat",
        EDfile,
        fstFile]

    #hardcoded for now, for the results in the corresponding folder
    ADtsr = np.array([7.58, 6.32, 5.42, 4.74, 4.21, 3.78, 3.16, 2.53, 1.90])
    ADvel = np.array([5.,6.,7.,8.,9.,10.,12.,15.,20.])
    AD_xvals = ADtsr

elif args.configuration == "DTU_10MW":

    fstFile = "DTU10MW.fst"
    outFile = "DTU10MW.out"
    EDfile = "DTU10MWED.dat"
    IWfile = "DTU10MWInflowWind.dat"

    #TODO: define standard names and look for the proper file instead of hardcoding it
    fileList = [IWfile,
        "DTU10MWAD_Blade.dat",
        "DTU10MWAD15.dat",
        "DTU10MWED_Tower.dat",
        "DTU10MWED_Blade.dat",
        EDfile,
        fstFile]

    #hardcoded for now, for the results in the corresponding folder
    ADtsr = np.array([14.01, 9.34, 7.81, 7.81, 7.81, 7.81, 7.47])
    ADvel = np.array([4.,6.,8.,9.,10.,11.,12.])
    AD_xvals = ADvel

path_to_openfast = config["lofi"]["path_2_openfast"]

# =============================================================
# Performance function to postproduce High-Fidelity results
# =============================================================

def WT_performance(V, span, A, rho, tsr, torque):
    tip_speed = tsr * V
    om = tip_speed / span
    rpm = om / (2 * np.pi) * 60

    pwr = torque * om
    cp = pwr / (0.5 * rho * V ** 3 * A)
    return cp, pwr, rpm, om, tip_speed

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
        extraCp = WT_performance(extraV, R, areaRef, rho, extraTSR, extraQ)
        extraCp = extraCp[0]

        extraX = extraTSR
        
    elif args.configuration == "DTU_10MW":
        extraFile = "QEll.csv" 

        extraData = np.genfromtxt(os.path.join(path_to_case, extraFolder, extraFile), delimiter=';')
        extraV = extraData[:,0]
        extraOm = np.array([.63, .63, .70, .88, .96, 1.01, 1.01, 1.01])
        extraTSR = extraOm * R / extraData[:,0]
        extraQ = extraData[:,1]
        extraCp = WT_performance(extraV, R, areaRef, rho, extraTSR, extraQ)
        extraCp = extraCp[0]

        extraX = extraV

# ================================================
# High-Fidelity runs with ADflow
# ================================================
spanRef = R # used for moment normalisation

hifi_torque = []
hifi_thrust = []
hifi_cp = []
hifi_file = os.path.join(baseDir, "scripts", "Wrapped_hifi_Analysis.py")
outputDirectory = os.path.join(path_to_case, "ADflow", args.output)
if not os.path.exists(outputDirectory):
    os.mkdir(outputDirectory)
for i in range(len(Vlist)):  # Looping over a range of input tip speed ratios
    tsr = tsrlist[i] * rotsign
    Vel = Vlist[i]
    
    #TODO: use Tag instead of the long name of the configuration
    name = f"{args.configuration}_L{args.hifimesh}_V{Vel:.0f}_TSR{tsrlist[i] * 100:.0f}"
    if not args.plotonly:
        if MPI.COMM_WORLD.rank == 0:
            print(f"Starting Hi-fi analysis at tsr={tsr}")
        exec(compile(open(hifi_file, "rb").read(), hifi_file, "exec"))  # Running the ADflow runscript

        # Extracting performance information
        torque = funcs[f"{ap.name}_mx"]
        thrust = funcs[f"{ap.name}_fx"]
    else:
        #Name used for plotting purposes only
        # TODO: we should probably rerun the cases with the new name and generate new output files, then we can remove outsname and use name directly for --plotonly
        outsname = f"Analysis_{Tag:s}_V{Vel:.0f}_TSR{tsrlist[i] * 100:.0f}_000_lift.dat"
        res = getLiftDistribution(os.path.join(outputDirectory,outsname))
           
        Ico = 'Coordinate' + str.capitalize(spanDir)
        torque = Nblade*np.trapz(np.array(res['Lift'][:])*np.array(res[Ico][:]),np.array(res[Ico][:]))
        thrust = Nblade*np.trapz(np.array(res['Drag'][:]),np.array(res[Ico][:]))

    cp, pwr, rpm, om, tip_speed = WT_performance(Vel, spanRef, areaRef, rho, tsr, torque)

    hifi_thrust.append(thrust)
    hifi_torque.append(torque)
    hifi_cp.append(abs(cp))

# ================================================
# Low-Fidelity runs with OpenFAST
# ================================================
lofi_torque = []
lofi_thrust = []
lofi_cp = []
lofi_file = os.path.join(baseDir, "scripts", "Wrapped_lofi_Analysis.py")
outputDirectory = os.path.join(path_to_case, "OpenFAST", args.output)
if not os.path.exists(outputDirectory):
    os.mkdir(outputDirectory)
if MPI.COMM_WORLD.rank == 0:
    for i in range(len(Vlist)):  # Looping over a range of input tip speed ratios
        tsr = tsrlist[i]
        Vel = Vlist[i]
        rpm = rpmlist[i]
        outputFile = os.path.join(outputDirectory, f"{args.configuration}_V{Vel:.0f}_TSR{tsr * 100:.0f}.out")

        #computing results
        if not args.plotonly:
            print(f"Starting Lo-fi analysis at tsr={tsr}")
            exec(compile(open(lofi_file, "rb").read(), lofi_file, "exec"))  # Running the OpenFast runscript
        
        #postprocessing output files
        thrust, torque, power, fN, fT = OFparse(outputFile,nodeR)

        cp, pwr, rpm, om, tip_speed = WT_performance(Vel, R, np.pi*R**2, rho, tsr, torque)

        lofi_torque.append(torque)
        lofi_thrust.append(thrust)
        lofi_cp.append(cp)


# ================================================
# Low-Fidelity runs with AeroDyn 
# CAUTION: the wrapper does not execute AeroDyn:
#   Data should be obtained independently.
# ================================================
suffixes = [""]
AD_torque = np.zeros([len(ADvel),len(suffixes)])
AD_thrust = np.zeros([len(ADvel),len(suffixes)])
AD_cp = np.zeros([len(ADvel),len(suffixes)])
outputDirectory = os.path.join(path_to_case, "AeroDyn", args.output)
if MPI.COMM_WORLD.rank == 0 and args.withADres:
    for i in range(len(ADvel)):  # Looping over a range of input tip speed ratios
        tsr = ADtsr[i]
        Vel = ADvel[i]
        for j in range(len(suffixes)):  
            # Caution: the naming of the files assumes that they are numbered in the same order as the list of velocity you provide in ADvel
            outputFile = os.path.join(outputDirectory + suffixes[j], f"{Tag:s}.{i+1:d}.out")

            #postprocessing output files
            thrust, torque, power, fN, fT = OFparse(outputFile,nodeR)

            cp, pwr, rpm, om, tip_speed = WT_performance(Vel, R, np.pi*R**2, rho, tsr, torque)

            AD_torque[i,j] = torque
            AD_thrust[i,j] = thrust
            AD_cp[i,j] = cp

# ================================================
# Plotting the results
# ================================================

globaloutputs = os.path.join(baseDir, args.output)

if MPI.COMM_WORLD.rank == 0:
    if not os.path.exists(globaloutputs):
        os.mkdir(globaloutputs)

    print(hifi_torque)
    print(lofi_torque)
    print(hifi_cp)
    print(lofi_cp)

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
            Et[i], Eq[i], Ep[i], Ets[i], Eqs[i], Eps[i] = UAEHparse(os.path.join(exp_folder,"uae6.z07.00.h%02.0f00000.hd1"%Vel))
            Ecp[i], pwr, rpm, om, tip_speed = WT_performance(Vel, R, np.pi*R**2, rho, tsr, Eq[i])
            Ecps[i], pwr, rpm, om, tip_speed = WT_performance(Vel, R, np.pi*R**2, rho, tsr, Eqs[i])

    f, ax = plt.subplots(figsize=(10, 7.5))
    plt.plot(xvals, hifi_cp, label="ADflow (old) L1", marker="x", color=(0.5, 0, 0))
    plt.plot(xvals, lofi_cp, label='OpenFAST', marker="o")
    if args.withADres:
        plt.plot(AD_xvals, AD_cp, label='AaerDyn only', marker="s")
    if extraFolder and args.withEllipsys:
        plt.plot(extraX, extraCp, label=extraFolder, marker="^")
    if not np.isnan(sum(Eq)):
        plt.errorbar(xvals, Ecp, yerr=Ecps, color='black', label='Expe', marker="D")
    # ax.set_xlim(0, -40)
    plt.title("Power coefficient", fontsize=18)
    if args.configuration == "NREL_PhaseVI_UAE":
        plt.xlabel(r"TSR", fontsize=16)
    else:
        plt.xlabel(r"$V$", fontsize=16)
    plt.ylabel(r"$C_p$", fontsize=16)
    plt.grid()
    plt.tick_params(axis="both", labelsize=16)
    plt.legend(fontsize=16)
    # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(N, N_list)
    f.tight_layout()
    plt.savefig(f"{globaloutputs}/Cp.pdf")


    f, ax = plt.subplots(figsize=(10, 7.5))
    plt.plot(xvals, hifi_torque, label="ADflow (old) L1", marker="x", color=(0.5, 0, 0))
    plt.plot(xvals, lofi_torque, label='OpenFAST', marker="o")
    if args.withADres:
        plt.plot(AD_xvals, AD_torque, label='AeroDyn only', marker="s")
    if extraFolder and args.withEllipsys:
        plt.plot(extraX, extraQ, label=extraFolder, marker="^")
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
    plt.legend(loc="upper right", fontsize=16)
    # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(N, N_list)
    f.tight_layout()
    plt.savefig(f"{globaloutputs}/Q.pdf")

    plt.show()