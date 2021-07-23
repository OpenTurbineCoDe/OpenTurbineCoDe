#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 22:46:05 2021
This code is develioed for assign the thicknesses of 9 segments of DTU10MW blade.
THen, generate and return the FE solver to the caller.
# Created by Xianping DU xianping.du@gmail.com
"""

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
def setup(file,tsn,ts,tw,to):
    bdfFile = file
    structOptions = {
        "gravityVector": [0, 0, -9.81],
        "projectVector": [1, 0, 0],  # normal to planform
        "useMonitor": True,
        "monitorFrequency": 1,
    }
    FEASolver = pytacs.pyTACS(bdfFile, options=structOptions)

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

    # add the leading panel (the nose in the DTU10 MW report)
    # treat it as upper skin
    groupName = "U_SKIN"
    for i in range(0, 18, 2):
        patchName = ["SPAR.03" + "/" + f"SEG.{i:02}", "SPAR.03" + "/" + f"SEG.{i + 1:02}"]
        FEASolver.addDVGroup(groupName, include=patchName)

    # ==============================================================================
    #       Set-up constitutive properties for each DVGroup
    # ==============================================================================
    def conCallBack(dvNum, compDescripts, userDescript, specialDVs, **kargs):
        # dvNum:Current counter
        # the conCallBack will be called 'FEASolver.DVGroups'times to assgin
        # constitive for each DV group

        # Define Aluminium material properties and shell thickness limits
        rho_2024 = 2780  # Density, kg/m^3
        E_2024 = 73.1e9  # Elastic Modulus, Pa
        ys_2024 = 324e6  # Yield Strength, Pa
        nu = 0.33  # Poisson's ratio
        kcorr = 5.0 / 6.0  # Shear correction factor for isotropic shells
        tMin = 0.0016  # Min thickness m
        tMax = 0.10  # Max thickness m

        # Set shell thickness depending on component type:f"SEG.{j:02}"
        # Tour sizes are four vectors with 18 thicknesses for 18 segment along the span
        if "SKIN" in userDescript:
            if any(["SPAR" in d for d in compDescripts]):
                for i in range(9):  # depends
                    if any([f"SEG.{2*i:02}" in d for d in compDescripts]):
                        t=tsn[i]  # skin nose thickness
            else:
                # skin thicknesses for the three regions: leading panels, caps, trailing pabels
                for j in range(3):
                    if any([f"SEG.{j:02}" in d for d in compDescripts]):
                        for i in range(9): 
                            if any([f"SKIN.{2*i:03}" in d for d in compDescripts]):
                                t=ts[j][i]  
            
        elif "SPAR" in userDescript:
            if any(["SPAR.01" in d for d in compDescripts]):
                # check web B
                for i in range(9):
                    if any([f"SEG.{2*i:02}" in d for d in compDescripts]):
                        t=tw[i]
                
            elif any(["SPAR.02" in d for d in compDescripts]):
                # check web C
                for i in range(9):
                    if any([f"SEG.{2*i:02}" in d for d in compDescripts]):
                        t=tw[i]
            else:
                # check web D
                for i in range(9):
                    if any([f"SEG.{2*i:02}" in d for d in compDescripts]):
                        t=to[i]
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

    # Write out components to visualize design variables (contour of dv0)
    FEASolver.writeDVVisualization("Struct_solutions/dv_visual.f5")

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
        FEASolver.addFunction(
            name + "KSBuckling",
            functions.AverageKSBuckling,
            include=comps,
            KSWeight=KSWeight,
            safetyFactor=safetyFactor,
        )

    return FEASolver