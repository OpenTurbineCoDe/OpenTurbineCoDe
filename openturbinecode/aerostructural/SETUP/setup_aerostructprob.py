try:
    from baseclasses import AeroStructProblem
except ImportError:
    print("Baseclasses currently not available")


def setup(comm, ap, sp):

    asp = AeroStructProblem(ap, sp)

    return asp
