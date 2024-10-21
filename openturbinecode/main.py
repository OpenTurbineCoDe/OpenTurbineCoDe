"""
    There may be a message "Using weis.aeroelasticse in ROSCO_toolbox..."
    This is not an error message and comes from WEIS/ROSCO/ROSCO_toolbox/turbine.py
    Associated message: Warning - The following packages/executables are not found:
    ['pCrunch', 'pyFAST', 'adflow', 'pgl', 'TACS/pyTACS', 'pygeo', 'AeroelasticSE', 'pimpleFoam']
"""

import argparse
import sys
import os
import logging
from pathlib import Path

from openturbinecode.utils.logger import setup_logger
import openturbinecode.utils.io as io
import openturbinecode.master_GUI.GUI as GUI
import openturbinecode.DLC_manager.dump_IECcase as DLC_manager
import openturbinecode.aerodynamics.aerodynamics_module as aero
import openturbinecode.structure.structure_module as struc
import openturbinecode.aerostructural.aerostructural_module as aerostruct
import openturbinecode.controls.control_module as ctrl
import openturbinecode.geometry.geometry_module as geom

log = setup_logger('root', 'logs/app.log', level=logging.INFO)


class OpenTurbineCoDe:
    def __init__(self, args):
        log.info('Initializing OpenTurbineCoDe...')

        # Initialize paths
        self.path_to_root = Path(__file__).resolve().parent.parent  # OpenTurbineCoDe path
        self.turbine_schema = self.path_to_root / "models" / "defaults" / "OTCD_schema.yaml"
        self.model_schema = self.path_to_root / "models" / "defaults" / "modeling_schema.yaml"
        self.path_to_case = self.path_to_root / "models" / "DTU_10MW" / "Madsen2019"  # Default path to case

        # Parse input arguments
        self.parse_args(args)

        # Load turbine case
        self.load_run_options()

        # Parse turbine parameters
        if self.turb_yaml:
            self.load_turbine_case(firstLoad=True)
        else:
            self.turb_data = {}

        # Parse model parameters if present
        if self.model_yaml:
            self.load_modeling_options()
        else:
            self.modeling_options = {}
            self.modeling_options["OpenTurbineCoDe"] = {}

        # Initialize submodules
        self.initialize_submodules()
        log.info('OpenTurbineCoDe initialization complete.')

    def initialize_submodules(self):
        """Initializes all submodules of OpenTurbineCoDe.
        """
        # Initialize submodules
        self.aero_module = aero.Aerodynamics(self.path_to_case, turb_data=self.turb_data, models=self.modeling_options)
        self.struct_module = struc.Structural(self.path_to_case, turb_data=self.turb_data, models=self.modeling_options)
        self.aero_struct_module = aerostruct.Aerostructural(self.path_to_case, turb_data=self.turb_data, models=self.modeling_options)  # noqa: E501
        self.control_module = ctrl.Control(self.path_to_case, turb_data=self.turb_data, models=self.modeling_options)
        self.geometry_module = geom.Geometry(self.path_to_case, turb_data=self.turb_data, models=self.modeling_options)

    # parse parameters coming from command line execution
    def parse_args(self, args):
        """
        Parses command-line arguments to extract file paths for turbine, models, and run options.
            args (Namespace): The command-line arguments.
        Attributes:
            turb_yaml (str): Path to the turbine file.
            model_yaml (str): Path to the models file.
            run_yaml (str): Path to the run options file.
            path_to_case (str): Directory path of the turbine file.
        Notes:
            OTCD.turb_yaml is the argument that the user input after --turbine .
            This should be the path to the turbine file, with a appended to the front if it wasn't there already.
            Same deal for OTCD.model_yaml for --models and OTCD.run_yaml for --runoptions.
        """
        # Parse command-line arguments
        self.turb_yaml = io.arg_to_path(args, "turbine")
        self.model_yaml = io.arg_to_path(args, "models")
        self.run_yaml = io.arg_to_path(args, "runoptions")

        log.info(self.turb_yaml)

        if self.turb_yaml:
            self.path_to_case = os.path.dirname(self.turb_yaml)

    # import run options under the form of a dictionary and making it available as an attribute to this object
    def load_run_options(self):
        self.run_options = io.load_yaml(self.run_yaml)

        self.verbose = True
        if self.run_options:
            self.verbose = self.run_options["General"]["verbosity"]

        log.info('Run options loaded.')

    # import turbine data under the form of a dictionary and making it available as an attribute to this object
    def load_turbine_case(self, firstLoad=False):
        self.turb_data = io.validate_with_defaults(self.turb_yaml, self.turbine_schema)

        # UPDATE EVERY CHILD MODULE
        if not firstLoad and self.turb_data:
            # Note: we don't call reload_turbdata from each module because it is safer here with validate_with_defaults
            self.aero_module.turb_data = self.turb_data
            self.struct_module.turb_data = self.turb_data
            self.aero_struct_module.turb_data = self.turb_data
            self.geometry_module.set_turbdata(self.turb_data)
            self.control_module.turb_data = self.turb_data

        log.info('Turbine case loaded.')
        # Runs either when you input a turbine file as an argument or when you load a turbine case in the GUI.

    # import modeling options under the form of a dictionary and making it available as an attribute to this object
    def load_modeling_options(self):
        self.modeling_options = io.validate_with_defaults(self.model_yaml, self.model_schema)

        log.info('Modeling options loaded.')

    def save_turbine_case(self):
        self.turb_yaml = self.path_to_case + os.sep + os.path.basename(self.turb_yaml)
        print(self.turb_yaml)
        io.write_yaml(self.turb_data, self.turb_yaml)

        log.info('Turbine case saved.')

    def setPathToCase(self, path):
        self.path_to_case = path
        self.aero_module.setPathToCase(path)
        self.struct_module.setPathToCase(path)
        self.aero_struct_module.setPathToCase(path)
        self.control_module.setPathToCase(path)
        self.geometry_module.setPathToCase(path)
        # Defines the path in all submodules. Called in GUI.py.

    def update_MainParams(self, PRated, nblade, D, HubD, HubHeight, Vin, Vout, Overhang, Tilt, Precone):
        self.turb_data["assembly"]["rated_power"] = PRated
        self.turb_data["assembly"]["number_of_blades"] = nblade
        self.turb_data["assembly"]["rotor_diameter"] = D
        self.turb_data["assembly"]["hub_height"] = HubHeight

        self.turb_data["components"]["hub"]["diameter"] = HubD
        self.turb_data["components"]["hub"]["cone_angle"] = Precone
        self.turb_data["components"]["nacelle"]["outer_shape_bem"]["overhang"] = Overhang
        self.turb_data["components"]["nacelle"]["outer_shape_bem"]["uptilt_angle"] = Tilt

        self.turb_data["control"]["supervisory"]["Vin"] = Vin
        self.turb_data["control"]["supervisory"]["Vout"] = Vout
        # Updates turbine data from what was in the turbine.yaml file. Called in GUI.py.

    # Move the definition of this function to IO?
    def update_DLCoptions(self, DLC_list, n_ws, n_seeds, TMax, Vrated):
        # check that DLC exists
        if "DLC" not in self.modeling_options["OpenTurbineCoDe"]:
            self.modeling_options["OpenTurbineCoDe"]["DLC"] = {}
            self.modeling_options["OpenTurbineCoDe"]["DLC"]["run"] = False

        self.modeling_options["OpenTurbineCoDe"]["DLC"]["DLC_list"] = DLC_list
        self.modeling_options["OpenTurbineCoDe"]["DLC"]["n_ws"] = n_ws
        self.modeling_options["OpenTurbineCoDe"]["DLC"]["n_seeds"] = n_seeds
        self.modeling_options["OpenTurbineCoDe"]["DLC"]["TMax"] = TMax

        self.turb_data["control"]["supervisory"]["Vrated"] = Vrated
        # Updates DLCs from what was in the model.yaml file. Called in GUI.py after you click Generate DLC.    TG

    def call_generateDLC(self):
        DLC_list = OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["DLC_list"]
        n_ws = OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["n_ws"]
        n_seeds = OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["n_seeds"]
        TMax = OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["TMax"]

        # Pass info on Omega and pitch, to avoid NaN in test matrix (AeroDyn, Elastodyn)
        DLC_manager.generateDLC(OTCD.path_to_case, OTCD.turb_data, DLC_list, n_ws, n_seeds, TMax)
        # Updates DLCs based on the information from the update_DLCoptions function.
        # Called in GUI.py after you click Generate DLC.


