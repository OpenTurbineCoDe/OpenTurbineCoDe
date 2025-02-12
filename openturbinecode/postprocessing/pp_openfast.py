import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

from fnmatch import fnmatch

from openturbinecode.utils import plotter as plot

# Load the data
from pCrunch import LoadsAnalysis, FatigueParams
from pCrunch.io import load_FAST_out

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
    la = LoadsAnalysis(
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


def get_and_plot_time_series(openfast_bin, channel: str, output_dir):
    """Plots the time series of a channel from an OpenFAST binary output file

    Args:
        openfast_bin (OpenFAST): OpenFAST binary output file
        channel (str): Channel to plot
        output_dir (Path): Path to the directory to save the plot
    """
    plots_dir = output_dir / "plots"
    try:
        df: pd.DataFrame = openfast_bin.df
        unit = str(openfast_bin.units[np.argmax(openfast_bin.channels == channel)])
        plot_data = df[['Time', channel]].to_numpy()
        plot.time_series(plot_data, ylabel=f'{channel} [{unit}]', title=f'{channel} Time Series',
                         filename=f'{plots_dir / f"{channel}_Time_Series.svg"}')
    except KeyError:
        print(f"Channel '{channel}' not found in OpenFAST output file.")
    except Exception as e:
        print(f"An error occurred while plotting '{channel}' time series: {e}")

    return None


def plot_all_time_series(openfast_bin):
    """Plots all time series plots for all channels

    Args:
        openfast_bin (_type_): _description_
    """
    for channel in openfast_bin.channels:
        get_and_plot_time_series(openfast_bin, channel)

    return None


def get_parametric_analysis_data(output_dir: Path):
    """
    Gets parametric analysis data from OpenFAST output files.

    Args:
        output_dir (Path): Path to the directory containing OpenFAST case directories.

    Returns:
        dict: A dictionary where keys are parameter combinations and values are
              the binary output data from OpenFAST.
    """
    parametric_data = {}

    # Get all directory names in the output directory
    case_dirs = [d for d in output_dir.iterdir() if d.is_dir()]

    for case_dir in case_dirs:
        # Parse parameter values from directory names
        # Assumes directories are named like 'velocity_8.0_tip_speed_ratio_-5'
        case_name = case_dir.name
        param_values = {}
        try:
            # Use a split-by-underscore approach, but keep parameter-value pairs intact
            components = case_name.split("_")
            param_name = []
            for comp in components:
                # Use a regex to detect valid numerical values (including negative numbers)
                if re.fullmatch(r'-?\d+(\.\d+)?', comp):  # Matches integers and floats, including negative
                    param_value = float(comp)
                    # Join the collected parameter name and reset for the next one
                    param_values["_".join(param_name)] = param_value
                    param_name = []
                else:
                    # Build the parameter name across multiple components
                    param_name.append(comp)

            if param_name:  # If there's an unpaired name, raise an error
                raise ValueError(f"Invalid case name format: {case_name}")

        except ValueError as e:
            print(f"Error parsing parameters from case directory '{case_name}': {e}")
            continue

        # Load the binary output data
        try:
            openfast_bin = get_binary_output_data(case_dir)
        except Exception as e:
            print(f"Error loading binary data for case '{case_name}': {e}")
            continue

        # Store in dictionary linking parameters to binary data
        parametric_data[tuple(param_values.items())] = openfast_bin

    return parametric_data


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


def plot_parametric_response(df_parametric, response_channel, independent, output_dir, plot_fc_data=None):
    """
    Plots the parametric response using the processed simulation DataFrame.

    Args:
        df_parametric (pd.DataFrame): DataFrame containing parametric analysis results.
        response_channel (str): The channel to be plotted on the y-axis.
        independent (str): The parameter to be plotted on the x-axis.
        output_dir (Path): The directory where the plot will be saved.
        plot_fc_data (str): FOCAL-1 data file identifier for additional validation data plotting.
    """
    # Ensure the output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load the FC data if needed
    fc_data = None
    if plot_fc_data:
        fc_data = load_fc_data(plot_fc_data, independent, response_channel)

    # Check if the specified response channel exists in the DataFrame
    if response_channel not in df_parametric.columns:
        print(f"Skipping plot for {response_channel}: not found in the DataFrame.")
        return

    # Extract the independent and response data
    x_vals = df_parametric[independent]
    y_vals = df_parametric[response_channel]

    # Compute y-axis limits
    y_min = y_vals.min()
    y_max = y_vals.max()

    # If FOCAL-1 data is available, include its range in the y-axis limits
    if fc_data is not None:
        fc_y_vals = fc_data.iloc[:, 1]  # Response values from FOCAL-1 data
        y_min = min(y_min, fc_y_vals.min())
        y_max = max(y_max, fc_y_vals.max())

    # Adjust the limits to add some padding for better visualization
    padding = 0.1 * (y_max - y_min)
    y_min -= padding
    y_max += padding

    # Plot the parametric response
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, 'o-', label=f"Simulation Data ({response_channel})")

    # Add FOCAL-1 validation data if available
    if fc_data is not None:
        plt.plot(
            fc_data.iloc[:, 0],  # Independent variable
            fc_data.iloc[:, 1],  # Response variable
            'o-',  # Line with circle markers
            color="red",
            label="FOCAL-1 Validation Data"
        )

    # Add labels, legend, and adjust the y-axis limits
    plt.xlabel(f"{independent} (Independent Variable)")
    plt.ylabel(f"{response_channel} (Response Channel)")
    plt.title(f"Parametric Response: {response_channel} vs {independent}")
    plt.ylim([y_min, y_max])
    plt.legend()
    plt.grid(True)

    # Save the plot
    plot_file = output_dir / f"parametric_response_{response_channel}_vs_{independent}.png"
    plt.savefig(plot_file, dpi=300)
    plt.close()

    print(f"Plot saved at {plot_file}")


