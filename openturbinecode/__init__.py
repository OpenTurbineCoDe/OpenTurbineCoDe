import subprocess
from .utils import utilities as ut

failed_imports = []
try: # check adflow import
    import adflow
except ImportError as err:
    failed_imports.append("adflow")

try:  # check local installation of openfast
    subprocess.run(['openfast', '--help'], shell=True, check=True, capture_output=True)
except subprocess.CalledProcessError as err:
    if err.returncode != 1:  #openfast exits with code 1 when called with `-h`
        # second attempt: check if the path specified by the user works
        
        config = ut.read_config()
        path_to_openfast = config["lofi"]["path_2_openfast"]
    
        try:  # check local installation of openfast
            subprocess.run([path_to_openfast + 'openfast', '--help'], shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            if err.returncode != 1:  #openfast exits with code 1 when called with `-h`
                failed_imports.append("openfast")

if len(failed_imports) > 0:
    print("Warning - The following packages/executables are not found:", failed_imports)