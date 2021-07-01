
import argparse
import sys
import os
import numpy as np

import openturbinecode.meshing.surf_mesher_PGL as pgl
import openturbinecode.utils.io as io
import openturbinecode.utils.utilities as ut
import openturbinecode.master_GUI.GUI as GUI
import openturbinecode.sample_module.sample_script as sample

class OpenTurbineCoDe:

    def __init__(self, args):
        print('Hello, this is OpenTurbineCoDe.')

        # initializatio nof global constants/options
        self.path_to_root = os.path.dirname( os.path.dirname( os.path.realpath(__file__) ))
        self.turbine_schema = self.path_to_root + os.sep + "models" + os.sep + 'defaults' + os.sep + "OTCD_schema.yaml"
        # self.model_schema = self.path_to_root #TODO
        # self.run_schema = self.path_to_root #TODO
        self.path_to_case = ""

        # parse input arguments
        self.parse_args(args)

        # parse run params
        self.load_run_options()    

        # parse turbine_params (only if turbine data present)
        if self.turb_yaml:
            self.load_turbine_case()
        
        # parse model params
        self.load_modeling_options()    

        self.printv('initilization done')

    # ---------------- IO/PARSING FUNCTIONS --------------------------------------
    #parse parameters coming from command line execution
    def parse_args(self,args):
        self.turb_yaml = (args.turbine) if "turbine" in args else ""
        self.model_yaml = (args.models) if "models" in args else ""
        self.run_yaml = (args.runoptions) if "runoptions" in args else ""

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
    def load_turbine_case(self):
        self.turb_data = io.validate_with_defaults(self.turb_yaml,self.turbine_schema)

        self.printv('turbine case loaded')

    #import modeling options under the form of a dictionary and making it available as an attribute to this object
    def load_modeling_options(self):
        self.modeling_options = io.load_yaml(self.model_yaml) #TODO: change for validate_with_defaults

        self.printv('modeling options loaded')

    # ---------------- UTILITY FUNCTIONS --------------------------------------
    #print function for non-essential/informative messages (wont be printed if the code is not set to verbose)
    def printv(self,str):
        if(self.verbose):
            print(str)



    #=====  MAIN FUNCTIONS ===============================================
        
    #...

    #=====  GEOMETRY FUNCTIONS ===============================================
    
    #...

    #=====  MESHING FUNCTIONS ===============================================
    #write all the geometry files required by PGL, from global turbine data 
    def call_writePGLinputs(self):
        planform_file = self.modeling_options["OpenTurbineCoDe"]["Meshing"]["Aero"]["PGL"]["planform_file"]
        pgl.writePGLinputs(self.turb_data, self.path_to_case, planform_file)
    
    #generate and write aerodynamic surface mesh with PGL
    def call_generateSurfMesh(self):
        R = self.turb_data["assembly"]["rotor_diameter"] / 2.
        R0 = self.turb_data["components"]["hub"]["diameter"] / 2.
        
        #determine the blending parameter, basically corresponding to the relative thickness of each airfoil
        
        afs = self.turb_data["airfoils"]
        blend_var = np.zeros(len(afs))
        airfoil_list = []
        i = 0
        for af in afs:
            blend_var[i] = af["relative_thickness"]
            airfoil_list.append(af["name"])
            i+=1
            
        print(airfoil_list)
        print(blend_var)

        #Call the function:
        mesh_file = self.modeling_options["OpenTurbineCoDe"]["Meshing"]["Aero"]["PGL"]["meshName"]
        planform_file = self.modeling_options["OpenTurbineCoDe"]["Meshing"]["Aero"]["PGL"]["planform_file"]
        pgl.generateSurfMesh(R0, R, self.path_to_case, planform_file, airfoil_list, blend_var, mesh_file)


    #=====  AERODYNAMICS ===============================================
    
    #...
    # example changes that need to be merged.

    #=====  STRUCTURE ===============================================
    
    #...

    #=====  AERO-STrUCTURE ===============================================
    
    #...

    #=====  CCD ===============================================
    
    #...

    #=====  SAMPLE MODULE ===============================================

    def sample_hello_world(self):
        print("Hello, running from " + self.path_to_root)
        sample.hello_from_sample()
        sample.new_function()



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--turbine", help="Path to the turbine case file (e.g. turbine.yaml)", type=str, default="")
    parser.add_argument("--models", help="Path to the modeling options file (e.g. modeling_options.yaml)", type=str, default="")
    parser.add_argument("--runoptions", help="Path to the run options file (e.g. run_options.yaml)", type=str, default="")
    parser.add_argument("--GUI", action='store_true', help="Run PyTurbineCoDe with the GUI")
    args = parser.parse_args()

    OTCD = OpenTurbineCoDe(args) #initialize me

    if args.GUI:
        print('Starting the GUI')
        # =========== CALL THE MASTER GUI ============
        GUI.run(OTCD)
        # ============================================
    else:
        if not OTCD.path_to_case:
            print('You did not provide a turbine case. I will not be able to do anything. Exiting.')
            sys.exit(0)

        if not OTCD.turb_data:
            print('I did not find any data in your turbine yaml file... Exiting')
            sys.exit(0)

        if not OTCD.modeling_options:
            print('You did not provide a modeling option file. I don''t know what to do. Exiting.')
            sys.exit(0)

        # --- From here on, we are going to run whatever was specified in the run/modeling option files ---

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
    