# ======================================================================
#         Import modules
# ======================================================================
import numpy as np
import os
import shutil
# import csv

# ======================================================================
#         Filling in the data where we need them in the input files
# ======================================================================

# take filename in inputDir, replace the list of [value] on [iline], and place it in outputDir
# mod = 0 (replace the value)|1 (multipy by value)|2 (add value)
# TODO: These functions should be generalized and imported from utils (?)


def replaceInFile(filename, inputDir, outputDir, iline, value, mod=0, fmt="  %9.5f"):
    ifi = os.path.join(inputDir, filename)
    ofi = os.path.join(outputDir, filename)
    buffer = ""

    ifh = []
    try:
        ifh = open(ifi, "rt")
    except Exception:
        print('Could not open files: ' + ifh)
        exit(1)

    l = 0  # index of read file
    lr = 0  # index of replaced values
    for line in ifh.readlines():
        l += 1
        if l in iline:
            if mod == 1:
                # multiply the value in the file
                line = "%9.6E" % (float(line[0:12])*value) + line[11:]
            elif mod == 2:
                # multiply the value in the file
                line = "%9.6E" % (float(line[0:12])+value) + line[11:]
            else:
                line = fmt % value[lr] + line[11:]

            buffer += line
            lr += 1
        else:
            buffer += line
    ifh.close()

    ofh = []
    try:
        ofh = open(ofi, "wt")
    except Exception:
        print('Could not open files: ' + ofh)
        exit(1)
    ofh.write(buffer)
    ofh.close()

# line and colomn indices start at 1
# mod = 0 (replace the value)|1 (multipy by value)|2 (add value)


def replaceInFileTable(filename, inputDir, outputDir, iline, icol, value, mod=0, separator=',', EF=False):
    ifi = os.path.join(inputDir, filename)
    ofi = os.path.join(outputDir, filename)

    buffer = ""

    ifh = []
    try:
        ifh = open(ifi, "rt")
    except Exception:
        print('Could not open files: ' + ifh)
        exit(1)

    l = 0  # index of read file
    lr = 0  # index of replaced values
    for line in ifh.readlines():
        l += 1
        if l in iline:
            # parse line:
            linesp = line.replace('\n', '').split(separator)
            line = ''

            if mod == 1:
                linesp[icol-1] = "%9.6E" % (float(linesp[icol-1])*value)
            elif mod == 2:
                linesp[icol-1] = "%9.6E" % (float(linesp[icol-1])+value)
            else:
                linesp[icol-1] = "%9.6E" % (value[lr])

            # reconstruct the line:
            for j in linesp:
                line += j + separator
            line = line[0:-len(separator)]  # erase last separator
            line += '\n'

            buffer += line
            lr += 1

            if EF and lr == len(iline):
                break
        else:
            buffer += line
    ifh.close()

    # if the file was too short, let's extend it:
    if mod == 0 and lr < len(iline):
        for ll in range(lr, len(iline)):
            line = ''
            linesp[icol-1] = "%9.6E" % (value[ll])

            for j in linesp:
                line += j + separator
            line = line[0:-len(separator)]  # erase last separator
            line += '\n'
            buffer += line

    ofh = []
    try:
        ofh = open(ofi, "wt")
    except Exception:
        print('Could not open files: ' + ofh)
        exit(1)
    ofh.write(buffer)
    ofh.close()


# TODO: add another dictionary for parameter sweeps?
def LoFiAeroStruct(tsr, Vel, pitch, R, rho, T, config, options):

    # ======================================================================
    #         Unpack options/params
    # ======================================================================
    path_to_case = options["path_to_case"]
    outputFile = options["outputFile"]
    case_tag = options["case_tag"]
    # casename = options["casename"]
    # spanDir  = options["spanDir"]

    # TODO: do something with pitch
    # TODO: do something with rho
    # TODO: do something with T

    rotRate_z = tsr * Vel / R
    rpm = rotRate_z / (2 * np.pi) * 60

    # ======================================================================
    #         Copying the working files
    # ======================================================================

    fileDirectory = os.path.join(path_to_case, config["lofi_code"])
    workingDirectory = os.path.join(path_to_case, config["lofi_code"], "workdir")

    shutil.rmtree(workingDirectory, True)
    os.mkdir(workingDirectory)

    for file in config["files"]["fileList"]:
        shutil.copy(os.path.join(fileDirectory, file), os.path.join(workingDirectory, file))
    for dir in config["files"]["dirList"]:
        shutil.copytree(os.path.join(fileDirectory, dir), os.path.join(workingDirectory, dir))

    if 'OpenFAST' in config["lofi_code"]:
        # elastodyn: rpm, line 35
        replaceInFile(config["files"]["EDfile"], fileDirectory, workingDirectory, [35], [rpm])

        # inflow wind: Uinf, line 12
        replaceInFile(config["files"]["IWfile"], fileDirectory, workingDirectory, [12], [Vel])

        run_cmd = config["path_to_openfast"] + " " + config["files"]["fstFile"]
        outFile = case_tag + ".out"

    elif 'AeroDyn' in config["lofi_code"]:
        raise Warning("Please run frim the standalone aero module")
    # ======================================================================
    #         Run OpenFAST / AeroDyn
    # ======================================================================

    # change to workdir and run
    cwd = os.getcwd()
    os.chdir(workingDirectory)

    flag = os.system(run_cmd)

    if flag != 0:
        print("ERROR - Execution failed during call to %s" %
              config["lofi_code"])
        exit(1)

    # go back to where we were
    os.chdir(cwd)

    # Copy the results into the ouput file
    fromdir = os.path.join(workingDirectory, outFile)
    shutil.copy(fromdir, outputFile)
