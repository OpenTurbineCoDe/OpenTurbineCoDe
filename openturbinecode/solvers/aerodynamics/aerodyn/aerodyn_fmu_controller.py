from openturbinecode.configs.pathing import PROJECT_ROOT
import sys
import json


def run_simulation(input_data):
    # Example: input_data = {"wind_speed": 12.0, "pitch_angle": 5.0}
    wind_speed = input_data["wind_speed"]
    pitch_angle = input_data["pitch_angle"]

    # Simulate AeroDyn or other logic here
    aero_force = wind_speed * pitch_angle  # Placeholder computation

    # Return results as a dictionary
    return {"aero_force": aero_force}


if __name__ == "__main__":
    # Paths
    output_dir = PROJECT_ROOT / "solvers" / "aerodynamics" / "aerodyn" / "aerodyn_fmu"
    script_path = output_dir / "resources" / "aerodyn_fmu.py"  # Adjust the script path accordingly

    # Read JSON input from stdin
    input_json = sys.stdin.read()
    input_data = json.loads(input_json)

    # Run simulation
    output_data = run_simulation(input_data)

    # Write JSON output to stdout
    print(json.dumps(output_data))
