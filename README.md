# Open Turbine Co-Design


## Installation / Configuration

Make sure you `pip installed` the following dependencies:
- numpy
- mpi4py

Adapt `config.json` to specify the path to your OpenFAST executable.
:warning: we currently only support OpenFAST v2.4.

To install this package, run 
```
pip3 install -e .
```


## TODO
 - [ ] license
 - [ ] include dependencies in `setup.py`
 - [ ] consider using git lfs for managing cgns files

## Models
This folder gathers a collection of test cases for the ARPA-E Atlantis project on Open Turbine control Co-Design (originally part of OpenTurbineTestCases).

Folders are organized as follows:
- level 0: reference turbine
- level 1: variants
- level 2: solver/level of fidelity
- level 3+: all *input* files/folders required to run the test cases

This repository does *not* contain the main pieces of software for the coupled optimization and for the control co-design loop.

## Aerodynamics wrapper

The draft wrapper currently available iteratively runs ADflow and OpenFAST (v2.4) scripts over a set of tsr for a fixed inflow velocity, and returns a plot of Cp over tsr.
To check the available input options type:

    python aero_wrapper.py --help

### Usage

To run the aero wrapper use e.g. the following command:

    mpirun -np <number of procs> python aero_compute_standalone.py --V <V1 V2 V3> --tsrlist <TSR1 TSR2 TSR3>

To produce the plot comparing data from all the available sources on the UAE turbine, run:

    python3 aero_compute_standalone.py --V 5. 6. 7. 8. 9. 10. 12. 15. 20. --tsrlist 7.58 6.32 5.42 4.74 4.21 3.78 3.16 2.53 1.90 --plotonly --fidelities AeroDyn OpenFAST ADflow --withEllipsys

For DTU 10MW:
    python3 aero_compute_standalone.py --V 6. 8. 10. 12. --tsrlist 9.34 7.81 7.81 7.474 --configuration DTU_10MW --variant=Madsen2019 --plotonly --withEllipsys 

:warning: some parameters (turbine data, file names, etc.) are currently hardcoded, see the first sections in `aero_wrapper.py`.