import os
from pathlib import Path

# Path to the PythonFMU class script
script_path = Path(__file__).parent / "definition.py"

# Build command
build_command = f"pythonfmu build -f {script_path}"

# Run the build command
os.system(build_command)
