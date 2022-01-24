try:
    from adflow import ADFLOW

    _has_adflow = True
except ImportError:
    _has_adflow = False
import numpy as np


def requires_adflow(function):  # TODO turn this into requires_MACH
    def check_requirement(*args, **kwargs):
        if not _has_adflow:
            raise ImportError("adflow is required to do this.")
        return function(*args, *kwargs)

    return check_requirement


@requires_adflow
def setup(comm, gridFile, hifimesh, restart, outputDirectory, rotRate_z, spanDir, spanRef):

    AEROSOLVER = ADFLOW
    CFL = 1.5
    MGCYCLE = "sg"
    MGSTART = -1
    nCycles = 200000

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

    # Create solver
    CFDSolver = AEROSOLVER(options=aeroOptions, comm=comm)

    # setRotationRate(self, rotCenter, rotRate, cgnsBlocks=None)
    CFDSolver.setRotationRate([0, 0, 0], [rotRate_z, 0, 0])

    pos = np.array([0.1, 0.25, 0.5, 0.75, 0.9]) * spanRef
    CFDSolver.addSlices(spanDir, pos, sliceType="absolute")
    CFDSolver.addLiftDistribution(150, spanDir)

    return CFDSolver
