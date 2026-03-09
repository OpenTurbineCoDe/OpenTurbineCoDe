import numpy as np
import logging


def convert_fXYZ_to_uXYZ(infilename, outfilename="new.xyz", single_precision=False):
    """Function to convert an unformatted plot3d multiblock grids to formatted.

    Args:
        infilename (str): Name of the file to read.
        outfilename (str, optional): Name of the file to write. Defaults to "new.xyz".
        single_precision (bool, optional): Read file as single precision. Defaults to False.

    Returns:
        None
    """
    # based off PGL/main/domain.py

    try:
        from scipy.io import FortranFile
    except ImportError as e:
        logging.error(f"Error in convert_fXYZtouXYZ: {e}.")
        raise ImportError('Install scipy: pip install scipy')

    # write out plot3d
    fsam = open(outfilename, "w")

    with FortranFile(infilename) as f:
        # read number of blocks
        nb = f.read_ints(dtype=np.int32)[0]
        fsam.write(str(nb) + "\n")

        bsizes = f.read_ints(dtype=np.int32)
        for idim in bsizes:
            fsam.write(str(idim) + " ")
        fsam.write("\n")

        bsizes = bsizes.reshape(nb, 3)

        # read per block data
        for n in range(nb):
            # bname = name + '-%04d' % n
            ni, nj, nk = bsizes[n, :]

            # read x, y, z data
            if single_precision:
                xt = f.read_reals(dtype=np.float32)
            else:
                xt = f.read_reals()

            for coord in xt:
                fsam.write("%.15f " % coord)
            fsam.write("\n")

    fsam.close()
