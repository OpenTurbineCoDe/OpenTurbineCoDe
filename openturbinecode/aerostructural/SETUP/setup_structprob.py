from baseclasses import StructProblem


def setup(dispFuncs,comm, ap):

    sp = StructProblem(ap.name, evalFuncs=dispFuncs)

    return sp
