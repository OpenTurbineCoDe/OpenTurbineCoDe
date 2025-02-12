# flake8: noqa: E501
from pathlib import Path
from openturbinecode.solvers.aerostructural.openfast.options import AeroDynConfig
from .util import add_header, add_line, add_table_entry

OPENFAST_VERSION = 300

def generate_aerodyn_config(location: Path, config: AeroDynConfig):
    """Generate the AeroDyn input file for OpenFAST."""
    contents = """------- AERODYN v15 for OpenFAST INPUT FILE -----------------------------------------------
DTU 10MW onshore reference wind turbine v0.1 - OpenFAST v3.5.3
"""

    # Add all sections
    contents = write_general_options(contents, config)
    contents = write_environmental_conditions(contents, config)
    contents = write_bemt_options(contents, config)
    contents = write_dbemt_options(contents, config)
    contents = write_lagrangian_theory(contents, config)
    contents = write_beddos_leishman(contents, config)
    contents = write_airfoil_info(contents, config)
    contents = write_rotor_blade(contents, config)
    contents = write_hub(contents, config)
    contents = write_nacelle(contents, config)
    contents = write_tail_fin(contents, config)
    contents = write_tower_aero(contents, config)
    contents = write_outputs(contents, config)

    # Write to file
    with open(location / f"{config.model.name}_AD15.dat", "w") as file:
        file.write(contents)

    return contents

def write_general_options(contents, config: AeroDynConfig):
    contents = add_header(contents, "General Options")
    contents = add_line(contents, str(config.echo).upper(), "Echo", "Echo the input to \"<rootname>.AD.ech\"?  (flag)")
    contents = add_line(contents, f'\"{config.dt_aero}\"', "DTAero", "Time interval for aerodynamic calculations (s)")
    contents = add_line(contents, config.wake_model, "WakeMod", "Type of wake/induction model (0=none, 1=BEMT, 2=DBEMT)")
    contents = add_line(contents, config.airfoil_aero_model, "AFAeroMod", "Type of blade airfoil aerodynamics model (1=steady model, 2=Beddoes-Leishman unsteady model)")
    contents = add_line(contents, config.tower_potential_flow, "TwrPotent", "Type tower influence on wind based on potential flow around the tower")
    contents = add_line(contents, str(config.tower_shadow).upper(), "TwrShadow", "Calculate tower influence on wind based on downstream tower shadow")
    contents = add_line(contents, str(config.tower_aero).upper(), "TwrAero", "Calculate tower aerodynamic loads")
    contents = add_line(contents, str(config.frozen_wake).upper(), "FrozenWake", "Assume frozen wake during linearization")
    contents = add_line(contents, str(config.cavitation_check).upper(), "CavitCheck", "Perform cavitation check")
    if OPENFAST_VERSION > 300:
        contents = add_line(contents, str(config.buoyancy_effects).upper(), "Buoyancy", "Include buoyancy effects in calculations")
    contents = add_line(contents, str(config.compute_acoustics).upper(), "CompAA", "Compute airfoil aerodynamics")
    contents = add_line(contents, f'{config.acoustics_input_file}', "AA_InputFile", "File containing airfoil aerodynamic data")
    return contents

def write_environmental_conditions(contents, config: AeroDynConfig):
    contents = add_header(contents, "Environmental Conditions")
    contents = add_line(contents, f"{config.air_density:.3f}", "AirDens", "Air density (kg/m^3)")
    contents = add_line(contents, f"{config.kinematic_viscosity:.3E}", "KinVisc", "Kinematic air viscosity (m^2/s)")
    contents = add_line(contents, f"{config.speed_of_sound:.2f}", "SpdSound", "Speed of sound (m/s)")
    contents = add_line(contents, f"{config.atmospheric_pressure:.3f}", "Patm", "Atmospheric pressure (Pa)")
    contents = add_line(contents, f"{config.vapor_pressure:.3f}", "Pvap", "Vapor pressure of air (Pa)")
    if OPENFAST_VERSION == 300:
        contents = add_line(contents, f"{config.fluid_depth}", "FluidDepth", "Depth of fluid (m)")
    return contents

