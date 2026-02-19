# flake8: noqa: E501

from pathlib import Path
from ..options import AeroDynDriverConfig
from .util import add_header, add_word, add_line, add_table_entry


def generate_aerodyn_standalone_config(location: Path, config: AeroDynDriverConfig):
    """Generate the AeroDyn input configuration file.
    """

    contents = ""
    contents = write_header(contents, config)
    contents = write_input(contents, config)
    contents = write_environmental(contents, config)
    contents = write_inflow(contents, config)
    contents = write_turbine_data(contents, config)
    contents = write_turbine_geometry(contents, config)
    contents = write_turbine_motion(contents, config)
    contents = write_time_dependent_analysis(contents, config)
    contents = write_combined_case_analysis(contents, config)
    contents = write_outputs(contents, config)

    with open(location / f"{config.model.name}_ADdriver.inp", "w") as file:
        file.write(contents)

    return None

def write_header(contents, config: AeroDynDriverConfig):
    # Header
    contents = add_header(contents, "AeroDyn Standalone Input File")
    contents = add_word(contents, "Fixed")

    return contents

def write_input(contents, config: AeroDynDriverConfig):
    contents = add_header(contents, "Input Configuration")
    contents = add_line(contents, "False", "Echo", "Echo input data to <RootName>.ech (flag)")
    contents = add_line(contents, str(config.mhk_system), "MHK", "MHK turbine type (switch) (0: not an MHK turbine, 1: fixed MHK, 2: floating MHK)")
    contents = add_line(contents, config.analysis_type, "AnalysisType", "Analysis type (1: multiple turbines, 2: one turbine, 3: one, combined case)")
    contents = add_line(contents, f"{config.t_max:.2f}", "TMax", "Total run time (s)")
    contents = add_line(contents, f"{config.dt:.4f}", "DT", "Simulation time step (s)")
    contents = add_line(contents, f'"{config.aerodyn_file}"', "AeroFile", "Primary AeroDyn input file")

    return contents

def write_environmental(contents, config: AeroDynDriverConfig):
    # Environmental Conditions
    contents = add_header(contents, "Environmental Conditions")
    contents = add_line(contents, f"{config.air_density:.3f}", "FldDens", "Working fluid density (kg/m^3)")
    contents = add_line(contents, f"{config.kinematic_viscosity:.4E}", "KinVisc", "Kinematic viscosity (m^2/s)")
    contents = add_line(contents, f"{config.speed_of_sound:.1f}", "SpdSound", "Speed of sound (m/s)")
    contents = add_line(contents, f"{config.atmospheric_pressure:.1f}", "Patm", "Atmospheric pressure (Pa)")
    contents = add_line(contents, f"{config.vapor_pressure:.1f}", "Pvap", "Vapor pressure (Pa)")
    contents = add_line(contents, f"{config.water_depth:.1f}", "WtrDpth", "Water depth (m)")

    return contents

def write_inflow(contents, config: AeroDynDriverConfig):
    contents = add_header(contents, "Inflow Data")
    contents = add_line(contents, config.comp_inflow, "CompInflow", "Compute inflow velocities (0=Steady, 1=InflowWind)")
    contents = add_line(contents, f'"{config.inflow_wind_file}"', "InflowFile", "InflowWind input file [used only when CompInflow=1]")
    contents = add_line(contents, f"{config.horizontal_wind_speed:.2f}", "HWindSpeed", "Horizontal wind speed (m/s) [used only when CompInflow=0]")
    contents = add_line(contents, f"{config.wind_ref_height:.1f}", "RefHt", "Reference height for wind speed (m)")
    contents = add_line(contents, f"{config.power_law_exp:.4f}", "PLExp", "Power law exponent")

    return contents

def write_turbine_data(contents, config: AeroDynDriverConfig):
    # Turbine Data
    contents = add_header(contents, "Turbine Data")
    contents = add_line(contents, config.num_turbines, "NumTurbines", "Number of turbines")

    return contents

