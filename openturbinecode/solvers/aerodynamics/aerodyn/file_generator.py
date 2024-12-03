# flake8: noqa: E501
from pathlib import Path
from openturbinecode.configs.pathing import PROJECT_ROOT
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.solvers.aerodynamics.aerodyn.options import (AeroDynInputConfig,
                                                                  AeroDynConfig,
                                                                  InflowWindConfig)

def add_line(contents:str, value:str, identifier:str, description:str):
    """Add a line to the configuration file."""
    return contents + f"{value:>20}   {identifier:<14} - {description}\n"

def add_header(contents:str, header:str):
    """Add a header to the configuration file."""
    return contents + f"===== {header} {'='*(80-len(header))}\n"

def add_table_entry(contents:str, header_cols:list):
    """Add a table header to the configuration file."""
    return contents + " ".join([f"{col:<14}" for col in header_cols]) + "\n"

def add_word(contents:str, word:str):
    """Add a word to the configuration file."""
    return contents + f"{word}\n"

def generate_aerodyn_standalone_config(location: Path, config: AeroDynInputConfig):
    """Generate the AeroDyn input configuration file."""
    contents = ""
    # Header
    contents = add_header(contents, "AeroDyn Standalone Input File")
    contents = add_word(contents, "Fixed")
    # Input Configuration
    contents = add_header(contents, "Input Configuration")
    contents = add_line(contents, "False", "Echo", "Echo input data to <RootName>.ech (flag)")
    contents = add_line(contents, str(config.mhk_system), "MHK", "MHK turbine type (switch) (0: not an MHK turbine, 1: fixed MHK, 2: floating MHK)")
    contents = add_line(contents, config.analysis_type, "AnalysisType", "Analysis type (1: multiple turbines, 2: one turbine, 3: one, combined case)")
    contents = add_line(contents, f"{config.t_max:.2f}", "TMax", "Total run time (s)")
    contents = add_line(contents, f"{config.dt:.4f}", "DT", "Simulation time step (s)")
    contents = add_line(contents, f'"{config.aerodyn_file}"', "AeroFile", "Primary AeroDyn input file")
    # Environmental Conditions
    contents = add_header(contents, "Environmental Conditions")
    contents = add_line(contents, f"{config.air_density:.3f}", "FldDens", "Working fluid density (kg/m^3)")
    contents = add_line(contents, f"{config.kinematic_viscosity:.4E}", "KinVisc", "Kinematic viscosity (m^2/s)")
    contents = add_line(contents, f"{config.speed_of_sound:.1f}", "SpdSound", "Speed of sound (m/s)")
    contents = add_line(contents, f"{config.atmospheric_pressure:.1f}", "Patm", "Atmospheric pressure (Pa)")
    contents = add_line(contents, f"{config.vapor_pressure:.1f}", "Pvap", "Vapor pressure (Pa)")
    contents = add_line(contents, f"{config.water_depth:.1f}", "WtrDpth", "Water depth (m)")
    # Inflow Data
    contents = add_header(contents, "Inflow Data")
    contents = add_line(contents, config.comp_inflow, "CompInflow", "Compute inflow velocities (0=Steady, 1=InflowWind)")
    contents = add_line(contents, f'"{config.inflow_wind_file}"', "InflowFile", "InflowWind input file [used only when CompInflow=1]")
    contents = add_line(contents, f"{config.horizontal_wind_speed:.2f}", "HWindSpeed", "Horizontal wind speed (m/s) [used only when CompInflow=0]")
    contents = add_line(contents, f"{config.wind_ref_height:.1f}", "RefHt", "Reference height for wind speed (m)")
    contents = add_line(contents, f"{config.power_law_exp:.4f}", "PLExp", "Power law exponent")
    # Turbine Data
    contents = add_header(contents, "Turbine Data")
    contents = add_line(contents, config.num_turbines, "NumTurbines", "Number of turbines")
    # Turbine Geometry
    contents = add_header(contents, "Turbine Geometry")
    contents = add_line(contents, str(config.basic_hawt_format), "BasicHAWTFormat(1)", "Basic HAWT input format (True/False)")
    contents = add_line(contents, "0,0,0", "BaseOriginInit(1)", "Coordinate of tower base in base coordinates (m)")
    contents = add_line(contents, config.num_blades, "NumBlades(1)", "Number of blades")
    contents = add_line(contents, f"{config.hub_radius:.2f}", "HubRad(1)", "Hub radius (m)")
    contents = add_line(contents, f"{config.hub_height:.2f}", "HubHt(1)", "Hub height (m)")
    contents = add_line(contents, f"{config.hub_overhang:.2f}", "Overhang(1)", "Overhang (m)")
    contents = add_line(contents, "0", "ShftTilt(1)", "Shaft tilt (deg)")
    contents = add_line(contents, "5.0", "Precone(1)", "Blade precone (deg)")
    contents = add_line(contents, "1.2", "Twr2Shft(1)", "Vertical distance from tower-top to rotor shaft (m)")
    # Turbine Motion
    contents = add_header(contents, "Turbine Motion")
    contents = add_line(contents, config.motion_type, "BaseMotionType(1)", "Base motion type (0: fixed, 1: sinusoidal, 2: arbitrary)")
    contents = add_line(contents, "0", "DegreeOfFreedom(1)", "Degree of freedom (1=xg, 2=yg, ..., 6=theta_zg)")
    contents = add_line(contents, "0", "Amplitude(1)", "Amplitude of sinusoidal motion")
    contents = add_line(contents, "0", "Frequency(1)", "Frequency of sinusoidal motion")
    contents = add_line(contents, '"unused"', "BaseMotionFileName(1)", "Arbitrary base motion filename [used only when BaseMotionType=2]")
    contents = add_line(contents, f"{config.nacelle_yaw:.1f}", "NacYaw(1)", "Yaw angle of nacelle (deg)")
    contents = add_line(contents, f"{config.rotor_speed:.1f}", "RotSpeed(1)", "Rotor speed (rpm)")
    contents = add_line(contents, f"{config.blade_pitch:.1f}", "BldPitch(1)", "Blade pitch (deg)")
    # Time Dependent Analysis
    contents = add_header(contents, "Time-dependent Analysis")
    contents = add_line(contents, f'"{config.timeseries_file}"', "TimeAnalysisFileName", "Time series filename (6 columns: Time, HWndSpeed, PLExp, RotSpd, Pitch, Yaw)")
    # Combined-Case Analysis
    contents = add_header(contents, "Combined-Case Analysis")
    contents = add_line(contents, "0", "NumCases", "Number of cases to run")
    contents = add_table_entry(contents, ["HWndSpeed", "PLExp", "RotSpd", "Pitch", "Yaw", "dT", "Tmax", "DOF", "Amplitude", "Frequency"])
    contents = add_table_entry(contents, ["(m/s)", "(-)", "(rpm)", "(deg)", "(deg)", "(s)", "(s)", "(-)", "(-)", "(Hz)"])
    # Outputs
    contents = add_header(contents, "Output Settings")
    contents = add_line(contents, '"ES15.8E2"', "OutFmt", "Format for text output (10 characters)")
    contents = add_line(contents, "2", "OutFileFmt", "Tabular output file format (1: text, 2: binary, 3: both)")
    contents = add_line(contents, "0", "WrVTK", "VTK visualization output (0: none, 1: animation)")
    contents = add_line(contents, "1", "WrVTK_Type", "VTK visualization type (1: surfaces, 2: lines, 3: both)")
    contents = add_line(contents, "0", "VTKHubRad", "VTK hub radius (m)")
    contents = add_line(contents, "0,0,0,0,0,0", "VTKNacDim", "VTK nacelle dimensions (x0, y0, z0, Lx, Ly, Lz)")

    with open(location / "DTU_10MW_ADdriver.inp", "w") as file:
        file.write(contents)

    return None


