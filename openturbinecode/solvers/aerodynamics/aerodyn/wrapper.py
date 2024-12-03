"""This is a wrapper for the Aerodyn aerodynamic solver. From the top level if aerodyn is prescribed as the passed
parameter for the solver, this wrapper will be called. This wrapper will manage the case files, preprocess,
run the simulation, and post-process the results. The main method will call all of these methods in order.

This wrapper receives a turbine model object and options dictionary as input. The options dictionary contains the case.
"""
import openturbinecode.solvers.aerodynamics.aerodyn.utils as utils
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.configs.pathing import AERODYN_RUN

# Debugging flags
BOOL_RUN_CASE = True
BOOL_POST_PROCESS = False


class AerodynWrapper:
    def __init__(self, turbine: TurbineModel, options: dict):
        """Initialization method for the AerodynWrapper class. This initializes the turbine and options attributes.
        It parses the options parameters and assigns them to the class attributes.

        Args:
            turbine (TurbineModel): Model of the turbine to be simulated.
            options (dict): Dictionary containing the case name and case class.
        """
        self.turbine = turbine
        self.case_name = options["case_name"]
        self.case_class = options["case_class"]

    def main(self):
        # Create the path to the case directory
        path_to_case = AERODYN_RUN / self.case_name

        if BOOL_RUN_CASE:
            # Manage the case files
            self.manage_case_files(path_to_case)

            # Preprocess the case
            self.preprocess(path_to_case)

            # Run the simulation
            self.run_simulation(path_to_case)

        # Post-process the simulation
        if BOOL_POST_PROCESS:
            self.post_process()

    def manage_case_files(self, path_to_case):
        # Create a new directory in the $FOAM_RUN directory
        utils.make_aerodyn_run_directory(path_to_case=path_to_case)

        # Clear the case directory
        utils.clear_case_directory(path_to_case=path_to_case)

        # Copy the axial turbine case files to the output directory
        utils.copy_axial_turbine_case(path_to_case=path_to_case)

    def preprocess(self, path_to_case):
        # Preprocess the case directory
        utils.preprocess_case(path_to_case=path_to_case)

    def run_simulation(self, path_to_case):
        # Run the Aerodyne standalone simulation
        utils.run_aerodyn_case(path_to_case=path_to_case)

    def post_process(self):
        # Extract the simulation results
        pass


# Example usage
if __name__ == "__main__":
    turbine = None
    options = {
        'case_name': "test_case",  # Use Windows path
        'case_class': "axialFlowTurbineAL"
    }

    wrapper = AerodynWrapper(turbine, options)
    wrapper.main()
