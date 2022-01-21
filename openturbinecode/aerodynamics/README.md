# Aerodynamics module

This module is a python wrapper for `OpenFAST` and `ADflow`, enabling aerodynamics performance evaluation of wind turbine rotors via conventional and high-fidelity analysis respectively. Additional medium-fidelity capabilities  

The code is run via command line execution, but a demonstrative GUI is provided to familiarize the users with the tool capabilities. 

## Dependencies

## Installation

- Base Package:  
  - Python ≥ 3.6 
  - Numpy 
  - jsonschema 
  - Matplotlib 
  - scp 
- GUI 
  - PyQt5 
  - pyqtgraph 

Optional dependencies: 
  - Conventional analysis 
    - OpenFAST v2.4.0 : https://github.com/OpenFAST/openfast 
  - High-Fidelity analysis 
    - ADflow: https://github.com/mdolab/adflow  
    
## Installation

Please follow instructions in the master README.

## Usage

OpenFAST and AeroDyn can be run directly from the module. This is also true for ADflow. However, when operated from the GUI, only single processor execution is available. MPI runs for HPC architectures must be handled separately.  
For the medium fidelity level, the aerodynamic module can generate the input file for TurbineFOAM. TurbineFOAM provides an implementation of the Actuator Line Model for wind turbine simulation. The user is in charge of handling the unput file as the present framework does not support direct call to TurbineFOAM. 

### GUI

    python3 openturbinecode/aerodynamics/aerodynamics_gui.py

### Command line

An example script is available under `./examples/01_Aerodynamics_Standalone/`. To run the aero wrapper use e.g. the following command:

    mpirun -np <number of procs> python3 aero_compute_standalone.py --V <V1 V2 V3> --tsrlist <TSR1 TSR2 TSR3>

To produce the plot comparing data from all the available sources on the UAE turbine, run:

    python3 aero_compute_standalone.py --V 5. 6. 7. 8. 9. 10. 12. 15. 20. --tsrlist 7.58 6.32 5.42 4.74 4.21 3.78 3.16 2.53 1.90 --plotonly --fidelities AeroDyn OpenFAST ADflow --withEllipsys

For DTU 10MW (provided you did `cp -r ../../models/DTU_10MW/Madsen2019 case_aero_standalone`):
    python3 aero_compute_standalone.py --V 6. 8. 10. 12. --tsrlist 9.34 7.81 7.81 7.474 --configuration DTU_10MW --plotonly --withEllipsys 

:warning: some parameters (turbine data, file names, etc.) are currently hardcoded, see the first sections in `aero_wrapper.py` and `aero_compute_standalone.py`.