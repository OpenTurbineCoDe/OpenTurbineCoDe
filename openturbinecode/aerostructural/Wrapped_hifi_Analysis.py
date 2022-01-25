# ======================================================================
#         Import modules
# ======================================================================
import numpy as np
import os
import json
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

from .SETUP import (
    setup_adflow,
    setup_aerostruct,
    setup_aerostructprob,
    setup_geometry,
    setup_tacs,
    setup_structprob,
    setup_warping,
)

"""
Definition of a decorator to be used on every function that requires the sprcific module
"""


def requires_adflow(function):  # TODO turn this into requires_MACH
    def check_requirement(*args, **kwargs):
        if not _has_adflow:
            raise ImportError("adflow is required to do this.")
        function(*args, *kwargs)

    return check_requirement


def pickleWrite(fname, obj, comm=None):
    """
    Parallel pickle.dump function, only performs operations on the root proc
    """
    if (comm is None) or (comm is not None and comm.rank == 0):
        with open(fname, "wb") as handle:
            pickle.dump(obj, handle)
    if comm is not None:
        comm.barrier()


@requires_adflow
def HiFiAeroStruct(tsr, Vel, pitch, rho, T, options, optimize=False):

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
    init_funcs_file = f"{outputDirectory}/init_funcs.json"
    if MPI.COMM_WORLD.rank == 0:
        print("Rotation Rate:", rotRate_z)
        print("RPM:", rpm)

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

    # ---- pyGeo setup
    FFDfldr = f"{path_to_case}/ADflow/INPUT/"
    fix_root_sect = 1
    geom_dvs = []

    if optimize:
        for key in options["opt_dvs"]:
            if options["opt_dvs"][key] is True and key != "structThick":
                geom_dvs.append(key)
    else:
        for key in options["analysis_input"]:
            geom_dvs.append(key)
            geom_dvs.append("pitch")

    DVGeoG, DVGeoc1, DVGeoc2, DVGeoc3 = setup_geometry.setup(fix_root_sect, geom_dvs, comm, ap.name, FFDfldr)

    # ---- ADflow setup
    gridFile = f"{path_to_case}/ADflow/INPUT/{case_tag}_L{hifimesh}.cgns"
    CFDSolver = setup_adflow.setup(comm, gridFile, hifimesh, restart, outputDirectory, rotRate_z, spanDir, spanRef)
    CFDSolver.setDVGeo(DVGeoG)
    # ---- IDwarp - Warping setup
    mesh = setup_warping.setup(comm, gridFile)
    CFDSolver.setMesh(mesh)

    # ---- TACS - Create structurual solver
    bdfFile = f"{path_to_case}/ADflow/INPUT/DTU_10MW_RWT_blade3D_rotated_3in1_AprilMay2021.bdf"
    FEASolver = setup_tacs.setup(comm, bdfFile)
    FEASolver.setDVGeo(DVGeoG)
    dispFuncs = FEASolver.functionList.keys()
    # Functions to keep track of for sensitivity evaluation
    objConFuncs = ["TotalMass"] + [f for f in dispFuncs if "KSFailure" in f]
    if options["opt_constraints"]["displ"] is True:
        objConFuncs += [f for f in dispFuncs if "displacement" in f]
    if options["opt_constraints"]["thrust"] is True:
        objConFuncs += ["fx"]
    if options["opt_obj"]["torque"] is True:
        objConFuncs += ["mx"]

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
        DVGeoG.setDesignVars(x)
        FEASolver.setDesignVars(x)
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
        if not os.path.exists(init_funcs_file):
            with open(init_funcs_file, "w") as outfile:
                fun = funcs.copy()
                json.dump(fun, outfile)

        return funcs

    def Sens(x, funcs):
        funcsSens = {}
        AS.evalFunctionsSens(asp, funcsSens, evalFuncs=objConFuncs)
        AS.checkAdjointSolutionFailure(asp, funcsSens)

        if comm.rank == 0:
            print("MDA sensitivites")
            print("+ ----------------------------- +")
            pprint(funcsSens)
        return funcsSens

    def objCon(funcs, printOK):
        funcs["obj"] = 0.0
        with open(init_funcs_file) as confile:
            init_funcs = json.load(confile)
        MP.gcomm.barrier()

        if options["opt_obj"]["mass"] is True:
            funcs["obj"] += options["opt_obj"]["massWeight"] * (
                funcs[f"{ap.name}_TotalMass"] / init_funcs[f"{ap.name}_TotalMass"]
            )
        if options["opt_obj"]["torque"] is True:
            funcs["obj"] += options["opt_obj"]["torqueWeight"] * (funcs[f"{ap.name}_mx"] / init_funcs[f"{ap.name}_mx"])

        if options["opt_constraints"]["thrust"] is True:
            funcs["thrust_con_" + ap.name] = funcs[f"{ap.name}_fx"] / (
                init_funcs[f"{ap.name}_fx"] * 1.05  # Hardcoded - 5% increase allowed
            )

        if options["opt_constraints"]["displ"] is True:
            fname = f"{ap.name}_displacement_u"
            funcs[f"displacement_con_{ap.name}"] = funcs[fname] / 1.05  # Hardcoded - 5% increase allowed

        if printOK:
            pprint(funcs)
        return funcs

    if optimize:

        optProb = Optimization("Optimization", MP.obj, comm=MPI.COMM_WORLD)

        # Add variables from aeroProblem
        ap.addVariablesPyOpt(optProb)

        # --- Add DVGeo variables ---
        DVGeoG.addVariablesPyOpt(optProb)

        if options["opt_dvs"]["structThick"] is True:
            FEASolver.addVariablesPyOpt(optProb)
            FEASolver.addConstraintsPyOpt(optProb)

        if options["opt_constraints"]["stress"] is True:
            for f in FEASolver.functionList:
                if "KSFailure" in f:
                    optProb.addCon(f"{ap.name}_{f}", upper=1.0)

        if options["opt_constraints"]["thrust"] is True:
            optProb.addCon("thrust_con_" + ap.name, upper=1.0)

        if options["opt_constraints"]["displ"] is True:
            optProb.addCon("displacement_con_" + ap.name, upper=1.0)
        # Add Objective
        optProb.addObj("obj")

        MP.setProcSetObjFunc("standard", Obj)
        MP.setProcSetSensFunc("standard", Sens)
        MP.setObjCon(objCon)
        MP.setOptProb(optProb)
        optProb.printSparsity()

        # Optimizer option
        if options["opt_options"]["optimizer"].lower() == "snopt":
            optOptions = {
                "Major feasibility tolerance": options["opt_options"]["tol"],  # target nonlinear constraint violation
                "Major optimality tolerance": options["opt_options"]["tol"],  # target complementarity gap
                "Function precision": 1.0e-5,
                "Major iterations limit": options["opt_options"]["max_iters"],
                "Verify level": -1,  # check on gradients : -1 means disable the check
                "Violation limit": 0.01,
                "Major step limit": 0.1,
                "Penalty parameter": 1e1,
                "Print file": f"{outputDirectory}/SNOPT_print.out",
                "Summary file": f"{outputDirectory}/SNOPT_summary.out",
            }
        elif options["opt_options"]["optimizer"].lower() == "slsqp":
            optOptions = {
                "MAXIT": options["opt_options"]["max_iters"],
                "ACC": options["opt_options"]["tol"],
                "IFILE": f"{outputDirectory}/SLSQP.out",
            }
        elif options["opt_options"]["optimizer"].lower() == "ipopt":
            optOptions = {
                "max_iter": options["opt_options"]["max_iters"],
                "tol": options["opt_options"]["tol"],
                "output_file": f"{outputDirectory}/IPOPT.out",
            }
        else:
            raise Warning("Invalid optimizer selected")
        # Instantiate Optimizer object
        opt = OPT(options["opt_options"]["optimizer"], options=optOptions)

        # Run Optimization
        histFile = f"{outputDirectory}/{options['opt_options']['optimizer']}_hist.hst"
        sol = opt(optProb, MP.sens, storeHistory=histFile)
        if MPI.COMM_WORLD.rank == 0:
            print(sol)
    else:

        # initial DV values
        x = DVGeoG.getValues()
        # Retrieve thickness defined in the setup file
        thk = FEASolver.getValues()
        x.update(thk)

        # updating DVs with user inputs
        for key in options["analysis_input"]:
            x[key] = options["analysis_input"][key]
        x["pitch"] = pitch

        coords = mesh.getSurfaceCoordinates()
        DVGeoG.addPointSet(coords, "coords")
        funcs = Obj(x)

    if MPI.COMM_WORLD.rank == 0:
        print(funcs)

    funcs["mx"] = funcs[f"{ap.name}_mx"]
    funcs["fx"] = funcs[f"{ap.name}_fx"]

    pickleWrite(f"{outputDirectory}/Funcs.pkl", funcs)

    return funcs, ap
