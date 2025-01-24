# flake8: noqa: E501
from pathlib import Path
from openturbinecode.solvers.aerostructural.openfast.options import InflowWindConfig
from .util import add_header, add_line

def generate_inflow_wind_config(location: Path, config: InflowWindConfig):
    """Generate the InflowWind input file."""
    contents = """------- INFLOWWIND v3.01.* INPUT FILE -------------------------------------------
DTU 10MW onshore reference wind turbine v0.1 - OpenFAST v2.4
"""

    # Add all sections
    contents = write_general_options(contents, config)
    contents = write_steady_wind_conditions(contents, config)
    contents = write_uniform_wind_conditions(contents, config)

    # Write to file
    with open(location / f"{config.model.name}_IW.dat", "w") as file:
        file.write(contents)

    return contents

def write_general_options(contents, config: InflowWindConfig):
    contents = add_header(contents, "General Options")
    contents = add_line(contents, config.echo, "Echo", "Echo input data to <RootName>.ech")
    contents = add_line(contents, config.wind_type, "WindType", "Switch for wind file type")
    contents = add_line(contents, config.propagation_dir, "PropagationDir", "Direction of wind propagation (deg)")
    return contents

def write_steady_wind_conditions(contents, config: InflowWindConfig):
    contents = add_header(contents, "Parameters for Steady Wind Conditions")
    contents = add_line(contents, config.h_wind_speed, "HWindSpeed", "Horizontal wind speed (m/s)")
    contents = add_line(contents, config.ref_height, "RefHt", "Reference height for horizontal wind speed (m)")
    contents = add_line(contents, config.power_law_exp, "PLExp", "Power law exponent")
    return contents

def write_uniform_wind_conditions(contents, config: InflowWindConfig):
    contents = add_header(contents, "Parameters for Uniform Wind File")
    contents = add_line(contents, config.uniform_filename, "Filename_Uni", "Filename of time series data for uniform wind field")
    contents = add_line(contents, config.uniform_ref_height, "RefHt_Uni", "Reference height for horizontal wind speed (m)")
    return contents
