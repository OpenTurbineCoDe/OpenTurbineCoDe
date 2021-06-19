failed_imports = []
try:
    import adflow
except ImportError as err:
    failed_imports.append("adflow")

if len(failed_imports) > 0:
    print("Warning - The following packages are not installed:", failed_imports)