def write_turbine_geometry(contents, config: AeroDynDriverConfig):
    """Write turbine geometry based on BasicHAWTFormat."""
    contents = add_header(contents, "Turbine Geometry")
    
    if config.basic_hawt_format:
        # Basic HAWT format settings
        contents = add_line(contents, str(config.basic_hawt_format), "BasicHAWTFormat(1)", "Basic HAWT input format (True/False)")
        contents = add_line(contents, ",".join(f"{v:.2f}" for v in config.base_origin), "BaseOriginInit(1)", "Coordinate of tower base in base coordinates (m)")
        contents = add_line(contents, config.num_blades, "NumBlades(1)", "Number of blades")
        contents = add_line(contents, f"{config.hub_origin[2]:.2f}", "HubRad(1)", "Hub radius (m)")  # Assume z-coordinate is radius
        contents = add_line(contents, f"{config.nacelle_origin[2]:.2f}", "HubHt(1)", "Hub height (m)")
        contents = add_line(contents, f"{config.hub_origin[0]:.2f}", "Overhang(1)", "Overhang (m)")
        contents = add_line(contents, f"{config.hub_orientation[1]:.2f}", "ShftTilt(1)", "Shaft tilt (deg)")
        contents = add_line(contents, f"{config.hub_orientation[2]:.2f}", "Precone(1)", "Blade precone (deg)")
        contents = add_line(contents, f"{config.hub_origin[2] / 2:.2f}", "Twr2Shft(1)", "Vertical distance from tower-top to rotor shaft (m)")
    else:
        # Extended format settings
        contents = add_line(contents, str(config.basic_hawt_format), "BasicHAWTFormat(1)", "Basic HAWT input format (True/False)")
        contents = add_line(contents, ",".join(f"{v:.2f}" for v in config.base_origin), "BaseOriginInit(1)", "x,y,z coordinates of turbine base origin (m)")
        contents = add_line(contents, ",".join(f"{v:.1f}" for v in config.base_orientation), "BaseOrientationInit(1)", "Successive rotations (theta_x, theta_y, theta_z) of the base frame (deg)")
        contents = add_line(contents, str(config.has_tower).upper(), "HasTower(1)", "True if turbine has a tower (flag)")
        contents = add_line(contents, str(config.hawt_projection).upper(), "HAWTprojection(1)", "True if turbine is a horizontal axis turbine (flag)")
        contents = add_line(contents, ",".join(f"{v:.2f}" for v in config.tower_base), "TwrOrigin_t(1)", "Coordinate of tower base in base coordinates (m)")
        contents = add_line(contents, ",".join(f"{v:.2f}" for v in config.nacelle_origin), "NacOrigin_t(1)", "x,y,z coordinates of nacelle origin in base coordinates (m)")
        contents = add_line(contents, ",".join(f"{v:.2f}" for v in config.hub_origin), "HubOrigin_n(1)", "x,y,z coordinates of hub origin in nacelle coordinates (m)")
        contents = add_line(contents, ",".join(f"{v:.1f}" for v in config.hub_orientation), "HubOrientation_n(1)", "Rotations (theta_x, theta_y, theta_z) defining hub orientation from nacelle (deg)")
        # Blade settings
        contents = add_header(contents, "Turbine Blades")
        contents = add_line(contents, config.num_blades, "NumBlades(1)", "Number of blades for the current rotor (-)")
        for i in range(config.num_blades):
            contents = add_line(contents, ",".join(f"{v:.2f}" for v in config.blade_origins[i]), f"BldOrigin_h(1_{i+1})", f"Origin of blade {i+1} wrt. hub origin in hub coordinates (m)")
            contents = add_line(contents, ",".join(f"{v:.1f}" for v in config.blade_orientations[i]), f"BldOrientation_h(1_{i+1})", f"Orientation of blade {i+1} wrt. hub (azimuth, precone, pitch) (deg)")
            contents = add_line(contents, f"{config.blade_hub_radii[i]:.1f}", f"BldHubRad_bl(1_{i+1})", f"z-offset in blade coordinates of blade {i+1} where radial input data start (m)")
    return contents



def write_turbine_motion(contents, config: AeroDynDriverConfig):
    # Turbine Motion
    contents = add_header(contents, "Turbine Motion")
    contents = add_line(contents, config.motion_type, "BaseMotionType(1)", "Base motion type (0: fixed, 1: sinusoidal, 2: arbitrary)")
    contents = add_line(contents, "0", "DegreeOfFreedom(1)", "Degree of freedom (1=xg, 2=yg, ..., 6=theta_zg)")
    contents = add_line(contents, "0", "Amplitude(1)", "Amplitude of sinusoidal motion")
    contents = add_line(contents, "0", "Frequency(1)", "Frequency of sinusoidal motion")
    contents = add_line(contents, '"unused"', "BaseMotionFileName(1)", "Arbitrary base motion filename [used only when BaseMotionType=2]")
    contents = add_line(contents, f"{config.nacelle_yaw:.1f}", "NacYaw(1)", "Yaw angle of nacelle (deg)")
    contents = add_line(contents, f'{config.rotor_speed}', "RotSpeed(1)", "Rotor speed (rpm)")
    contents = add_line(contents, f"{config.blade_pitch:.1f}", "BldPitch(1)", "Blade pitch (deg)")

    return contents

def write_time_dependent_analysis(contents, config: AeroDynDriverConfig):
    # Time Dependent Analysis
    contents = add_header(contents, "Time-dependent Analysis")
    contents = add_line(contents, f'"{config.timeseries_file}"', "TimeAnalysisFileName", "Time series filename (6 columns: Time, HWndSpeed, PLExp, RotSpd, Pitch, Yaw)")

    return contents

def write_combined_case_analysis(contents, config: AeroDynDriverConfig):
    # Combined-Case Analysis
    contents = add_header(contents, "Combined-Case Analysis")
    contents = add_line(contents, "0", "NumCases", "Number of cases to run")
    contents = add_table_entry(contents, ["HWndSpeed", "PLExp", "RotSpd", "Pitch", "Yaw", "dT", "Tmax", "DOF", "Amplitude", "Frequency"])
    contents = add_table_entry(contents, ["(m/s)", "(-)", "(rpm)", "(deg)", "(deg)", "(s)", "(s)", "(-)", "(-)", "(Hz)"])

    return contents

def write_outputs(contents, config: AeroDynDriverConfig):
    # Outputs
    contents = add_header(contents, "Output Settings")

    contents = add_line(contents, '"ES15.8E2"', "OutFmt", "Format for text output (10 characters)")
    contents = add_line(contents, "1", "OutFileFmt", "Tabular output file format (1: text, 2: binary, 3: both)")
    contents = add_line(contents, "0", "WrVTK", "VTK visualization output (0: none, 1: animation)")
    contents = add_line(contents, "1", "WrVTK_Type", "VTK visualization type (1: surfaces, 2: lines, 3: both)")
    contents = add_line(contents, "0", "VTKHubRad", "VTK hub radius (m)")
    contents = add_line(contents, "0,0,0,0,0,0", "VTKNacDim", "VTK nacelle dimensions (x0, y0, z0, Lx, Ly, Lz)")

    return contents