if __name__ == '__main__':
    # Runs if the main.py file was run directly in the command line and not called by another program.
    parser = argparse.ArgumentParser()
    parser.add_argument("--turbine", help="Path to the turbine case file (e.g. turbine.yaml)", type=str, default="")
    parser.add_argument("--models", help="Path to the modeling options file (e.g. modeling_options.yaml)", type=str, default="")  # noqa: E501
    parser.add_argument("--runoptions", help="Path to the run options file (e.g. run_options.yaml)", type=str, default="")  # noqa: E501

    # These three arguments allow the user to type in the path to a file
    # after typing in --turbine , --models , or --runoptions.
    parser.add_argument("--GUI", action='store_true', help="Run PyTurbineCoDe with the GUI")
    parser.add_argument("--plotonly", action='store_true', help="Do not compute anything")

    # These two arguments check whether the user input --GUI or --plotonly
    args = parser.parse_args()

    # Initialize the OpenTurbineCoDe object
    OTCD = OpenTurbineCoDe(args)

    if args.GUI:
        # If the user input --GUI
        log.info('Initializing GUI...')
        GUI.run(OTCD)
    else:
        if not OTCD.turb_yaml:
            log.info('You did not provide a turbine case. I will not be able to do anything. Exiting.')
            sys.exit(0)

        if not OTCD.turb_data:
            log.info('I did not find any data in your turbine yaml file. Exiting')
            sys.exit(0)

        # If no file, file is empty or non-existent
        if not OTCD.modeling_options or "OpenTurbineCoDe" not in OTCD.modeling_options or not OTCD.modeling_options["OpenTurbineCoDe"]:  # noqa: E501
            log.info('You did not provide a valid modeling option file. I don''t know what to do. Exiting.')
            sys.exit(0)

        # --- From here on, we are going to run whatever was specified in the run/modeling option files ---

        # DLC GENERATION
        if OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["run"]:
            log.info('Running the DLC generator...')
            OTCD.call_generateDLC()
            log.info('...done.')

        # GEOMETRY ACTIVITIES
        if OTCD.modeling_options["OpenTurbineCoDe"]["Geometry"]["PGL"]["writeFiles"]:
            log.info('Writing PGL files...')
            OTCD.call_writePGLinputs()
            # Should this be geom.Geometry.call_writePGLinputs() ? This function is not defined in OTCD.
            log.info('...done.')

        # MESHING ACTIVITIES
        # aero:
        if OTCD.modeling_options["OpenTurbineCoDe"]["Meshing"]["Aero"]["PGL"]["run"]:
            log.info('Running PGL...')
            OTCD.call_generateSurfMesh()
            # Should this be geom.Geometry.call_generateSurfMesh() ? This function is not defined in OTCD.
            log.info('...done.')

    log.info('Exiting.')
