# fast.py

# flake8: noqa: E501
from pathlib import Path
from openturbinecode.solvers.aerostructural.openfast.options import FastConfig
from .util import add_header, add_line

OPENFAST_VERSION = 300

def generate_fast_config(location: Path, config: FastConfig):
    """Generate the OpenFAST input file."""
    contents = """------- OpenFAST INPUT FILE -------------------------------------------
# Test - OpenFAST v15
"""

    # Add all sections
    contents = write_simulation_control(contents, config)
    contents = write_feature_switches(contents, config)
    contents = write_environmental_conditions(contents, config)
    contents = write_input_files(contents, config)
    contents = write_output_settings(contents, config)
    contents = write_linearization(contents, config)
    contents = write_visualization(contents, config)

    # Write to file
    with open(location / f"{config.model.name}.fst", "w") as file:
        file.write(contents)

    return contents

def write_simulation_control(contents, config: FastConfig):
    contents = add_header(contents, "Simulation Control")
    contents = add_line(contents, "False", "Echo", "Echo input data to <RootName>.ech (flag)")
    contents = add_line(contents, "FATAL", "AbortLevel", "Error level when simulation should abort (string) {\"WARNING\", \"SEVERE\", \"FATAL\"}")
    contents = add_line(contents, config.t_max, "TMax", "Total run time (s)")
    contents = add_line(contents, config.dt, "DT", "Integration time step (s)")
    contents = add_line(contents, config.interp_order, "InterpOrder", "Interpolation order for input/output time history (-) {1=linear, 2=quadratic}")
    contents = add_line(contents, config.num_correction, "NumCrctn", "Number of correction iterations (-) {0=explicit calculation, i.e., no corrections}")
    contents = add_line(contents, config.dt_ujac, "DT_UJac", "Time between calls to get Jacobians (s)")
    contents = add_line(contents, config.ujac_scale_factor, "UJacSclFact", "Scaling factor used in Jacobians (-)")
    return contents

def write_feature_switches(contents, config: FastConfig):
    contents = add_header(contents, "Feature Switches and Flags")
    contents = add_line(contents, config.elastic, "CompElast", "Compute structural dynamics (switch) {1=ElastoDyn; 2=ElastoDyn + BeamDyn for blades}")
    contents = add_line(contents, config.inflow, "CompInflow", "Compute inflow wind velocities (switch) {0=still air; 1=InflowWind; 2=external from OpenFOAM}")
    contents = add_line(contents, config.aero, "CompAero", "Compute aerodynamic loads (switch) {0=None; 1=AeroDyn v14; 2=AeroDyn v15}")
    contents = add_line(contents, config.servo, "CompServo", "Compute control and electrical-drive dynamics (switch) {0=None; 1=ServoDyn}")
    contents = add_line(contents, config.hydro, "CompHydro", "Compute hydrodynamic loads (switch) {0=None; 1=HydroDyn}")
    contents = add_line(contents, config.sub, "CompSub", "Compute sub-structural dynamics (switch) {0=None; 1=SubDyn}")
    contents = add_line(contents, config.mooring, "CompMooring", "Compute mooring system (switch) {0=None; 1=MAP++; 2=FEAMooring; 3=MoorDyn; 4=OrcaFlex}")
    contents = add_line(contents, config.ice, "CompIce", "Compute ice loads (switch) {0=None; 1=IceFloe; 2=IceDyn}")
    if OPENFAST_VERSION > 300:
        contents = add_line(contents, config.mhk, "MHK", "Compute marine hydrokinetic loads (switch) {0=None; 1=MHK}")
    return contents

def write_environmental_conditions(contents, config: FastConfig):
    if OPENFAST_VERSION > 300:
        contents = add_header(contents, "Environmental Conditions")
        contents = add_line(contents, config.gravity, "Gravity", "Gravitational acceleration (m/s^2)")
        contents = add_line(contents, config.air_density, "AirDens", "Air density (kg/m^3)")
        contents = add_line(contents, config.water_density, "WtrDens", "Water density (kg/m^3)")
        contents = add_line(contents, config.kinematic_viscosity, "KinVisc", "Kinematic viscosity of air (m^2/s)")
        contents = add_line(contents, config.speed_sound, "SpdSound", "Speed of sound (m/s)")
        contents = add_line(contents, config.atm_pressure, "Patm", "Atmospheric pressure (Pa)")
        contents = add_line(contents, config.vapor_pressure, "Pvap", "Vapour pressure of air (Pa)")
        contents = add_line(contents, config.water_depth, "WtrDpth", "Water depth (m)")
        contents = add_line(contents, config.water_level_offset, "MSL2SWL", "Offset between still-water level and mean sea level (m)")
    return contents

