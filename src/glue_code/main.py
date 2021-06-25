
import argparse
import sys
import os
import numpy as np

import utils.io as io
import meshing.surf_mesher_PGL as pgl

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

    # ---------------- IO/PARSING FUNCTIONS --------------------------------------
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

        #=========================================================================
        #temporary definition for a quick demo:
        self.turbine_data = {}
        self.turbine_data["R"] = 89.166
        self.turbine_data["R0"] = 2.8

        self.turbine_data["airfoils"] = {}
        self.turbine_data["airfoils"]["cylinder"] = {} #should further define their coordinates, etc.
        self.turbine_data["airfoils"]["cylinder"]["relative_thickness"] = 100
        self.turbine_data["airfoils"]["ffaw3241"] = {}
        self.turbine_data["airfoils"]["ffaw3241"]["relative_thickness"] = 24.1
        self.turbine_data["airfoils"]["ffaw3301"] = {}
        self.turbine_data["airfoils"]["ffaw3301"]["relative_thickness"] = 30.1
        self.turbine_data["airfoils"]["ffaw3360"] = {}
        self.turbine_data["airfoils"]["ffaw3360"]["relative_thickness"] = 36.0
        self.turbine_data["airfoils"]["ffaw3480"] = {}
        self.turbine_data["airfoils"]["ffaw3480"]["relative_thickness"] = 48.0
        self.turbine_data["airfoils"]["tc72"] = {} 
        self.turbine_data["airfoils"]["tc72"]["relative_thickness"] = 20. #??

        self.turbine_data["airfoil_position"] = {}
        self.turbine_data["airfoil_position"]["grid"] = [0.00, 0.01, 0.195, 0.242, 0.495, 0.585, 0.685, 1.000]
        self.turbine_data["airfoil_position"]["labels"] = ["cylinder", "cylinder", "ffaw3360", "ffaw3301", "ffaw3301", "ffaw3241", "ffaw3241", "tc72"]

        self.turbine_data["chord"] = {}
        self.turbine_data["chord"]["grid"] = [0.0000, 0.0176, 0.0313, 0.0420, 0.0507, 0.0579, 0.0642, 0.0700, 0.0758, 0.0821, 0.0893, 0.0980, 0.1087, 0.1224, 0.1400, 0.1610, 0.1841, 0.2093, 0.2366, 0.2660, 0.2973, 0.3305, 0.3653, 0.4015, 0.4387, 0.4766, 0.5148, 0.5529, 0.5905, 0.6273, 0.6628, 0.6969, 0.7293, 0.7597, 0.7882, 0.8145, 0.8387, 0.8608, 0.8809, 0.8990, 0.9153, 0.9299, 0.9429, 0.9544, 0.9646, 0.9736, 0.9816, 0.9885, 0.9946, 1.0000]
        self.turbine_data["chord"]["value"] = [4.6000, 4.5931, 4.5978, 4.6148, 4.6386, 4.6660, 4.6954, 4.7281, 4.7658, 4.8118, 4.8713, 4.9513, 5.0628, 5.2202, 5.4370, 5.6899, 5.9143, 6.0264, 6.0012, 5.8845, 5.7025, 5.4638, 5.1768, 4.8570, 4.5206, 4.1798, 3.8431, 3.5198, 3.2178, 2.9422, 2.6954, 2.4776, 2.2871, 2.1222, 1.9805, 1.8591, 1.7546, 1.6650, 1.5865, 1.5119, 1.4348, 1.3505, 1.2612, 1.1671, 1.0612, 0.9571, 0.8629, 0.7594, 0.5397, 0.0962]

        self.turbine_data["twist"] = {}
        self.turbine_data["twist"]["grid"] = self.turbine_data["chord"]["grid"]
        self.turbine_data["twist"]["value"] = [0.20944, 0.20949, 0.20946, 0.20937, 0.20930, 0.20928, 0.20930, 0.20940, 0.20958, 0.20982, 0.21005, 0.21007, 0.20960, 0.20748, 0.20117, 0.18658, 0.16357, 0.13858, 0.11736, 0.10226, 0.09130, 0.08149, 0.07208, 0.06309, 0.05388, 0.04356, 0.03218, 0.02026, 0.00824, -0.00344, -0.01433, -0.02412, -0.03264, -0.03974, -0.04541, -0.04972, -0.05276, -0.05458, -0.05517, -0.05466, -0.05302, -0.05030, -0.04657, -0.04191, -0.03634, -0.03016, -0.02353, -0.01611, -0.00817, -0.00065]

        self.turbine_data["pitch_axis"] = {}
        self.turbine_data["pitch_axis"]["grid"] = self.turbine_data["chord"]["grid"]
        self.turbine_data["pitch_axis"]["value"] = [0.5000, 0.5030, 0.5010, 0.4950, 0.4870, 0.4800, 0.4730, 0.4660, 0.4590, 0.4520, 0.4440, 0.4350, 0.4230, 0.4080, 0.3890, 0.3690, 0.3520, 0.3390, 0.3310, 0.3290, 0.3330, 0.3410, 0.3530, 0.3680, 0.3870, 0.4070, 0.4270, 0.4470, 0.4650, 0.4810, 0.4950, 0.5060, 0.5150, 0.5220, 0.5250, 0.5270, 0.5260, 0.5230, 0.5190, 0.5130, 0.5070, 0.4990, 0.4920, 0.4850, 0.4770, 0.4700, 0.4640, 0.4570, 0.4520, 0.4460]
        #=========================================================================
        self.printv('turbine case loaded')

    def load_modeling_options(self):
        self.modeling_options = io.load_yaml(self.model_yaml) #TODO: change for validate_with_defaults

        #=========================================================================
        #temporary definition for a quick demo:
        self.sim_params = {}
        self.sim_params["PGL"] = {}
        self.sim_params["PGL"]["planform_file"] = 'planform.dat'
        #=========================================================================
        self.printv('modeling options loaded')

    # ---------------- UTILITY FUNCTIONS --------------------------------------
    def printv(self,str):
        if(self.verbose):
            print(str)

    # ---------------- MESHING FUNCTIONS --------------------------------------
    def call_writePGLinputs(self):
        pgl.writePGLinputs(self.turbine_data, self.path_to_case, self.sim_params["PGL"]["planform_file"])

    def call_generateSurfMesh(self):
        R = self.turbine_data["R"]
        R0 = self.turbine_data["R0"]
        
        #determine the blending parameter, basically corresponding to the relative thickness of each airfoil
        
        afs = self.turbine_data["airfoils"]
        blend_var = np.zeros(len(afs))
        airfoil_list = []
        i = 0
        for af in afs:
            blend_var[i] = afs[af]["relative_thickness"]
            airfoil_list.append(af)
            i+=1
        
        print(airfoil_list)
        print(blend_var)

        #Call the function:
        pgl.generateSurfMesh(R0, R, self.path_to_case, self.sim_params["PGL"]["planform_file"], airfoil_list, blend_var, "demo_mesh")


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
        
        #=========================================================================
        #temporary demo:
        OTCD.call_writePGLinputs()

        OTCD.call_generateSurfMesh()
        #=========================================================================
        

    OTCD.printv('Done, byebye')
    