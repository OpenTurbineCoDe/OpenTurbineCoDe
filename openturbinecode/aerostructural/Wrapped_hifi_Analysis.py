# ======================================================================
#         Import modules
# ======================================================================
import numpy as np
from mpi4py import MPI
import pickle
from pprint import pprint

try:
    from baseclasses import AeroProblem
    from multipoint import multiPointSparse
    from pyoptsparse import Optimization, OPT
except ImportError as err:  # noqa
    _has_adflow = False
else:
    _has_adflow = True

from .SETUP import setup_adflow, setup_aerostruct, setup_aerostructprob, setup_tacs, setup_structprob, setup_warping

"""
Definition of a decorator to be used on every function that requires the sprcific module
"""


def requires_adflow(function):  # TODO turn this into requires_MACH
    def check_requirement(*args, **kwargs):
        if not _has_adflow:
            raise ImportError("adflow is required to do this.")
        function(*args, *kwargs)

    return check_requirement


def pickleWrite(fname, obj, comm=None):  # TODO: move this somewhere more appropriate
    """
    Parallel pickle.dump function, only performs operations on the root proc
    """
    if (comm is None) or (comm is not None and comm.rank == 0):
        with open(fname, "wb") as handle:
            pickle.dump(obj, handle)
    if comm is not None:
        comm.barrier()


