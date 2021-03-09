# ======================================================================
#         Import modules
# ======================================================================
# import numpy as np
import shutil
import csv

# ======================================================================
#         Input Information + HARDCODED VALUES
# ======================================================================
# Several file names come from higher level

# HARDCODED VALUES FOR NOW:
dirList =["AeroData"]


# ======================================================================
#         Copying the working files
# ======================================================================

fileDirectory = os.path.join(path_to_case, "OpenFAST") #, args.output
workingDirectory = os.path.join(path_to_case, "OpenFAST", "workdir")

shutil.rmtree(workingDirectory,True)
os.mkdir(workingDirectory)

for file in fileList:
    shutil.copy(os.path.join(fileDirectory,file), os.path.join(workingDirectory,file))
for dir in dirList:
    shutil.copytree(os.path.join(fileDirectory,dir), os.path.join(workingDirectory,dir))    

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
replaceInFile(EDfile, fileDirectory, workingDirectory, [35], [rpm])

# inflow wind: Uinf, line 12
replaceInFile(IWfile, fileDirectory, workingDirectory, [12], [Vel])


# ======================================================================
#         Run OpenFAST
# ======================================================================

os.chdir(workingDirectory)

flag = os.system(path_to_openfast + "openfast "+ fstFile)

if flag!=0:
    print("Execution failed during call to OpenFAST")
    #exit(1)

#Copy the results into the ouput file
fromdir = os.path.join(workingDirectory, outFile)
shutil.copy(fromdir, outputFile)


