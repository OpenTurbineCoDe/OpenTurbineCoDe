# Open Turbine Control co-Design

This is a repository for the Open Turbine Control co-Design code.
*This software is in BETA version.*
 
The Master framework provides:  
1) a library of models and examples,  
2) a GUI with capabilities of  
    -  top-level pre-processing,   
    -  simple analysis and optimization execution, 
    -  top-level post-processing, 
    -  case data display, comparison, storage and recall. 

The purpose of the GUI is to familiarize the user with basic functionalities explored in the Open Turbine Control co-Design project (https://arpa-e.energy.gov/technologies/projects/computationally-efficient-control-co-design-optimization-framework-mixed). However, it does **NOT** provide access to the entire set of functionalities and code developed during the project, which rely on dedicated user scripts. The examples provided in this repository merely constitute an introduction to more complex case studies. One of the main limitations to the use of the GUI is that it is currently not compatible with MPI, nor with HPC architectures. However, it is still possible to run separate case with MPI on HPC, and then plot the results with the GUI. 

Please refer to the documentation of each module for more details.

<!-- ------------------------------------------------------------------------------ -->
## TODO
 - [ ] license
 - [ ] see most recent PR for additional TODO items

<!-- ------------------------------------------------------------------------------ -->

## Installation / Configuration

This software was tested under unix and windows environments. 

### Dependencies

Make sure you `pip installed` the following dependencies:
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
    - Geometry 
    - BB3D : https://github.com/smbarr/BB3D 
    - Salome : https://salome-platform.org/downloads/current-version  
    - PGL : https://gitlab.windenergy.dtu.dk/frza/PGL  
  - High-Fidelity analysis 
    - ADflow: https://github.com/mdolab/adflow  
    - MACH-Aero : https://github.com/mdolab/MACH-Aero  
    - TACS/pyTACS: https://github.com/mdolab/pytacs 
    - PyAeroStructure: https://github.com/mdolab/pyaerostructure  
  - Controls 
    - pandas 
    - ROSCO_toolbox (through WEIS, see below) 
    - PCrunch (through WEIS, see below)
  - DLC generation 
    - AeroelasticSE (through WEIS, see below) 

This wrapper code was made tolerant to missing optional dependencies. This means that you may install only the optional dependencies that you need. For example, if you aim to run low-fidelity aerodynamic analysis, OpenFAST should be sufficient. Please refer to the documentation of each module to determine your needs. Please follow the instructions provided by the external dependencies to install them.

If `OpenFAST` and `AeroDyn` are not already in your path, you may adapt `openturbinecode/config.json` to specify the path to your executables. They are usually located respectively under `/path/to/openfast/build/glue-codes/openfast/openfast` and `/path/to/openfast/build/modules/aerodyn/aerodyn_driver`.
:warning: we currently only support OpenFAST v2.4.

Some of the optional dependencies are distributed through WEIS. We recommend using the guidelines provided in WEIS documentation for the full install. However, since only some parts of WEIS are necessary, a light install should be sufficient. After having downloaded the WEIS sources from https://github.com/WISDEM/WEIS, proceed with:
```
export PYTHONPATH=$PYTHONPATH:/path/to/WEIS
cd /path/to/WEIS/ROSCO_toolbox
python3 install -e .
cd /path/to/WEIS/pCrunch
python3 install -e .
```
Some dependencies of `AeroelasticSE` might need to be installed manually, e.g. `ruamel_yaml`.

### Installation

We recommend in-place installation (`-e`). To install this package, run 
```
pip3 install -e .
```

If you want to ensure you have all the requirements for a specific application, you can install with the following command: 
```
pip3 install -e .[gui, high-fidelity, meshing, controls] 
```
where you can select only what you need from the list in the brackets. This should at least ensure that the python dependencies are installed. 

<!-- ------------------------------------------------------------------------------ -->

## Quick start guide

**To run the master GUI**, from the root of the folder, execute

    python3 openturbinecode/main.py --GUI

The GUI should pop up. There are other ways to run the main function without the GUI. For example, you can start the GUI and load turbine data at the same time:

    python3 openturbinecode/main.py --GUI --turbine ./models/DTU_10MW/Madsen2019/Madsen2019_10.yaml 

The turbine file must follow the WindIO onthology format. Examples are provided in the `/models` subfolder. 

**To run any standalone GUI**, from the root of the folder, execute (*replace MODULE with the specific module you want):

python3 openturbinecode/MODULE/MODULE_gui.py 

## Models
This folder gathers a collection of test cases for the ARPA-E Atlantis project on Open Turbine control Co-Design (originally part of OpenTurbineTestCases).

Folders are organized as follows:
- level 0: reference turbine
- level 1: variants
- level 2: solver/level of fidelity
- level 3+: all *input* files/folders required to run the test cases

We invite the user to copy the example folder in a working location before starting experimenting with the code.

<!-- ------------------------------------------------------------------------------ -->

## Examples

### Aerodynamics wrapper

The aerodynamic standalone wrapper runs ADflow, OpenFAST (v2.4) and/or AeroDyn over a set of tsr and inflow velocities, and returns a plot of Cp over tsr. To use it in command line, first 

    cd ./examples/01_Aerodynamics_Standalone/

To check the available input options type:

    python3 aero_compute_standalone.py --help

Before running anything, you need to define a case folder. We recommend starting from one of those provided in `./models`:

    cp -r ../../models/NREL_PhaseVI_UAE/original case_aero_standalone

Recall that you can also call the related GUI by running

    python3 openturbinecode/aerodynamics/aerodynamics_gui.py  

from the OTCD root folder.

### Mesh Generation

This is just a demo of how the framework can be used to call functions of different modules.

To run the example in command line, do:

    cd ./examples/02_Mesh_Generation_PGL
    python3 ../../openturbinecode/main.py --runoptions ./run_options.yaml --turbine ./Madsen2019_10.yaml --models ./modeling_options.yaml

It should generate the PGL geometry files and the surface mesh. Options for the operations to perform are passed through the `run_options.yaml` file.

You can also call the GUI by running

    python3 openturbinecode/geometry/geometry_gui.py 

from the OTCD root folder.


### DLC generation (DEMO)

You can generate DLC files im command line:

    cd ./examples/03_DLC_Generation
    python3 ../../openturbinecode/main.py --runoptions ./run_options.yaml --turbine ./Madsen2019_10.yaml --models ./modeling_options.yaml

Options for the operations to perform are passed through the `run_options.yaml` file.

You can also generate DLC from the master GUI. For example, still from the example folder, run

    python3 ../../openturbinecode/main.py --GUI --turbine ./Madsen2019_10.yaml --models ./modeling_options.yaml

From the main panel, jump to the DLC tab. Adjust the parameters there as needed, and hit `generate DLCs`.

<!-- ------------------------------------------------------------------------------ -->

## User guidelines
### Case management, data handling, 
Every time the user will want to start a project, a case study, etc. we suggest that he starts from one of the examples given in the `models` folder. He should create a working copy of an entire model at a location of his choice, e.g. doing 
 
    cp -r ./models/DTU_10MW/Madsen2019  /path/to/case

At a later stage in this project, we might provide the ability to perform that operation automatically from the GUI.

From there, all the actions performed from OpenTurbineCoDe will either modify or create new files in the file-tree under /path/to/case. For example, we can imagine that we generate the case files for an OpenFOAM run in some sub-folder there. Having everything centralized in a single, well-organized folder will allow us for example to sync the entire file-tree between a local machine and a cluster, so that some of the computationally expensive operations are performed on HPC and results are then synced back.

<!-- ------------------------------------------------------------------------------ -->
## Developers guidelines
### Code philosophy

We work with a "parent-child" organization. There is a single, overarching entity that controls the entire execution of the code, that is, the `main` file of OpenTurbineCoDe. The code in there is in charge of interpreting user commands and data (either provided in command line or through a GUI) and then, from this information, call the relevant submodule functions. One big advantage of this approach is the following: we intend to be able to execute the exact same code either on a local computer, or on a supercomputer. For instance, a user can pull up the GUI on his local computer, generate some geometry files and set up and save a case; them, he can take the exact same file architecture to a supercomputer and execute the same code without the GUI in order to produce the results he asked for in the case file. This way, we ensure portability and maintainability.

The `main` routine, also called *backend* or simply *framework*, defines a python class. This means that we can create objects of the type `OpenTurbineCoDe`. The object will have attribute variables, mostly related to main/common parameters that we want to be able to pass to every module: the path to the executed case, the level of fidelity, etc. Most likely also, it should also have a complete definition of a given turbine, potentially under the form of a dictionary (*see utils/IO, and mechanisms to load/save turbine data, even though this is currently still in development*). 

Importantly, we also define functions associated with the `OpenTurbineCoDe` object. These are really the entry point to any other functionality of the framework. For any action that the developer's want to expose to the user, there should be an associated function in the `main`. This way, we ensure to centralize all the feature of the framework at a single place. However, the function in `main` should call specific functions of the submodules.

Another important aspect is the independency of the sub-modules. Let's take an example to illustrate this. The aerodynamic module (either low or high-fidelity) requires input files from other modules: global parameters, DLC definition, geometry module and potentially meshing module. We however want to make sure that the aerodynamic module can actually run in a _standalone_ fashion, meaning that it does not require that the other above-mentioned module be executed beforehand. To do this, we always leave the possibility to the user to specify a set of files that correspond to the output of these other modules. So the user should be able to choose if he wants to provide his own **external** files (meshes, DLC generated wind, aerodyn files, etc.), or to use **internal** files (i.e. those generated previously). 

### User interaction with the code

As mentioned previously, we intend for the user to be able to run `OpenTurbineCoDe` with or without GUI.
The master GUI is a specific submodule that deserves attention. 
For clarity and maintainability, we want to separate as much as possible the GUI-related handling (graphical representations, buttons, bars, menus, etc.) and the actual code executing actions. This is also part of the reason why we define a `main`. 
For instance, you can think of the functions defined in `main` as the action that the code need to do when you hit a specific button (e.g., write a set of files, run a solver, etc.). In practice, the script of the GUI will call the related function when the use hits the button, and that will trigger the action.

### Code architecture

The `OpenTurbineCoDe` class is defined in `openturbinecode/main.py`. This is where we define functions to call the various modules: every single module should expose a number of functions that can be called to perform actions, e.g. from the `main`. The handling of the case files (potentially including turbine data, simulations parameters, etc.) also goes in the `OpenTurbineCoDe` class. 
All other sub-modules have dedicated sub-folders under `openturbinecode`. Feel free to create new ones if you need.
Again, the idea is that we can run the main script of `OpenTurbineCoDe` either from the command line, or use it to start the GUI. In GUI mode, the actions triggered from the UI elements should call functions of the `OpenTurbineCoDe` class, which then in turn call functions in other modules. This way, we centralize all the GUI-related stuff in the `master_GUI` folder. 

See an work-in-progress example for the geometry module in the `master` branch.

### IO management

*This part is still under reflection, but we propose a vision here. It is partially inspired from NREL standards, and how reference tools such as WISDEM operate.*

It is possible to manage all data required to run OpenTurbineCoDe, and control the execution, with data/control files. We plan to work with 3 different types of files:
- turbine data files: collects all information pertaining to the definition of the turbine
- modeling option files AND run option files: specifies main/global options, and controls what needs to be done from the main - they basically are equivalent to and replace the GUI when `OpenTurbineCoDe` is run in command line (i.e., 
from a super-computer).

### Misc features

The `OpenTurbineCoDe` class defines its own `print` function. Please use it to display informative, non-essential messages. They will be shown in terminal if the code is set to be verbose. All critical messages (warnings/errors) should however use std/err print functions.

<!-- ------------------------------------------------------------------------------ -->

## Specific guidelines for development

### GUI

**Editing the UI file** requires the QTDesigner app.

**Naming conventions**: When designing the UI with Qt tools, be very careful to **give a name** to every graphical object you create. For instance, if you add a line object, it will automatically be named something like `lineEdit_XX`. Please change this to a name meaningful to your module, e.g. `struct_line_YoungModulus`. This is to make sure that, when we develop the UI in parallel, there will be no duplicates in the named objects.

### Single modules

**Dependencies**: specific external python modules should ideally not be hard requirements. Ideally, the code should be able to run a specific module with only the related dependencies, and without the dependencies of all the other modules. This means that we guarantee standalone execution of each module. 
For example, to run the low-fidelity aerodynamics, I don't need to have `adflow` installed. See how this is managed at the top of `Wrapped_hifi_Analysis.py`. If you need to add external dependencies, please also amend the `./openturbinecode/setup.py` file so that the user gets a warning on all the modules he needs to install.

<!-- ------------------------------------------------------------------------------ -->

