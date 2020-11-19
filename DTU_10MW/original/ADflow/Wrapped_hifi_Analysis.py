# ======================================================================
#         Import modules
# ======================================================================
import numpy as np
from mpi4py import MPI
from baseclasses import AeroProblem
from adflow import ADFLOW
from multipoint import multiPointSparse


# ======================================================================
#         Input Information
# ======================================================================
# Coming from higher level

outputDirectory = os.path.join(path_to_case, args.output)

# =================== Thermodynamic conditions ==========================

# Below, we will specify wind speed, rho and temperature:
#                'V' + 'rho' + 'T'

V = [args.V]
rho = [1.225]  # density to calc: 'P', 'mu' and 'q'
T = [284.15]  # [Kelvin].Eqv to 11C.
# fixed settings
areaRef = 24977.46975854018  # expl: ref. area to normalize lift and drag

# chordRef is used for moment normalisation
spanRef = 89.166  # 89.166 [m] with the hub extension, see chordRef

tip_speed_ratio = args.tsr
rotRate_z = tip_speed_ratio * V[0] / spanRef
rpm = rotRate_z / (2 * np.pi) * 60

if MPI.COMM_WORLD.rank == 0:
    print("Rotation Rate:", rotRate_z)
    print("RPM:", rpm)

aeroProblems = []
nFlowCases = len(V)
for i in range(nFlowCases):
    name = f"Hifi_L{args.hifimesh}_V{args.V:.0f}_TSR{args.tsr * 100:.0f}"
    if args.restart is not None:
        name = name + "_restart"
    ap = AeroProblem(name=name, V=V[i], T=T[i], rho=rho[i], areaRef=areaRef, chordRef=spanRef, evalFuncs=["mx"])
    aeroProblems.append(ap)

AEROSOLVER = ADFLOW
gridFile = f"{path_to_case}/ADflow/INPUT/{args.configuration}_L{args.hifimesh}.cgns"
CFL = 1.5
MGCYCLE = "sg"
MGSTART = -1
nCycles = 200000

aeroOptions = {
    # Common Parameters
    "gridFile": gridFile,
    "restartFile": args.restart,
    "outputDirectory": outputDirectory,
    # Physics Parameters
    "equationType": "RANS",
    "smoother": "dadi",
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

if args.hifimesh >= 2:
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
comm, setComm, setFlags, groupFlags, ptID = MP.createCommunicators()

# Create solver
CFDSolver = AEROSOLVER(options=aeroOptions, comm=comm)

# setRotationRate(self, rotCenter, rotRate, cgnsBlocks=None)
CFDSolver.setRotationRate([0, 0, 0], [rotRate_z, 0, 0])

pos = np.array([0.1, 0.25, 0.5, 0.75, 0.9]) * spanRef
CFDSolver.addSlices("y", pos, sliceType="absolute")
CFDSolver.addLiftDistribution(150, "y")

# ======================================================================
#         Functions:
# ======================================================================

funcs = {}

for i in range(nFlowCases):
    CFDSolver(aeroProblems[i])
    CFDSolver.evalFunctions(aeroProblems[i], funcs)

if MPI.COMM_WORLD.rank == 0:
    print(funcs)
