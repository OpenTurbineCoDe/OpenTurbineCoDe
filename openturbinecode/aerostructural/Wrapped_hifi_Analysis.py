# ======================================================================
#         Import modules
# ======================================================================
import numpy as np
from mpi4py import MPI
import pickle

try:
    from baseclasses import AeroProblem
    from adflow import ADFLOW
    from multipoint import multiPointSparse
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
def HiFiAeroStruct(tsr,Vel,pitch,rho,T,options):
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

    # Create solver
    CFDSolver = AEROSOLVER(options=aeroOptions, comm=comm)

    # setRotationRate(self, rotCenter, rotRate, cgnsBlocks=None)
    CFDSolver.setRotationRate([0, 0, 0], [rotRate_z, 0, 0])

    pos = np.array([0.1, 0.25, 0.5, 0.75, 0.9]) * spanRef
    CFDSolver.addSlices(spanDir, pos, sliceType="absolute")
    CFDSolver.addLiftDistribution(150, spanDir)

    # ======================================================================
    #         Functions:
    # ======================================================================
    
    funcs = {}
    CFDSolver(ap)
    CFDSolver.evalFunctions(ap, funcs)

    if MPI.COMM_WORLD.rank == 0:
        print(funcs)

    funcs["mx"] = funcs[f"{ap.name}_mx"]
    funcs["fx"] = funcs[f"{ap.name}_fx"]

    outputdir = options["outputDirectory"]

    pickleWrite(f"{outputdir}/Funcs.pkl", funcs)
    
    return funcs, ap
