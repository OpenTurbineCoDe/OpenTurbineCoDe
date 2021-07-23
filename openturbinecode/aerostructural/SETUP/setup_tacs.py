try:
    import pytacs
    from tacs_orig import functions, constitutive
except ImportError as err:
    _has_tacs = False
else:
    _has_tacs = True

"""
Definition of a decorator to be used on every function that requires the sprcific module
"""
def requires_tacs(function):
    def check_requirement(*args,**kwargs):
        if not _has_tacs:
            raise ImportError("TACS and pyTACS are required to do this.")
        function(*args,*kwargs)
    return check_requirement


@requires_tacs
def setup(comm, bdfFile):

    structOptions = {
        "gravityVector": [0, 0, -9.81],
        "projectVector": [1, 0, 0],  # normal to planform
        "useMonitor": True,
        "monitorFrequency": 1,
    }


    FEASolver = pytacs.pyTACS(bdfFile, comm=comm, options=structOptions)

    # ==============================================================================
    #       Set up design variable groups
    # ==============================================================================
    # Split each spar into 9 design variable groups
    # SPAR.00: webC
    # SPAR.01: webB
    # SPAR.02: webA
    # SPAR.03: leading panel (probably need to be merge to the skin...)
    FEASolver.addDVGroup("SPARS", include="SPAR.00", nGroup=9)
    FEASolver.addDVGroup("SPARS", include="SPAR.01", nGroup=9)
    FEASolver.addDVGroup("SPARS", include="SPAR.02", nGroup=9)
    # FEASolver.addDVGroup("SPARS", include="SPAR.03", nGroup=9)

    # Now create the skin groups, from side of body outwards, 2 skin panels per group
    for skin in ["U", "L"]:
        groupName = f"{skin}_SKIN"
        for i in range(0, 18, 2):
            # iterate in spanwise direction
            # every two sections form a group

            for j in range(3):
                # iterate in chordwise dir (4 spars -> 3 groups)
                patchName = [
                    f"{skin}_SKIN.{i:03}" + "/" + f"SEG.{j:02}",
                    f"{skin}_SKIN.{i + 1:03}" + "/" + f"SEG.{j:02}",
                ]

                FEASolver.addDVGroup(groupName, include=patchName)

    # add the leading panel
    # treat it as upper skin
    groupName = "U_SKIN"
    for i in range(0, 18, 2):
        patchName = ["SPAR.03" + "/" + f"SEG.{i:02}", "SPAR.03" + "/" + f"SEG.{i + 1:02}"]
        FEASolver.addDVGroup(groupName, include=patchName)

    # ==============================================================================
    #       Set-up constitutive properties for each DVGroup
    # ==============================================================================
    def conCallBack(dvNum, compDescripts, userDescript, specialDVs, **kargs):

        # Define Aluminium material properties and shell thickness limits
        rho_2024 = 2780  # Density, kg/m^3
        E_2024 = 73.1e9  # Elastic Modulus, Pa
        ys_2024 = 324e6  # Yield Strength, Pa
        nu = 0.33  # Poisson's ratio
        kcorr = 5.0 / 6.0  # Shear correction factor for isotropic shells
        tMin = 0.0016  # Min thickness m
        tMax = 0.10  # Max thickness m

        # Set shell thickness depending on component type
        if "SKIN" in userDescript:
            t = 0.009
        elif "SPAR" in userDescript:
            if any(["SPAR.01" in d for d in compDescripts]):
                # check web B
                t = 0.01
            elif any(["SPAR.02" in d for d in compDescripts]):
                # check web C
                t = 0.01
            else:
                t = 0.008
        else:
            raise Exception(
                f"Oops, you didn't define a thickness for this kind of component (userDescript: {userDescript}) :("
            )

        # Create constitutive object
        con = constitutive.isoFSDTStiffness(rho_2024, E_2024, nu, kcorr, ys_2024, t, dvNum, tMin, tMax)
        scale = [100.0]
        return con, scale

    # TACS will now create the constitutive objects for the different DV groups
    FEASolver.createTACSAssembler(conCallBack)

    # ==============================================================================
    #       Add functions
    # ==============================================================================

    funcGroups = {"USkin": "U_SKIN", "LSkin": "L_SKIN", "LESpar": "SPAR.02", "TESpar": "SPAR.01", "LEPatch": "SPAR.03"}
    safetyFactor = 1.5
    KSWeight = 100.0

    # Add a total mass function then, for each component group add a mass, max failure and KS failure function
    FEASolver.addFunction("TotalMass", functions.StructuralMass)
    for name, comps in funcGroups.items():
        FEASolver.addFunction(name + "Mass", functions.StructuralMass, include=comps)
        FEASolver.addFunction(
            name + "MaxFailure", functions.AverageMaxFailure, include=comps, safetyFactor=safetyFactor
        )
        FEASolver.addFunction(
            name + "KSFailure", functions.AverageKSFailure, include=comps, KSWeight=KSWeight, safetyFactor=safetyFactor
        )

    return FEASolver