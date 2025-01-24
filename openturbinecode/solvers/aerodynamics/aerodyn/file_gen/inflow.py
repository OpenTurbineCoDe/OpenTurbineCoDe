# flake8: noqa E501

from pathlib import Path
from openturbinecode.solvers.aerodynamics.aerodyn.options import InflowWindConfig
from .util import add_header, add_line, add_word


def generate_inflow_wind_config(location: Path, config: InflowWindConfig):
    """Generate the InflowWind input configuration file."""
    contents = ""
    contents = write_header(contents, config)
    contents = write_general_options(contents, config)
    contents = write_steady_wind_conditions(contents, config)
    contents = write_uniform_wind_conditions(contents, config)
    contents = write_turbsim_conditions(contents, config)
    contents = write_bladed_conditions(contents, config)
    contents = write_hawc_conditions(contents, config)
    contents = write_scaling_parameters(contents, config)
    contents = write_lidar_parameters(contents, config)
    contents = write_output_settings(contents, config)

    with open(location / f"{config.model.name}_IW.dat", "w") as file:
        file.write(contents)

    return None


def write_header(contents, config: InflowWindConfig):
    contents = add_header(contents, "InflowWind v3.01 Input File")
    contents = add_word(contents, "DTU 10MW onshore reference wind turbine v0.1 - OpenFAST v2.4")
    return contents


def write_general_options(contents, config: InflowWindConfig):
    contents = add_header(contents, "General Options")
    contents = add_line(contents, str(config.echo).upper(), "Echo", "Echo input data to <RootName>.ech (flag)")
    contents = add_line(contents, config.wind_type, "WindType", "Switch for wind file type (1=steady; 2=uniform; etc.)")
    contents = add_line(contents, f"{config.propagation_dir:.1f}", "PropagationDir", "Direction of wind propagation (degrees)")
    contents = add_line(contents, f"{config.upflow_angle:.1f}", "VFlowAng", "Upflow angle (degrees)")
    contents = add_line(contents, str(config.use_cubic_interpolation).upper(), "VelInterpCubic", "Use cubic interpolation for velocity in time")
    contents = add_line(contents, config.num_velocity_points, "NWindVel", "Number of points to output the wind velocity (0 to 9)")
    return contents


def write_steady_wind_conditions(contents, config: InflowWindConfig):
    contents = add_header(contents, "Parameters for Steady Wind Conditions [used only for WindType = 1]")
    contents = add_line(contents, f"{config.h_wind_speed:.2f}", "HWindSpeed", "Horizontal wind speed (m/s)")
    contents = add_line(contents, f"{config.ref_height:.2f}", "RefHt", "Reference height for horizontal wind speed (m)")
    contents = add_line(contents, f"{config.power_law_exp:.2f}", "PLExp", "Power law exponent")
    return contents


def write_uniform_wind_conditions(contents, config: InflowWindConfig):
    contents = add_header(contents, "Parameters for Uniform Wind File [used only for WindType = 2]")
    contents = add_line(contents, f'"{config.uniform_filename}"', "Filename_Uni", "Filename of time series data for uniform wind field")
    contents = add_line(contents, f"{config.uniform_ref_height:.2f}", "RefHt_Uni", "Reference height for horizontal wind speed (m)")
    contents = add_line(contents, f"{config.ref_length:.2f}", "RefLength", "Reference length for linear horizontal and vertical shear")
    return contents


def write_turbsim_conditions(contents, config: InflowWindConfig):
    contents = add_header(contents, "Parameters for Binary TurbSim Full-Field Files [used only for WindType = 3]")
    contents = add_line(contents, f'"{config.turbsim_filename}"', "Filename_BTS", "Name of the Full field wind file to use (.bts)")
    return contents


def write_bladed_conditions(contents, config: InflowWindConfig):
    contents = add_header(contents, "Parameters for Binary Bladed-style Full-Field Files [used only for WindType = 4]")
    contents = add_line(contents, f'"{config.bladed_rootname}"', "FilenameRoot", "Rootname of the full-field wind file to use (.wnd, .sum)")
    contents = add_line(contents, str(config.tower_file).upper(), "TowerFile", "Have tower file (.twr) (flag)")
    return contents


def write_hawc_conditions(contents, config: InflowWindConfig):
    contents = add_header(contents, "Parameters for HAWC-format Binary Files [Only used with WindType = 5]")
    contents = add_line(contents, f'"{config.hawc_file_u}"', "FileName_u", "Name of the file containing the u-component fluctuating wind (.bin)")
    contents = add_line(contents, f'"{config.hawc_file_v}"', "FileName_v", "Name of the file containing the v-component fluctuating wind (.bin)")
    contents = add_line(contents, f'"{config.hawc_file_w}"', "FileName_w", "Name of the file containing the w-component fluctuating wind (.bin)")
    contents = add_line(contents, config.hawc_nx, "nx", "Number of grids in the x direction")
    contents = add_line(contents, config.hawc_ny, "ny", "Number of grids in the y direction")
    contents = add_line(contents, config.hawc_nz, "nz", "Number of grids in the z direction")
    return contents


def write_scaling_parameters(contents, config: InflowWindConfig):
    contents = add_header(contents, "Scaling Parameters for Turbulence")
    contents = add_line(contents, config.scale_method, "ScaleMethod", "Turbulence scaling method")
    contents = add_line(contents, f"{config.scale_factor_x:.1f}", "SFx", "Turbulence scaling factor for the x direction")
    contents = add_line(contents, f"{config.scale_factor_y:.1f}", "SFy", "Turbulence scaling factor for the y direction")
    contents = add_line(contents, f"{config.scale_factor_z:.1f}", "SFz", "Turbulence scaling factor for the z direction")
    return contents


def write_lidar_parameters(contents, config: InflowWindConfig):
    contents = add_header(contents, "LIDAR Parameters")
    contents = add_line(contents, config.lidar_sensor_type, "SensorType", "Switch for lidar configuration")
    contents = add_line(contents, config.lidar_num_pulse_gates, "NumPulseGate", "Number of lidar measurement gates")
    return contents


def write_output_settings(contents, config: InflowWindConfig):
    contents = add_header(contents, "Output Settings")
    contents = add_line(contents, str(config.sum_print).upper(), "SumPrint", "Print summary data to <RootName>.IfW.sum (flag)")
    for output in config.output_list:
        contents = add_word(contents, f'"{output}"')
    contents = add_word(contents, "END of input file")
    return contents
