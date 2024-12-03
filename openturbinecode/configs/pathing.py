from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
WSL_ROOT = Path("\\\\wsl.localhost\\Ubuntu")
FOAM_RUN = Path("/home/caw/OpenFOAM/caw-v2406/run")

# turbinesFoam case directories
AXIAL_RUN = Path("/home/caw/OpenFOAM/caw-v2406/turbinesFoam/tutorials/axialFlowTurbineAL")

# OpenFAST case directories
OPENFAST_RUN = Path("D:/") / "GitHub" / "Solvers" / "openfast" / "run"

# AeroDyn case directories
AERODYN_RUN = Path("D:/") / "GitHub" / "Solvers" / "aerodynamics" / "aerodyn" / "run"
