import shutil
from pathlib import Path
from fmpy.fmi2 import FMU2Slave
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.solvers.aerodynamics.aerodyn.utils import (
    make_aerodyn_run_directory,
    preprocess_case,
    run_aerodyn_exe
)


class AeroDynFMU(FMU2Slave):
    """
    FMU wrapper for AeroDyn simulation.
    This class handles input/output mapping and executes AeroDyn with provided inputs.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = TurbineModel(name="AeroDyn_FMU_Model")
        self.case_directory = Path("aerodyn_fmu_case")
        self.step_size = 0.0
        self.position = [0.0, 0.0, 0.0]  # Placeholder for P input
        self.velocity = [0.0, 0.0, 0.0]  # Placeholder for V input
        self.orientation = [0.0] * 9     # Placeholder for O input (direction cosine matrix)
        self.loads = [0.0, 0.0, 0.0]    # Placeholder for L output (aerodynamic loads)

    def setup_experiment(self, start_time, stop_time):
        """Setup the AeroDyn experiment."""
        # Create the case directory
        if self.case_directory.exists():
            shutil.rmtree(self.case_directory)
        make_aerodyn_run_directory(self.case_directory)

        # Preprocess the case with the current turbine model
        preprocess_case(self.case_directory, self.model)

    def do_step(self, current_time, step_size, no_set_fmu_state_prior_to_current_point=True):
        """Perform a simulation step."""
        self.step_size = step_size

        # Update the model with the current inputs
        self.model.position = self.position
        self.model.velocity = self.velocity
        self.model.orientation = self.orientation

        # Write updated inputs to the AeroDyn input files
        preprocess_case(self.case_directory, self.model)

        # Run AeroDyn
        success = run_aerodyn_exe(self.case_directory, self.model)
        if not success:
            raise RuntimeError("AeroDyn simulation failed during FMU step.")

        # Extract outputs (e.g., aerodynamic loads) from AeroDyn results
        # Placeholder logic; implement actual AeroDyn output parsing
        self.loads = [1.0, 2.0, 3.0]  # Replace with actual results

        return True

    def get_real(self, vr):
        """Get real variable values."""
        if vr == 0:  # Position
            return self.position
        elif vr == 1:  # Velocity
            return self.velocity
        elif vr == 2:  # Orientation
            return self.orientation
        elif vr == 4:  # Loads
            return self.loads
        else:
            raise ValueError(f"Unknown value reference: {vr}")

    def set_real(self, vr, value):
        """Set real variable values."""
        if vr == 0:  # Position
            self.position = value
        elif vr == 1:  # Velocity
            self.velocity = value
        elif vr == 2:  # Orientation
            self.orientation = value
        elif vr == 3:  # Step size
            self.step_size = value
        else:
            raise ValueError(f"Unknown value reference: {vr}")


if __name__ == "__main__":
    # Example initialization and execution of the FMU
    fmu = AeroDynFMU()
    fmu.setup_experiment(0, 10)

    # Simulate a sequence of steps
    for step in range(10):
        current_time = step * 0.1
        fmu.set_real(0, [1.0, 2.0, 3.0])  # Example position input
        fmu.set_real(1, [0.0, 0.0, 10.0])  # Example velocity input
        fmu.set_real(2, [1.0] * 9)         # Example orientation input
        fmu.do_step(current_time, 0.1)
        loads = fmu.get_real(4)
        print(f"Step {step}: Loads = {loads}")
