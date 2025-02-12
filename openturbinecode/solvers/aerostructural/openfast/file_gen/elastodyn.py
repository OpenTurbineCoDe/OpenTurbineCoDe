# elastodyn.py

# flake8: noqa: E501
from pathlib import Path
from openturbinecode.solvers.aerostructural.openfast.options import ElastoDynConfig
from .util import add_header, add_line, add_word

OPENFAST_VERSION = 300

def generate_elastodyn_config(location: Path, config: ElastoDynConfig):
    """Generate the ElastoDyn input file."""
    contents = """------- ELASTODYN v1.03.* INPUT FILE -------------------------------------------
IEA 15 MW offshore reference model monopile configuration
"""

    # Add all sections
    contents = write_simulation_control(contents, config)
    contents = write_environmental_condition(contents, config)
    contents = write_degrees_of_freedom(contents, config)
    contents = write_initial_conditions(contents, config)
    contents = write_turbine_configuration(contents, config)
    contents = write_mass_and_inertia(contents, config)
    contents = write_blade(contents, config)
    contents = write_rotor_teeter(contents, config)
    contents = write_drivetrain(contents, config)
    contents = write_furling(contents, config)
    contents = write_tower(contents, config)
    contents = write_output_settings(contents, config)

    # Write to file
    with open(location / f"{config.model.name}_ED.dat", "w") as file:
        file.write(contents)

    return contents

