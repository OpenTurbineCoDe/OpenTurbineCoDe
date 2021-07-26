# ======================================================================
#         Import modules
# ======================================================================
import numpy as np
from mpi4py import MPI
import pickle
from pprint import pprint

from .SETUP import setup_aerostruct, setup_aerostructprob, setup_tacs, setup_structprob, setup_warping

try:
    from baseclasses import AeroProblem
    from adflow import ADFLOW
    from multipoint import multiPointSparse
    from pyoptsparse import Optimization, OPT
except ImportError as err:
    _has_adflow = False
else:
    _has_adflow = True

"""
Definition of a decorator to be used on every function that requires the sprcific module
"""
def requires_adflow(function):  # TODO turn this into requires_MACH
    def check_requirement(*args,**kwargs):
        if not _has_adflow:
            raise ImportError("adflow is required to do this.")
        function(*args,*kwargs)
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
def HiFiAeroStruct(tsr,Vel,pitch,rho,T,options,optimize=False):
    #TODO: use the pitch variable!

    # ======================================================================
    #         Unpack options/params
    # ======================================================================
    path_to_case = options["path_to_case"]
    outputDirectory = options["outputDirectory"]
    case_tag = options["case_tag"]
    casename = options["casename"]
    spanRef  = options["spanRef"]
    spanDir  = options["spanDir"]
    areaRef  = options["areaRef"]
    restart  = options["restart"] if "restart" in options else None
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

    AEROSOLVER = ADFLOW
    gridFile = f"{path_to_case}/ADflow/INPUT/{case_tag}_L{hifimesh}.cgns"
    CFL = 1.5
    MGCYCLE = "sg"
    MGSTART = -1
    nCycles = 200000

    # TODO: for future maintainability, we might need to take the aeroOptions and ADflow instantiation to a separate file
    # to be also accessed by the optimization script

    aeroOptions = {
        # Common Parameters
        "gridFile": gridFile,
        "restartFile": restart,
        "outputDirectory": outputDirectory,
        # Physics Parameters
        "equationType": "RANS",
        "smoother": "DADI",
        "lowspeedpreconditioner": True,
        "userotationsa": True,
        "useqcr": True,
        "useblockettes": False,
        "vis2": 0.250,
        "restrictionrelaxation": 1.0,
        # Common Parameters
        "CFL": CFL,
        "CFLCoarse": CFL,
        "MGCycle": MGCYCLE,
        "MGStartLevel": MGSTART,
        "nCyclesCoarse": 250,
        "nCycles": nCycles,
        # Newton-Krylov Parameters
        "usenksolver": True,
        "nkswitchtol": 1e-14,
        "nkinnerpreconits": 2,
        "nkjacobianlag": 3,
        "nkouterpreconits": 3,
        "nkpcilufill": 2,
        "nksubspacesize": 100,
        # Approximate Newton-Krylov Parameters
        "useanksolver": True,
        "ankswitchtol": 1.0,
        "anklinearsolvetol": 0.05,
        "ankcflexponent": 0.5,
        "ankmaxiter": 60,
        "ankpcilufill": 2,
        "nsubiterturb": 10,
        "ankstepmin": 0.01,
        "anksecondordswitchtol": 1e-2,
        # 'ankcfllimit':500.,
        "anklinresmax": 0.1,
        # Convergence Parameters
        "L2Convergence": 1e-11,
        "L2ConvergenceCoarse": 1e-6,
        # Adjoint Parameters
        "adjointL2Convergence": 1e-9,
        "ADPC": True,
        "adjointMaxIter": 500000,
        "adjointSubspaceSize": 500,
        "ILUFill": 2,
        "ASMOverlap": 1,
        "outerPreconIts": 3,
        # Special
        "monitorvariables": ["cpu", "resrho", "cl", "cd", "resturb", "cfx", "cmx", "yplus"],
        # Output files
        "volumevariables": ["resrho", "resturb"],
        "surfacevariables": ["cp", "mach", "yplus", "sepsensor", "p", "temp"],
    }

    if int(hifimesh) >= 2:
        # Different options for coarser meshes
        aeroOptions["nkswitchtol"] = 1e-8
        aeroOptions["anklinresmax"] = 0.9
        aeroOptions["ankcfllimit"] = 500.0

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

    # Create solver
    CFDSolver = AEROSOLVER(options=aeroOptions, comm=comm)

    # setRotationRate(self, rotCenter, rotRate, cgnsBlocks=None)
    CFDSolver.setRotationRate([0, 0, 0], [rotRate_z, 0, 0])

    pos = np.array([0.1, 0.25, 0.5, 0.75, 0.9]) * spanRef
    CFDSolver.addSlices(spanDir, pos, sliceType="absolute")
    CFDSolver.addLiftDistribution(150, spanDir)

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

        funcs["obj"] += funcs[f"{ap.name}_TotalMass"] / numDesignPoints

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
