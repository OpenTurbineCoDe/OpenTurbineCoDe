
import argparse

class OpenTurbineCoDe:

    def __init__(self, args):
        print('Hello, this is OpenTurbineCoDe.')
        # turbine_params ...
        self.load_case(args)
        # simulation params ...
        print('initilization done')

    def load_case(self,file):
        # ...
        self.data = {}
        # self.data = io.load_turbine(...)
        print('case loaded')



if __name__ == '__main__':
    

    parser = argparse.ArgumentParser()
    parser.add_argument("--case", help="Path to the case file", type=str, default="case.yaml")
    parser.add_argument("--GUI", action='store_true', help="Run PyTurbineCoDe with the GUI")
    args = parser.parse_args()

    OTCD = OpenTurbineCoDe(args.case) #initialize me

    #do some arg parsing:
    if args.GUI:
        print('Starting the GUI')
        ##something like:
        #start_gui(OTCD)
    else:
        print('no GUI. One day, I could read a dedicated file that tells me what to do.')
        

    print('Done, byebye')
    