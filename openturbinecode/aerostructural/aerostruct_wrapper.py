"""
OpenTurbineCoDe aerodynamic wrapper

authors: Denis-Gabriel Caprace, Marco Mangano
"""

# ================================================
# External python imports
# ================================================

import numpy as np
import os
import time
from mpi4py import MPI
import pickle
from sqlitedict import SqliteDict
from collections import OrderedDict

# sys.path.insert(1, './scripts')
# from OTCDparser import OFparse, getLiftDistribution
# from utilities import WT_performance
# # from Wrapped_lofi_Analysis import compute_lofi

from ..utils import OTCDparser as parser
from ..utils import utilities as ut
from .Wrapped_hifi_Analysis import HiFiAeroStruct
from .Wrapped_lofi_Analysis import LoFiAeroStruct


def pickleRead(fname, comm=None):  # TODO: move this somewhere more appropriate
    """
    This is a paralle pickle.load function, which is performed on the root proc only.
    Error checking is necessary to provide py2 compatibility.
    """
    b = None
    if (comm is None) or (comm is not None and comm.rank == 0):
        if fname.split(".")[-1] == "pkl":
            try:
                with open(fname, "rb") as f:
                    b = pickle.load(f)
            except UnicodeDecodeError:  # if pickled with py2
                with open(fname, "rb") as f:
                    b = pickle.load(f, encoding="latin1")
        else:
            b = OrderedDict(SqliteDict(fname))
    if comm is not None:
        comm.barrier()
        b = comm.bcast(b)
    return b