def write_bemt_options(contents, config: AeroDynConfig):
    contents = add_header(contents, "Blade-Element/Momentum Theory Options")
    contents = add_line(contents, config.skewed_wake_model, "SkewMod", "Type of skewed-wake correction model (1=uncoupled, 2=Pitt/Peters, 3=coupled)")
    contents = add_line(contents, f'\"{config.skew_factor}\"', "SkewModFactor", "Constant used in Pitt/Peters skewed wake model (15/32*pi)")
    contents = add_line(contents, str(config.tip_loss).upper(), "TipLoss", "Use the Prandtl tip-loss model")
    contents = add_line(contents, str(config.hub_loss).upper(), "HubLoss", "Use the Prandtl hub-loss model")
    contents = add_line(contents, str(config.tangential_induction).upper(), "TanInd", "Include tangential induction in BEMT calculations")
    contents = add_line(contents, str(config.axial_induction_drag).upper(), "AIDrag", "Include the drag term in the axial-induction calculation")
    contents = add_line(contents, str(config.tangential_induction_drag).upper(), "TIDrag", "Include the drag term in the tangential-induction calculation")
    contents = add_line(contents, f'\"{config.induction_tolerance}\"', "IndToler", "Convergence tolerance for BEMT nonlinear solve residual equation")
    contents = add_line(contents, config.max_iterations, "MaxIter", "Maximum number of iteration steps")
    return contents

def write_dbemt_options(contents, config: AeroDynConfig):
    contents = add_header(contents, "Dynamic Blade-Element/Momentum Theory Options")
    contents = add_line(contents, config.dynamic_bemt_model, "DBEMT_Mod", "Type of dynamic BEMT (DBEMT) model (1=constant tau1, 2=time-dependent tau1)")
    contents = add_line(contents, f"{config.tau1_constant:.1f}", "tau1_const", "Time constant for DBEMT (s)")
    return contents

def write_lagrangian_theory(contents, config: AeroDynConfig):
    contents = add_header(contents, "OLAF -- cOnvecting LAgrangian Filaments (Free Vortex Wake) Theory Options")
    contents = add_line(contents, f'\"{config.olaf_input_file}\"', "OLAFInputFileName", "Input file for OLAF")
    return contents

def write_beddos_leishman(contents, config: AeroDynConfig):
    contents = add_header(contents, "Beddoes-Leishman Unsteady Airfoil Aerodynamics Options")
    contents = add_line(contents, config.unsteady_aero_model, "UAMod", "Unsteady Aero Model Switch (1=Baseline model, 2=Gonzalez's variant, 3=Minemma/Pierce variant)")
    contents = add_line(contents, str(config.f_lookup).upper(), "FLookup", "Flag for f' lookup or best-fit exponential equations")
    # contents = add_line(contents, f"{config.ua_radius[0]:.2f}", "UAStartRad", "Starting radius for dynamic stall (fraction of rotor radius) [used only when AFAeroMod=2]")
    # contents = add_line(contents, f"{config.ua_radius[1]:.2f}", "UAEndRad", "Ending radius for dynamic stall (fraction of rotor radius) [used only when AFAeroMod=2]")
    return contents

def write_airfoil_info(contents, config: AeroDynConfig):
    contents = add_header(contents, "Airfoil Information")
    contents = add_line(contents, config.airfoil_table_mode, "AFTabMod", "Interpolation method for multiple airfoil tables")
    contents = add_line(contents, config.angle_of_attack_column, "InCol_Alfa", "The column in the airfoil tables that contains the angle of attack")
    contents = add_line(contents, config.lift_coefficient_column, "InCol_Cl", "The column in the airfoil tables that contains the lift coefficient")
    contents = add_line(contents, config.drag_coefficient_column, "InCol_Cd", "The column in the airfoil tables that contains the drag coefficient")
    contents = add_line(contents, config.pitching_moment_column, "InCol_Cm", "The column in the airfoil tables that contains the pitching-moment coefficient")
    contents = add_line(contents, config.cpmin_column, "InCol_Cpmin", "The column in the airfoil tables that contains the Cpmin coefficient")
    contents = add_line(contents, config.num_airfoil_files, "NumAFfiles", "Number of airfoil files used")
    contents = add_line(contents, f'"{config.airfoil_files[0]}"', "AFNames", "Names of airfoil files")

    for file in config.airfoil_files[1:]:
        contents += f'"{file}"\n'
    return contents

