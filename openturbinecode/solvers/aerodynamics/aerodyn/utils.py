import shutil
import subprocess
from pathlib import Path
from openturbinecode.models.turbine_model import TurbineModel  # Import the TurbineModel for loading and type hinting
import openturbinecode.solvers.aerodynamics.aerodyn.options as options  # Import the OpenFAST options classes
from openturbinecode.configs.pathing import AERODYN_RUN, PROJECT_ROOT  # Import necessary Path objects
from openturbinecode.solvers.aerodynamics.aerodyn import file_generator as file_gen  # Import the AeroDyn file generator


def make_aerodyn_run_directory(path_to_case: Path):
    """
    Create a new directory inside the $FOAM_RUN directory using a direct WSL path.

    Parameters:
    directory_name (str): Name of the new directory to create inside the WSL path.
    """
    # Check if directory is already created
    if not path_to_case.exists():
        print(f"Creating new directory: {path_to_case}")
        path_to_case.mkdir(parents=True, exist_ok=True)
    else:
        print(f"Directory already exists: {path_to_case}")

    return None


def run_aerodyn_exe(path_to_case: Path):
    """
    Run the OpenFAST simulation.

    Parameters:
    directory_name (str): Name of the directory containing the simulation case.

    Returns:
    bool: True if the simulation completed successfully, False otherwise.
    """
    print(f"Starting AeroDyn simulation in {path_to_case}...")

    aerodyn_exe = AERODYN_RUN / "AeroDyn_Driver_x64.exe"
    aerodyn_input = path_to_case / "DTU_10MW_ADdriver.inp"

    # Ensure the directory and input file exist
    if not path_to_case.is_dir():
        print(f"Error: Case directory '{path_to_case}' does not exist.")
        return False
    if not aerodyn_input.is_file():
        print(f"Error: Input file '{aerodyn_input}' does not exist.")
        return False

    # Command to execute the OpenFAST simulation
    command = [str(aerodyn_exe), str(aerodyn_input)]

    try:
        # Run the simulation in the case directory
        _ = subprocess.run(
            command,
            cwd=path_to_case,
            shell=False,  # Avoid using shell=True for security reasons
            check=True    # Raise an exception if the command fails
        )
        print("OpenFAST simulation completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: AeroDyn simulation failed with return code {e.returncode}.")
        return False
    except FileNotFoundError:
        print("Error: 'AeroDyn_Driver_x64.exe' not found. Ensure it is in your PATH.")
        return False


def clear_case_directory(path_to_case: Path):
    """
    Clear the case directory of all files.

    Parameters:
    case_dir (Path): Path to the case directory containing the simulation files.
    """
    print("Clearing case directory...")

    # Remove the case directory and all its contents
    shutil.rmtree(path_to_case)


def copy_axial_turbine_case(path_to_case: Path):
    """
    Copy the axial turbine case files to the output directory.

    Parameters:
    case_dir (Path): Path to the case directory containing the simulation files.
    """
    print("Copying axial turbine case files to new case directory...")

    madsen_2019 = PROJECT_ROOT / "models" / "DTU_10MW" / "Madsen2019" / "AeroDyn"

    # We can copy these using windows commands in Powershell
    shutil.copytree(madsen_2019, path_to_case, dirs_exist_ok=True)


def preprocess_case(path_to_case: Path, model: TurbineModel = TurbineModel()):
    """Ovewrite the default OpenFAST files with new model parameters.

    Args:
        directory_name (str): The directory name in $FOAM_RUN to preprocess.
    """

    # Create class instances for the new model parameters
    aerodyn_standalone_config = options.AeroDynInputConfig(model)
    aero_config = options.AeroDynConfig(model)
    inflow_config = options.InflowWindConfig(model)

    # Overwrite default files with those from new model parameters
    file_gen.generate_aerodyn_standalone_config(path_to_case, aerodyn_standalone_config)
    file_gen.generate_aerodyn_config(path_to_case, aero_config)
    file_gen.generate_inflow_wind_config(path_to_case, inflow_config)

    return None


def run_aerodyn_case(path_to_case: Path, model: TurbineModel = TurbineModel()):
    """Run an OpenFAST simulation with the given turbine model.

    Args:
        directory_name (str): Name of directory to create in OpenFAST run directory.
        model (TurbineModel, optional): Loaded turbine model. Defaults to TurbineModel().
    """
    # Create a new directory in the $FOAM_RUN directory
    make_aerodyn_run_directory(path_to_case)

    # Clear the case directory
    clear_case_directory(path_to_case)

    # Copy the axial turbine case files to the output directory
    copy_axial_turbine_case(path_to_case)

    # Preprocess the case directory, will overwrite the default files with new model parameters
    preprocess_case(path_to_case, model)

    # Run the openfast simulation
    run_aerodyn_exe(path_to_case)


if __name__ == "__main__":
    """This effectively tests all utilities via run_aerodyn_case.
    """
    # Run an aerodyn case with default model parameters in the test_case directory
    path_to_case = AERODYN_RUN / "test_case"
    run_aerodyn_case(path_to_case)
