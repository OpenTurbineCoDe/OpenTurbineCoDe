import numpy as np

def convert_fXYZ_to_uXYZ(infilename,outfilename="new.xyz",single_precision=False):
    """
    method to convert an unformatted plot3d multiblock grids to formatted

    parameters
    ----------
    filename: str
        name of the file to read
    single_precision: bool
        read file as single precision
    """
    #based off PGL/main/domain.py

    try:
        from scipy.io import FortranFile
    except:
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
            #bname = name + '-%04d' % n
            ni, nj, nk = bsizes[n,:]
            
            # read x, y, z data
            if single_precision:
                xt = f.read_reals(dtype=np.float32)
            else:
                xt = f.read_reals()
            
            for coord in xt:
                fsam.write("%.15f " % coord)
            fsam.write("\n")
            
            # # split into blocks
            # nt = ni * nj * nk
            # xt = xt.reshape(3, nt)
            # # split into x, y, z and reshape into ni, nj, nk
            # x = xt[0,:].reshape(nk,nj,ni).swapaxes(0,2)
            # y = xt[1,:].reshape(nk,nj,ni).swapaxes(0,2)
            # z = xt[2,:].reshape(nk,nj,ni).swapaxes(0,2)
            
    fsam.close()


# convert_fXYZ_to_uXYZ("DTU_10MW_RWT_mesh_1b.xyz","DTU_10MW_RWT_mesh_1b.unf.xyz")