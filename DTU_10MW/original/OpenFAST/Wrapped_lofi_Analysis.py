# ================================================
# External python imports
# ================================================
import argparse
import numpy as np
import os
parser = argparse.ArgumentParser()
parser.add_argument("--V", help="Inflow wind speed", type=float, default=8.0)
args = parser.parse_args()
tsr = 5.
path_to_case = '/Users/DeeGee/OneDrive - UCL/BYU_ATLANTIS/Github/OpenTurbineTestCases/NREL_PhaseVI_UAE/original/'

# ======================================================================
#         Import modules
# ======================================================================
# import numpy as np
import shutil
import csv

# ======================================================================
#         Input Information + HARDCODED VALUES
# ======================================================================
# Coming from higher level

# HARDCODED VALUES FOR NOW:
R = 5.029
R0 = 0.508
om = tsr * args.V / R
rpm = om / (2 * np.pi) * 60

nodeidxs = np.array([1, 9, 29, 35, 48, 68, 75, 85, 92])

fstFile = "20kWturbine.fst"
outFile = "20kWturbine.out"
EDfile = "20kWElastoDyn.dat"
IWfile = "20kW_InflowWind.dat"
path_to_openfast = "/Users/DeeGee/Documents/BYU/devel/openfast_v2.3/build/glue-codes/openfast/"


#TODO: look for the proper file instead of hardcoding it
fileList = ["20kWturbine.out",
    "20kW_InflowWind.dat",
    "20kWADBlade.dat",
    "20kWAeroDyn.dat",
    "20kWED_Tower.dat",
    "20kWEDBlade.dat",
    "20kWElastoDyn.dat",
    "20kWturbine.ech",
    "20kWturbine.fst"]
dirList =["AeroData",
    "Airfoils"]

# ======================================================================
#         Copying the working files
# ======================================================================

fileDirectory = os.path.join(path_to_case, "OpenFAST") #, args.output
outputDirectory = os.path.join(fileDirectory, "results")

shutil.rmtree(outputDirectory,True)
os.mkdir(outputDirectory)

for file in fileList:
    shutil.copy(os.path.join(fileDirectory,file), os.path.join(outputDirectory,file))
for dir in dirList:
    shutil.copytree(os.path.join(fileDirectory,dir), os.path.join(outputDirectory,dir))    

# ======================================================================
#         Filling in the data where we need them in the input files
# ======================================================================

#take filename in inputDir, replace the list of [value] on [iline], and place it in outputDir
def replaceInFile(filename, inputDir, outputDir, iline, value):
    ifi = os.path.join(inputDir, filename)
    ofi = os.path.join(outputDir, filename)
    
    try:
        ifh = open(ifi, "rt")
        ofh = open(ofi, "wt")
    except Exception:
        print('Could not open files: '+ ifh +' or ' + ofh)
        exit(1)
    
    l = 0 #index of read file
    lr = 0 #index of replaced values
    for line in ifh.readlines():
        l+=1
        if l in iline:
            line = "  %9.5f"%value[lr] + line[11:]
            ofh.write(line)
            lr+=1
        else:
            ofh.write(line)
    ofh.close()
    ifh.close()

# elastodyn: rpm, line 35
replaceInFile(EDfile, fileDirectory, outputDirectory, [35], [rpm])

# inflow wind: Uinf, line 12
replaceInFile(IWfile, fileDirectory, outputDirectory, [12], [args.V])


# ======================================================================
#         Run OpenFAST
# ======================================================================

os.chdir(outputDirectory)

flag = os.system(path_to_openfast + "openfast "+ fstFile)

# os.path.join(path_to_case

if flag!=0:
    print("Execution failed during call to OpenFAST")
    #exit(1)

# ======================================================================
#         PostProcessing of OpenFAST
# ======================================================================

nodeR = nodeidxs/100.*(R-R0) + R0

fN = np.zeros(len(nodeR))
fT = np.zeros(len(nodeR))

data = np.array([])

try:
    # Reading the csv output
    ofh = open(outFile)

    for row in csv.reader(ofh, delimiter='\t' ):
        if len(row)<=1:
            continue
        Ncol = len(row)
        data = np.append(data,row)
    ofh.close()

    data = np.resize(data,[int(len(data)/Ncol),Ncol])

    # Identifying the rows of interest
    i = 0
    ifN0 = np.nan
    ifT0 = np.nan
    for str in data[0,:]:
        if "B1N1Fn" in str:
            ifN0 = i
        elif "B1N1Ft" in str:
            ifT0 = i
        i+=1

    # Time averaging the results for each spanwise station
    for i in range(len(nodeR)):
        fN[i] = np.mean(data[2:-1,ifN0+i].astype(np.float))
        fT[i] = np.mean(data[2:-1,ifT0+i].astype(np.float))

    thrust = np.trapz(fN,nodeR)
    torque = np.trapz(fT*np.array(nodeR),nodeR)

except Exception:
    print("Error while hanlding openfast result for TSR=%f and V=%f"%(tsr,args.V))
    torque = np.nan
    cp = np.nan

