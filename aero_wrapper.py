# ================================================
# External python imports
# ================================================
import argparse
import numpy as np
import os
import sys
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
parser.add_argument("--hifimesh", help="CFD mesh level - [0,1,2,3,4]", type=int, default=3)
parser.add_argument("--V", help="Inflow wind speed", type=float, default=[7.0], nargs="+")
parser.add_argument("--tsrlist", help="Prescribed tip speed ratio", type=float, default=[5.42], nargs="+")
parser.add_argument("--restart", help="Name of the restart file", type=str, default=None)
parser.add_argument("--plotonly", action='store_true', help="Skip the computations (outputs must be present in folders)")
parser.add_argument("--withADres", action='store_true', help="Look for AeroDyn-only results and plot them")
parser.add_argument("--withEllipsys", action='store_true', help="Look for EllipSys3D results and plot them")
args = parser.parse_args()

baseDir = os.path.dirname(os.path.abspath(__file__))
path_to_case = os.path.join(baseDir, args.configuration, "original")

# =============================================================
# Parse the parser data
# =============================================================

if isinstance(args.V,list): #sweeping tsr with constant vel
    tsrlist = np.array(args.tsrlist)
    V = np.ones(np.shape(tsrlist))*args.V
elif isinstance(args.tsrlist,list): #sweeping vel with constant tsr
    V = np.array(args.V)
    tsrlist = np.ones(np.shape(V)) *args.tsrlist
else:
    if len(args.V) != len(args.tsrlist):
        printf("ERROR: V and tsrlist must have the same size")
        exit(1)
    V = np.array(args.V)
    tsrlist = np.array(args.tsrlist)

# V = np.array([5.,6.,7.,8.,9.,10.,12.,15.,20.])
# tsrlist = np.array([7.58,6.32,5.42,4.74,4.21,3.78,3.16,2.53,1.90])

# =============================================================
# Turbine data
# =============================================================

T = 284.15  # [Kelvin].Eqv to 11C.
rho = 1.225

# Setting the correct reference system and blade span for the selected configuration
if args.configuration == "NREL_PhaseVI_UAE":
    spanDir = "y"
    R = 5.029
elif args.configuration == "DTU_10MW":
    spanDir = "z" #DTU
    R = 89.166  # DTU

R0 = 0.508  # TODO: what is this parameter? The spanwise location of the root?
om = tsrlist * V / R
rpm = om / (2 * np.pi) * 60

Nblade = 2
areaRef = np.pi*R**2

# TODO: Are these the spanwise stations used for OpenFast computations?
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
    fileList = [outFile,
        IWfile,
        "20kWADBlade.dat",
        "20kWAD15.dat",
        "20kWED_Tower.dat",
        "20kWEDBlade_experiment.dat",
        EDfile,
        "20kWturbine.ech",
        fstFile]

elif args.configuration == "DTU_10MW":

    # Temporarily assigning None values
    fstFile = None
    outFile = None
    EDfile = None
    IWfile = None

    #TODO: define standard names and look for the proper file instead of hardcoding it
    fileList = None


# TODO: This should not be hardcoded here. We should just tell the user to add their openfast path to their .bashrc file, so then in the lofi runscript we just os.system("openfast", fstfile)
path_to_openfast = "/Users/DeeGee/Documents/BYU/devel/openfast_v2.4/build/glue-codes/openfast/"

# =============================================================
# Extra CFD data from EllipSys3D
# =============================================================

extraFolder = "EllipSys3D"
extraFile = "LSStorque.csv" #low speed shaft torque. This file contains inflow vel in the first column, and torques in the second one.
if extraFolder and args.withEllipsys:
    extraData = np.genfromtxt(os.path.join(path_to_case, extraFolder, extraFile), delimiter=';')
    extraTSR = om[0] * R / extraData[:,0]
    


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


# ================================================
# High-Fidelity runs with ADflow
# ================================================
spanRef = R # used for moment normalisation

hifi_torque = []
hifi_thrust = []
hifi_cp = []
hifi_file = os.path.join(baseDir, "scripts", "Wrapped_hifi_Analysis.py")
outputDirectory = os.path.join(path_to_case, "ADflow", args.output)
for i in range(len(V)):  # Looping over a range of input tip speed ratios
    tsr = tsrlist[i]
    Vel = V[i]
    
    if not args.plotonly:
        print(f"Starting Hi-fi analysis at tsr={tsr}")
        exec(compile(open(hifi_file, "rb").read(), hifi_file, "exec"))  # Running the ADflow runscript

        # Extracting performance information
        torque = funcs[f"{ap.name}_mx"]
        thrust = np.nan #TO BE SET
    else:
        #CAUTION: WE SHOULD SET THIS NAME BEFORE THIS IF AND USE IF IN hifi_file
        name = f"Analysis_UAE_V{Vel:.0f}_TSR{tsr * 100:.0f}_000_lift.dat"
        res = getLiftDistribution(os.path.join(outputDirectory,name))
           
        torque = Nblade*np.trapz(np.array(res['Lift'][:])*np.array(res['CoordinateZ'][:]),np.array(res['CoordinateZ'][:]))
        thrust = Nblade*np.trapz(np.array(res['Drag'][:]),np.array(res['CoordinateZ'][:]))

    cp, pwr, rpm, om, tip_speed = WT_performance(Vel, spanRef, areaRef, rho, tsr, torque)

    hifi_thrust.append(thrust)
    hifi_torque.append(torque)
    hifi_cp.append(cp)


