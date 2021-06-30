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

import utils.OTCDparser as parser
import utils.utilities as ut


# TODO: add the ability to specify blade pitch
def aero_Wrapper(tsrlist, Vlist, T, rho, R0, R, Nblade, fidelity, options, configuration, path_to_case):
    #TEMPS:
    baseDir = os.path.dirname(os.path.abspath(__file__))
    
    # =============================================================
    # Parse additional config input file(s)
    # =============================================================
    
    config = ut.read_config()
    path_to_openfast = config["lofi"]["path_2_openfast"]

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
    # =============================================================

    if configuration == "NREL_PhaseVI_UAE":

        case_prefix = "20kWturbine"
        fstFile = case_prefix + ".fst"
        EDfile = "20kWEDexp.dat"
        IWfile = "20kW_InflowWind.dat"
        ADdrvfile = "20kWturbineADdriver.inp"

        #TODO: define standard names and look for the proper file instead of hardcoding it
        OFfileList = [IWfile,
            "20kWADBlade.dat",
            "20kWAD15.dat",
            "20kWED_Tower.dat",
            "20kWEDBlade_experiment.dat",
            EDfile,
            fstFile]

        ADfileList = [ADdrvfile,
            "20kWADBlade.dat",
            "20kWAD15.dat",]

    elif configuration == "DTU_10MW":

        case_prefix = "DTU10MW"
        fstFile = case_prefix + ".fst"
        EDfile = case_prefix+"ED.dat"
        IWfile = case_prefix+"InflowWind.dat"
        ADdrvfile = case_prefix+"ADdriver.inp"

        #TODO: define standard names and look for the proper file instead of hardcoding it
        OFfileList = [IWfile,
            "DTU10MWAD_Blade.dat",
            "DTU10MWAD15.dat",
            "DTU10MWED_Tower.dat",
            "DTU10MWED_Blade.dat",
            EDfile,
            fstFile]

        ADfileList = [ADdrvfile,
            "DTU10MWAD_Blade.dat",
            "DTU10MWAD15.dat",]

    else:
        raise ValueError("unknown configuration")


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
        hifi_file = os.path.join(baseDir, "Wrapped_hifi_Analysis.py")
        outputDirectory = os.path.join(path_to_case, "ADflow", output)

        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)
        for i in range(len(Vlist)):  # Looping over a range of input tip speed ratios
            tsr = tsrlist[i] * rotsign
            Vel = Vlist[i]
            
            #TODO: use Tag instead of the long name of the configuration
            name = f"{configuration}_L{hifimesh}_V{Vel:.0f}_TSR{tsrlist[i] * 100:.0f}"
            if not plotonly:
                #TODO: change for a func
                # # inputs:
                # spanDir 
                # rotsign 
                # output  
                # omlist  
                # rpmlist 
                # areaRef 

                if MPI.COMM_WORLD.rank == 0:
                    print(f"Starting Hi-fi analysis at tsr={tsr}")
                exec(compile(open(hifi_file, "rb").read(), hifi_file, "exec"))  # Running the ADflow runscript

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

        lofi_file = os.path.join(baseDir, "Wrapped_lofi_Analysis.py")
        outputDirectory = os.path.join(path_to_case, "OpenFAST", output)
        lofi_code = "OpenFAST"
        fileList = OFfileList
        # omlist  
        # rpmlist ...

        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)
        if MPI.COMM_WORLD.rank == 0:
            for i in range(len(Vlist)):  # Looping over a range of input tip speed ratios
                tsr = tsrlist[i]
                Vel = Vlist[i]
                rpm = rpmlist[i]
                outputFile = os.path.join(outputDirectory, f"{configuration}_V{Vel:.0f}_TSR{tsr * 100:.0f}.out")

                #computing results
                if not plotonly:
                    print(f"Starting Lo-fi analysis at tsr={tsr}")
                    exec(compile(open(lofi_file, "rb").read(), lofi_file, "exec"))  # Running the OpenFast runscript
                
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
        lofi_file = os.path.join(baseDir, "Wrapped_lofi_Analysis.py")
        outputDirectory = os.path.join(path_to_case, "AeroDyn", output)

        lofi_code = "AeroDyn"
        fileList = ADfileList
        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)
        if MPI.COMM_WORLD.rank == 0:
            #TODO: use a single drive file with multiple inflow velocities instead
            for i in range(len(Vlist)):
                tsr = tsrlist[i]
                Vel = Vlist[i]
                rpm = rpmlist[i]
                outputFile = os.path.join(outputDirectory, f"{configuration}_V{Vel:.0f}_TSR{tsr * 100:.0f}.out")

                #computing results
                if not plotonly:
                    print(f"Starting AeroDyn analysis at tsr={tsr}")
                    exec(compile(open(lofi_file, "rb").read(), lofi_file, "exec"))  # Running the OpenFast runscript
                
                #postprocessing output files
                thr, trq, power, fN, fT = parser.OFparse(outputFile)

                CP, pwr, rpm, om, tip_speed = ut.WT_performance(Vel, R, np.pi*R**2, rho, tsr, trq)

                torque.append(trq)
                thrust.append(thr)
                cp.append(CP)

    elif 'turbinesFoam' in fidelity:
        almFolder = os.path.join(path_to_case, "turbinesFoam")
        os.chdir(almFolder)
        for i in range(len(tsrList)):
            caseName = "tsr" + str(i)
            shutil.copy('source', caseName)
            os.chdir(caseName)
            fname = open('0/include/initialConditions', 'w')
            fname.write("/*--------------------------------*- C++ -*----------------------------------*\ \n")
            fname.write("| =========                 |                                                 | \n")
            fname.write("| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           | \n")
            fname.write("|  \\    /   O peration     | Version:  4.x                                   | \n")
            fname.write("|   \\  /    A nd           | Web:      www.OpenFOAM.org                      | \n")
            fname.write("|    \\/     M anipulation  |                                                 | \n")
            fname.write("\*---------------------------------------------------------------------------*/ \n")

            fname.write("WndVel		" + self.lineEdit_7.text() + ';\n')
            fname.write("TSR		" + str(tsr) + ';\n')
            fname.write("BldPitchAng	" + self.lineEdit_3.text() + ';\n')
            fname.write("Yaw		" + self.lineEdit_4.text() + ';\n')

            fname.write("EndTime		" + self.lineEdit_11.text() + ';\n')
            fname.write("WriteInterval		" + self.lineEdit_5.text() + ';\n')
            fname.write("DynamicStall	" + self.comboBox_11.currentText() + ';\n');
            fname.write("EndEffectsModel	" + self.comboBox_10.currentText() + ';\n');
            fname.write("Processors" + self.comBox_11.currentText() + ';\n');
            fname.close()   

            subprocess.run(["of4x"])
            subprocess.run(["mpirun -np " + self.comBox_11.currentText() + "pimpleFoam -parallel > log&" ])
            os.chdir("..")  
        os.chdir("..")      


    return torque, thrust, cp
