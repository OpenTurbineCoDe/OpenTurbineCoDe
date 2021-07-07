import subprocess
from .utils import utilities as ut

failed_imports = []
# -------------------- ADFLOW ----------------------------
try: # check adflow import
    import adflow
except ImportError as err:
    failed_imports.append("adflow")

# -------------------- PGL ----------------------------
try: # check pgl import
    import PGL
except ImportError as err:
    failed_imports.append("pgl")

# -------------------- AeroelasticSE ----------------------------
try:
    from weis.aeroelasticse.CaseGen_IEC import CaseGen_IEC
    from weis.aeroelasticse.runFAST_pywrapper   import runFAST_pywrapper
except ImportError as err:
    failed_imports.append("AeroelasticSE")

# -------------------- OpenFAST ----------------------------
try:  # check local installation of openfast
    config = ut.read_config()
    path_to_openfast = config["lofi"]["path_to_openfast"]

    subprocess.run([path_to_openfast, '--help'], shell=True, check=True, capture_output=True)
except subprocess.CalledProcessError as err:
    if err.returncode != 1:  #openfast exits with code 1 when called with `-h`
        failed_imports.append("openfast")

# -------------------- Aerodyn driver ----------------------------
try:  # check local installation of aerodyn
    config = ut.read_config()
    path_to_aerodyn = config["lofi"]["path_to_aerodyn"]

    subprocess.run([path_to_aerodyn, '--help'], shell=True, check=True, capture_output=True)
except subprocess.CalledProcessError as err:
    if err.returncode != 1:  #openfast exits with code 1 when called with `-h`
        failed_imports.append("aerodyn")

# -------------------- ---------------- ----------------------------

if len(failed_imports) > 0:
    print("Warning - The following packages/executables are not found:", failed_imports)