def write_rotor_blade(contents, config: AeroDynConfig):
    contents = add_header(contents, "Rotor/Blade Properties")
    contents = add_line(contents, str(config.include_pitching_moment).upper(), "UseBlCm", "Include aerodynamic pitching moment in calculations")
    for i, blade_file in enumerate(config.blade_files, start=1):
        contents += f'"{blade_file}"    ADBlFile({i})        - Name of file containing distributed aerodynamic properties for Blade #{i} (-)\n'
    return contents

def write_hub(contents, config: AeroDynConfig):
    # Hub Properties
    if OPENFAST_VERSION > 300:
        contents = add_header(contents, "Hub Properties")
        contents = add_line(contents, f"{config.hub_volume:.1f}", "VolHub", "Hub volume (m^3)")
        contents = add_line(contents, f"{config.hub_center_of_buoyancy_x:.1f}", "HubCenBx", "Hub center of buoyancy x direction offset (m)")
        
    return contents

def write_nacelle(contents, config: AeroDynConfig):
    # Nacelle Properties
    if OPENFAST_VERSION > 300:
        contents = add_header(contents, "Nacelle Properties")
        contents = add_line(contents, f"{config.nacelle_volume:.1f}", "VolNac", "Nacelle volume (m^3)")
        contents = add_line(contents, f"{config.nacelle_center_of_buoyancy_b:.1f},0,0", "NacCenB", "Position of nacelle center of buoyancy from yaw bearing in nacelle coordinates (m)")

    return contents

def write_tail_fin(contents, config: AeroDynConfig):
    # Tail fin Aerodynamics
    if OPENFAST_VERSION > 300:
        contents = add_header(contents, "Tail fin Aerodynamics")
        contents = add_line(contents, str(config.tail_fin_aero).upper(), "TFinAero", "Calculate tail fin aerodynamics model (flag)")
        contents = add_line(contents, f'"{config.tail_fin_file}"', "TFinFile", "Input file for tail fin aerodynamics [used only when TFinAero=True]")

    return contents

def write_tower_aero(contents, config: AeroDynConfig):
    # Tower Influence and Aerodynamics
    contents = add_header(contents, "Tower Influence and Aerodynamics")
    contents = add_line(contents, str(len(config.tower_data)), "NumTwrNds", "Number of tower nodes used in the analysis  (-) [used only when TwrPotent/=0, TwrShadow=True, or TwrAero=True]")
    contents = add_table_entry(contents, ["TwrElev", "TwrDiam", "TwrCd", "TwrTI", "TwrCb"])
    contents = add_table_entry(contents, ["(m)", "(m)", "(-)", "(-)", "(-)"])
    # Iterate over DataFrame rows
    for _, row in config.tower_data.iterrows():
        contents = add_table_entry(contents, [f"{row['TwrElev']:.3f}", f"{row['TwrDiam']:.3f}", f"{row['TwrCd']:.4f}", f"{row['TwrTI']:.4f}", f"{row['TwrCb']:.4f}",])

    return contents
    return contents

def write_outputs(contents, config: AeroDynConfig):
    contents = add_header(contents, "Outputs")
    contents = add_line(contents, str("True").upper(), "SumPrint", "Generate a summary file listing input options")
    contents = add_line(contents, len(config.blade_node_outputs), "NBlOuts", "Number of blade node outputs")
    contents = add_line(contents, ", ".join(map(str, config.blade_node_outputs)), "BlOutNd", "Blade nodes whose values will be output")
    contents = add_line(contents, len(config.tower_node_outputs), "NTwOuts", "Number of tower node outputs")
    contents = add_line(contents, ", ".join(map(str, config.tower_node_outputs)), "TwOutNd", "Tower nodes whose values will be output")

    for output in config.outputs:
        contents += f'"{output}"\n'

    contents += "END of input file\n"
    return contents
