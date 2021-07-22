try:
    from pyaerostructure import AeroStruct, TACSLDTransfer
except ImportError:
    print("pyAerostructure not currently available")


def setup(outdir, comm, CFDSolver, FEASolver):
    transferOptions = {}
    # Create transfer object
    transfer = TACSLDTransfer(CFDSolver, FEASolver, comm, options=transferOptions)
    mdOptions = {
        # Tolerances
        "outputDir": outdir,
        "relTol": 1e-7,
        "adjointRelTol": 1e-7,
        # Output Options
        "saveIterations": True,
        # Solution Options
        "damp0": 0.5,
        "nMDIter": 25,
        "MDSolver": "GS",
        # "MDSubSpaceSize": 40,
        # Adjoint optoins
        "adjointSolver": "KSP",
        "nadjointiter": 100,
        # Monitor Options
        "monitorVars": ["cl", "cd", "lift", "norm_u", "damp"],
    }
    # Create the final aerostructural solver
    AS = AeroStruct(CFDSolver, FEASolver, transfer, comm, options=mdOptions)

    return AS
