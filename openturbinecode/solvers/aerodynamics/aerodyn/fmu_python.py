"""This is a PythonFMU for interfacing with AeroDyn using YAML inputs/outputs for blades and nodes.
This class defines the the behavior of the FMU to the dynamic program master.

"""
import numpy as np
from pythonfmu import Fmi2Causality, Fmi2Slave, Real
from openturbinecode.configs.pathing import PROJECT_ROOT, AERODYN_FMU, AERODYN_RUN
# Turbine model class
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.solvers.aerodynamics.aerodyn import utils as aerodyn_util


class AeroDynSlave(Fmi2Slave):
    """This is a PythonFMU for interfacing with AeroDyn using YAML inputs/outputs for blades and nodes.

    Args:
        Fmi2Slave (pythonfmu class): Inherit from the Fmi2Slave class

    Returns:
        None: No return
    """

    author = "Cody Wright"
    description = "PythonFMU for interfacing with AeroDyn using YAML inputs/outputs for blades and nodes"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # General rotor variables
        self.num_blades = 3  # Number of blades per rotor
        self.num_nodes_per_blade = 50  # Maximum number of nodes per blade

        # AeroDyn case directories
        self.test_case_path = AERODYN_RUN / "test_case"

        # Initialize variables for 3 blades, each with 3 nodes
        self.positions = [0.0] * self.num_blades
        self.velocities = [0.0] * self.num_blades
        self.orientations = [0.0] * self.num_blades
        self.loads = [[0.0] * self.num_blades for _ in range(self.num_nodes_per_blade)]  # 3 blades, each with 3 nodes

        # Test input
        self.test_input = 0.0

        # We use YAML files for inputs and outputs from the fmu subdirectory
        self.input_file = AERODYN_FMU / "input.yaml"
        self.output_file = AERODYN_FMU / "output.yaml"

        self.register_inputs_and_outputs(self.num_blades, self.num_nodes_per_blade)

    def register_inputs_and_outputs(self, num_blades, num_nodes_per_blade):
        """Register inputs for the AeroDyn FMU. These are initialized in the FMU constructor and
        will be accessible only through the .fmu. These are not initialized per instance of the FMU call.

        We register the following inputs:
        - position_{i + 1} (Real): Position of blade i
        - velocity_{i + 1} (Real): Velocity of blade i
        - orientation_{i + 1} (Real): Orientation of blade i

        The following outputs are registered:
        - load_b{i + 1}_n{j + 1} (Real): Load on node j of blade i

        Args:
            num_blades (int): Number of blades
            num_nodes_per_blade (int): Number of nodes per blade
        """
        # Loop through each blade
        for i in range(num_blades):
            # Register position, velocity, and orientation inputs
            self.register_variable(Real(f"position_{i + 1}",
                                        causality=Fmi2Causality.input,
                                        getter=lambda idx=i: self.positions[idx],
                                        setter=lambda value, idx=i: self.positions.__setitem__(idx, value)))

            self.register_variable(Real(f"velocity_{i + 1}",
                                        causality=Fmi2Causality.input,
                                        getter=lambda idx=i: self.velocities[idx],
                                        setter=lambda value, idx=i: self.velocities.__setitem__(idx, value)))

            self.register_variable(Real(f"orientation_{i + 1}",
                                        causality=Fmi2Causality.input,
                                        getter=lambda idx=i: self.orientations[idx],
                                        setter=lambda value, idx=i: self.orientations.__setitem__(idx, value)))

            # # Register the outputs for each node of the blade
            # for j in range(num_nodes_per_blade):
            #     self.register_variable(Real(f"load_b{i + 1}_n{j + 1}",
            #                                 causality=Fmi2Causality.output,
            #                                 getter=lambda idx_b=i, idx_n=j: self.loads[idx_b][idx_n],
            #                                 setter=lambda value, idx_b=i, idx_n=j: self.loads[idx_b].__setitem__(idx_n, value)))  # noqa: E501

    def do_step(self, current_time, step_size):
        """Perform a single step of the AeroDyn simulation.
        """
        print(f"do_step called with current_time={current_time}, step_size={step_size}")
        # Extract inputs from the dynamic simulation tool
        self.assign_inputs()

        # Place inputs into a dictionary for updating the model configuration file
        model_name, aero_inputs = self.format_inputs_for_model_update()

        # Load the model from the configuration file and update according to the inputs
        model: TurbineModel = self.load_model(model_name)

        # Update the model with the current inputs
        # model.update_model(aero_inputs)

        # Perform calculations (or call AeroDyn)
        print("Running case: AeroDyn FMU case.")
        aerodyn_util.run_aerodyn_case(self.test_case_path, model)

        # # Conduct post-processing
        # aero_outputs = [0]

        # # Update outputs
        # for i, blade_loads in enumerate(aero_outputs):
        #     for j, load in enumerate(blade_loads):
        #         self.set_real(f"load_b{i + 1}_n{j + 1}", load)

        return True

    def assign_inputs(self):
        """Extract inputs from the simulation tool and assign them to the model."""

        def get_variable_value(name):
            for key, var in self.vars.items():
                if var.name == name:
                    return var.getter()
            raise KeyError(f"Variable '{name}' not found")

        for i in range(self.num_blades):  # Assuming 3 blades
            try:
                self.positions[i] = get_variable_value(f"position_{i + 1}")
                self.velocities[i] = get_variable_value(f"velocity_{i + 1}")
                self.orientations[i] = get_variable_value(f"orientation_{i + 1}")
                print(f"Assigned Blade {i + 1}: Position={self.positions[i]}, Velocity={self.velocities[i]}, Orientation={self.orientations[i]}")  # noqa: E501
            except KeyError as e:
                print(f"KeyError: {e} for Blade {i + 1}")
                raise
            except Exception as e:
                print(f"Error: {e} during input assignment for Blade {i + 1}")
                raise

    def format_inputs_for_model_update(self):
        """Format inputs for updating the model configuration file.
        """
        # Place inputs into a dictionary for updating the model configuration file
        # For right now we just update the rpm of the rotor
        model_name = "IEA_15MW"
        aero_inputs = {
            "blade.rotor_speed": [4]
        }
        return model_name, aero_inputs

    def load_model(self, model_name):
        """Load the model from the configuration file and update according to the inputs.
        """
        # Load in model
        model = TurbineModel(name=model_name)
        model.read_from_yaml(PROJECT_ROOT / "models" / "defaults" / f"{model_name}.yaml")

        return model


if __name__ == "__main__":
    # Create an instance of AeroDynSlave for testing
    slave = AeroDynSlave(instance_name="test_instance")

    # Manually set test inputs
    slave.test_input = 1.0  # Simulate an input value

    # Simulate the `do_step` logic
    current_time = 0.0
    step_size = 1.0

    # Define simulation inputs
    inputs = np.array([
        (0.0, 1.0, 2.0, 3.0, 0.1, 0.2, 0.3, 0.01, 0.02, 0.03),  # Initial inputs
        (5.0, 1.5, 2.5, 3.5, 0.2, 0.3, 0.4, 0.02, 0.03, 0.04)   # Mid-simulation inputs
    ], dtype=[
        ('time', np.float64),
        ('position_1', np.float64), ('position_2', np.float64), ('position_3', np.float64),
        ('velocity_1', np.float64), ('velocity_2', np.float64), ('velocity_3', np.float64),
        ('orientation_1', np.float64), ('orientation_2', np.float64), ('orientation_3', np.float64)
    ])
    try:
        print("Running do_step simulation manually:")
        result = slave.do_step(current_time, step_size)
        print(f"do_step result: {result}")
    except Exception as e:
        print(f"Error during manual do_step execution: {e}")
