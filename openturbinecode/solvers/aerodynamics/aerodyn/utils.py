import shutil
import subprocess
import pandas as pd
from pathlib import Path
from openturbinecode.models.turbine_model import TurbineModel  # Import the TurbineModel for loading and type hinting
import openturbinecode.solvers.aerodynamics.aerodyn.options as options  # Import the AeroDyn options classes
from openturbinecode.configs.pathing import AERODYN_RUN, PROJECT_ROOT  # Import necessary Path objects
from openturbinecode.solvers.aerodynamics.aerodyn.file_gen import driver, aerodyn, inflow  # Import the file generation functions
from openturbinecode.solvers.aerodynamics.aerodyn.post import get_binary_output_data  # Import the postprocessing functions


def make_aerodyn_run_directory(path_to_case: Path):
    """
    Create a new directory for AeroDyn simulations.

    Args:
        path_to_case (Path): Path to the directory for the case.
    """
    if not path_to_case.exists():
        print(f"Creating new directory: {path_to_case}")
        path_to_case.mkdir(parents=True, exist_ok=True)
    else:
        print(f"Directory already exists: {path_to_case}")


def run_aerodyn_exe(path_to_case: Path, model: TurbineModel) -> bool:
    """
    Run the AeroDyn simulation.

    Args:
        path_to_case (Path): Path to the directory containing the simulation case.
        model (TurbineModel): Turbine model with simulation parameters.

    Returns:
        bool: True if the simulation completed successfully, False otherwise.
    """
    print(f"Starting AeroDyn simulation in {path_to_case}...")

    aerodyn_exe = AERODYN_RUN / "AeroDyn_Driver_x64.exe"
    aerodyn_input = path_to_case / f"{model.name}_ADdriver.inp"

    # Ensure the directory and input file exist
    if not path_to_case.is_dir():
        print(f"Error: Case directory '{path_to_case}' does not exist.")
        return False
    if not aerodyn_input.is_file():
        print(f"Error: Input file '{aerodyn_input}' does not exist.")
        return False

    command = [str(aerodyn_exe), str(aerodyn_input)]

    try:
        subprocess.run(command, cwd=path_to_case, check=True)
        print("AeroDyn simulation completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: AeroDyn simulation failed with return code {e.returncode}.")
        return False
    except FileNotFoundError:
        print("Error: 'AeroDyn_Driver_x64.exe' not found.")
        return False


def clear_case_directory(path_to_case: Path):
    """
    Clear the case directory of all files.

    Args:
        path_to_case (Path): Path to the case directory.
    """
    print(f"Clearing case directory: {path_to_case}")
    shutil.rmtree(path_to_case)


def copy_axial_turbine_case(path_to_case: Path, model: TurbineModel):
    """
    Copy the axial turbine case files to the output directory.

    Args:
        path_to_case (Path): Path to the case directory.
        model (TurbineModel): Turbine model to determine the case files.
    """
    print(f"Copying axial turbine case files to: {path_to_case}")
    model_dir = {
        "DTU_10MW": PROJECT_ROOT / "models" / "DTU_10MW" / "Madsen2019" / "AeroDyn",
        "IEA_15MW": PROJECT_ROOT / "models" / "IEA_15MW" / "AeroDyn",
    }.get(model.name)

    if not model_dir:
        raise ValueError(f"Unknown turbine model: {model.name}")

    shutil.copytree(model_dir, path_to_case, dirs_exist_ok=True)


def preprocess_case(path_to_case: Path, model: TurbineModel, stop_time: float = None):
    """
    Overwrite default AeroDyn files with new model parameters.

    Args:
        path_to_case (Path): Path to the directory for the case.
        model (TurbineModel): Turbine model with updated parameters.
    """
    print(f"Preprocessing case: {path_to_case}")

    aerodyn_standalone_config = options.AeroDynDriverConfig(model, stop_time)
    aero_config = options.AeroDynConfig(model)
    inflow_config = options.InflowWindConfig(model)

    driver.generate_aerodyn_standalone_config(path_to_case, aerodyn_standalone_config)
    aerodyn.generate_aerodyn_config(path_to_case, aero_config)
    inflow.generate_inflow_wind_config(path_to_case, inflow_config)


def postprocess_case(path_to_case: Path):
    """
    Postprocess the AeroDyn simulation results.

    Args:
        path_to_case (Path): Path to the directory for the case.
        model (TurbineModel): Turbine model with updated parameters.
    """
    print(f"Postprocessing case: {path_to_case}")

    # Postprocess the results
    bin_output = get_binary_output_data(path_to_case)

    df: pd.DataFrame = bin_output.df

    # Get the last row of the DataFrame
    last_row = df.iloc[-1]

    # Determine the number of blades and nodes from the available channels
    num_blades = max(int(col[1]) for col in df.columns if col.startswith("B") and col[1].isdigit())
    num_nodes_per_blade = max(int(col[3]) for col in df.columns if col.startswith("B") and len(col) > 3 and col[3].isdigit())

    # Prepare nested list for aerodynamic loads
    outputs = [[0.0] * num_nodes_per_blade for _ in range(num_blades)]

    # Extract data for each blade and node based on naming convention (e.g., B1N1Fx, B1N2Fx, ...)
    for blade in range(1, num_blades + 1):
        for node in range(1, num_nodes_per_blade + 1):
            # Example channel naming convention (modify as needed to match your output channels):
            force_key = f"B{blade}N{node}Cy"  # Replace "Fx" with actual desired channel suffix if needed

            if force_key in last_row:
                outputs[blade - 1][node - 1] = last_row[force_key]
            else:
                print(f"Warning: Missing channel '{force_key}' in output data.")

    # Extract blade nodal loads

    return outputs


def run_aerodyn_case(path_to_case: Path, model: TurbineModel, stop_time: float = None):
    """
    Run an AeroDyn simulation with the given turbine model.

    Args:
        path_to_case (Path): Path to the directory for the case.
        model (TurbineModel): Turbine model with parameters.
    """
    make_aerodyn_run_directory(path_to_case)
    clear_case_directory(path_to_case)
    copy_axial_turbine_case(path_to_case, model)
    preprocess_case(path_to_case, model, stop_time)
    run_aerodyn_exe(path_to_case, model)


if __name__ == "__main__":
    """Example use of run_aerodyn_case for testing utilities."""
    test_case_path = AERODYN_RUN / "test_case"
    default_model = TurbineModel(name="DTU_10MW", hub_radius=2.8, tower_height=119.0)
    run_aerodyn_case(test_case_path, default_model)
