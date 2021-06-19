import subprocess

failed_imports = []
try: # check adflow import
    import adflow
except ImportError as err:
    failed_imports.append("adflow")

try:  # check local installation of openfast
    subprocess.run(['openfast', '--help'], shell=True, check=True)
except subprocess.CalledProcessError as err:
    failed_imports.append("openfast")

if len(failed_imports) > 0:
    print("Warning - The following packages are not installed:", failed_imports)