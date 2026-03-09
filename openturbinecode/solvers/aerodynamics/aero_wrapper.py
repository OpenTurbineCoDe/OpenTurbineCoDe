from pathlib import Path
from math import nan
import numpy as np
from mpi4py import MPI
from openturbinecode.utils import OTCDparser as parser
from openturbinecode.utils import utilities as ut
from .Wrapped_hifi_Analysis import HiFiAero
from .Wrapped_lofi_Analysis import LoFiAero


def aero_wrapper(tsrlist, Vlist, pitchlist, T, rho, R0, R, Nblade, options, Rlist=None):
    config = ut.read_config()
    config["hifi"] = {}
    config["lofi"]["files"] = {}

    # Parsing and checking options
    if "case_tag" not in options or "path_to_case" not in options or "fidelity" not in options:
        raise ValueError("Missing required options: 'case_tag', 'path_to_case', or 'fidelity'")
    path_to_case = Path(options["path_to_case"])
    case_tag = options["case_tag"]
    plotonly = options.get("plotonly", False)
    output_dir = options.get("output", "outputs")

    omlist = tsrlist * Vlist / R
    rpmlist = omlist / (2 * np.pi) * 60
    Rlist = Rlist if Rlist is not None else np.ones(np.size(omlist))

    config["lofi"]["files"]["fstFile"] = f"{case_tag}.fst"
    config["lofi"]["files"]["EDfile"] = f"{case_tag}_ED.dat"
    config["lofi"]["files"]["IWfile"] = f"{case_tag}_IW.dat"
    config["lofi"]["files"]["ADdrvfile"] = f"{case_tag}_ADdriver.inp"
    config["lofi"]["files"]["ADbladefile"] = f"{case_tag}_ADBlade.dat"
    config["lofi"]["files"]["OFfileList"] = [config["lofi"]["files"]["IWfile"],
                                             config["lofi"]["files"]["ADbladefile"],
                                             f"{case_tag}_AD15.dat",
                                             f"{case_tag}_EDTower.dat",
                                             f"{case_tag}_EDBlade.dat",
                                             config["lofi"]["files"]["EDfile"],
                                             config["lofi"]["files"]["fstFile"]]
    config["lofi"]["files"]["ADfileList"] = [config["lofi"]["files"]["ADdrvfile"],
                                             config["lofi"]["files"]["ADbladefile"],
                                             f"{case_tag}_AD15.dat"]

    torque, thrust, cp = [], [], []

    match options["fidelity"]:
        case 'ADflow':
            torque, thrust, cp = run_hifi(tsrlist, Vlist, pitchlist, rho, T, R, Nblade, config, options, Rlist, path_to_case / "ADflow" / output_dir, plotonly)
        case 'OpenFAST':
            torque, thrust, cp = run_lofi_openfast(tsrlist, Vlist, pitchlist, rho, T, R, Nblade, config, options, Rlist, path_to_case / "OpenFAST" / output_dir, plotonly)
        case 'AeroDyn':
            torque, thrust, cp = run_lofi_aerodyn(tsrlist, Vlist, pitchlist, rho, T, R, Nblade, config, options, Rlist, path_to_case / "AeroDyn" / output_dir, plotonly)
        case 'turbinesFoam':
            torque, thrust, cp = run_turbinesfoam(tsrlist, Vlist, pitchlist, R, Nblade, options, Rlist, path_to_case / "turbinesFoam", case_tag)
        case _:
            raise ValueError(f"Unknown fidelity option: {options['fidelity']}")

    return torque, thrust, cp


def run_hifi(tsrlist, Vlist, pitchlist, rho, T, R, Nblade, config, options, Rlist, output_dir, plotonly):
    torque, thrust, cp = [], [], []

    options["outputDirectory"] = output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(len(Vlist)):
        tsr = tsrlist[i] * options["rotsign"]
        vel = Vlist[i]
        pitch = pitchlist[i]
        span_ref = Rlist[i] * R
        area_ref = np.pi * span_ref ** 2
        options["spanRef"], options["areaRef"] = span_ref, area_ref

        casename = f"{options['case_tag']}_L{options['hifimesh']}_V{vel:.0f}_TSR{tsrlist[i] * 100:.0f}"
        options["casename"] = casename

        if not plotonly:
            if MPI.COMM_WORLD.rank == 0:
                print(f"Starting Hi-fi analysis at tsr={tsr}")

            funcs, ap = HiFiAero(tsr, vel, pitch, rho, T, options, Rscale=Rlist[i])
            trq, thr = (funcs[f"{ap.name}_mx"], funcs[f"{ap.name}_fx"]) if funcs else (np.nan, np.nan)
        else:
            output_file = output_dir / f"{casename}_000_lift.dat"
            trq, thr = postprocess_hifi(output_file, Nblade, options["spanDir"]) if output_file.is_file() else (np.nan, np.nan)

        CP, pwr, rpm, om, tip_speed = ut.WT_performance(vel, span_ref, area_ref, rho, tsr, trq)
        thrust.append(thr)
        torque.append(trq)
        cp.append(abs(CP))

    return torque, thrust, cp


