# flake8: noqa E501

from pathlib import Path
from openturbinecode.solvers.aerostructural.openfast.options import InflowWindConfig
from .util import add_header, add_line, add_word

OPENFAST_VERSION = 300

def generate_inflow_wind_config(location: Path, config: InflowWindConfig):
    """Generate the InflowWind input configuration file."""
    contents = """------- InflowWind v3.01.* INPUT FILE -------------------------------------------------------------------------
IEA 15 MW Offshore Reference Turbine
"""

    # Add all sections
    contents = write_general_options(contents, config)
    contents = write_steady_wind_conditions(contents, config)
    contents = write_uniform_wind_conditions(contents, config)
    contents = write_turbsim_conditions(contents, config)
    contents = write_bladed_conditions(contents, config)
    contents = write_hawc_conditions(contents, config)
    contents = write_scaling_parameters(contents, config)
    contents = write_mean_wind_profile(contents, config)
    contents = write_lidar_parameters(contents, config)
    contents = write_output_settings(contents, config)

    with open(location / f"{config.model.name}_IW.dat", "w") as file:
        file.write(contents)

    return None

def write_general_options(contents, config: InflowWindConfig):
    contents = add_header(contents, "General Options")
    contents = add_line(contents, str(config.echo).upper(), "Echo", "Echo input data to <RootName>.ech (flag)")
    contents = add_line(contents, config.wind_type, "WindType", "Switch for wind file type (1=steady; 2=uniform; etc.)")
    contents = add_line(contents, f"{config.propagation_dir:.1f}", "PropagationDir", "Direction of wind propagation (degrees)")
    contents = add_line(contents, f"{config.upflow_angle:.1f}", "VFlowAng", "Upflow angle (degrees)")
    if OPENFAST_VERSION > 300:
        contents = add_line(contents, str(config.use_cubic_interpolation).upper(), "VelInterpCubic", "Use cubic interpolation for velocity in time")
    contents = add_line(contents, config.num_velocity_points, "NWindVel", "Number of points to output the wind velocity (0 to 9)")
    contents = add_line(contents, f"{config.wind_vxi_list[0]:.1f}", "WindVxiList", "List of coordinates in the inertial X direction (m)")
    contents = add_line(contents, f"{config.wind_vyi_list[0]:.1f}", "WindVyiList", "List of coordinates in the inertial Y direction (m)")
    contents = add_line(contents, f"{config.wind_vzi_list[0]:.1f}", "WindVziList", "List of coordinates in the inertial Z direction (m)")
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
    contents = add_line(contents, f"{config.hawc_dx:.1f}", "dx", "Distance between points in the x direction (m)")
    contents = add_line(contents, f"{config.hawc_dy:.1f}", "dy", "Distance between points in the y direction (m)")
    contents = add_line(contents, f"{config.hawc_dz:.1f}", "dz", "Distance between points in the z direction (m)")
    contents = add_line(contents, f"{config.hawc_ref_height:.1f}", "RefHt_Hawc", "Reference height (m)")
    return contents

def write_scaling_parameters(contents, config: InflowWindConfig):
    contents = add_header(contents, "Scaling Parameters for Turbulence")
    contents = add_line(contents, config.scale_method, "ScaleMethod", "Turbulence scaling method")
    contents = add_line(contents, f"{config.scale_factor_x:.1f}", "SFx", "Turbulence scaling factor for the x direction")
    contents = add_line(contents, f"{config.scale_factor_y:.1f}", "SFy", "Turbulence scaling factor for the y direction")
    contents = add_line(contents, f"{config.scale_factor_z:.1f}", "SFz", "Turbulence scaling factor for the z direction")
    contents = add_line(contents, f"{config.sigma_x:.1f}", "SigmaFx", "Turbulence standard deviation for x direction")
    contents = add_line(contents, f"{config.sigma_y:.1f}", "SigmaFy", "Turbulence standard deviation for y direction")
    contents = add_line(contents, f"{config.sigma_z:.1f}", "SigmaFz", "Turbulence standard deviation for z direction")
    return contents

def write_mean_wind_profile(contents, config: InflowWindConfig):
    contents = add_header(contents, "Mean Wind Profile Parameters")
    contents = add_line(contents, f"{config.h_wind_speed:.1f}", "URef", "Mean u-component wind speed at the reference height (m/s)")
    contents = add_line(contents, config.wind_profile_type, "WindProfile", "Wind profile type (0=constant;1=logarithmic,2=power law)")
    contents = add_line(contents, f"{config.power_law_exp_hawc:.2f}", "PLExp_Hawc", "Power law exponent (-) (used for PL wind profile type only)")
    contents = add_line(contents, f"{0.03}", "Z0", "Surface roughness length (m) (used for LG wind profile type only)")
    contents = add_line(contents, f"{config.x_offset:.2f}", "XOffset", "Initial offset in +x direction (shift of wind box) (-)")

    return contents

def write_lidar_parameters(contents, config: InflowWindConfig):
    if OPENFAST_VERSION > 300:
        contents = add_header(contents, "LIDAR Parameters")
        contents = add_line(contents, config.lidar_sensor_type, "SensorType", "Switch for lidar configuration")
        contents = add_line(contents, config.lidar_num_pulse_gates, "NumPulseGate", "Number of lidar measurement gates")
        contents = add_line(contents, f"{config.lidar_pulse_spacing:.1f}", "PulseSpacing", "Distance between range gates (m)")
        contents = add_line(contents, config.lidar_num_beams, "NumBeam", "Number of lidar measurement beams")
        contents = add_line(contents, f"{config.lidar_focal_distance_x:.1f}", "FocalDistanceX", "Focal distance in x direction (m)")
        contents = add_line(contents, f"{config.lidar_focal_distance_y:.1f}", "FocalDistanceY", "Focal distance in y direction (m)")
        contents = add_line(contents, f"{config.lidar_focal_distance_z:.1f}", "FocalDistanceZ", "Focal distance in z direction (m)")
        contents = add_line(contents, " ".join(f"{value:.1f}" for value in config.lidar_rotor_apex_offset),  "RotorApexOffsetPos", "Offset of lidar from hub height (m)")
        contents = add_line(contents, f"{config.lidar_ref_speed:.1f}", "URefLid", "Reference average wind speed for lidar (m/s)")
        contents = add_line(contents, f"{config.measurement_interval:.2f}", "MeasurementInterval", "Time between each measurement (s)")
        contents = add_line(contents, str(config.lidar_radial_velocity).upper(), "LidRadialVel", "Return radial component (TRUE/FALSE)")
        contents = add_line(contents, config.consider_hub_motion, "ConsiderHubMotion", "Consider hub motion's impact on lidar measurements")
    return contents

def write_output_settings(contents, config: InflowWindConfig):
    contents = add_header(contents, "Output Settings")
    contents = add_line(contents, str(config.sum_print).upper(), "SumPrint", "Print summary data to <RootName>.IfW.sum (flag)")
    contents = add_word(contents, "OutList The next line(s) contains a list of output parameters.")
    for output in config.output_list:
        contents = add_word(contents, f'"{output}"')
    contents = add_word(contents, "END of input file")
    return contents
