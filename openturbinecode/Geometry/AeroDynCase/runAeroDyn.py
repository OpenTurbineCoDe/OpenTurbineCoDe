import os, sys, shutil, tempfile, math, PyAeroDyn, numpy
import matplotlib.pyplot as plt


## prepare data
WSP = 10
RPM = 7.51
Yaw = 0
Pitch = 0
dT = 0.01
Tmax = 1
ShearExp = numpy.arange(0, 1, 0.1)
Cp = numpy.array([])

for ii in ShearExp:
    shutil.copyfile('driver.dvr.org', 'driver.dvr')
    f1 = open('driver.dvr', 'a')
    param = [ii, ShearExp, RPM, Pitch, Yaw, dT, Tmax]
    for line in param:
        f1.write(str(line))
        f1.write("\t")
    f1.close()

## run AeroDyn
    PyAeroDyn.PyAeroDyn()

## postProcessing
    result = numpy.loadtxt('Test014.1.out', skiprows=8, usecols=(1,))
    Cp = numpy.append(Cp, result[-1])


# Plot figures

plt.plot(ShearExp, Cp)
plt.xlabel('$U$', fontsize=16)
plt.ylabel('$C_P$', fontsize=16)
plt.ylim(0, 0.6)
plt.show()



