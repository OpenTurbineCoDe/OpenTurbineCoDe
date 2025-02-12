import shutil
import subprocess
from pathlib import Path
import openturbinecode.solvers.aerostructural.openfast.options as options
from openturbinecode.configs.pathing import OPENFAST_RUN, PROJECT_ROOT
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.solvers.aerostructural.openfast.file_gen import fast, elastodyn, aerodyn, inflow


def make_openfast_run_directory(directory_name):
    """
    Create a new directory inside the $FOAM_RUN directory using a direct WSL path.

    Parameters:
    directory_name (str): Name of the new directory to create inside the WSL path.
    """
    path_to_case: Path = OPENFAST_RUN / directory_name
    # Check if directory is already created
    if not path_to_case.exists():
        print(f"Creating new directory: {path_to_case}")
        path_to_case.mkdir(parents=True, exist_ok=True)
    else:
        print(f"Directory already exists: {path_to_case}")

    return None


def run_openfast_exe(directory_name: str, model: TurbineModel):
    """
    Run the OpenFAST simulation.

    Parameters:
    directory_name (str): Name of the directory containing the simulation case.

    Returns:
    bool: True if the simulation completed successfully, False otherwise.
    """
    print(f"Starting OpenFAST simulation in {directory_name}...")

    path_to_case = Path(OPENFAST_RUN) / directory_name
    fst_exe = Path(OPENFAST_RUN).parent / "openfast_x64_v300.exe"
    fst_file = path_to_case / f"{model.name}.fst"

    # Ensure the directory and input file exist
    if not path_to_case.is_dir():
        print(f"Error: Case directory '{path_to_case}' does not exist.")
        return False
    if not fst_file.is_file():
        print(f"Error: Input file '{fst_file}' does not exist.")
        return False

    # Command to execute the OpenFAST simulation
    command = [str(fst_exe), str(fst_file)]

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
        print(f"Error: OpenFAST simulation failed with return code {e.returncode}.")
        return False
    except FileNotFoundError:
        print("Error: 'openfast_x64.exe' not found. Ensure it is in your PATH.")
        return False


def clear_case_directory(directory_name):
    """
    Clear the case directory of all files.

    Parameters:
    case_dir (Path): Path to the case directory containing the simulation files.
    """
    print("Clearing case directory...")

    path_to_case: Path = OPENFAST_RUN / directory_name

    # Remove the case directory and all its contents
    shutil.rmtree(path_to_case)


def copy_axial_turbine_case(directory_name, model: TurbineModel):
    """
    Copy the axial turbine case files to the output directory.

    Parameters:
    case_dir (Path): Path to the case directory containing the simulation files.
    """
    print("Copying axial turbine case files to new case directory...")
    match model.name:
        case "DTU_10MW":
            model_dir = PROJECT_ROOT / "models" / "DTU_10MW" / "Madsen2019" / "OpenFAST"
            path_to_case: Path = OPENFAST_RUN / directory_name
        case "IEA_15MW":
            model_dir = PROJECT_ROOT / "models" / "IEA_15MW" / "OpenFAST"
            path_to_case: Path = OPENFAST_RUN / directory_name
        case "IEA_15MW_AB":
            model_dir = PROJECT_ROOT / "models" / "IEA_15MW_AB"
            path_to_case: Path = OPENFAST_RUN / directory_name

    # We can copy these using windows commands in Powershell
    shutil.copytree(model_dir, path_to_case, dirs_exist_ok=True)


def preprocess_case(directory_name, model: TurbineModel = TurbineModel()):
    """Ovewrite the default OpenFAST files with new model parameters.

    Args:
        directory_name (str): The directory name in $FOAM_RUN to preprocess.
    """

    path_to_case = OPENFAST_RUN / directory_name

    # Create class instances for the new model parameters
    fast_config = options.FastConfig(model)
    aero_config = options.AeroDynConfig(model)
    elast_config = options.ElastoDynConfig(model)
    inflow_config = options.InflowWindConfig(model)

    # Overwrite default files with those from new model parameters
    fast.generate_fast_config(path_to_case, fast_config)
    aerodyn.generate_aerodyn_config(path_to_case, aero_config)
    elastodyn.generate_elastodyn_config(path_to_case, elast_config)
    inflow.generate_inflow_wind_config(path_to_case, inflow_config)

    return None


def run_openfast_case(directory_name, model: TurbineModel = TurbineModel()):
    """Run an OpenFAST simulation with the given turbine model.

    Args:
        directory_name (str): Name of directory to create in OpenFAST run directory.
        model (TurbineModel, optional): Loaded turbine model. Defaults to TurbineModel().
    """
    # Create a new directory in the $FOAM_RUN directory
    make_openfast_run_directory(directory_name)

    # Clear the case directory
    clear_case_directory(directory_name)

    # Copy the axial turbine case files to the output directory
    copy_axial_turbine_case(directory_name, model)

    # Preprocess the case directory
    preprocess_case(directory_name, model)

    # Run the openfast simulation
    run_openfast_exe(directory_name, model)


if __name__ == "__main__":
    run_openfast_case("test_case")