def write_simulation_control(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Simulation Control")
    contents = add_line(contents, str(config.echo), "Echo", "Echo input data to \"<RootName>.ech\" (flag)")
    contents = add_line(contents, config.integration_method, "Method", "Integration method: {1: RK4, 2: AB4, or 3: ABM4} (-)")
    contents = add_line(contents, config.time_step, "DT", "Integration time step (s)")
    return contents

def write_environmental_condition(contents, config: ElastoDynConfig):
    if OPENFAST_VERSION == 300:
        contents = add_header(contents, "Environmental Conditions")
        contents = add_line(contents, config.gravity, "Gravity", "Gravitational acceleration (m/s^2)")
    return contents

def write_degrees_of_freedom(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Degrees of Freedom")
    contents = add_line(contents, str(config.flap_dof1), "FlapDOF1", "First flapwise blade mode DOF (flag)")
    contents = add_line(contents, str(config.flap_dof2), "FlapDOF2", "Second flapwise blade mode DOF (flag)")
    contents = add_line(contents, str(config.edge_dof), "EdgeDOF", "First edgewise blade mode DOF (flag)")
    contents = add_line(contents, str(config.teeter_dof), "TeetDOF", "Rotor-teeter DOF (flag) [unused for 3 blades]")
    contents = add_line(contents, str(config.drivetrain_dof), "DrTrDOF", "Drivetrain rotational-flexibility DOF (flag)")
    contents = add_line(contents, str(config.generator_dof), "GenDOF", "Generator DOF (flag)")
    contents = add_line(contents, str(config.yaw_dof), "YawDOF", "Yaw DOF (flag)")
    contents = add_line(contents, str(config.fore_aft_tower_dof1), "TwFADOF1", "First fore-aft tower bending-mode DOF (flag)")
    contents = add_line(contents, str(config.fore_aft_tower_dof2), "TwFADOF2", "Second fore-aft tower bending-mode DOF (flag)")
    contents = add_line(contents, str(config.side_to_side_tower_dof1), "TwSSDOF1", "First side-to-side tower bending-mode DOF (flag)")
    contents = add_line(contents, str(config.side_to_side_tower_dof2), "TwSSDOF2", "Second side-to-side tower bending-mode DOF (flag)")
    contents = add_line(contents, str(config.platform_surge_dof), "PtfmSgDOF", "Platform horizontal surge translation DOF (flag)")
    contents = add_line(contents, str(config.platform_sway_dof), "PtfmSwDOF", "Platform horizontal sway translation DOF (flag)")
    contents = add_line(contents, str(config.platform_heave_dof), "PtfmHvDOF", "Platform vertical heave translation DOF (flag)")
    contents = add_line(contents, str(config.platform_roll_dof), "PtfmRDOF", "Platform roll tilt rotation DOF (flag)")
    contents = add_line(contents, str(config.platform_pitch_dof), "PtfmPDOF", "Platform pitch tilt rotation DOF (flag)")
    contents = add_line(contents, str(config.platform_yaw_dof), "PtfmYDOF", "Platform yaw rotation DOF (flag)")
    return contents

def write_initial_conditions(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Initial Conditions")
    contents = add_line(contents, config.out_of_plane_deflection, "OoPDefl", "Initial out-of-plane blade-tip displacement (meters)")
    contents = add_line(contents, config.in_plane_deflection, "IPDefl", "Initial in-plane blade-tip deflection (meters)")
    contents = add_line(contents, config.blade_pitch[0], "BlPitch(1)", "Blade 1 initial pitch (degrees)")
    contents = add_line(contents, config.blade_pitch[1], "BlPitch(2)", "Blade 2 initial pitch (degrees)")
    contents = add_line(contents, config.blade_pitch[2], "BlPitch(3)", "Blade 3 initial pitch (degrees) [unused for 2 blades]")
    contents = add_line(contents, config.teeter_deflection, "TeetDefl", "Initial or fixed teeter angle (degrees) [unused for 3 blades]")
    contents = add_line(contents, config.azimuth_angle, "Azimuth", "Initial azimuth angle for blade 1 (degrees)")
    contents = add_line(contents, config.rotor_speed, "RotSpeed", "Initial or fixed rotor speed (rpm)")
    contents = add_line(contents, config.nacelle_yaw, "NacYaw", "Initial or fixed nacelle-yaw angle (degrees)")
    contents = add_line(contents, config.tower_top_fore_aft_disp, "TTDspFA", "Initial fore-aft tower-top displacement (meters)")
    contents = add_line(contents, config.tower_top_side_disp, "TTDspSS", "Initial side-to-side tower-top displacement (meters)")
    contents = add_line(contents, config.platform_surge_disp, "PtfmSurge", "Initial or fixed horizontal surge translational displacement of platform (meters)")
    contents = add_line(contents, config.platform_sway_disp, "PtfmSway", "Initial or fixed horizontal sway translational displacement of platform (meters)")
    contents = add_line(contents, config.platform_heave_disp, "PtfmHeave", "Initial or fixed vertical heave translational displacement of platform (meters)")
    contents = add_line(contents, config.platform_roll_disp, "PtfmRoll", "Initial or fixed roll tilt rotational displacement of platform (degrees)")
    contents = add_line(contents, config.platform_pitch_disp, "PtfmPitch", "Initial or fixed pitch tilt rotational displacement of platform (degrees)")
    contents = add_line(contents, config.platform_yaw_disp, "PtfmYaw", "Initial or fixed yaw rotational displacement of platform (degrees)")
    return contents

def write_turbine_configuration(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Turbine Configuration")
    contents = add_line(contents, config.num_blades, "NumBl", "Number of blades (-)")
    contents = add_line(contents, config.tip_radius, "TipRad", "The distance from the rotor apex to the blade tip (meters)")
    contents = add_line(contents, config.hub_radius, "HubRad", "The distance from the rotor apex to the blade root (meters)")
    contents = add_line(contents, config.precone_angles[0], "PreCone(1)", "Blade 1 cone angle (degrees)")
    contents = add_line(contents, config.precone_angles[1], "PreCone(2)", "Blade 2 cone angle (degrees)")
    contents = add_line(contents, config.precone_angles[2], "PreCone(3)", "Blade 3 cone angle (degrees) [unused for 2 blades]")
    contents = add_line(contents, config.hub_center_mass, "HubCM", "Distance from rotor apex to hub mass [positive downwind] (meters)")
    contents = add_line(contents, config.undersling_length, "UndSling", "Undersling length [distance from teeter pin to the rotor apex] (meters) [unused for 3 blades]")
    contents = add_line(contents, 0.0, "Delta3", "Delta-3 angle for teetering rotors (degrees) [unused for 3 blades]")
    contents = add_line(contents, config.azimuth_b1_up, "AzimB1Up", "Azimuth value to use for I/O when blade 1 points up (degrees)")
    contents = add_line(contents, config.overhang, "OverHang", "Distance from yaw axis to rotor apex [3 blades] or teeter pin [2 blades] (meters)")
    contents = add_line(contents, 0.0, "ShftGagL", "Distance from rotor apex [3 blades or teeter pin [2 blades] to shaft strain gages [positive for upwind rotors] (meters)")
    contents = add_line(contents, config.shaft_tilt, "ShftTilt", "Rotor shaft tilt angle (degrees)")
    contents = add_line(contents, config.nacelle_cm[0], "NacCMxn", "Downwind distance from the tower-top to the nacelle CM (meters)")
    contents = add_line(contents, config.nacelle_cm[1], "NacCMyn", "Lateral distance from the tower-top to the nacelle CM (meters)")
    contents = add_line(contents, config.nacelle_cm[2], "NacCMzn", "Vertical distance from the tower-top to the nacelle CM (meters)")
    contents = add_line(contents, config.nacelle_imu[0], "NcIMUxn", "Downwind distance from the tower-top to the nacelle IMU (meters)")
    contents = add_line(contents, config.nacelle_imu[1], "NcIMUyn", "Lateral distance from the tower-top to the nacelle IMU (meters)")
    contents = add_line(contents, config.nacelle_imu[2], "NcIMUzn", "Vertical distance from the tower-top to the nacelle IMU (meters)")
    contents = add_line(contents, config.tower_to_shaft, "Twr2Shft", "Vertical distance from the tower-top to the rotor shaft (meters)")
    contents = add_line(contents, config.tower_height, "TowerHt", "Height of tower above ground level (meters)")
    contents = add_line(contents, config.base_tower_height, "TowerBsHt", "Height of tower base above ground level (meters)")
    contents = add_line(contents, config.platform_cm[0], "PtfmCMxt", "Downwind distance from the ground level to the platform CM (meters)")
    contents = add_line(contents, config.platform_cm[1], "PtfmCMyt", "Lateral distance from the ground level to the platform CM (meters)")
    contents = add_line(contents, config.platform_cm[2], "PtfmCMzt", "Vertical distance from the ground level to the platform CM (meters)")
    contents = add_line(contents, config.platform_vert_ref, "PtfmRefzt", "Vertical distance from the ground level to the platform reference point (meters)")
    return contents

def write_mass_and_inertia(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Mass and Inertia")
    contents = add_line(contents, config.tip_mass[0], "TipMass(1)", "Tip-brake mass, blade 1 (kg)")
    contents = add_line(contents, config.tip_mass[1], "TipMass(2)", "Tip-brake mass, blade 2 (kg)")
    contents = add_line(contents, config.tip_mass[2], "TipMass(3)", "Tip-brake mass, blade 3 (kg)")
    contents = add_line(contents, config.hub_mass, "HubMass", "Hub mass (kg)")
    contents = add_line(contents, config.hub_inertia, "HubIner", "Hub inertia about rotor axis (kg m^2)")
    contents = add_line(contents, config.generator_inertia, "GenIner", "Generator inertia about HSS (kg m^2)")
    contents = add_line(contents, config.nacelle_mass, "NacMass", "Nacelle mass (kg)")
    contents = add_line(contents, config.nacelle_yaw_inertia, "NacYIner", "Nacelle inertia about yaw axis (kg m^2)")
    contents = add_line(contents, config.yaw_bearing_mass, "YawBrMass", "Yaw bearing mass (kg)")
    contents = add_line(contents, config.platform_mass, "PtfmMass", "Platform mass (kg)")
    contents = add_line(contents, config.platform_inertia[0], "PtfmRIner", "Platform inertia for roll tilt rotation about the platform CM (kg m^2)")
    contents = add_line(contents, config.platform_inertia[1], "PtfmPIner", "Platform inertia for pitch tilt rotation about the platform CM (kg m^2)")
    contents = add_line(contents, config.platform_inertia[2], "PtfmYIner", "Platform inertia for yaw rotation about the platform CM (kg m^2)")
    return contents

def write_blade(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Blade")
    contents = add_line(contents, config.num_blade_nodes, "BldNodes", "Number of blade nodes (per blade) used for analysis (-)")
    for i, blade_file in enumerate(config.blade_files, start=1):
        contents = add_line(contents, blade_file, f"BldFile({i})", f"Name of file containing properties for blade {i} (quoted string)")
    return contents

def write_rotor_teeter(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Rotor-Teeter")
    contents = add_line(contents, config.teeter_mode, "TeetMod", "Rotor-teeter spring/damper model {0: none, 1: standard, 2: user-defined from routine UserTeet} (switch) [unused for 3 blades]")
    contents = add_line(contents, config.teeter_damping, "TeetDmpP", "Rotor-teeter damper position (degrees) [used only for 2 blades and when TeetMod=1]")
    contents = add_line(contents, config.teeter_damping, "TeetDmp", "Rotor-teeter damping constant (N-m/(rad/s)) [used only for 2 blades and when TeetMod=1]")
    contents = add_line(contents, 0.0, "TeetCDmp", "Rotor-teeter rate-independent Coulomb-damping moment (N-m) [used only for 2 blades and when TeetMod=1]")
    contents = add_line(contents, 0.0, "TeetSStP", "Rotor-teeter soft-stop position (degrees) [used only for 2 blades and when TeetMod=1]")
    contents = add_line(contents, 0.0, "TeetHStP", "Rotor-teeter hard-stop position (degrees) [used only for 2 blades and when TeetMod=1]")
    contents = add_line(contents, 0.0, "TeetSSSp", "Rotor-teeter soft-stop linear-spring constant (N-m/rad) [used only for 2 blades and when TeetMod=1]")
    contents = add_line(contents, 0.0, "TeetHSSp", "Rotor-teeter hard-stop linear-spring constant (N-m/rad) [used only for 2 blades and when TeetMod=1]")
    return contents

def write_drivetrain(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Drivetrain")
    contents = add_line(contents, config.gearbox_efficiency, "GBoxEff", "Gearbox efficiency (%)")
    contents = add_line(contents, config.gear_ratio, "GBRatio", "Gearbox ratio (-)")
    contents = add_line(contents, config.torsional_spring, "DTTorSpr", "Drivetrain torsional spring (N-m/rad)")
    contents = add_line(contents, config.torsional_damper, "DTTorDmp", "Drivetrain torsional damper (N-m/(rad/s))")
    return contents

def write_furling(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Furling")
    contents = add_line(contents, str(False), "Furling", "Furling system (flag)")
    contents = add_line(contents, '"unused"', "FurlFile", "Name of file containing furling properties (quoted string)")
    return contents

def write_tower(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Tower")
    contents = add_line(contents, config.num_tower_nodes, "TwrNodes", "Number of tower nodes used for analysis (-)")
    contents = add_line(contents, config.tower_file, "TwrFile", "Name of file containing tower properties (quoted string)")
    return contents

def write_output_settings(contents, config: ElastoDynConfig):
    contents = add_header(contents, "Output Settings")
    contents = add_line(contents, str(True), "SumPrint", "Print summary data to \"<RootName>.sum\" (flag)")
    contents = add_line(contents, 1, "OutFile", "Switch to determine where output will be placed: {1: in module output file only; 2: in glue code output file only; 3: both} (currently unused)")
    contents = add_line(contents, str(True), "TabDelim", "Use tab delimiters in text tabular output file? (flag) (currently unused)")
    contents = add_line(contents, '"ES10.3E2"', "OutFmt", "Format used for text tabular output (except time). Resulting field should be 10 characters. (quoted string) (currently unused)")
    contents = add_line(contents, 0.0, "TStart", "Time to begin tabular output (s) (currently unused)")
    contents = add_line(contents, 1, "DecFact", "Decimation factor for tabular output {1: output every time step} (-) (currently unused)")
    contents = add_line(contents, 1, "NTwGages", "Number of tower nodes that have strain gages for output [0 to 9] (-)")
    contents = add_line(contents, "20", "TwrGagNd", "List of tower nodes that have strain gages [1 to TwrNodes] (-) [unused if NTwGages=0]")
    contents = add_line(contents, 3, "NBlGages", "Number of blade nodes that have strain gages for output [0 to 9] (-)")
    contents = add_line(contents, "5, 9, 13", "BldGagNd", "List of blade nodes that have strain gages [1 to BldNodes] (-) [unused if NBlGages=0]")
    contents = add_line(contents, '"OutList"', "OutList", "The next line(s) contains a list of output parameters.  See OutListParameters.xlsx for a listing of available output channels, (-)")

    for output in config.output:
        contents += f'"{output}"\n'

    contents = add_word(contents, "End of input file")

    return contents
