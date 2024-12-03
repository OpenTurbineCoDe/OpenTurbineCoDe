import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
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


def plot_parametric_response(parametric_data, response_channel, dependent, output_dir):
    """
    Plots the parametric response of the OpenFAST case directories.

    Args:
        parametric_data (dict): A dictionary where keys are parameter combinations and values are
                                the binary output data from OpenFAST.
                                Keys are tuples of (parameter_name, parameter_value).
        response_channel (str): The channel to be plotted on the y-axis.
        dependent (str): The parameter to be plotted on the x-axis.
        output_dir (Path): The directory where the plot will be saved.
    """

    # Ensure the output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare a dictionary to organize data by the remaining parameter(s)
    grouped_data = defaultdict(list)

    for params, openfast_bin in parametric_data.items():
        # Convert params to a dictionary for easy access
        param_dict = dict(params)

        # Check if both dependent and response channel exist
        if dependent not in param_dict or response_channel not in openfast_bin.channels:
            print(f"Skipping case due to missing data: {params}")
            continue

        # Group data by parameters other than the dependent
        group_key = tuple((k, v) for k, v in params if k != dependent)
        grouped_data[group_key].append((param_dict[dependent], openfast_bin[response_channel]))

    # Plot each group
    plt.figure(figsize=(10, 6))
    ylim_max = 0
    for group_key, data in grouped_data.items():
        data.sort(key=lambda x: x[0])  # Sort by the dependent variable
        x_vals = [x[0] for x in data]
        y_vals = [np.mean(y) for _, y in data]  # Compute the mean of the response channel
        ylim_max = max(ylim_max, max(y_vals))

        # Create a label based on the group key
        label = ", ".join([f"{k}={v}" for k, v in group_key])
        plt.plot(x_vals, y_vals, label=label)

    # Add labels, legend, and save the plot
    plt.xlabel(f"{dependent} (Dependent Variable)")
    plt.ylabel(f"{response_channel} (Response Channel)")
    plt.title("Parametric Response")
    plt.legend(title="Other Parameters")
    plt.grid(True)
    plt.ylim([0, ylim_max * 1.1])

    # Save the plot
    plot_file = output_dir / f"parametric_response_{response_channel}_vs_{dependent}.png"
    plt.savefig(plot_file, dpi=300)
    plt.close()

    print(f"Plot saved at {plot_file}")