def postprocess_hifi(output_file, Nblade, spanDir):
    res = parser.getLiftDistribution(output_file)
    Ico = f'Coordinate{spanDir.capitalize()}'
    trq = Nblade * np.trapz(np.array(res['Lift']) * np.array(res[Ico]), np.array(res[Ico]))
    thr = Nblade * np.trapz(np.array(res['Drag']), np.array(res[Ico]))
    return trq, thr


def run_lofi_openfast(tsrlist, Vlist, pitchlist, rho, T, R, Nblade, config, options, Rlist, output_dir, plotonly):
    torque, thrust, cp = [], [], []
    options["outputDirectory"] = output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    config["lofi"]["lofi_code"], config["lofi"]["files"]["fileList"] = "OpenFAST", config["lofi"]["files"]["OFfileList"]

    for i in range(len(Vlist)):
        tsr, vel, rpm, pitch = tsrlist[i], Vlist[i], Rlist[i] * R, pitchlist[i] * 180 / np.pi
        span_ref = Rlist[i] * R
        area_ref = np.pi * span_ref ** 2
        output_file = output_dir / f"{options['case_tag']}_V{vel:.0f}_TSR{tsr * 100:.0f}.out"
        options["outputFile"] = output_file

        if not plotonly:
            print(f"Starting Lo-fi analysis at tsr={tsr}")
            LoFiAero(tsr, vel, pitch, R, rho, T, config["lofi"], options, Rscale=Rlist[i])

        if output_file.is_file():
            thr, trq, _, _, _ = parser.OFparse(output_file)
            CP, _, _, _, _ = ut.WT_performance(vel, span_ref, area_ref, rho, tsr, trq)
        else:
            print(f"ERROR: could not find output file {output_file}.")
            trq, thr, CP = np.nan, np.nan, np.nan

        thrust.append(thr)
        torque.append(trq)
        cp.append(CP)

    return torque, thrust, cp


def run_lofi_aerodyn(tsrlist, Vlist, pitchlist, rho, T, R, Nblade, config, options, Rlist, output_dir, plotonly):
    torque, thrust, cp = [], [], []
    options["outputDirectory"] = output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    config["lofi"]["lofi_code"], config["lofi"]["files"]["fileList"] = "AeroDyn", config["lofi"]["files"]["ADfileList"]

    for i in range(len(Vlist)):
        tsr, vel, rpm, pitch = tsrlist[i], Vlist[i], Rlist[i] * R, pitchlist[i] * 180 / np.pi
        span_ref = Rlist[i] * R
        area_ref = np.pi * span_ref ** 2
        output_file = output_dir / f"{options['case_tag']}_V{vel:.0f}_TSR{tsr * 100:.0f}.out"
        options["outputFile"] = output_file

        if not plotonly:
            print(f"Starting AeroDyn analysis at tsr={tsr}")
            LoFiAero(tsr, vel, pitch, R, rho, T, config["lofi"], options, Rscale=Rlist[i])

        if output_file.is_file():
            thr, trq, _, _, _ = parser.OFparse(output_file)
            CP, _, _, _, _ = ut.WT_performance(vel, span_ref, area_ref, rho, tsr, trq)
        else:
            print(f"ERROR: could not find output file {output_file}.")
            trq, thr, CP = np.nan, np.nan, np.nan

        thrust.append(thr)
        torque.append(trq)
        cp.append(CP)

    return torque, thrust, cp


def run_turbinesfoam(tsrlist, Vlist, pitchlist, R, Nblade, options, Rlist, alm_folder, case_tag):
    torque, thrust, cp = [], [], []

    alm_folder.mkdir(parents=True, exist_ok=True)
    for idx, tsr in enumerate(tsrlist):
        vel, pitch = Vlist[idx], pitchlist[idx]
        span_ref = Rlist[idx] * R
        area_ref = np.pi * span_ref ** 2
        case_folder = alm_folder / f"tsr{idx}"
        subfolder = case_folder / '0/include'
        subfolder.mkdir(parents=True, exist_ok=True)

        # Define missing parameters as needed
        yaw, end_time, write_interval, dynamic_stall, end_effects_model = 0.0, 1.0, "???", "???", "???"
        processors = MPI.COMM_WORLD.Get_size()

        with open(subfolder / 'initialConditions', 'w') as fname:
            fname.write("|*--------------------------------*- C++ -*----------------------------------*| \n")
            fname.write("| =========                 |                                                 | \n")
            fname.write("| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           | \n")
            fname.write("|  \\    /   O peration     | Version:  4.x                                   | \n")
            fname.write("|   \\  /    A nd           | Web:      www.OpenFOAM.org                      | \n")
            fname.write("|    \\/     M anipulation  |                                                 | \n")
            fname.write("|*---------------------------------------------------------------------------*| \n")
            fname.write(f"WndVel \t{vel};\n")
            fname.write(f"TSR \t{tsr};\n")
            fname.write(f"BldPitchAng \t{pitch};\n")
            fname.write(f"Yaw \t{yaw};\n")
            fname.write(f"EndTime \t{end_time};\n")
            fname.write(f"WriteInterval \t{write_interval};\n")
            fname.write(f"DynamicStall \t{dynamic_stall};\n")
            fname.write(f"EndEffectsModel \t{end_effects_model};\n")
            fname.write(f"Processors \t{processors};\n")

        torque.append(nan)
        thrust.append(nan)
        cp.append(nan)

    return torque, thrust, cp
