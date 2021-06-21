"""
OpenTurbineCoDe aerodynamic wrapper

authors: Denis-Gabriel Caprace, Marco Mangano
"""

# ================================================
# External python imports
# ================================================
import numpy as np
import os
import sys
from mpi4py import MPI

# sys.path.insert(1, './scripts')
# from OTCDparser import OFparse, getLiftDistribution
# from utilities import WT_performance
# # from Wrapped_lofi_Analysis import compute_lofi 

from ..utils import OTCDparser as parser
from ..utils import utilities as ut
from .Wrapped_hifi_Analysis import HiFiAero
from .Wrapped_lofi_Analysis import LoFiAero


# TODO: add the ability to specify blade pitch
def aero_Wrapper(args, tsrlist, Vlist, T, rho, R0, R, Nblade, fidelity, options, path_to_case):
    # baseDir = os.path.dirname(os.path.abspath(__file__))
    
    # =============================================================
    # Parse additional config input file(s)
    # =============================================================
    
    config = ut.read_config()
    config["hifi"] = {}
    config["lofi"]["files"] = {}

    # =============================================================
    # Turbine data unpacking
    # =============================================================

    # Tag = options["tag"]
    if "spanDir" in options:
        spanDir = options["spanDir"]
    if "rotsign" in options:
        rotsign = options["rotsign"]
    if "hifimesh" in options:
        hifimesh = options["hifimesh"]

    if "output" in options:
        output = options["output"] #output folder
    else:
        output = "output"
    plotonly = ("plotonly" in options and options["plotonly"]) 
    

    omlist = tsrlist * Vlist / R #absolute value of the rotation rate
    rpmlist = omlist / (2 * np.pi) * 60

    areaRef = np.pi*R**2

    # =============================================================
    # File names for the lofi analysis
    # TODO: use read values instead of HARDCODED VALUES
    # TODO: need a better management of file lists for OF/AD - more uniformity across files, etc.
    # =============================================================

    if args.configuration not in ["NREL_PhaseVI_UAE","DTU_10MW"]:
        raise ValueError("unknown configuration")

    config["lofi"]["files"]["fstFile"] = args.configuration + ".fst"
    config["lofi"]["files"]["EDfile"] = args.configuration + "_ED.dat"
    config["lofi"]["files"]["IWfile"] = args.configuration + "_IW.dat"
    config["lofi"]["files"]["ADdrvfile"] = args.configuration + "_ADdriver.inp"

    #TODO: define standard names and look for the proper file instead of hardcoding it
    config["lofi"]["files"]["OFfileList"] = [config["lofi"]["files"]["IWfile"],
        args.configuration + "_ADBlade.dat",
        args.configuration + "_AD15.dat",
        args.configuration + "_EDTower.dat",
        args.configuration + "_EDBlade.dat",
        config["lofi"]["files"]["EDfile"],
        config["lofi"]["files"]["fstFile"]]

    config["lofi"]["files"]["ADfileList"] = [config["lofi"]["files"]["ADdrvfile"],
        args.configuration + "_ADBlade.dat",
        args.configuration + "_AD15.dat",]

    config["lofi"]["files"]["dirList"] = ["AeroData"]

    # ================================================
    # Definition of the ouptus. TODO: pre-allocate...
    # ================================================
    torque = []
    thrust = []
    cp = []

    # ================================================
    # High-Fidelity runs with ADflow
    # ================================================
    if 'ADflow' in fidelity:
        spanRef = R # used for moment normalisation
        outputDirectory = os.path.join(path_to_case, "ADflow", output)

        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory, exist_ok=True)
        for i in range(len(Vlist)):  # Looping over a range of input tip speed ratios
            tsr = tsrlist[i] * rotsign # Caution: tsr is signed!
            Vel = Vlist[i]
            
            #TODO: use Tag instead of the long name of the configuration
            name = f"{args.configuration}_L{hifimesh}_V{Vel:.0f}_TSR{tsrlist[i] * 100:.0f}"
            if not plotonly:
                
                if MPI.COMM_WORLD.rank == 0:
                    print(f"Starting Hi-fi analysis at tsr={tsr}")
                funcs, ap = HiFiAero(name,args,tsr,Vel,spanRef,spanDir,rho,areaRef,T,path_to_case,outputDirectory)

                trq = funcs[f"{ap.name}_mx"]
                thr = funcs[f"{ap.name}_fx"]
            else:
                #Name used for plotting purposes only
                outsname = f"Analysis_{case_prefix:s}_V{Vel:.0f}_TSR{tsrlist[i] * 100:.0f}_000_lift.dat"
                res = parser.getLiftDistribution(os.path.join(outputDirectory,outsname))
                
                Ico = 'Coordinate' + str.capitalize(spanDir)
                trq = Nblade*np.trapz(np.array(res['Lift'][:])*np.array(res[Ico][:]),np.array(res[Ico][:]))
                thr = Nblade*np.trapz(np.array(res['Drag'][:]),np.array(res[Ico][:]))

            # Extracting performance information
            CP, pwr, rpm, om, tip_speed = ut.WT_performance(Vel, spanRef, areaRef, rho, tsr, trq)

            thrust.append(thr)
            torque.append(trq)
            cp.append(abs(CP))


    # ================================================
    # Low-Fidelity runs with OpenFAST
    # ================================================
    elif 'OpenFAST' in fidelity:

        outputDirectory = os.path.join(path_to_case, "OpenFAST", output)
        config["lofi"]["lofi_code"] = "OpenFAST"
        config["lofi"]["files"]["fileList"] = config["lofi"]["files"]["OFfileList"]
        # omlist  
        # rpmlist ...

        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)
        if MPI.COMM_WORLD.rank == 0:
            for i in range(len(Vlist)):  # Looping over a range of input tip speed ratios
                tsr = tsrlist[i]
                Vel = Vlist[i]
                rpm = rpmlist[i]
                outputFile = os.path.join(outputDirectory, f"{args.configuration}_V{Vel:.0f}_TSR{tsr * 100:.0f}.out")

                #computing results
                if not plotonly:
                    print(f"Starting Lo-fi analysis at tsr={tsr}")

                    # Running the OpenFast runscript
                    LoFiAero(args,config["lofi"],tsr,Vel,R,spanDir,rho,areaRef,T,path_to_case,outputFile,outputDirectory)
                
                #postprocessing output files
                thr, trq, power, fN, fT = parser.OFparse(outputFile)

                CP, pwr, rpm, om, tip_speed = ut.WT_performance(Vel, R, np.pi*R**2, rho, tsr, trq)

                torque.append(trq)
                thrust.append(thr)
                cp.append(CP)


    # ================================================
    # Low-Fidelity runs with AeroDyn 
    # ================================================
    elif 'AeroDyn' in fidelity:
        outputDirectory = os.path.join(path_to_case, "AeroDyn", output)

        config["lofi"]["lofi_code"] = "AeroDyn"
        config["lofi"]["files"]["fileList"] = config["lofi"]["files"]["ADfileList"]
        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)
        if MPI.COMM_WORLD.rank == 0:
            #TODO: use a single drive file with multiple inflow velocities instead
            for i in range(len(Vlist)):
                tsr = tsrlist[i]
                Vel = Vlist[i]
                rpm = rpmlist[i]
                outputFile = os.path.join(outputDirectory, f"{args.configuration}_V{Vel:.0f}_TSR{tsr * 100:.0f}.out")

                #computing results
                if not plotonly:
                    print(f"Starting AeroDyn analysis at tsr={tsr}")
                    
                    # Running the OpenFast runscript
                    LoFiAero(args,config["lofi"],tsr,Vel,R,spanDir,rho,areaRef,T,path_to_case,outputFile,outputDirectory)
                
                #postprocessing output files
                thr, trq, power, fN, fT = parser.OFparse(outputFile)

                CP, pwr, rpm, om, tip_speed = ut.WT_performance(Vel, R, np.pi*R**2, rho, tsr, trq)

                torque.append(trq)
                thrust.append(thr)
                cp.append(CP)

    return torque, thrust, cp
