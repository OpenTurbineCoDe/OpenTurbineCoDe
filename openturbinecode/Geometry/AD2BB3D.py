# Convert AeroDyn blade definition file to BB3D input file

# Created by Kai Zhang (kai.zhang3@rutgers.edu)
# Jan 16, 2020

# Keys to use this code
# 1. Make sure that the airfoil coordinates are from the top trailing edge to bottom trailing edge
# 2. BB3D code can not handle a loft with too many sections. Mannual rearrangement of the loft distribution (less than 10 each) is necessary
# 3. It is recommended that different lofts are used on two sides of abrupt geometric change, e.g., from cylinder to airfoil
# 4. To many number of lofts is also not recommended

## Translate from airfoil ID number to airfoil name
def ID2Name(ID):
    if ID==1:
        return "Cylinder.dat"
    elif ID ==2:
        return "ffaw3600.dat"
    elif ID ==3:
        return "ffaw3480.dat"
    elif ID ==4:
        return "ffaw3360.dat"
    elif ID ==5:
        return "ffaw3301.dat"
    elif ID ==6:
        return "ffaw3241.dat"
    else:
        print("Error! Please check airfoil ID!")

## Decide loft arrangements
def loftID(ID):
    if ID==1:
	return 1
    else:
        return 2

## Main program starts here
with open('AeroDynCase/blade.dat', 'r') as f:
    next(f)
    next(f)
    next(f)
    next(f)
    next(f)
    next(f)
    content = [x.strip().split()[0:] for x in f]

NoSec = len(content)

fn = open('data.dat', 'w')
fn.write(str(NoSec) + " ## Number of blade sections" + '\n')
fn.write('2'  + " ## Number of lofts" + '\n')
fn.write('2'  + " ## Number of spars" + '\n')
for i in range(1, NoSec+1):
    fn.write(str(i) + "     "+ ID2Name(int(content[i-1][6])) + '\n')

fn.write("#NODE RNODES   TWIST   DRNODES  CHORD  AEROCENT  AEROORIG LOFT  " + '\n')
for i in range(1,NoSec+1):
    fn.write(str(i) +'\t'+ content[i-1][0] +'\t'+  content[i-1][4] +'\t'+ '0' +'\t'+ content[i-1][5] +'\t'+ '0.125' +'\t'+ '0.25' +'\t'+ str(loftID(int(content[i-1][6]))) +'\t'+ '\n')

fn.write('#SPAR PERCENTAGE' + '\n' + '0.15' + '\n' + '0.5' + '\n')







    


