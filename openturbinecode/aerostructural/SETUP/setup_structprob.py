try:
    from baseclasses import StructProblem
except ImportError:
    print("Baseclasses currently not available")

def setup(dispFuncs,comm, ap):

    sp = StructProblem(ap.name, evalFuncs=dispFuncs)

    return sp
