# import subprocess
# from .utils import utilities as ut

# failed_imports = []
# # -------------------- pandas ----------------------------
# try: 
#     import pandas
# except ImportError as err:
#     failed_imports.append("pandas")

# # -------------------- pCrunch ----------------------------
# try: 
#     from pCrunch import analysis    #TG 7/1 edited from "Analysis" to "analysis." Python is case-sensitive and the proper file name is lowercase.
# except ImportError as err:
#     failed_imports.append("pCrunch")

# try: 
#     from rosco import controller
# except ImportError as err:
#     failed_imports.append("ROSCO_toolbox")
#     print(f"Error importing ROSCO_toolbox: {err}")
#     print("------------------------------------------")
#     print("Something is not right with pCrunch")
#     print("Please manually patch pCrunch to correctly import ROSCO_toolbox")
#     print("------------------------------------------")

# # -------------------- openmdao ----------------------------
# try: 
#     import openmdao.api
# except ImportError as err:
#     failed_imports.append("openmdao")

# # -------------------- pyFAST ----------------------------
# try: 
#     import pyFAST.input_output
# except ImportError as err:
#     failed_imports.append("pyFAST")
    
# # -------------------- ADFLOW ----------------------------
# try: # check adflow import
#     import adflow
# except ImportError as err:
#     failed_imports.append("adflow")

# # -------------------- PGL ----------------------------
# try: # check pgl import
#     import PGL
# except ImportError as err:
#     failed_imports.append("pgl")

# # -------------------- TACS ----------------------------
# try: # check adflow import
#     import pytacs
#     from tacs_orig import functions, constitutive

# except ImportError as err:
#     failed_imports.append("TACS/pyTACS")
    
# # -------------------- TACS ----------------------------
# try: # check adflow import
#     from pygeo import DVGeometry
    
# except ImportError as err:
#     failed_imports.append("pygeo")

# # -------------------- AeroelasticSE ----------------------------
# try:
#     from weis.aeroelasticse.CaseGen_IEC import CaseGen_IEC    #commented out by TG 6/30
#     #from ROSCO_toolbox.ofTools.case_gen.CaseGen_IEC import CaseGen_IEC    #TG 6/30
#     from weis.aeroelasticse.runFAST_pywrapper   import runFAST_pywrapper
# except ImportError as err:
#     failed_imports.append("AeroelasticSE")


# # -------------------- OpenFAST ----------------------------
# try:  # check local installation of openfast
#     config = ut.read_config()
#     path_to_openfast = config["lofi"]["path_to_openfast"]

#     subprocess.run([path_to_openfast, '--help'], shell=True, check=True, capture_output=True)
# except subprocess.CalledProcessError as err:
#     if err.returncode != 1:  #openfast exits with code 1 when called with `-h`
#         failed_imports.append("openfast")

# # -------------------- OpenFOAM / pimpleFoam ----------------------------
# try:  # check local installation of pimpleFoam
#     config = ut.read_config()
#     path_to_pimpleFoam = config["mefi"]["path_to_pimpleFoam"]

#     #subprocess.run([path_to_pimpleFoam, '--version'], shell=True, check=True, capture_output=True)    #Commented out by TG 8/16
#     subprocess.run([path_to_pimpleFoam, '-help'], shell=True, check=True, capture_output=True)    #TG 8/16 PimpleFoam doesn't have --version command
# except subprocess.CalledProcessError as err:
#     #if err.returncode != 0:  #TODO: check the exit code of 
#     if err.returncode != 1:    #TG 8/16 pimpleFoam exits with code 1 when called with help
#         failed_imports.append("pimpleFoam")

# # -------------------- Aerodyn driver ----------------------------
# try:  # check local installation of aerodyn
#     config = ut.read_config()
#     path_to_aerodyn = config["lofi"]["path_to_aerodyn"]

#     subprocess.run([path_to_aerodyn, '--help'], shell=True, check=True, capture_output=True)
# except subprocess.CalledProcessError as err:
#     if err.returncode != 1:  #openfast exits with code 1 when called with `-h`
#         failed_imports.append("aerodyn")

# # -------------------- PyQt5 ----------------------------
# try: 
#     import PyQt5.QtWidgets
# except ImportError as err:
#     failed_imports.append("PyQt5")


# # -------------------- ---------------- ----------------------------

# if len(failed_imports) > 0:
#     print("Warning - The following packages/executables are not found:", failed_imports)