# Open Turbine Co-Design


## Installation / Configuration

Make sure you `pip installed` the following dependencies:
- numpy
- mpi4py
- ...

If `openfast` and `aerodyn` are not already in your path, you may adapt `config.json` to specify the path to your executables. They are usualy located respectively under `/path/to/openfast/build/glue-codes/openfast/openfast` and `/path/to/openfast/build/modules/aerodyn/aerodyn_driver`.
:warning: we currently only support OpenFAST v2.4.

To install this package, run 
```
pip3 install -e .
```


## TODO
 - [ ] license
 - [ ] include dependencies in `setup.py`
 - [ ] consider using git lfs for managing cgns files

## Developer guidelines

*What follows is just a proposition for arranging the entire code, data structures, workflows.*

### Case management, data handling, 
Every time the user will want to start a project, a case study, etc. we suggest that he starts from one of the examples given in the `models` folder. He should create a working copy of an entire model at a location of his choice, e.g. doing 
 
    cp -r ./models/DTU_10MW/Madsen2019  /path/to/case

From there, all the actions performed from OpenTurbineCoDe will either modify or create new files in the file-tree under /path/to/case. For example, we can imagine that we generate the case files for an OpenFOAM run in some sub-folder there. Having everyting centralized in a single, well-organized folder will allow us for example to sync the entire file-tree between a local machine and a cluster, so that some of the computationally expensive operations are performed on HPC and results are then synced back.

### Code architecture

The `OpenTurbineCoDe` class is defined in `src/glue_code`. This is where we define functions to call the various modules: every single module should expose a number of functions that can be called to perform actions, e.g. from the GUI. The handling of the case files (potentially including turbine data, simulations parameters, etc.) also goes in the `OpenTurbineCoDe` class. The idea is that we can run the main script of `OpenTurbineCoDe` either from the command line, or use it to start the GUI. In GUI mode, the actions triggered from the UI elements should call functions of the `OpenTurbineCoDe` class, which then in turn call functions in other modules. This way, we centralize all the GUI related stuff in the `master_GUI` folder. 

See an work-in-progress example for the geometry module in the `dev/meshing` branch.

## Models
This folder gathers a collection of test cases for the ARPA-E Atlantis project on Open Turbine control Co-Design (originally part of OpenTurbineTestCases).

Folders are organized as follows:
- level 0: reference turbine
- level 1: variants
- level 2: solver/level of fidelity
- level 3+: all *input* files/folders required to run the test cases

This repository does *not* contain the main pieces of software for the coupled optimization and for the control co-design loop.

## Aerodynamics wrapper

The aerodynamic standalone wrapper runs ADflow, OpenFAST (v2.4) and/or AeroDyn over a set of tsr and inflow velocities, and returns a plot of Cp over tsr. To use it, first 

    cd ./examples/01_Aerodynamics_Standalone/

To check the available input options type:

    python3 aero_compute_standalone.py --help

Before running anything, you need to define a case folder. We recommend starting from one of those provided in `./models`:

    cp -r ../../models/NREL_PhaseVI_UAE/original case_aero_standalone

### Usage

To run the aero wrapper use e.g. the following command:

    mpirun -np <number of procs> python3 aero_compute_standalone.py --V <V1 V2 V3> --tsrlist <TSR1 TSR2 TSR3>

To produce the plot comparing data from all the available sources on the UAE turbine, run:

    python3 aero_compute_standalone.py --V 5. 6. 7. 8. 9. 10. 12. 15. 20. --tsrlist 7.58 6.32 5.42 4.74 4.21 3.78 3.16 2.53 1.90 --plotonly --fidelities AeroDyn OpenFAST ADflow --withEllipsys

For DTU 10MW (provided you did `cp -r ../../models/DTU_10MW/Madsen2019 case_aero_standalone`):
    python3 aero_compute_standalone.py --V 6. 8. 10. 12. --tsrlist 9.34 7.81 7.81 7.474 --configuration DTU_10MW --plotonly --withEllipsys 

:warning: some parameters (turbine data, file names, etc.) are currently hardcoded, see the first sections in `aero_wrapper.py` and `aero_compute_standalone.py`.