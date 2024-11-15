import pandas as pd
import numpy as np

from fnmatch import fnmatch

from openturbinecode.utils import plotter as plot

# Load the data
from pCrunch import LoadsAnalysis, FatigueParams
from pCrunch.io import load_FAST_out


from pathlib import Path


output_dir = Path("D:/") / "GitHub" / "Solvers" / "openfast" / "test_case"


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


def get_and_plot_time_series(openfast_bin, channel: str):
    try:
        df: pd.DataFrame = openfast_bin.df
        unit = str(openfast_bin.units[np.argmax(openfast_bin.channels == channel)])
        plot_data = df[['Time', channel]].to_numpy()
        plot.time_series(plot_data, ylabel=f'{channel} [{unit}]', title=f'{channel} Time Series',
                         filename=f'{output_dir / f"{channel}_Time_Series.svg"}')
    except KeyError:
        print(f"Channel '{channel}' not found in OpenFAST output file.")
    except Exception as e:
        print(f"An error occurred while plotting '{channel}' time series: {e}")

    return None


# Platform Response
get_and_plot_time_series(openfast_bin, 'PtfmHeave')
get_and_plot_time_series(openfast_bin, 'PtfmPitch')
get_and_plot_time_series(openfast_bin, 'PtfmSurge')
get_and_plot_time_series(openfast_bin, 'PtfmRoll')
get_and_plot_time_series(openfast_bin, 'PtfmSway')
get_and_plot_time_series(openfast_bin, 'PtfmYaw')

# Blade 1 Response
get_and_plot_time_series(openfast_bin, 'BldPitch1')
get_and_plot_time_series(openfast_bin, 'IPDefl1')
get_and_plot_time_series(openfast_bin, 'OoPDefl1')
get_and_plot_time_series(openfast_bin, 'RootFxb1')
get_and_plot_time_series(openfast_bin, 'RootFyb1')
get_and_plot_time_series(openfast_bin, 'RootFzb1')
get_and_plot_time_series(openfast_bin, 'TipDxb1')
get_and_plot_time_series(openfast_bin, 'TipDyb1')
get_and_plot_time_series(openfast_bin, 'TipDzb1')

# Rotor Response
get_and_plot_time_series(openfast_bin, 'RotSpeed')
get_and_plot_time_series(openfast_bin, 'RotThrust')
get_and_plot_time_series(openfast_bin, 'RotTorq')

# Aero Responses
get_and_plot_time_series(openfast_bin, 'RtAeroPwr')
get_and_plot_time_series(openfast_bin, 'RtAeroCp')
get_and_plot_time_series(openfast_bin, 'RtAeroCq')
get_and_plot_time_series(openfast_bin, 'RtAeroCt')
get_and_plot_time_series(openfast_bin, 'RtAeroFxh')
get_and_plot_time_series(openfast_bin, 'RtAeroMxh')
