
import argparse
import sys
import os
import numpy as np

import openturbinecode.utils.io as io
import openturbinecode.utils.utilities as ut
import openturbinecode.master_GUI.GUI as GUI
import openturbinecode.sample_module.sample_script as sample
import openturbinecode.DLC_manager.dump_IECcase as DLC_manager


import openturbinecode.aerodynamics.aerodynamics_module as aero
# import openturbinecode.structure.structure_module as struc
import openturbinecode.aerostructural.aerostructural_module as aerostruct
import openturbinecode.controls.control_module as ctrl
import openturbinecode.geometry.geometry_module as geom
# ...

class OpenTurbineCoDe:

    def __init__(self, args):
        print('Hello, this is OpenTurbineCoDe.')

        # --- initialization of global constants/options ---
        self.path_to_root = os.path.dirname( os.path.dirname( os.path.realpath(__file__) ))
        self.turbine_schema = self.path_to_root + os.sep + "models" + os.sep + 'defaults' + os.sep + "OTCD_schema.yaml"
        self.model_schema = self.path_to_root + os.sep + "models" + os.sep + 'defaults' + os.sep + "modeling_schema.yaml"
        # self.run_schema = self.path_to_root #TODO
        self.path_to_case = self.path_to_root + os.sep + "models" + os.sep + "DTU_10MW" + os.sep + "Madsen2019" + os.sep  # hack to run without specifying a module - we are not reading from yaml yet
        # self.path_to_case = os.getcwd()

        # --- parse input arguments ---
        self.parse_args(args)

        # --- managing IO / loading files if needed ---
        # parse run params (only if modeling options present)
        self.load_run_options()    

        # parse turbine_params (only if turbine data present)
        if self.turb_yaml:
            self.load_turbine_case(firstLoad = True)
        else:
            self.turb_data = {}
        
        # parse model params
        if self.model_yaml:
            self.load_modeling_options()    
        else:
            self.modeling_options = {}
            self.modeling_options["OpenTurbineCoDe"] = {}

        # --- initializing submodules ---

        self.myAero = aero.Aerodynamics(self.path_to_case, turb_data=self.turb_data,models=self.modeling_options, plotonly=args.plotonly)
        # self.myStruc = struc.Structure(self.path_to_case, turb_data=self.turb_data,models=self.modeling_options)
        self.myAeroStruct = aerostruct.Aerostructural(self.path_to_case, turb_data=self.turb_data,models=self.modeling_options)
        self.myCtrl = ctrl.Control(self.path_to_case, turb_data=self.turb_data, models=self.modeling_options)
        self.myGeom = geom.Geometry(self.path_to_case, turb_data=self.turb_data, models=self.modeling_options)
        self.printv('initilization done. \n\n')

    # ---------------- IO/PARSING FUNCTIONS --------------------------------------

    #parse parameters coming from command line execution
    def parse_args(self,args):
        self.turb_yaml  = io.arg_to_path(args,"turbine") #(args.turbine) if "turbine" in args else ""
        self.model_yaml = io.arg_to_path(args,"models") #(args.models) if "models" in args else ""
        self.run_yaml   = io.arg_to_path(args,"runoptions") #(args.runoptions) if "runoptions" in args else ""
        print(self.turb_yaml)
        if self.turb_yaml:
            self.path_to_case = os.path.dirname(self.turb_yaml) 

    #import run options under the form of a dictionary and making it available as an attribute to this object
    def load_run_options(self):
        self.run_options = io.load_yaml(self.run_yaml) #TODO: change for validate_with_defaults

        #parsing important options:
        self.verbose = True #TODO: replace this with a default schema
        if self.run_options:
            self.verbose = self.run_options["General"]["verbosity"]

        self.printv('run options loaded')

    #import turbine data under the form of a dictionary and making it available as an attribute to this object
    def load_turbine_case(self, firstLoad = False):
        self.turb_data = io.validate_with_defaults(self.turb_yaml,self.turbine_schema)

        #UPDATE EVERY CHILD 
        if not firstLoad and self.turb_data:
            self.myAero.turb_data = self.turb_data
            #...

        self.printv('turbine case loaded')

    #import modeling options under the form of a dictionary and making it available as an attribute to this object
    def load_modeling_options(self):
        self.modeling_options = io.validate_with_defaults(self.model_yaml, self.model_schema)

        #UPDATE EVERY CHILD MODULE
        #...
        
        self.printv('modeling options loaded')

    #save turbine data
    def save_turbine_case(self):
        self.turb_yaml = self.path_to_case + os.sep + os.path.basename(self.turb_yaml)
        print(self.turb_yaml)
        io.write_yaml(self.turb_data,self.turb_yaml)
        
        self.printv('turbine case saved')

    #TODO: write modeling option file

    # ---------------- UTILITY FUNCTIONS --------------------------------------
    #print function for non-essential/informative messages (wont be printed if the code is not set to verbose)
    def printv(self,str):
        if(self.verbose):
            print(str)
    
    #def printMes(self, mes):
    #    self.MessageBox.append(mes)
    #    self.cursot = self.MessageBox.textCursor()
    #    self.MessageBox.moveCursor(self.cursot.End)

    #=====  MAIN FUNCTIONS ===============================================
        
    def setPathToCase(self,path):
        self.path_to_case = path
        self.myAero.setPathToCase(path)
        # self.myStruc.setPathToCase(path)
        # self.myAeroStruct.setPathToCase(path)
        # self.myCtrl.setPathToCase(path)
        # self.myGeom.setPathToCase(path)

    def update_MainParams(self, PRated, nblade, D, HubD, HubHeight, Vin, Vout, Overhang, Tilt, Precone):
        self.turb_data["assembly"]["rated_power"] = PRated 
        self.turb_data["assembly"]["number_of_blades"] = nblade 
        self.turb_data["assembly"]["rotor_diameter"] = D 
        self.turb_data["assembly"]["hub_height"] = HubHeight 
        
        self.turb_data["components"]["hub"]["diameter"] = HubD 
        self.turb_data["components"]["hub"]["cone_angle"] = Precone 
        self.turb_data["components"]["nacelle"]["outer_shape_bem"]["overhang"] = Overhang 
        self.turb_data["components"]["nacelle"]["outer_shape_bem"]["uptilt_angle"] = Tilt 

        self.turb_data["control"]["supervisory"]["Vin"]   = Vin     
        self.turb_data["control"]["supervisory"]["Vout"]  = Vout  

    #...

    #TODO: move the definition of this function to IO?
    def update_DLCoptions(self, DLC_list, n_ws, n_seeds, TMax, Vrated):
        # check that DLC exists
        if not "DLC" in self.modeling_options["OpenTurbineCoDe"]:
            self.modeling_options["OpenTurbineCoDe"]["DLC"] = {}
            self.modeling_options["OpenTurbineCoDe"]["DLC"]["run"] = False

        self.modeling_options["OpenTurbineCoDe"]["DLC"]["DLC_list"]= DLC_list 
        self.modeling_options["OpenTurbineCoDe"]["DLC"]["n_ws"]    = n_ws     
        self.modeling_options["OpenTurbineCoDe"]["DLC"]["n_seeds"] = n_seeds  
        self.modeling_options["OpenTurbineCoDe"]["DLC"]["TMax"]    = TMax   

        self.turb_data["control"]["supervisory"]["Vrated"]         = Vrated

    def call_generateDLC(self):
        DLC_list = OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["DLC_list"]
        n_ws = OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["n_ws"]
        n_seeds = OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["n_seeds"]
        TMax = OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["TMax"]

        #TODO: pass info on Omega and pitch, to avoid NaN in test matrix (AeroDyn, Elastodyn)
        DLC_manager.generateDLC(OTCD.path_to_case, OTCD.turb_data, DLC_list, n_ws, n_seeds, TMax)



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--turbine", help="Path to the turbine case file (e.g. turbine.yaml)", type=str, default="")
    parser.add_argument("--models", help="Path to the modeling options file (e.g. modeling_options.yaml)", type=str, default="")
    parser.add_argument("--runoptions", help="Path to the run options file (e.g. run_options.yaml)", type=str, default="")
    parser.add_argument("--GUI", action='store_true', help="Run PyTurbineCoDe with the GUI")
    parser.add_argument("--plotonly", action='store_true', help="Do not compute anything")
    args = parser.parse_args()

    OTCD = OpenTurbineCoDe(args) #initialize me

    if args.GUI:
        print('Starting the GUI')
        # =========== CALL THE MASTER GUI ============
        GUI.run(OTCD)
        # ============================================
    else:
        if not OTCD.turb_yaml:
            print('You did not provide a turbine case. I will not be able to do anything. Exiting.')
            sys.exit(0)

        if not OTCD.turb_data:
            print('I did not find any data in your turbine yaml file... Exiting')
            sys.exit(0)

        #If no file, file is empty or non-existent
        if not OTCD.modeling_options or "OpenTurbineCoDe" not in OTCD.modeling_options or not OTCD.modeling_options["OpenTurbineCoDe"]:
            print('You did not provide a valid modeling option file. I don''t know what to do. Exiting.')
            sys.exit(0)

        # --- From here on, we are going to run whatever was specified in the run/modeling option files ---

        #=====  DLC GENERATION ====================================================
        if OTCD.modeling_options["OpenTurbineCoDe"]["DLC"]["run"]:
            OTCD.printv('Running the DLC generator...')
            OTCD.call_generateDLC()
            OTCD.printv('...done.')

        #=====  GEOMETRY ACTIVITIES ===============================================
        if OTCD.modeling_options["OpenTurbineCoDe"]["Geometry"]["PGL"]["writeFiles"]:
            OTCD.printv('Writing PGL files...')
            OTCD.call_writePGLinputs()
            OTCD.printv('...done.')

        #=====  MESHING ACTIVITIES ===============================================
        #aero:
        if OTCD.modeling_options["OpenTurbineCoDe"]["Meshing"]["Aero"]["PGL"]["run"]:
            OTCD.printv('Running PGL...')
            OTCD.call_generateSurfMesh()
            OTCD.printv('...done.')
        
    OTCD.printv('Done, byebye')
