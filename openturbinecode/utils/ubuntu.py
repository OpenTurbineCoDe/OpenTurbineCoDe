import subprocess
from pathlib import Path

from openturbinecode.configs.pathing import WSL_ROOT, FOAM_RUN, AXIAL_RUN


def run_ubuntu_command(command):
    """
    Run a command in the Ubuntu subsystem on Windows.

    Parameters:
    command (str): Command to run in the Ubuntu subsystem.

    Returns:
    bool: True if the command was successful, False otherwise.
    """
    # Call openfoam sourcing to set up the environment variables for OpenFOAM run
    command = f"source /usr/lib/openfoam/openfoam2406/etc/bashrc && {command}"

    # Run the command in WSL
    process = subprocess.Popen(["ubuntu", "run", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Monitor the process
    for line in process.stdout:
        print(line, end="")

    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Command failed with error:")
        print(stderr)
        return False
    print(f"Command {command} completed successfully.")
    return True


def path_to_ubuntu(path: Path):
    """Convert a Windows path to a WSL path."""
    return str(path).replace("\\", "/")


if __name__ == "__main__":
    # wsl_path = "$FOAM_RUN"
    # command = f"mkdir -p {wsl_path}/{"test_case"}"
    command = f"cd {path_to_ubuntu(AXIAL_RUN)} && ./Allclean && ls"
    print(command)
    run_ubuntu_command(command)