# TODO: add another dictionary for parameter sweeps?
@requires_adflow
def HiFiAeroStruct(tsr, Vel, pitch, rho, T, options, optimize=False):
    # TODO: use the pitch variable!

    # ======================================================================
    #         Unpack options/params
    # ======================================================================
    path_to_case = options["path_to_case"]
    outputDirectory = options["outputDirectory"]
    case_tag = options["case_tag"]
    casename = options["casename"]
    spanRef = options["spanRef"]
    spanDir = options["spanDir"]
    areaRef = options["areaRef"]
    restart = options["restart"] if "restart" in options else None
    hifimesh = options["hifimesh"]

    # ======================================================================
    #         Input Information
    # ======================================================================

    rotRate_z = tsr * Vel / spanRef
    rpm = rotRate_z / (2 * np.pi) * 60

    print("Rotation Rate:", rotRate_z)
    print("RPM:", rpm)

    # TODO: we need to clarify if / how we loop over V and tsr

    if restart is not None:
        casename = casename + "_restart"
    ap = AeroProblem(name=casename, V=Vel, T=T, rho=rho, areaRef=areaRef, chordRef=spanRef, evalFuncs=["mx", "fx"])

    # ======================================================================
    #         Create multipoint communication object
    # ======================================================================
    MP = multiPointSparse(MPI.COMM_WORLD)
    nGroup = 1
    nProcPerGroup = MPI.COMM_WORLD.size
    MP.addProcessorSet("standard", nMembers=nGroup, memberSizes=nProcPerGroup)
    comm, _, _, _, _ = MP.createCommunicators()

    # ======================================================================
    #         Create aerostruct solver
    # ======================================================================

    gridFile = f"{path_to_case}/ADflow/INPUT/{case_tag}_L{hifimesh}.cgns"
    CFDSolver = setup_adflow.setup(comm, gridFile, hifimesh, restart, outputDirectory, rotRate_z, spanDir, spanRef)

    # ---- IDwarp - Warping setup
    mesh = setup_warping.setup(comm, gridFile)
    CFDSolver.setMesh(mesh)

    # ---- TACS - Create structurual solver
    bdfFile = f"{path_to_case}/ADflow/INPUT/DTU_10MW_RWT_blade3D_rotated_3in1_AprilMay2021.bdf"
    FEASolver = setup_tacs.setup(comm, bdfFile)
    dispFuncs = FEASolver.functionList.keys()  # Functions to keep track of
    objConFuncs = ["TotalMass"] + [f for f in dispFuncs if "KSFailure" in f]

    # --- pyAeroStrucuture - Create aerostructural solver ---
    AS = setup_aerostruct.setup(outputDirectory, comm, CFDSolver, FEASolver)

    # ---- Structproblem instantiation
    sp = setup_structprob.setup(dispFuncs, comm, ap)

    # ---- AeroStructproblem instantiation
    asp = setup_aerostructprob.setup(comm, ap, sp)

    # ======================================================================
    #         Functions and sensitivities:
    # ======================================================================

    def Obj(x):
        if comm.rank == 0:
            print("Design Variables")
            pprint(x)
        funcs = {}
        printfuncs = {}
        FEASolver.setDesignVars(x)
        # asp.setDesignVars(x)
        AS(asp)
        AS.evalFunctions(asp, funcs, evalFuncs=objConFuncs)
        AS.checkSolutionFailure(asp, funcs)

        # Evaluate other functions for printout
        CFDSolver.evalFunctions(asp.AP, printfuncs)
        FEASolver.evalFunctions(asp.SP, printfuncs)
        if comm.rank == 0:
            print("MDA results")
            print("+ ----------------------------- +")
            pprint(printfuncs)

        return funcs

    def Sens(x, funcs):
        funcsSens = {}
        AS.evalFunctionsSens(asp, funcsSens, evalFuncs=objConFuncs)  # + aero_problems[i].evalFuncs)
        AS.checkAdjointSolutionFailure(asp, funcsSens)
        # DVCon.evalFunctionsSens(funcsSens)
        if comm.rank == 0:
            print("MDA sensitivites")
            print("+ ----------------------------- +")
            pprint(funcsSens)
        return funcsSens

    def objCon(funcs, printOK):
        funcs["obj"] = 0.0

        funcs["obj"] += funcs[f"{ap.name}_TotalMass"]

        if printOK:
            pprint(funcs)
        return funcs

    if optimize:

        optProb = Optimization("Mass minimization", MP.obj, comm=MPI.COMM_WORLD)

        # Add variables from aeroProblem
        ap.addVariablesPyOpt(optProb)

        FEASolver.addVariablesPyOpt(optProb)

        for f in FEASolver.functionList:
            if "KSFailure" in f:
                optProb.addCon(f"{ap.name}_{f}", upper=1.0)

        # Add Objective
        optProb.addObj("obj", scale=1e-5)

        MP.setProcSetObjFunc("standard", Obj)
        MP.setProcSetSensFunc("standard", Sens)
        MP.setObjCon(objCon)
        MP.setOptProb(optProb)
        optProb.printSparsity()

        # Optimizer option
        optOptions = {
            "Major feasibility tolerance": 1.0e-4,  # target nonlinear constraint violation
            "Major optimality tolerance": 1.0e-4,  # target complementarity gap
            "Function precision": 1.0e-5,  # TODO we might want to be more conservative?
            "Major iterations limit": 500,
            "Verify level": -1,  # check on gradients : -1 means disable the check
            "Violation limit": 0.01,
            "Major step limit": 0.1,
            "Penalty parameter": 1e1,
            "Print file": f"{outputDirectory}/SNOPT_print.out",
            "Summary file": f"{outputDirectory}/SNOPT_summary.out",
        }
        # Instantiate Optimizer object
        opt = OPT("snopt", options=optOptions)

        # Run Optimization
        histFile = f"{outputDirectory}/snopt_hist.hst"
        sol = opt(optProb, MP.sens, storeHistory=histFile)
        if MPI.COMM_WORLD.rank == 0:
            print(sol)
    else:

        # Retrieve thickness defined in the setup file
        thk = FEASolver.getValues()
        funcs = Obj(thk)

    # AS(asp)
    # AS.evalFunctions(asp, funcs)
    # AS.checkSolutionFailure(asp, funcs)

    if MPI.COMM_WORLD.rank == 0:
        print(funcs)

    funcs["mx"] = funcs[f"{ap.name}_mx"]
    funcs["fx"] = funcs[f"{ap.name}_fx"]

    pickleWrite(f"{outputDirectory}/Funcs.pkl", funcs)

    return funcs, ap
