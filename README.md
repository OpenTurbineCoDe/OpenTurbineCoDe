# Open Turbine Test Cases

This repository gathers a collection of test cases for the ARPA-E Atlantis project on Open Turbine control Co-Design.

Folders are organized as follows:
- level 0: reference turbine
- level 1: variants
- level 2: solver/level of fidelity
- level 3+: all *input* files/folders required to run the test cases

This repository does *not* contain the main pieces of software for the coupled optimization and for the control co-design loop.


## TODO
 - [ ] license

## Aerodynamics wrapper

The draft wrapper currently available iteratively runs ADflow and OpenFAST (v2.4) scripts over a set of tsr for a fixed inflow velocity, and returns a plot of Cp over tsr.
To check the available input options type:

    `python aero_wrapper.py --help`

To run the aero wrapper use e.g. the following command:

    `mpirun -np <number of procs> python aero_wrapper.py --V <V1 V2 V3> --tsrlist <TSR1 TSR2 TSR3>`

:warning: some parameters (turbine data, file names, etc.) are currently hardcoded, see the first sections in `aero_wrapper.py`.