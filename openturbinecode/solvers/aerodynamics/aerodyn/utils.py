import shutil
import subprocess
from pathlib import Path
from openturbinecode.models.turbine_model import TurbineModel  # Import the TurbineModel for loading and type hinting
import openturbinecode.solvers.aerodynamics.aerodyn.options as options  # Import the AeroDyn options classes
from openturbinecode.configs.pathing import AERODYN_RUN, PROJECT_ROOT  # Import necessary Path objects
from openturbinecode.solvers.aerodynamics.aerodyn import file_generator as file_gen  # Import the AeroDyn file generator


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


def preprocess_case(path_to_case: Path, model: TurbineModel):
    """
    Overwrite default AeroDyn files with new model parameters.

    Args:
        path_to_case (Path): Path to the directory for the case.
        model (TurbineModel): Turbine model with updated parameters.
    """
    print(f"Preprocessing case: {path_to_case}")

    aerodyn_standalone_config = options.AeroDynInputConfig(model)
    aero_config = options.AeroDynConfig(model)
    inflow_config = options.InflowWindConfig(model)

    file_gen.generate_aerodyn_standalone_config(path_to_case, aerodyn_standalone_config)
    file_gen.generate_aerodyn_config(path_to_case, aero_config)
    file_gen.generate_inflow_wind_config(path_to_case, inflow_config)


def run_aerodyn_case(path_to_case: Path, model: TurbineModel):
    """
    Run an AeroDyn simulation with the given turbine model.

    Args:
        path_to_case (Path): Path to the directory for the case.
        model (TurbineModel): Turbine model with parameters.
    """
    make_aerodyn_run_directory(path_to_case)
    clear_case_directory(path_to_case)
    copy_axial_turbine_case(path_to_case, model)
    preprocess_case(path_to_case, model)
    run_aerodyn_exe(path_to_case, model)


if __name__ == "__main__":
    """Example use of run_aerodyn_case for testing utilities."""
    test_case_path = AERODYN_RUN / "test_case"
    default_model = TurbineModel(name="DTU_10MW", hub_radius=2.8, tower_height=119.0)
    run_aerodyn_case(test_case_path, default_model)
