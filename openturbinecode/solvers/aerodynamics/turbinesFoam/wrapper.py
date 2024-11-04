from pathlib import Path
import turbinesFoam_utils as util
import post_processing as pp

BOOL_RUN_CASE = False
BOOL_POST_PROCESS = True


class turbinesFoamWrapper:
    def __init__(self, turbine, options):
        self.turbine = turbine
        self.case_name = options["case_name"]
        self.case_class = options["case_class"]

    def main(self):
        if BOOL_RUN_CASE:
            # Manage the case files
            self.manage_case_files()

            # Preprocess the case
            self.preprocess()

            # Run the simulation
            self.run_simulation()

        # Post-process the simulation
        if BOOL_POST_PROCESS:
            self.post_process()

    def manage_case_files(self):
        # Create a new directory in the $FOAM_RUN directory
        util.make_directory_in_foam_run(self.case_name)

        # Clear the case directory
        util.clear_case_directory(self.case_name)

        # Copy the axial turbine case files to the output directory
        util.copy_axial_turbine_case(self.case_name)

    def preprocess(self):
        # Preprocess the case directory
        util.preprocess_case(self.case_name)

    def run_simulation(self):
        # Run the turbinesFoam simulation
        util.allrun_turbinesFoam_case(self.case_name)

    def post_process(self):
        # Extract the simulation results
        print("Post-processing simulation results...")
        match self.case_class:
            case "axialFlowTurbineAL":
                post = pp.AxialFlowPostProcessing(self.case_name)
                post.plot_cp()
                post.plot_spanwise()
            case _:
                print("Invalid case class.")


# Example usage
if __name__ == "__main__":
    turbine = None
    options = {
        'case_name': "test_case",  # Use Windows path
        'case_class': "axialFlowTurbineAL"
    }

    wrapper = turbinesFoamWrapper(turbine, options)
    wrapper.main()
