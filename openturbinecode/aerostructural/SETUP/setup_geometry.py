# ================================
#         Import modules
# ================================
from pygeo import DVGeometry
import numpy as np


def setup(fix_root_sect, geom_dvs, comm, caseName, FFDfldr):

    # ==============================
    #       Load FFDs
    # ==============================

    FFDFile1 = FFDfldr + "FFD1_IEA.xyz"
    FFDFile2 = FFDfldr + "FFD2_IEA.xyz"
    FFDFile3 = FFDfldr + "FFD3_IEA.xyz"
    FFDFileG = FFDfldr + "FFDG_IEA.xyz"
    DVGeoc1 = DVGeometry(FFDFile1, child=True)  # child 1
    DVGeoc2 = DVGeometry(FFDFile2, child=True)  # child 2
    DVGeoc3 = DVGeometry(FFDFile3, child=True)  # child 3
    DVGeoG = DVGeometry(FFDFileG)  # Main grid

    # IMPORTANT: Number of fixed root sections
    fix_root_sect = fix_root_sect

    # Add the reference axis for the 3 children FFD
    rotType = 0
    zfraction = 0.25
    if comm.rank == 0:
        print("pyGeo rotation type:", rotType)
    # Note that the function sets up the pyGeo object attribute and returns
    nRefAxPts1 = DVGeoc1.addRefAxis("RefAx_wing_box1", zFraction=zfraction, alignIndex="k", rotType=rotType)
    nRefAxPts2 = DVGeoc2.addRefAxis(  # noqa F841
        "RefAx_wing_box2", zFraction=zfraction, alignIndex="k", rotType=rotType, rot0ang=-120
    )
    nRefAxPts3 = DVGeoc3.addRefAxis(  # noqa F841
        "RefAx_wing_box3", zFraction=zfraction, alignIndex="k", rotType=rotType, rot0ang=120
    )

    # add children # **cannot** be called before adRefAxis()
    DVGeoG.addChild(DVGeoc1)
    DVGeoG.addChild(DVGeoc2)
    DVGeoG.addChild(DVGeoc3)

    nTwist = nRefAxPts1 - fix_root_sect  # ---  Number of twist variables

    # =============================================
    #       Define pitch callback-function
    # =============================================
    def pitch(val, geo):
        # geo: DVGeoc1, DVGeoc2 or DVGeoc3
        # --------------------------------
        # MM: change range() starting index in the 'for' loop to pick which sections are excluded from the rotation. With 1, only the root section is fixed

        axis_key = list(geo.axis.keys())[0]  # returns the name of the refAxis for the current FFD obj provided as input

        x = DVGeoG.getValues()
        try:
            twst_vals = x["twist"]
        except KeyError:
            if comm.rank == 0 and axis_key[-1] == "1":
                print("Twist is not defined, assuming fixed blade pitch")
            twst_vals = [0] * nTwist
        pitch_vals = np.zeros(nRefAxPts1, "D")
        for i in range(1, fix_root_sect):
            pitch_vals[i] = val[0]
        for i in range(fix_root_sect, nRefAxPts1):
            pitch_vals[i] = twst_vals[i - fix_root_sect] + val[0]

        # using just nRefAxPts1 because the three children have the same number of spanwise sections (and Cp per section)
        for i in range(1, nRefAxPts1):
            geo.rot_theta[axis_key].coef[i] = pitch_vals[i]
            # assigns the same value to all the stations!
            # TODO: this fixes the overwriting! first twist, then pitch add a const val (check assign ordering) we might want to have twist to start from the second non-blocked section for opt formulation
            # WARNING: += is counted twice

    # =============================================
    #       Define twist callback-function
    # =============================================
    def twist(val, geo):
        # Same as pitch, but now val is a vector of size 1 x nTwist
        axis_key = list(geo.axis.keys())[0]
        for i in range(fix_root_sect, nRefAxPts1):
            geo.rot_theta[axis_key].coef[i] = val[i - fix_root_sect]

    # =============================================
    #       Define chord callback-function
    # =============================================
    def chord(val, geo):
        axis_key = list(geo.axis.keys())[0]

        for i in range(fix_root_sect, nRefAxPts1):
            geo.scale_z[axis_key].coef[i] = val[i - fix_root_sect]

    # =============================================
    #       Define thickness callback-function
    # =============================================
    def thickness(val, geo):
        axis_key = list(geo.axis.keys())[0]

        for i in range(fix_root_sect, nRefAxPts1):
            geo.scale_x[axis_key].coef[i] = val[i - fix_root_sect]

    # ===============================================
    #       Define span call-back function
    # ===============================================
    def span(val, geo):
        axis_key = list(geo.axis.keys())[0]
        C = geo.extractCoef(axis_key)
        for i in range(1, nRefAxPts1):  # the child ffds are identical so we just use 1 as reference
            if "_box1" in axis_key:  # no change in z coordinates for blade 1 - along y axis
                C[i, 1] *= val
            else:
                C[i, 1] *= val
                C[i, 2] *= val
        geo.restoreCoef(C, axis_key)

    # ===============================================
    #       Define sweep call-back function
    # ===============================================
    def sweep(val, geo):
        base_section = nRefAxPts1 - 3  # section from where we start sweeping
        axis_key = list(geo.axis.keys())[0]
        rotangle = geo.axis[axis_key]["rot0ang"]
        if rotangle is None:
            rotangle = 0.0
        rotangle = float(-rotangle / 180 * np.pi)

        C = geo.extractCoef(axis_key)
        for i in range(base_section, nRefAxPts1):
            C[i, 1] -= val[i - base_section] * np.sin(rotangle)
            C[i, 2] += val[i - base_section] * np.cos(rotangle)
        geo.restoreCoef(C, axis_key)

    # ==============================================================================
    #        Group DV information
    # ==============================================================================

    # --- Dictionary of DV funcs and bounds ---
    min_dihed = [-10] * nTwist
    min_dihed[0] = -0.1
    max_dihed = [10] * nTwist
    max_dihed[0] = 0.1
    dv_dict = {
        "pitch": {"func": pitch, "value": [0], "min": -34.5, "max": 34.5, "scale": 1},
        "twist": {"func": twist, "value": [0] * nTwist, "min": -34.5, "max": 34.5, "scale": 1},
        "chord": {"func": chord, "value": [1.0] * nTwist, "min": 0.7, "max": 1.4, "scale": 1},
        "thickness": {"func": thickness, "value": [1.0] * nTwist, "min": 0.7, "max": 1.4, "scale": 1},
        "span": {"func": span, "value": [1.0], "min": 0.7, "max": 1.5, "scale": 1},
        "sweep": {"func": sweep, "value": [0.0] * 3, "min": -15, "max": 0, "scale": 1},
    }

    # --- Add all the FFD childs in a list---

    allFFDs = [DVGeoc1, DVGeoc2, DVGeoc3]

    # =============================================
    #       Adding DVs
    # =============================================
    # We can use the same DV name (eg. 'pitch', 'span') for different child FFD.
    # The same design variable will be propagated to the different sub-blocks, each of these with their own refAxis, wihout the necessity of additional coupling or constraints.

    # --- Inserting children, global, and local DVs ---
    if comm.rank == 0:
        print("+ ------------------------------- +")
        print("Assembling FFD blocks:")

    n = 1

    for ffd in allFFDs:
        if comm.rank == 0:
            print(f"Inserting Child {n}")
        for key in geom_dvs:
            dv = dv_dict[key]
            ffd.addGlobalDV(
                dvName=key, value=dv["value"], func=dv["func"], lower=dv["min"], upper=dv["max"], scale=dv["scale"]
            )

        n += 1

    if comm.rank == 0:
        print("+ ------------------------------- +")

    return DVGeoG, DVGeoc1, DVGeoc2, DVGeoc3