def generate_aerodyn_config(location: Path, config: AeroDynConfig):
    """Generate the AeroDyn input file for OpenFAST."""
    contents = ""
    # Header
    contents = add_header(contents, "AeroDyn v15 Input File")
    contents = add_word(contents, "DTU 10MW onshore reference wind turbine v0.1 - OpenFAST v3.5.3")
    # General Options
    contents = add_header(contents, "General Options")
    contents = add_line(contents, str(config.echo).upper(), "Echo", "Echo the input to <RootName>.AD.ech (flag)")
    contents = add_line(contents, f'"{config.dt_aero}"', "DTAero", "Time interval for aerodynamic calculations (s)")
    contents = add_line(contents, config.wake_model, "WakeMod", "Type of wake/induction model (0=none, 1=BEMT, 2=DBEMT)")
    contents = add_line(contents, config.airfoil_aero_model, "AFAeroMod", "Type of blade airfoil aerodynamics model (1=steady model, 2=Beddoes-Leishman unsteady model)")
    contents = add_line(contents, config.tower_potential_flow, "TwrPotent", "Type tower influence on wind based on potential flow around the tower (0=none, 1=baseline potential flow, 2=potential flow with Bak correction)")
    contents = add_line(contents, str(config.tower_shadow).upper(), "TwrShadow", "Calculate tower influence on wind based on downstream tower shadow (flag)")
    contents = add_line(contents, str(config.tower_aero).upper(), "TwrAero", "Calculate tower aerodynamic loads (flag)")
    contents = add_line(contents, str(config.frozen_wake).upper(), "FrozenWake", "Assume frozen wake during linearization (flag)")
    contents = add_line(contents, str(config.cavitation_check).upper(), "CavitCheck", "Perform cavitation check (flag)")
    contents = add_line(contents, str(config.buoyancy_effects).upper(), "Buoyancy", "Include buoyancy effects (flag)")
    contents = add_line(contents, str(config.compute_acoustics).upper(), "CompAA", "Flag to compute AeroAcoustics calculation")
    contents = add_line(contents, f'"{config.acoustics_input_file}"', "AA_InputFile", "Aeroacoustics input file")
    # Environmental Conditions
    contents = add_header(contents, "Environmental Conditions")
    contents = add_line(contents, f"{config.air_density:.3f}", "AirDens", "Air density (kg/m^3)")
    contents = add_line(contents, f"{config.kinematic_viscosity:.3E}", "KinVisc", "Kinematic air viscosity (m^2/s)")
    contents = add_line(contents, f"{config.speed_of_sound:.2f}", "SpdSound", "Speed of sound (m/s)")
    contents = add_line(contents, f"{config.atmospheric_pressure:.1f}", "Patm", "Atmospheric pressure (Pa)")
    contents = add_line(contents, f"{config.vapor_pressure:.1f}", "Pvap", "Vapour pressure of fluid (Pa)")
    # Blade-Element/Momentum Theory Options
    contents = add_header(contents, "Blade-Element/Momentum Theory Options")
    contents = add_line(contents, config.skewed_wake_model, "SkewMod", "Type of skewed-wake correction model (1=uncoupled, 2=Pitt/Peters, 3=coupled)")
    contents = add_line(contents, f'"{config.skew_factor}"', "SkewModFactor", "Constant used in Pitt/Peters skewed wake model (15/32*pi)")
    contents = add_line(contents, str(config.tip_loss).upper(), "TipLoss", "Use the Prandtl tip-loss model")
    contents = add_line(contents, str(config.hub_loss).upper(), "HubLoss", "Use the Prandtl hub-loss model")
    contents = add_line(contents, str(config.tangential_induction).upper(), "TanInd", "Include tangential induction in BEMT calculations")
    contents = add_line(contents, str(config.axial_induction_drag).upper(), "AIDrag", "Include the drag term in the axial-induction calculation")
    contents = add_line(contents, str(config.tangential_induction_drag).upper(), "TIDrag", "Include the drag term in the tangential-induction calculation")
    contents = add_line(contents, f'"{config.induction_tolerance}"', "IndToler", "Convergence tolerance for BEMT nonlinear solve residual equation")
    contents = add_line(contents, config.max_iterations, "MaxIter", "Maximum number of iteration steps")
    # Dynamic Blade-Element/Momentum Theory Options
    contents = add_header(contents, "Dynamic Blade-Element/Momentum Theory Options")
    contents = add_line(contents, config.dynamic_bemt_model, "DBEMT_Mod", "Type of dynamic BEMT (DBEMT) model (1=constant tau1, 2=time-dependent tau1)")
    contents = add_line(contents, f"{config.tau1_constant:.1f}", "tau1_const", "Time constant for DBEMT (s)")
    # OLAF -- cOnvecting LAgrangian Filaments (Free Vortex Wake) Theory Options
    contents = add_header(contents, "OLAF -- cOnvecting LAgrangian Filaments (Free Vortex Wake) Theory Options")
    contents = add_line(contents, f'"{config.olaf_input_file}"', "OLAFInputFileName", "Input file for OLAF")
    # Beddoes-Leishman Unsteady Airfoil Aerodynamics Options
    contents = add_header(contents, "Beddoes-Leishman Unsteady Airfoil Aerodynamics Options")
    contents = add_line(contents, config.unsteady_aero_model, "UAMod", "Unsteady Aero Model Switch (1=Baseline model (Original), 2=Gonzalez's variant, 3=Minemma/Pierce variant)")
    contents = add_line(contents, str(config.f_lookup).upper(), "FLookup", "Flag for f' lookup or best-fit exponential equations")
    # Airfoil Information
    contents = add_header(contents, "Airfoil Information")
    contents = add_line(contents, config.airfoil_table_mode, "AFTabMod", "Interpolation method for multiple airfoil tables")
    contents = add_line(contents, config.angle_of_attack_column, "InCol_Alfa", "The column in the airfoil tables that contains the angle of attack")
    contents = add_line(contents, config.lift_coefficient_column, "InCol_Cl", "The column in the airfoil tables that contains the lift coefficient")
    contents = add_line(contents, config.drag_coefficient_column, "InCol_Cd", "The column in the airfoil tables that contains the drag coefficient")
    contents = add_line(contents, config.pitching_moment_column, "InCol_Cm", "The column in the airfoil tables that contains the pitching-moment coefficient")
    contents = add_line(contents, config.cpmin_column, "InCol_Cpmin", "The column in the airfoil tables that contains the Cpmin coefficient")
    contents = add_line(contents, config.num_airfoil_files, "NumAFfiles", "Number of airfoil files used")

     # Add airfoil files
    for file in config.airfoil_files:
        contents += f'"{file}"\n'

    # Rotor/Blade Properties
    contents = add_header(contents, "Rotor/Blade Properties")
    contents = add_line(contents, str(config.include_pitching_moment).upper(), "UseBlCm", "Include aerodynamic pitching moment in calculations")
    for i, blade_file in enumerate(config.blade_files, start=1):
        contents += f'"{blade_file}"    ADBlFile({i})        - Name of file containing distributed aerodynamic properties for Blade #{i} (-)\n'

    # Hub Properties
    contents = add_header(contents, "Hub Properties")
    contents = add_line(contents, f"{config.hub_volume:.1f}", "VolHub", "Hub volume (m^3)")
    contents = add_line(contents, f"{config.hub_center_of_buoyancy_x:.1f}", "HubCenBx", "Hub center of buoyancy x direction offset (m)")

    # Nacelle Properties
    contents = add_header(contents, "Nacelle Properties")
    contents = add_line(contents, f"{config.nacelle_volume:.1f}", "VolNac", "Nacelle volume (m^3)")
    contents = add_line(contents, f"{config.nacelle_center_of_buoyancy_b:.1f},0,0", "NacCenB", "Position of nacelle center of buoyancy from yaw bearing in nacelle coordinates (m)")

    # Tail fin Aerodynamics
    contents = add_header(contents, "Tail fin Aerodynamics")
    contents = add_line(contents, str(config.tail_fin_aero).upper(), "TFinAero", "Calculate tail fin aerodynamics model (flag)")
    contents = add_line(contents, f'"{config.tail_fin_file}"', "TFinFile", "Input file for tail fin aerodynamics [used only when TFinAero=True]")

    # Tower Influence and Aerodynamics
    contents = add_header(contents, "Tower Influence and Aerodynamics")
    contents = add_line(contents, str(len(config.tower_data)), "NumTwrNds", "Number of tower nodes used in the analysis  (-) [used only when TwrPotent/=0, TwrShadow=True, or TwrAero=True]")
    contents = add_table_entry(contents, ["TwrElev", "TwrDiam", "TwrCd", "TwrTI", "TwrCb"])
    contents = add_table_entry(contents, ["(m)", "(m)", "(-)", "(-)", "(-)"])
    # Iterate over DataFrame rows
    for _, row in config.tower_data.iterrows():
        contents = add_table_entry(contents, [f"{row['TwrElev']:.3E}", f"{row['TwrDiam']:.3E}", f"{row['TwrCd']:.4E}", f"{row['TwrTI']:.4E}", f"{row['TwrCb']:.4E}",])

    # Outputs
    contents = add_header(contents, "Outputs")
    contents = add_line(contents, 'False', "SumPrint", "Generate a summary file listing input options and interpolated properties to <rootname>.AD.sum (flag)")
    contents = add_line(contents, str(len(config.blade_node_outputs)), "NBlOuts", "Number of blade node outputs [0 - 9] (-)")
    contents = add_line(contents, ", ".join([str(i) for i in config.blade_node_outputs]), "BlOutNd", "Blade nodes whose values will be output (-)")
    contents = add_line(contents, str(len(config.tower_node_outputs)), "NTwOuts", "Number of tower node outputs [0 - 9] (-)")
    contents = add_line(contents, ", ".join([str(i) for i in config.tower_node_outputs]), "TwOutNd", "Tower nodes whose values will be output (-)")
    contents = add_word(contents, "OutList")
    # Output writer
    for output in config.outputs:
        contents = add_word(contents, f'"{output}"')

    # End of input file
    contents = add_word(contents, "END of input file")

    # Node Outputs
    # contents = add_header(contents, "Node Outputs")
    # contents = add_line(contents, "1", "BldNd_BladesOut", "Blades to output")
    # contents = add_line(contents, "99", "NumNodes", "Blade nodes on each blade (currently unused)")
    # contents = add_word(contents, "OutList")
    # for output in config.node_outputs:
    #     contents = add_word(contents, f'"{output}"')
    # contents = add_word(contents, "END of input file")

    # Write the file
    with open(location / "DTU_10MW_AD15.dat", "w") as file:
        file.write(contents)

    return contents