def write_input_files(contents, config: FastConfig):
    contents = add_header(contents, "Input Files")
    contents = add_line(contents, f'"{config.elastodyn_file}"', "EDFile", "Name of file containing ElastoDyn input parameters (quoted string)")
    contents = add_line(contents, f'"{config.beamdyn_blade_file[0]}"', "BDBldFile(1)", "Name of file containing BeamDyn input parameters for blade 1 (quoted string)")
    contents = add_line(contents, f'"{config.beamdyn_blade_file[1]}"', "BDBldFile(2)", "Name of file containing BeamDyn input parameters for blade 2 (quoted string)")
    contents = add_line(contents, f'"{config.beamdyn_blade_file[2]}"', "BDBldFile(3)", "Name of file containing BeamDyn input parameters for blade 3 (quoted string)")
    contents = add_line(contents, f'"{config.inflow_wind_file}"', "InflowFile", "Name of file containing inflow wind input parameters (quoted string)")
    contents = add_line(contents, f'"{config.aerodyn_file}"', "AeroFile", "Name of file containing aerodynamic input parameters (quoted string)")
    contents = add_line(contents, f'"{config.servodyn_file}"', "ServoFile", "Name of file containing control and electrical-drive input parameters (quoted string)")
    contents = add_line(contents, f'"{config.hydrodyn_file}"', "HydroFile", "Name of file containing hydrodynamic input parameters (quoted string)")
    contents = add_line(contents, f'"{config.subdyn_file}"', "SubFile", "Name of file containing sub-structural input parameters (quoted string)")
    contents = add_line(contents, f'"{config.mooring_file}"', "MooringFile", "Name of file containing mooring system input parameters (quoted string)")
    contents = add_line(contents, f'"{config.icedyn_file}"', "IceFile", "Name of file containing ice input parameters (quoted string)")
    return contents

def write_output_settings(contents, config: FastConfig):
    contents = add_header(contents, "Output")
    contents = add_line(contents, "True", "SumPrint", "Print summary data to \"<RootName>.sum\" (flag)")
    contents = add_line(contents, 10.0, "SttsTime", "Amount of time between screen status messages (s)")
    contents = add_line(contents, 99999.0, "ChkptTime", "Amount of time between creating checkpoint files for potential restart (s)")
    contents = add_line(contents, "default", "DT_Out", "Time step for tabular output (s) (or \"default\")")
    contents = add_line(contents, 0.0, "TStart", "Time to begin tabular output (s)")
    contents = add_line(contents, 2, "OutFileFmt", "Format for tabular output file (1: text, 2: binary, 3: both)")
    contents = add_line(contents, "True", "TabDelim", "Use tab delimiters in text tabular output file? (flag)")
    contents = add_line(contents, f"{config.output_format}", "OutFmt", "Format used for text tabular output (quoted string)")
    return contents

def write_linearization(contents, config: FastConfig):
    contents = add_header(contents, "Linearization")
    contents = add_line(contents, "False", "Linearize", "Linearization analysis (flag)")
    contents = add_line(contents, "False", "CalcSteady", "Calculate steady-state periodic operating point (flag)")
    contents = add_line(contents, 3, "TrimCase", "Controller parameter to be trimmed (1=yaw, 2=torque, 3=pitch)")
    contents = add_line(contents, 0.001, "TrimTol", "Tolerance for rotational speed convergence")
    contents = add_line(contents, 0.01, "TrimGain", "Proportional gain for rotational speed error")
    contents = add_line(contents, 0, "Twr_Kdmp", "Damping factor for the tower")
    contents = add_line(contents, 0, "Bld_Kdmp", "Damping factor for the blades")
    contents = add_line(contents, 2, "NLinTimes", "Number of times to linearize")
    contents = add_line(contents, "30.0, 60.0", "LinTimes", "List of times at which to linearize (s)")
    contents = add_line(contents, 1, "LinInputs", "Inputs included in linearization (0=none, 1=standard, 2=all module inputs)")
    contents = add_line(contents, 1, "LinOutputs", "Outputs included in linearization (0=none, 1=from OutList(s), 2=all module outputs)")
    contents = add_line(contents, "False", "LinOutJac", "Include full jacobians in linearization (flag)")
    contents = add_line(contents, "False", "LinOutMod", "Write module-level linearization (flag)")
    return contents

def write_visualization(contents, config: FastConfig):
    contents = add_header(contents, "Visualization")
    contents = add_line(contents, 0, "WrVTK", "VTK visualization output (0=none, 1=initialization, 2=animation)")
    contents = add_line(contents, 2, "VTK_type", "Type of VTK visualization data (1=surfaces, 2=basic meshes, 3=all meshes)")
    contents = add_line(contents, "False", "VTK_fields", "Write mesh fields to VTK data files? (true/false)")
    contents = add_line(contents, 15.0, "VTK_fps", "Frame rate for VTK output (frames per second)")
    return contents