# ================================================
# Low-Fidelity runs with AeroDyn / CCBlade
# ================================================
lofi_torque = []
lofi_thrust = []
lofi_cp = []
lofi_file = os.path.join(baseDir, "scripts", "Wrapped_lofi_Analysis.py")
outputDirectory = os.path.join(path_to_case, "OpenFAST", args.output)
if MPI.COMM_WORLD.rank == 0:
    for i in range(len(V)):  # Looping over a range of input tip speed ratios
        tsr = tsrlist[i]
        Vel = V[i]
        outputFile = os.path.join(outputDirectory, f"{args.configuration}_V{Vel:.0f}_TSR{tsr * 100:.0f}.out")

        #computing results
        if not args.plotonly and args.configuration == "NREL_PhaseVI_UAE":  # TODO: temporary fix because we do not have the DTU model for openFast yet
            print(f"Starting Lo-fi analysis at tsr={tsr}")
            exec(compile(open(lofi_file, "rb").read(), lofi_file, "exec"))  # Running the OpenFast runscript
        
        #postprocessing output files
        thrust, torque, power, fN, fT = OFparse(outputFile,nodeR)

        cp, pwr, rpm, om, tip_speed = WT_performance(Vel, R, np.pi*R**2, rho, tsr, torque)

        lofi_torque.append(torque)
        lofi_thrust.append(thrust)
        lofi_cp.append(cp)


AD_torque = []
AD_thrust = []
AD_cp = []
outputDirectory = os.path.join(path_to_case, "AeroDyn", args.output)
if MPI.COMM_WORLD.rank == 0 and args.withADres:
    for i in range(len(V)):  # Looping over a range of input tip speed ratios
        tsr = tsrlist[i]
        Vel = V[i]
        # Caution: the naming of the files assumes that they are numbered in the same order as the list of velocity you provide as an argument to the wrapper
        outputFile = os.path.join(outputDirectory, f"20kWturbine.{i+1:d}.out")

        #postprocessing output files
        thrust, torque, power, fN, fT = OFparse(outputFile,nodeR)

        cp, pwr, rpm, om, tip_speed = WT_performance(Vel, R, np.pi*R**2, rho, tsr, torque)

        AD_torque.append(torque)
        AD_thrust.append(thrust)
        AD_cp.append(cp)


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
    Ecp = np.zeros(np.shape(tsrlist))*np.nan
    Eqs = np.zeros(np.shape(tsrlist))*np.nan
    Ets = np.zeros(np.shape(tsrlist))*np.nan
    Ecps = np.zeros(np.shape(tsrlist))*np.nan
    if os.path.exists(exp_folder):
        for i in range(len(V)):  # Looping over a range of input tip speed ratios
            tsr = tsrlist[i]
            Vel = V[i]
            Et[i], Eq[i], Pwr, Ets[i], Eqs[i], Pwrs = UAEHparse(os.path.join(exp_folder,"uae6.z07.00.h%02.0f00000.hd1"%Vel))
            Ecp[i], pwr, rpm, om, tip_speed = WT_performance(Vel, R, np.pi*R**2, rho, tsr, Eq[i])
            Ecps[i], pwr, rpm, om, tip_speed = WT_performance(Vel, R, np.pi*R**2, rho, tsr, Eqs[i])


    f, ax = plt.subplots(figsize=(10, 7.5))
    plt.plot(tsrlist, hifi_cp, label="High Fidelity", marker="x", color=(0.5, 0, 0))
    plt.plot(tsrlist, lofi_cp, label='Low Fidelity', marker="o")
    if args.withADres:
        plt.plot(tsrlist, AD_cp, label='AaerDyn only', marker="s")
    #plt.plot(tsrlist, Ecp, label='Expe', marker="D", color='k')
    plt.errorbar(tsrlist, Ecp, yerr=Ecps, color='black', label='Expe', marker="D")
    # ax.set_xlim(0, -40)
    plt.title("Power coefficient", fontsize=18)
    plt.xlabel(r"TSR", fontsize=16)
    plt.ylabel(r"$C_p$", fontsize=16)
    plt.grid()
    plt.tick_params(axis="both", labelsize=16)
    plt.legend(loc="upper left", fontsize=16)
    # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(N, N_list)
    f.tight_layout()
    plt.savefig(f"{globaloutputs}/Cp.pdf")


    f, ax = plt.subplots(figsize=(10, 7.5))
    plt.plot(tsrlist, hifi_torque, label="High Fidelity", marker="x", color=(0.5, 0, 0))
    plt.plot(tsrlist, lofi_torque, label='Low Fidelity', marker="o")
    if args.withADres:
        plt.plot(tsrlist, AD_torque, label='AeroDyn only', marker="s")
    if extraFolder and args.withEllipsys:
        plt.plot(extraTSR, extraData[:,1], label=extraFolder, marker="^")
    #plt.plot(tsrlist, Eq, label='Expe', marker="D", color='k')
    plt.errorbar(tsrlist, Eq, yerr=Eqs, color='black', label='Expe', marker="D")
    # ax.set_xlim(0, -40)
    plt.title("Torque", fontsize=18)
    plt.xlabel(r"TSR", fontsize=16)
    plt.ylabel(r"$Q \: [Nm]$", fontsize=16)
    plt.grid()
    plt.tick_params(axis="both", labelsize=16)
    plt.legend(loc="upper right", fontsize=16)
    # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(N, N_list)
    f.tight_layout()
    plt.savefig(f"{globaloutputs}/Q.pdf")

    plt.show()