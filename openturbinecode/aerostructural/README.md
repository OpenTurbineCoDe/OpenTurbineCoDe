# Aerostructural module

This module is a python wrapper for `OpenFAST` and `MACH` frameworks, enabling aerostructural performance evaluation of wind turbine rotors via conventional and high-fidelity analysis respectively. MACH-based aerostructural optimization is also available. 

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
    - MACH-Aero : https://github.com/mdolab/MACH-Aero
    - TACS/pyTACS : https://github.com/mdolab/pyTACS
    - PyAeroStructure : https://github.com/mdolab/PyAeroStructure
    
## Installation

Please follow instructions in the master README.

## Usage

We provide example input files for the DTU 10MW configuration in the `/models` subfolder of OTCD.  


### Pre-processing 
Following the example scripts provided with the code, the user needs to provide a full set of yaml files for design case definition, `OpenFAST` input files, and ffd, cgns, and bdf meshes for high-fidelity.
The correct file location must be provided as input – the scripts default to the example file location.

### Execution 

Users have two options: 

- Use the GUI interface to select high level parameters and run analyses (both fidelities) or optimization (High-fidelity). From the root folder, run: 

	  python openturbinecode/aerostructural_gui.py 

  Note that the GUI-based runs can only run on a single processor.

- Run directly the main script 
  
      mpirun -np <selected-proc-#> python openturbinecode/aerostructural/aerostructural_module.py 

  Refer to inline comments and helper for options and tuning details 

### Post-processing 

The code provides base functionality to post-produce performance metrics of single analysis and optimization, or parametric sweeps.
Users can access the output files directly.
High-fidelity solution files can be loaded and processed using Tecplot or Paraview software.
Optimization trends can be visualized using `pyOptSparse`’s `OptView` tool.


