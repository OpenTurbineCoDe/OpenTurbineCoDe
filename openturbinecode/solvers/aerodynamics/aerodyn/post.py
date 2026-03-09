import numpy as np

from fnmatch import fnmatch

# Load the data
from pCrunch import AeroelasticOutput, FatigueParams
from pCrunch import load_FAST_out

from pathlib import Path


output_dir = Path("D:/") / "GitHub" / "Solvers" / "openfast" / "test_case"


def get_binary_output_data(output_dir):
    """Gets binary output data from OpenFAST output files

    Args:
        output_dir (Path): Path to the directory containing OpenFAST output files
    """

    def valid_extension(fp):
        return any([fnmatch(fp, ext) for ext in ["*.outb"]])

    outfiles = [f for f in output_dir.iterdir() if valid_extension(f)]

    outfiles.sort()

    print(f"Found {len(outfiles)} output files")

    # The new framework provides an object oriented framework to interact with
    # output files. The easiest way to use this is to use the 'load_FAST_out' function.

    outputs = load_FAST_out(outfiles[:3])
    print([type(m) for m in outputs])

    # An instance of 'OpenFASTBinary' (or 'OpenFASTAscii' if applicable) is created.
    # The instance stores the raw data but also provides many useful methods for
    # interacting with the data:

    # print(outputs[0].data)
    # print(outputs[0].time)
    print(outputs[0].channels)
    # print(outputs[0].maxima)
    # print(outputs[0].stddevs)

    # Individual channel time series can also be accessed with dict style indexing:
    # outputs[0]["Wind1VelX"]

    # Channel magnitudes are defined in a dict:
    magnitude_channels = {
        "RootMc1": ["RootMxc1", "RootMyc1", "RootMzc1"],
        "RootMc2": ["RootMxc2", "RootMyc2", "RootMzc2"],
        "RootMc3": ["RootMxc3", "RootMyc3", "RootMzc3"],
    }

    # Define channels (and their fatigue slopes) in a dict:
    fatigue_channels = {
        "RootMc1": FatigueParams(lifetime=25.0, slope=10.0, ult_stress=6e8),
        "RootMc2": FatigueParams(lifetime=25.0, slope=10.0, ult_stress=6e8),
        "RootMc3": FatigueParams(lifetime=25.0, slope=10.0, ult_stress=6e8),
    }

    # Define channels to save extreme data in a list:
    channel_extremes = [
        "RotSpeed",
        "RotThrust",
        "RotTorq",
        "RootMc1",
        "RootMc2",
        "RootMc3",
    ]

    # Convert list of Path objects to list of strings
    outfiles = [str(f) for f in outfiles]

    # The API has changed and is in more of an object oriented framework.
    la = AeroelasticOutput(
        outfiles[:5],                           # The primary input is a list of output files
        magnitude_channels=magnitude_channels,  # All of the following inputs are optional
        fatigue_channels=fatigue_channels,      #
        extreme_channels=channel_extremes,      #
        trim_data=(0,),                         # If 'trim_data' is passed, all input files will
    )                                           # be trimmed to (tmin, tmax(optional))

    la.process_outputs(cores=1,                 # Once LoadsAnalysis is configured, process outputs with
                       return_damage=True,      # optional return of Palmgren-Miner damage and
                       goodman=True)            # optional use of goodman correction for mean load values

    la.summary_stats

    openfast_bin = outputs[0]

    return openfast_bin


def calculate_torque_or_thrust(response_channel, param_dict, openfast_bin):
    """
    Calculate Torque or Thrust based on Ct or Cq values.

    Args:
        response_channel (str): Either "Torque" or "Thrust".
        param_dict (dict): Dictionary of parameters for the current OpenFAST case.
        openfast_bin: The binary output data from OpenFAST.

    Returns:
        np.ndarray: Calculated values for the response channel.
    """
    # Constants
    rho = 1.225  # Air density (kg/m^3)
    R = 121.44  # Rotor radius (m)
    U = param_dict.get("velocity")  # Wind speed (m/s)
    RPM = param_dict.get("rotor_speed")  # Rotor speed (RPM)
    omega = 2 * np.pi * RPM / 60  # Angular velocity (rad/s)
    A = np.pi * R**2  # Rotor swept area (m^2)

    if response_channel == "Torque":
        Cq = openfast_bin["RtAeroCq"]  # Get Cq from the OpenFAST binary data
        return (Cq * 0.5 * rho * A * U**3) / omega
    elif response_channel == "Thrust":
        Ct = openfast_bin["RtAeroCt"]  # Get Ct from the OpenFAST binary data
        return Ct * 0.5 * rho * A * U**2
    else:
        raise ValueError(f"Unsupported response_channel: {response_channel}")


if __name__ == "__main__":
    from openturbinecode.solvers.aerodynamics.aerodyn.utils import postprocess_case
    output_dir = Path("D:/") / "Wright" / "Solvers" / "aerodynamics" / "aerodyn" / "run" / "test_case"
    openfast_bin = postprocess_case(output_dir)

    print(openfast_bin)
