from pathlib import Path
import openturbinecode.solvers.aerodynamics.turbinesFoam.utils as util
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.solvers.aerodynamics.turbinesFoam.file_generator import FileGenerator
from openturbinecode.solvers.aerodynamics.turbinesFoam.options import turbineFoamAxialFlowOptions
import post_processing as pp
import pandas as pd
from dataclasses import dataclass

BOOL_RUN_CASE = True
BOOL_POST_PROCESS = True

GEN_FILES = True

MODEL = "IEA_15MW_AB_OF"  # Example turbine model, can be replaced with any valid model name
# MODEL = "DTU_10MW_OF"

STATE_FILE = "xview2"
FOAM_FILE = "foam.case"


@dataclass
class RunOptions:
    case_name: str = "test_case"
    case_class: str = "axialFlowTurbineAL"
    num_revolutions: int = 5
    time_step: float = 0.25  # degrees per time step
    model_tower: bool = False
    model_hub: bool = False
    tip_speed_ratio: float = 9.0
    wind_speed: float = 12.8  # m/s
    twist_offset: float = 0.0
    tilt_angle: float = -6.0  # degrees
    num_parallel_cores: int = 1
    mesh_density: int = 8


@dataclass
class PostOptions:
    calc_performance: bool = True
    plot_cp: bool = True
    plot_spanwise: bool = True
    min_angle: float = 1.0


class turbinesFoamWrapper:
    def __init__(self, turbine: TurbineModel, run_options, post_options: PostOptions):
        self.turbine: TurbineModel = turbine
        self.run_options = run_options
        self.post_options = post_options
        self.case_name = run_options.case_name
        self.case_class = run_options.case_class

        self.case_dir = Path(util.WSL_ROOT / util.FOAM_RUN / self.case_name)

        # Load the case options
        self.foam_options = self.load_case(self.turbine, self.case_class, run_options)

    def load_case(self, turbine: TurbineModel, case_name: str, run_options: dict):
        """Load a case from the OpenTurbineCode turbine model.

        Args:
            turbine (TurbineModel): The turbine model to load.
            case_name (str): The name of the case to load.
        """
        if case_name == "axialFlowTurbineAL":
            options = turbineFoamAxialFlowOptions(turbine, run_options)
        else:
            raise ValueError(f"Case {case_name} is not supported.")

        return options

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
            power, torque, thrust = self.post_process(self.post_options)
            return power, torque, thrust
            # pp.launch_paraview_for_case(self.case_name, state_file=STATE_FILE)

    def manage_case_files(self):
        # Create a new directory in the $FOAM_RUN directory
        util.make_directory_in_foam_run(self.case_name)

        # Clear the case directory
        util.clear_case_directory(self.case_name)

        # Copy the axial turbine case files to the output directory
        util.copy_axial_turbine_case(self.case_name)

    def preprocess(self):
        """Preprocess the case directory by generating the OpenFOAM files."""
        print("Preprocessing case files...")
        if GEN_FILES:
            generator = FileGenerator(self.turbine, self.run_options)

            # Generate the OpenFOAM files to the case directory
            generator.generate_files(self.case_dir)
        pass

    def run_simulation(self):
        # Preprocess the case directory
        util.initialize_run(self.case_name)

        # Run the turbinesFoam simulation
        util.allrun_turbinesFoam_case(self.case_name, self.run_options.num_parallel_cores)

    def post_process(self, post_options: PostOptions):
        # Extract the simulation results
        print("Post-processing simulation results...")
        util.create_paraview_file(self.case_name)

        match self.case_class:
            case "axialFlowTurbineAL":
                post = pp.AxialFlowPostProcessing(self.case_name, self.turbine)
                post.plot_cp()
                post.plot_spanwise()
                power, torque, thrust = post.calc_performance()
                for element_number in range(0, len(post.spanwise_dict)):
                    post.plot_element_time_series(element_number)
                return power, torque, thrust
            case _:
                print("Invalid case class.")


# Example usage
if __name__ == "__main__":
    turbine = TurbineModel(name=MODEL)
    turbine.read_from_yaml()
    if BOOL_POST_PROCESS:
        results_df = pd.DataFrame(columns=["TSR", "Power", "Torque", "Thrust"])
    for mesh_density in range(9, 10, 1):
        tsr = 9.0
        run_options = RunOptions(case_name=f"{MODEL}_TSR{tsr}_MD{mesh_density}", mesh_density=mesh_density, tip_speed_ratio=tsr)
        post_options = PostOptions()
        wrapper = turbinesFoamWrapper(turbine, run_options=run_options, post_options=post_options)
        power, torque, thrust = wrapper.main()
        if BOOL_POST_PROCESS:
            results_df = pd.concat(
                [
                    results_df,
                    pd.DataFrame(
                        {
                            "TSR": [tsr],
                            "Power": [power],  # Convert to MW
                            "Torque": [torque],  # Convert to MNm
                            "Thrust": [thrust],  # Convert to MN
                        }
                    ),
                ],
                ignore_index=True,
            )

    if BOOL_POST_PROCESS:
        results_df.to_csv(f"{MODEL}_performance_results.csv", index=False)
        print(results_df)
        wrapper.post_process(post_options)
  
