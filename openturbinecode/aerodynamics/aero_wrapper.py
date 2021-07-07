"""
OpenTurbineCoDe aerodynamic wrapper

authors: Denis-Gabriel Caprace, Marco Mangano
"""

# ================================================
# External python imports
# ================================================
from math import nan
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

    pitchlist = np.zeros(np.size(omlist)) #TODO: handle this feature

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

        if MPI.COMM_WORLD.rank == 0:
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

        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(outputDirectory):
                os.mkdir(outputDirectory)
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
        
        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(outputDirectory):
                os.mkdir(outputDirectory)
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

    elif 'turbinesFoam' in fidelity:
        almFolder = os.path.join(path_to_case, "turbinesFoam")
        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(almFolder):
                os.mkdir(almFolder)

        for i in range(len(tsrlist)):
            #params
            tsr = tsrlist[i]
            Vel = Vlist[i]
            rpm = rpmlist[i]
            pitch = pitchlist[i]
            yaw = 0.0

            EndTime = 1.0 #TODO
            WriteInterval = "???" #TODO
            DynamicStall = "???" #TODO
            EndEffectsModel = "???" #TODO

            #file handling
            caseName = "tsr" + str(i)
            caseFolder = almFolder + os.sep + caseName
            if MPI.COMM_WORLD.rank == 0:
                if not os.path.exists(almFolder):
                    os.mkdir(almFolder)
            
                # shutil.copy('source', caseName) #TODO manage the copy of this
                
                subfolder = caseFolder + os.sep + '0' + os.sep + 'include'
                os.makedirs(subfolder,exist_ok=True)

                fname = open(subfolder + os.sep + 'initialConditions', 'w')
                fname.write("/*--------------------------------*- C++ -*----------------------------------*\ \n")
                fname.write("| =========                 |                                                 | \n")
                fname.write("| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           | \n")
                fname.write("|  \\    /   O peration     | Version:  4.x                                   | \n")
                fname.write("|   \\  /    A nd           | Web:      www.OpenFOAM.org                      | \n")
                fname.write("|    \\/     M anipulation  |                                                 | \n")
                fname.write("\*---------------------------------------------------------------------------*/ \n")

                fname.write("WndVel \t" + str(Vel) + ';\n')
                fname.write("TSR \t" + str(tsr) + ';\n')
                fname.write("BldPitchAng \t" + str(pitch) + ';\n')
                fname.write("Yaw \t" + str(yaw) + ';\n')

                fname.write("EndTime \t" + str(EndTime) + ';\n')
                fname.write("WriteInterval \t" + WriteInterval + ';\n')
                fname.write("DynamicStall \t" + DynamicStall + ';\n')
                fname.write("EndEffectsModel \t" + EndEffectsModel + ';\n')
                fname.write("Processors \t" + str(MPI.COMM_WORLD.Get_size())  + ';\n')
                fname.close()   

            #TODO: enable this in a safer way:
            # subprocess.run(["of4x"])
            # subprocess.run(["mpirun -np " + self.comBox_11.currentText() + " pimpleFoam -parallel > log&" ])
        
        #TODO: manage post-processing
        torque.append(nan)
        thrust.append(nan)
        cp.append(nan)


    return torque, thrust, cp