# TODO: add the ability to specify blade pitch
# TODO: add another dictionary for parameter sweeps?
def aerostruct_Wrapper(tsrlist, Vlist, pitchlist, T, rho, R0, R, Nblade, options, optimize):

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

    if "spanDir" in options:
        spanDir = options["spanDir"]  # noqa
    if "rotsign" in options:
        rotsign = options["rotsign"]
    if "hifimesh" in options:
        hifimesh = options["hifimesh"]
    # TODO: set default values ?

    if "case_tag" not in options:
        raise ValueError("case_tag missing in options")
    if "path_to_case" not in options:
        raise ValueError("path_to_case missing in options")
    if "fidelity" not in options:
        raise ValueError("fidelity missing in options")

    path_to_case = options["path_to_case"]
    case_tag = options["case_tag"]

    plotonly = "plotonly" in options and options["plotonly"]

    if "output" in options:
        output = options["output"]  # output folder
    else:
        output = "outputs"

    # ========================================
    # initialization
    # ========================================

    omlist = tsrlist * Vlist / R  # absolute value of the rotation rate
    rpmlist = omlist / (2 * np.pi) * 60

    spanRef = R  # used for moment normalisation
    areaRef = np.pi * R ** 2
    options["spanRef"] = spanRef
    options["areaRef"] = areaRef

    # =============================================================
    # File names for the lofi analysis
    # TODO: use read values instead of HARDCODED VALUES
    # TODO: need a better management of file lists for OF/AD - more uniformity across files, etc.
    # =============================================================

    config["lofi"]["files"]["fstFile"] = case_tag + ".fst"
    config["lofi"]["files"]["EDfile"] = case_tag + "_ED.dat"
    config["lofi"]["files"]["IWfile"] = case_tag + "_IW.dat"
    config["lofi"]["files"]["ADdrvfile"] = case_tag + "_ADdriver.inp"

    # TODO: define standard names and look for the proper file instead of hardcoding it
    config["lofi"]["files"]["OFfileList"] = [
        config["lofi"]["files"]["IWfile"],
        case_tag + "_ADBlade.dat",
        case_tag + "_AD15.dat",
        case_tag + "_EDTower.dat",
        case_tag + "_EDBlade.dat",
        config["lofi"]["files"]["EDfile"],
        config["lofi"]["files"]["fstFile"],
    ]

    config["lofi"]["files"]["ADfileList"] = [
        config["lofi"]["files"]["ADdrvfile"],
        case_tag + "_ADBlade.dat",
        case_tag + "_AD15.dat",
    ]

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
    if "MACH" in options["fidelity"]:
        outputDirectory = os.path.join(path_to_case, "ADflow", output)
        exampleDirectory = os.path.join(path_to_case, "ADflow")
        options["outputDirectory"] = outputDirectory

        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(outputDirectory):
                os.makedirs(outputDirectory, exist_ok=True)
        for i in range(len(Vlist)):  # Looping over a range of input tip speed ratios
            tsr = tsrlist[i] * rotsign  # Caution: tsr is signed!
            Vel = Vlist[i]
            try:
                pitch = pitchlist[i]
            except IndexError:  # Hack due to the fact that numpy.array returns a weird float if the input is just a scalar
                pitch = pitchlist

            # TODO: use Tag instead of the long name of the configuration
            name = f"MDA_{case_tag}_L{hifimesh}_V{Vel:.0f}_TSR{tsrlist[i] * 100:.0f}"
            options["casename"] = name
            if not plotonly:

                if optimize:
                    if MPI.COMM_WORLD.rank == 0:
                        print("+ ------------------------------------ +")
                        print("Starting Optimization")
                        print("+ ------------------------------------ +")
                        time.sleep(3)
                        HiFiAeroStruct(tsr, Vel, pitch, rho, T, options, optimize=optimize)

                else:
                    if MPI.COMM_WORLD.rank == 0:
                        print(f"Starting Hi-fi analysis at tsr={tsr}")
                    HiFiAeroStruct(tsr, Vel, pitch, rho, T, options)
                outputdir = options["outputDirectory"]
                funcs = pickleRead(f"{outputdir}/Funcs.pkl")
                trq = funcs["mx"]
                thr = funcs["fx"]

                # Extracting performance information
                CP, pwr, rpm, om, tip_speed = ut.WT_performance(Vel, spanRef, areaRef, rho, tsr, trq)

                thrust.append(thr)
                torque.append(trq)
                cp.append(abs(CP))
            else:
                example_plots = os.path.join(exampleDirectory, "example_param_studies.py")
                os.system(f"python {example_plots}")

                # Name used for plotting purposes only
                # outsname = name + f"_000_lift.dat"
                # res = parser.getLiftDistribution(os.path.join(outputDirectory,outsname))

                # Ico = 'Coordinate' + str.capitalize(spanDir)
                # trq = Nblade*np.trapz(np.array(res['Lift'][:])*np.array(res[Ico][:]),np.array(res[Ico][:]))
                # thr = Nblade*np.trapz(np.array(res['Drag'][:]),np.array(res[Ico][:]))

            # TODO: temporarily disabling the "generalized" output vector
            # # Extracting performance information
            # CP, pwr, rpm, om, tip_speed = ut.WT_performance(Vel, spanRef, areaRef, rho, tsr, trq)

            # thrust.append(thr)
            # torque.append(trq)
            # cp.append(abs(CP))

    # ================================================
    # Low-Fidelity runs with OpenFAST
    # ================================================
    elif "OpenFAST" in options["fidelity"]:

        outputDirectory = os.path.join(path_to_case, "OpenFAST", output)
        options["outputDirectory"] = outputDirectory
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
                try:
                    pitch = pitchlist[i]
                except IndexError:  # Hack due to the fact that numpy.array returns a weird float if the input is just a scalar
                    pitch = pitchlist
                outputFile = os.path.join(outputDirectory, f"{case_tag}_V{Vel:.0f}_TSR{tsr * 100:.0f}.out")
                options["outputFile"] = outputFile

                # computing results
                if not plotonly:
                    print(f"Starting Lo-fi analysis at tsr={tsr}")

                    # Running the OpenFast runscript
                    LoFiAeroStruct(tsr, Vel, pitch, R, rho, T, config["lofi"], options)

                # postprocessing output files
                thr, trq, power, fN, fT = parser.OFparse(outputFile)

                CP, pwr, rpm, om, tip_speed = ut.WT_performance(Vel, R, np.pi * R ** 2, rho, tsr, trq)

                torque.append(trq)
                thrust.append(thr)
                cp.append(CP)

    return torque, thrust, cp
