"""This is a PythonFMU for interfacing with AeroDyn using YAML inputs/outputs for blades and nodes.
This class defines the the behavior of the FMU to the dynamic program master.

"""
from pythonfmu import Fmi2Causality, Fmi2Slave, Real
from openturbinecode.configs.pathing import PROJECT_ROOT, AERODYN_FMU, AERODYN_RUN
# Turbine model class
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.solvers.aerodynamics.aerodyn import utils as aerodyn_util


class AeroDynSlave(Fmi2Slave):
    """PythonFMU for interfacing with AeroDyn using YAML inputs/outputs for blades and nodes."""

    author = "Cody Wright"
    description = "PythonFMU for interfacing with AeroDyn using YAML inputs/outputs for blades and nodes"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Blade-specific variables
        self.num_blades = 3
        self.num_nodes_per_blade = 9
        self.blade_origins = [[0.0, 0.0, 0.0] for _ in range(self.num_blades)]  # Blade origins (x, y, z)
        self.blade_orientations = [[0.0, 0.0, 0.0] for _ in range(self.num_blades)]  # Blade orientations
        self.blade_hub_radii = [0.0 for _ in range(self.num_blades)]  # Blade hub radii

        # Initialize aerodynamic loads for all blades and nodes
        self.loads = [[0.0] * self.num_nodes_per_blade for _ in range(self.num_blades)]

        self.test_case_path = AERODYN_RUN / "test_case"

        # YAML files for inputs and outputs
        self.input_file = AERODYN_FMU / "input.yaml"
        self.output_file = AERODYN_FMU / "output.yaml"

        # Register blade-specific inputs
        self.register_inputs_and_outputs()

    def register_inputs_and_outputs(self):
        """Register inputs for AeroDyn FMU."""

        for idx in range(self.num_blades):
            # Register origin
            self.register_variable(Real(f"blade_origin_x_{idx+1}", causality=Fmi2Causality.input,
                                        getter=lambda idx=idx: self.blade_origins[idx][0],
                                        setter=lambda value, idx=idx: self.blade_origins[idx].__setitem__(0, value)))
            self.register_variable(Real(f"blade_origin_y_{idx+1}", causality=Fmi2Causality.input,
                                        getter=lambda idx=idx: self.blade_origins[idx][1],
                                        setter=lambda value, idx=idx: self.blade_origins[idx].__setitem__(1, value)))
            self.register_variable(Real(f"blade_origin_z_{idx+1}", causality=Fmi2Causality.input,
                                        getter=lambda idx=idx: self.blade_origins[idx][2],
                                        setter=lambda value, idx=idx: self.blade_origins[idx].__setitem__(2, value)))

            # Register orientation
            self.register_variable(Real(f"blade_orientation_azimuth_{idx+1}", causality=Fmi2Causality.input,
                                        getter=lambda idx=idx: self.blade_orientations[idx][0],
                                        setter=lambda value, idx=idx: self.blade_orientations[idx].__setitem__(0, value)))  # noqa: E501
            self.register_variable(Real(f"blade_orientation_precone_{idx+1}", causality=Fmi2Causality.input,
                                        getter=lambda idx=idx: self.blade_orientations[idx][1],
                                        setter=lambda value, idx=idx: self.blade_orientations[idx].__setitem__(1, value)))  # noqa: E501
            self.register_variable(Real(f"blade_orientation_pitch_{idx+1}", causality=Fmi2Causality.input,
                                        getter=lambda idx=idx: self.blade_orientations[idx][2],
                                        setter=lambda value, idx=idx: self.blade_orientations[idx].__setitem__(2, value)))  # noqa: E501

            # Register hub radius
            self.register_variable(Real(f"blade_hub_radius_{idx+1}", causality=Fmi2Causality.input,
                                        getter=lambda idx=idx: self.blade_hub_radii[idx],
                                        setter=lambda value, idx=idx: self.blade_hub_radii.__setitem__(idx, value)))

        # Register outputs for aerodynamic loads on each node of each blade
        for idx in range(self.num_blades):
            for jdx in range(self.num_nodes_per_blade):
                self.register_variable(Real(f"load_b{idx + 1}_n{jdx + 1}",
                                            causality=Fmi2Causality.output,
                                            getter=lambda idx_b=idx, idx_n=jdx: self.loads[idx_b][idx_n]))

    def do_step(self, current_time, step_size):
        """Perform a single step of the AeroDyn simulation."""
        print(f"do_step called with current_time={current_time}, step_size={step_size}")

        # Extract inputs from the dynamic simulation tool
        self.assign_blade_inputs()

        # Place inputs into a dictionary for updating the model configuration file
        model_name, aero_inputs = self.format_inputs_for_model_update()

        # Load the model from the configuration file and update according to the inputs
        model: TurbineModel = self.load_model(model_name)

        # Update the model with the current inputs
        model.update_model(aero_inputs)

        # Run the AeroDyn simulation
        print("Running AeroDyn simulation with updated geometry...")
        aerodyn_util.run_aerodyn_case(self.test_case_path, model, step_size)

        # Post-process outputs and update FMU variables
        print("Post-processing AeroDyn outputs...")
        outputs = aerodyn_util.postprocess_case(self.test_case_path)

        # Update FMU outputs
        for i in range(self.num_blades):
            for j in range(self.num_nodes_per_blade):
                try:
                    self.loads[i][j] = float(outputs[i][j])
                except IndexError:
                    print(f"IndexError: Blade {i + 1}, Node {j + 1} is out of bounds in the outputs.")
                    self.loads[i][j] = 0.0

        print("Simulation step completed.")

        return True

    def assign_blade_inputs(self):
        """Extract blade-related inputs from the simulation tool."""
        for idx in range(self.num_blades):
            self.blade_origins[idx] = [
                self.safe_get_real(self, f"blade_origin_x_{idx+1}"),
                self.safe_get_real(self, f"blade_origin_y_{idx+1}"),
                self.safe_get_real(self, f"blade_origin_z_{idx+1}")
            ]
            self.blade_orientations[idx] = [
                self.safe_get_real(self, f"blade_orientation_azimuth_{idx+1}"),
                self.safe_get_real(self, f"blade_orientation_precone_{idx+1}"),
                self.safe_get_real(self, f"blade_orientation_pitch_{idx+1}")
            ]
            self.blade_hub_radii[idx] = self.safe_get_real(self, f"blade_hub_radius_{idx+1}")

    def safe_get_real(self, fmu_instance, variable_name):
        """
        Safely retrieves a real variable from the FMU.

        Args:
            fmu_instance: The FMU instance containing the variable.
            variable_name (str): The name of the variable to retrieve
        Returns:
            float: The value of the variable.
        """
        for key, var in fmu_instance.vars.items():
            if var.name == variable_name:
                return var.getter()
        raise KeyError(f"Variable '{variable_name}' not found in the FMU.")

    def safe_set_real(self, fmu_instance, variable_name, value):
        """
        Safely sets a real variable in the FMU.

        Args:
            fmu_instance: The FMU instance containing the variable.
            variable_name (str): The name of the variable to set.
            value (float): The value to set for the variable.

        Returns:
            bool: True if the variable was set successfully, False otherwise.
        """
        for key, var in fmu_instance.vars.items():
            if var.name == variable_name:
                if var.setter:
                    var.setter(value)
                    print(f"Successfully set {variable_name} to {value}")
                    return True
                else:
                    print(f"Setter for variable '{variable_name}' is not defined.")
                    return False
        print(f"Variable '{variable_name}' not found in the FMU.")
        return False

    def format_inputs_for_model_update(self):
        """Format inputs for updating the model configuration file.
        """
        # Place inputs into a dictionary for updating the model configuration file
        # For right now we just update the rpm of the rotor
        model_name = "IEA_15MW"

        aero_inputs = {
            "blade.use_orientations": True,
            "blade.origins": self.blade_origins,
            "blade.orientations": self.blade_orientations,
            "blade.hub_radii": self.blade_hub_radii
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

    # Define test inputs for blade geometry
    test_inputs = {
        "blade_origins": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        "blade_orientations": [[0.0, -4.0, 0.0], [120.0, -4.0, 0.0], [240.0, -4.0, 0.0]],
        "blade_hub_radii": [3.0, 3.0, 3.0]
    }

    # Assign test inputs to the FMU variables
    slave.blade_origins = test_inputs["blade_origins"]
    slave.blade_orientations = test_inputs["blade_orientations"]
    slave.blade_hub_radii = test_inputs["blade_hub_radii"]

    # Simulate the `do_step` logic
    current_time = 0.0
    step_size = 1.0

    try:
        print("Running `do_step` simulation with test inputs:")
        result = slave.do_step(current_time, step_size)
        print(f"`do_step` result: {result}")

        # Display assigned inputs for verification
        for i in range(slave.num_blades):
            print(f"Blade {i + 1}:")
            print(f"  Origin: {slave.blade_origins[i]}")
            print(f"  Orientation: {slave.blade_orientations[i]}")
            print(f"  Hub Radius: {slave.blade_hub_radii[i]}")

        # Display outputs for verification
        for i in range(slave.num_blades):
            for j in range(slave.num_nodes_per_blade):
                print(f"Load on Blade {i + 1}, Node {j + 1}: {slave.loads[i][j]}")

    except Exception as e:
        print(f"Error during `do_step` execution: {e}")