def load_fc_data(fc_data_num: str, dependent, response):
    """
    Load the FOCAL-1 validation data for the specified load case.

    Args:
        fc_data_num (str): The load case number to load.

    Returns:
        pd.DataFrame: The FOCAL-1 validation data for the specified load case.
    """
    # Load the FOCAL-1 validation data for the specified load case
    fc_data_file = Path(__file__).parent / "data" / f"focal.campaign1.thr.{fc_data_num}.csv"
    df_fc = pd.read_csv(fc_data_file)
    df_fc.columns = df_fc.columns.str.strip()  # Strip leading/trailing whitespace from column names

    # Map OpenFAST columns to FOCAL-1 validation data columns
    # Column names: Time (sec), Wind Speed (m/s), Blade Pitch (deg), RPM [rpm], Rotor Thrust [N], Rotor Torque [Nm], Tower Top Fx [N], Tower Top Fy [N], Tower Top Fz [N], Tower Top Mx [Nm], Tower Top My [Nm], Tower Top Mz [Nm], BRBM flap [Nm], BRBM edge [Nm]
    column_mapping = {
        "Time": "Time (sec)",
        "WindVel1X": "Wind Speed (m/s)",
        "rotor_speed": "RPM [rpm]",
        "RtAeroPwer": "Rotor Power [W]",
        "RtAeroCt": "Rotor Thrust Coefficient [-]",
        "RtAeroCq": "Rotor Torque Coefficient [-]",
        "RtAeroFxh": "Rotor Thrust [N]",
        "RtAeroMxh": "Rotor Torque [Nm]",
        "Thrust": "Rotor Thrust [N]",
        "Torque": "Rotor Torque [Nm]",
        "RotThrust": "Rotor Thrust [N]",
        "RotTorq": "Rotor Torque [Nm]",
        "YawBrFxp": "Tower Top Fx [N]",
        "YawBrFyp": "Tower Top Fy [N]",
        "YawBrFzp": "Tower Top Fz [N]",
        "YawBrMxp": "Tower Top Mx [Nm]",
        "YawBrMyp": "Tower Top My [Nm]",
        "YawBrMzp": "Tower Top Mz [Nm]",
        "RootMxb1": "BRBM flap [Nm]",
        "RootMyb1": "BRBM edge [Nm]"
    }
    if column_mapping[dependent] not in df_fc.columns:
        print("Could not find dependent channel in FOCAL-1 validation data.")
        return None
    if column_mapping[response] not in df_fc.columns:
        print("Could not find response channel in FOCAL-1 validation data.")
        return None

    # Filter the data to plot only the specified dependent and response channels
    df_fc = df_fc[[column_mapping[dependent], column_mapping[response]]]

    return df_fc


def prepare_parametric_data(parametric_data, response_channels, independent, output_dir):
    """Prepares the parametric data for plotting, placing the parsed channel
    data in a pandas DataFrame.

    Args:
        parametric_data (_type_): _description_
        response_channels (_type_): _description_
        independent (_type_): _description_
        output_dir (_type_): _description_
    """
    # Ensure the output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create a DataFrame to store the parametric data
    df = pd.DataFrame()

    # Iterate over the parametric data
    for params, openfast_bin in parametric_data.items():
        # Convert params to a dictionary for easy access
        param_dict = dict(params)

        # Check if independent exists
        if independent not in param_dict:
            print(f"Skipping case due to missing independent parameter: {params}")
            continue

        # Initialize a dictionary to store the data for this case
        case_data = {independent: param_dict[independent]}

        # Iterate over the response channels
        for response_channel in response_channels:
            # Calculate response channel if needed
            if response_channel in ["Torque", "Thrust"]:
                if "RtAeroCt" not in openfast_bin.channels and "RtAeroCq" not in openfast_bin.channels:
                    print(f"Skipping case due to missing RtAeroCt or RtAeroCq data: {params}")
                    continue
                response_data = calculate_torque_or_thrust(response_channel, param_dict, openfast_bin)
            else:
                # Default behavior: use the channel directly
                if response_channel not in openfast_bin.channels:
                    print(f"Skipping case due to missing response channel: {params}")
                    continue
                response_data = openfast_bin[response_channel]

            # response_channel_plots = ['RtAeroFxh', 'RtAeroMxh', 'YawBrFxp', 'YawBrFyp',
            #                       'YawBrFzp', 'YawBrMxp', 'YawBrMyp', 'YawBrMzp', 'RootMxb1', 'RootMyb1']

            # Factored channels
            kN_channels = ["YawBrFxp", "YawBrFyp", "YawBrFzp", "YawBrMxp", "YawBrMyp", "YawBrMzp", "RootMxb1", "RootMyb1"]
            if response_channel in kN_channels:
                response_data = response_data * 1000  # Convert to N

            # Get the last value (steady state)
            print(f"Response data for {response_channel} in {params}: {response_data[-1:]}")
            # Lets get the mean value of the last 3/4 of the data set
            case_data[response_channel] = np.mean(response_data[-int(len(response_data)/4):])

        # Append the case data to the DataFrame
        df = pd.concat([df, pd.DataFrame([case_data])], ignore_index=True)

        # Sort by the independent variable
        df = df.sort_values(by=independent)

    return df


def dump_parametric_data(df: pd.DataFrame, output_dir: Path):
    """Dumps the parametric data to a CSV file.

    Args:
        df (_type_): _description_
    """
    df.to_csv(output_dir / "parametric_data.csv", index=False)