def generate_inflow_wind_config(location: Path, config: InflowWindConfig):
    """Generate the InflowWind input file for OpenFAST."""
    contents = f"""------- InflowWind v3.01.* INPUT FILE -------------------------------------------------------------------------
DTU 10MW onshore reference wind turbine v0.1 - OpenFAST v2.4 - rated power at wind speed 11.4m/s
---------------------------------------------------------------------------------------------------------------
{str(config.echo).upper():<15}Echo           - Echo input data to <RootName>.ech (flag)
{config.wind_type:<15}WindType       - switch for wind file type (1=steady; 2=uniform; 3=binary TurbSim FF; 4=binary Bladed-style FF; 5=HAWC format; 6=User defined)
{config.propagation_dir:<15.1f}PropagationDir - Direction of wind propagation (meteorological rotation from aligned with X (positive rotates towards -Y) -- degrees)
{config.upflow_angle:<15.1f}VFlowAng       - Upflow angle (degrees) (not used for native Bladed format WindType=7)
{str(config.use_cubic_interpolation).upper():<15}VelInterpCubic - Use cubic interpolation for velocity in time (false=linear, true=cubic) [Used with WindType=2,3,4,5,7]
{config.num_velocity_points:<15}NWindVel       - Number of points to output the wind velocity    (0 to 9)
{', '.join(map(str, config.wind_vxi_list)):<15}WindVxiList    - List of coordinates in the inertial X direction (m)
{', '.join(map(str, config.wind_vyi_list)):<15}WindVyiList    - List of coordinates in the inertial Y direction (m)
{', '.join(map(str, config.wind_vzi_list)):<15}WindVziList    - List of coordinates in the inertial Z direction (m)
================== Parameters for Steady Wind Conditions [used only for WindType = 1] =========================
{config.h_wind_speed:<15.2f}HWindSpeed     - Horizontal windspeed                            (m/s)
{config.ref_height:<15.2f}RefHt          - Reference height for horizontal wind speed      (m)
{config.power_law_exp:<15.2f}PLexp          - Power law exponent                              (-)
================== Parameters for Uniform wind file   [used only for WindType = 2] ============================
"{config.uniform_filename}"    Filename_Uni   - Filename of time series data for uniform wind field.      (-)
{config.uniform_ref_height:<15.2f}RefHt_Uni      - Reference height for horizontal wind speed                (m)
{config.ref_length:<15.2f}RefLength      - Reference length for linear horizontal and vertical shear (-)
================== Parameters for Binary TurbSim Full-Field files   [used only for WindType = 3] ==============
"{config.turbsim_filename}"    Filename_BTS       - Name of the Full field wind file to use (.bts)
================== Parameters for Binary Bladed-style Full-Field files   [used only for WindType = 4] =========
"{config.bladed_rootname}"    FilenameRoot   - Rootname of the full-field wind file to use (.wnd, .sum)
{str(config.tower_file).upper():<15}TowerFile      - Have tower file (.twr) (flag)
================== Parameters for HAWC-format binary files  [Only used with WindType = 5] =====================
"{config.hawc_file_u}"    FileName_u     - name of the file containing the u-component fluctuating wind (.bin)
"{config.hawc_file_v}"    FileName_v     - name of the file containing the v-component fluctuating wind (.bin)
"{config.hawc_file_w}"    FileName_w     - name of the file containing the w-component fluctuating wind (.bin)
{config.hawc_nx:<15}nx             - number of grids in the x direction (in the 3 files above) (-)
{config.hawc_ny:<15}ny             - number of grids in the y direction (in the 3 files above) (-)
{config.hawc_nz:<15}nz             - number of grids in the z direction (in the 3 files above) (-)
{config.hawc_dx:<15.2f}dx             - distance (in meters) between points in the x direction    (m)
{config.hawc_dy:<15.2f}dy             - distance (in meters) between points in the y direction    (m)
{config.hawc_dz:<15.2f}dz             - distance (in meters) between points in the z direction    (m)
{config.hawc_ref_height:<15.2f}RefHt_Hawc     - reference height; the height (in meters) of the vertical center of the grid (m)
  -------------   Scaling parameters for turbulence   ---------------------------------------------------------
{config.scale_method:<15}ScaleMethod    - Turbulence scaling method   [0 = none, 1 = direct scaling, 2 = calculate scaling factor based on a desired standard deviation]
{config.scale_factor_x:<15.1f}SFx            - Turbulence scaling factor for the x direction (-)   [ScaleMethod=1]
{config.scale_factor_y:<15.1f}SFy            - Turbulence scaling factor for the y direction (-)   [ScaleMethod=1]
{config.scale_factor_z:<15.1f}SFz            - Turbulence scaling factor for the z direction (-)   [ScaleMethod=1]
{config.sigma_x:<15.1f}SigmaFx        - Turbulence standard deviation to calculate scaling from in x direction (m/s)    [ScaleMethod=2]
{config.sigma_y:<15.1f}SigmaFy        - Turbulence standard deviation to calculate scaling from in y direction (m/s)    [ScaleMethod=2]
{config.sigma_z:<15.1f}SigmaFz        - Turbulence standard deviation to calculate scaling from in z direction (m/s)    [ScaleMethod=2]
  -------------   Mean wind profile parameters (added to HAWC-format files)   ---------------------------------
{config.u_ref:<15.1f}URef           - Mean u-component wind speed at the reference height (m/s)
{config.wind_profile_type:<15}WindProfile    - Wind profile type (0=constant;1=logarithmic,2=power law)
{config.power_law_exp_hawc:<15.2f}PLExp_Hawc     - Power law exponent (-) (used for PL wind profile type only)
{config.surface_roughness:<15.2f}Z0             - Surface roughness length (m) (used for LG wind profile type only)
{config.x_offset:<15.2f}XOffset         - Initial offset in +x direction (shift of wind box)
================== LIDAR Parameters ===========================================================================
{config.lidar_sensor_type:<15}SensorType          - Switch for lidar configuration (0 = None, 1 = Single Point Beam(s), 2 = Continuous, 3 = Pulsed)
{config.lidar_num_pulse_gates:<15}NumPulseGate        - Number of lidar measurement gates (used when SensorType = 3)
{config.lidar_pulse_spacing:<15.2f}PulseSpacing        - Distance between range gates (m) (used when SensorType = 3)
{config.lidar_num_beams:<15}NumBeam             - Number of lidar measurement beams (0-5)(used when SensorType = 1)
{config.lidar_focal_distance_x:<15.1f}FocalDistanceX      - Focal distance co-ordinates of the lidar beam in the x direction (m)
{config.lidar_focal_distance_y:<15.1f}FocalDistanceY      - Focal distance co-ordinates of the lidar beam in the y direction (m)
{config.lidar_focal_distance_z:<15.1f}FocalDistanceZ      - Focal distance co-ordinates of the lidar beam in the z direction (m)
{" ".join(map(str, config.lidar_rotor_apex_offset)):<15}RotorApexOffsetPos  - Offset of the lidar from hub height (m)
{config.lidar_ref_speed:<15.1f}URefLid             - Reference average wind speed for the lidar[m/s]
{config.measurement_interval:<15.2f}MeasurementInterval - Time between each measurement [s]
{str(config.lidar_radial_velocity).upper():<15}LidRadialVel        - TRUE => return radial component, FALSE => return 'x' direction estimate
{config.consider_hub_motion:<15}ConsiderHubMotion   - Flag whether to consider the hub motion's impact on Lidar measurements
====================== OUTPUT ==================================================
{str(config.sum_print).upper():<15}SumPrint     - Print summary data to <RootName>.IfW.sum (flag)
"""

    # Add output list
    for output in config.output_list:
        contents += f'"{output}"\n'

    contents += "END of input file (the word \"END\" must appear in the first 3 columns of this last OutList line)\n"
    contents += "---------------------------------------------------------------------------------------"

    # Write to file
    with open(location / "DTU_10MW_IW.dat", "w") as file:
        file.write(contents)

    return None


if __name__ == "__main__":
    # Define the turbine model and related configurations
    model = TurbineModel()
    aerodyn_standalone_config = AeroDynInputConfig(model)
    aerodyn_config = AeroDynConfig(model)
    inflow_wind_config = InflowWindConfig(model)

    # Output directory for generated files
    output_dir = PROJECT_ROOT / "solvers" / "aerodynamics" / "aerodyn"
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate configuration files
    generate_aerodyn_standalone_config(output_dir, aerodyn_standalone_config)
    generate_aerodyn_config(output_dir, aerodyn_config)
    generate_inflow_wind_config(output_dir, inflow_wind_config)

    print(f"Configuration files generated in: {output_dir}")
