from idwarp import USMesh


def setup(comm, gridFile):

    # ----- IDwarp options

    meshOptions = {
        # mham
        "gridFile": gridFile,
        # "warpType": "unstructured",
        "aExp": 3.0,
        "bExp": 5.0,
        "LdefFact": 10.0,  # affects how far the deformations are pushed away from the surface
        "alpha": 0.25,
        "errTol": 1e-5,
        # 'evalMode':'exact'
    }

    mesh = USMesh(options=meshOptions, comm=comm)

    return mesh
