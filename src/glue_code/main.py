
import argparse
import os
import sys

import utils.io as io

class OpenTurbineCoDe:

    def __init__(self, args):
        print('Hello, this is OpenTurbineCoDe.')

        # global constants
        self.path_to_root = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) )))
        self.turbine_schema = self.path_to_root + os.sep + "models" + os.sep + 'defaults' + os.sep + "OTCD_schema.yaml"
        # self.model_schema = self.path_to_root #TODO
        # self.run_schema = self.path_to_root #TODO
        self.path_to_case = ""

        # parse input arguments
        self.parse_args(args)

        # run params
        self.load_run_options()    

        # turbine_params (only if turbine data present)
        if self.turb_yaml:
            self.load_turbine_case()
        
        # model params
        self.load_modeling_options()    

        self.printv('initilization done')


    def parse_args(self,args):
        self.turb_yaml = args.turbine if "turbine" in args else ""
        self.model_yaml = args.models if "models" in args else ""
        self.run_yaml = args.runoptions if "runoptions" in args else ""
        
        if self.turb_yaml:
            self.path_to_case = os.path.dirname(self.turb_yaml)

    def load_run_options(self):
        self.run_options = io.load_yaml(self.run_yaml) #TODO: change for validate_with_defaults

        #parsing important options:
        self.verbose = self.run_options["General"]["verbosity"]

        self.printv('run options loaded')

    def load_turbine_case(self):
        self.turb_data = io.validate_with_defaults(self.turb_yaml,self.turbine_schema)
        self.printv('turbine case loaded')

    def load_modeling_options(self):
        self.modeling_options = io.load_yaml(self.model_yaml) #TODO: change for validate_with_defaults
        self.printv('modeling options loaded')

    def printv(self,str):
        if(self.verbose):
            print(str)

if __name__ == '__main__':
    

    parser = argparse.ArgumentParser()
    parser.add_argument("--turbine", help="Path to the turbine case file (e.g. turbine.yaml)", type=str, default="")
    parser.add_argument("--models", help="Path to the modeling options file (e.g. modeling_options.yaml)", type=str, default="")
    parser.add_argument("--runoptions", help="Path to the run options file (e.g. run_options.yaml)", type=str, default="")
    parser.add_argument("--GUI", action='store_true', help="Run PyTurbineCoDe with the GUI")
    args = parser.parse_args()

    OTCD = OpenTurbineCoDe(args) #initialize me

    #do some arg parsing:
    if args.GUI:
        print('Starting the GUI')
        ##something like:
        #start_gui(OTCD)
    else:
        if not OTCD.path_to_case:
            print('You did not provide a turbine case. I will not be able to do anything. Exiting.')
            sys.exit(0)

        #... do something, depending on what was sepcified in turbine, run, and modeling options
        

    OTCD.printv('Done, byebye')
    