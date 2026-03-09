# flake8: noqa: E501
from pathlib import Path
from openturbinecode.configs.pathing import PROJECT_ROOT
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.solvers.aerostructural.openfast.options import (FastConfig, ElastoDynConfig,
                                                                     AeroDynConfig, InflowWindConfig)

def generate_fast_config(location: Path, config: FastConfig):
    """Generate the FastConfig input file."""
    contents = f"""------- OpenFAST  INPUT FILE -------------------------------------------
# {"Test"} - OpenFAST v15
---------------------- SIMULATION CONTROL --------------------------------------
{str("True").ljust(14)} Echo            - Echo input data to <RootName>.ech (flag)
"{"FATAL"}"       AbortLevel      - Error level when simulation should abort (string) {{"WARNING", "SEVERE", "FATAL"}}
{str(config.t_max).ljust(14)} TMax             - Total run time (s)
{str(config.dt).ljust(14)} DT              - Recommended module time step (s)
{str(config.interp_order).ljust(14)} InterpOrder     - Interpolation order for input/output time history (-) {{1=linear, 2=quadratic}}
{str(config.num_correction).ljust(14)} NumCrctn        - Number of correction iterations (-) {{0=explicit calculation, i.e., no corrections}}
{str(config.dt_ujac).ljust(14)} DT_UJac         - Time between calls to get Jacobians (s)
{str(config.ujac_scale_factor).ljust(14)} UJacSclFact     - Scaling factor used in Jacobians (-)
---------------------- FEATURE SWITCHES AND FLAGS ------------------------------
{str(config.elastic).ljust(14)} CompElast       - Compute structural dynamics (switch) {{1=ElastoDyn; 2=ElastoDyn + BeamDyn for blades}}
{str(config.inflow).ljust(14)} CompInflow      - Compute inflow wind velocities (switch) {{0=still air; 1=InflowWind; 2=external from OpenFOAM}}
{str(config.aero).ljust(14)} CompAero        - Compute aerodynamic loads (switch) {{0=None; 1=AeroDyn v14; 2=AeroDyn v15}}
{str(config.servo).ljust(14)} CompServo       - Compute control and electrical-drive dynamics (switch) {{0=None; 1=ServoDyn}}
{str(config.hydro).ljust(14)} CompHydro       - Compute hydrodynamic loads (switch) {{0=None; 1=HydroDyn}}
{str(config.sub).ljust(14)} CompSub         - Compute sub-structural dynamics (switch) {{0=None; 1=SubDyn; 2=External Platform MCKF}}
{str(config.mooring).ljust(14)} CompMooring     - Compute mooring system (switch) {{0=None; 1=MAP++; 2=FEAMooring; 3=MoorDyn; 4=OrcaFlex}}
{str(config.ice).ljust(14)} CompIce         - Compute ice loads (switch) {{0=None; 1=IceFloe; 2=IceDyn}}
{str(config.mhk).ljust(14)} MHK             - MHK turbine type (switch) {{0=Not an MHK turbine; 1=Fixed MHK turbine; 2=Floating MHK turbine}}
---------------------- ENVIRONMENTAL CONDITIONS --------------------------------
{str(config.gravity).ljust(14)} Gravity         - Gravitational acceleration (m/s^2)
{str(config.air_density).ljust(14)} AirDens         - Air density (kg/m^3)
{str(config.water_density).ljust(14)} WtrDens         - Water density (kg/m^3)
{str(config.kinematic_viscosity).ljust(14)} KinVisc         - Kinematic viscosity of working fluid (m^2/s)
{str(config.speed_sound).ljust(14)} SpdSound        - Speed of sound in working fluid (m/s)
{str(config.atm_pressure).ljust(14)} Patm            - Atmospheric pressure (Pa) [used only for an MHK turbine cavitation check]
{str(config.vapor_pressure).ljust(14)} Pvap            - Vapour pressure of working fluid (Pa) [used only for an MHK turbine cavitation check]
{str(config.water_depth).ljust(14)} WtrDpth         - Water depth (m)
{str(config.water_level_offset).ljust(14)} MSL2SWL         - Offset between still-water level and mean sea level (m) [positive upward]
---------------------- INPUT FILES ---------------------------------------------
"{config.elastodyn_file}"    EDFile          - Name of file containing ElastoDyn input parameters (quoted string)
"{config.beamdyn_blade_file[0]}"    BDBldFile(1)    - Name of file containing BeamDyn input parameters for blade 1 (quoted string)
"{config.beamdyn_blade_file[1]}"    BDBldFile(2)    - Name of file containing BeamDyn input parameters for blade 2 (quoted string)
"{config.beamdyn_blade_file[2]}"    BDBldFile(3)    - Name of file containing BeamDyn input parameters for blade 3 (quoted string)
"{config.inflow_wind_file}"    InflowFile      - Name of file containing inflow wind input parameters (quoted string)
"{config.aerodyn_file}"    AeroFile        - Name of file containing aerodynamic input parameters (quoted string)
"{config.servodyn_file}"    ServoFile       - Name of file containing control and electrical-drive input parameters (quoted string)
"{config.hydrodyn_file}"      HydroFile       - Name of file containing hydrodynamic input parameters (quoted string)
"{config.subdyn_file}"      SubFile         - Name of file containing sub-structural input parameters (quoted string)
"{config.mooring_file}"      MooringFile     - Name of file containing mooring system input parameters (quoted string)
"{config.icedyn_file}"      IceFile         - Name of file containing ice input parameters (quoted string)
---------------------- OUTPUT --------------------------------------------------
False          SumPrint        - Print summary data to "<RootName>.sum" (flag)
          1   SttsTime        - Amount of time between screen status messages (s)
       1000   ChkptTime       - Amount of time between creating checkpoint files for potential restart (s)
        0.5   DT_Out          - Time step for tabular output (s) (or "default")
          0   TStart          - Time to begin tabular output (s)
          3   OutFileFmt      - Format for tabular (time-marching) output file (switch) (1: text file [<RootName>.out], 2: binary file [<RootName>.outb], 3: both)
True          TabDelim        - Use tab delimiters in text tabular output file? (flag) (uses spaces if false)
"ES10.3E2"    OutFmt          - Format used for text tabular output, excluding the time channel.  Resulting field should be 10 characters. (quoted string)
---------------------- LINEARIZATION -------------------------------------------
False         Linearize       - Linearization analysis (flag)
False         CalcSteady      - Calculate a steady-state periodic operating point before linearization? [unused if Linearize=False] (flag)
          3   TrimCase        - Controller parameter to be trimmed (1:yaw; 2:torque; 3:pitch) [used only if CalcSteady=True] (-)
     0.0001   TrimTol         - Tolerance for the rotational speed convergence [used only if CalcSteady=True] (-)
      0.001   TrimGain        - Proportional gain for the rotational speed error (>0) [used only if CalcSteady=True] (rad/(rad/s) for yaw or pitch; Nm/(rad/s) for torque)
          0   Twr_Kdmp        - Damping factor for the tower [used only if CalcSteady=True] (N/(m/s))
          0   Bld_Kdmp        - Damping factor for the blades [used only if CalcSteady=True] (N/(m/s))
          2   NLinTimes       - Number of times to linearize (-) [>=1] [unused if Linearize=False]
         30,         60    LinTimes        - List of times at which to linearize (s) [1 to NLinTimes] [unused if Linearize=False]
          1   LinInputs       - Inputs included in linearization (switch) (0=none; 1=standard; 2=all module inputs (debug)) [unused if Linearize=False]
          1   LinOutputs      - Outputs included in linearization (switch) (0=none; 1=from OutList(s); 2=all module outputs (debug)) [unused if Linearize=False]
False         LinOutJac       - Include full Jacobians in linearization output (for debug) (flag) [unused if Linearize=False; used only if LinInputs=LinOutputs=2]
False         LinOutMod       - Write module-level linearization output files in addition to output for full system? (flag) [unused if Linearize=False]
---------------------- VISUALIZATION ------------------------------------------
          0   WrVTK           - VTK visualization data output: (switch) (0=none; 1=initialization data only; 2=animation)
          1   VTK_type        - Type of VTK visualization data: (switch) (1=surfaces; 2=basic meshes (lines/points); 3=all meshes (debug)) [unused if WrVTK=0]
true         VTK_fields      - Write mesh fields to VTK data files? (flag) (true/false) [unused if WrVTK=0]
         20   VTK_fps         - Frame rate for VTK output (frames per second)(will use closest integer multiple of DT) [used only if WrVTK=2]
"""

    with open(location / f"{config.model.name}.fst", "w") as file:
        file.write(contents)

    return None

def generate_elastodyn_config(location: Path, config: ElastoDynConfig):
    """Generate the ElastoDyn input file for OpenFAST."""
    contents = f"""------- ELASTODYN v1.03.* INPUT FILE -------------------------------------------
DTU 10MW onshore reference wind turbine v0.1 - OpenFAST v2.4
---------------------- SIMULATION CONTROL --------------------------------------
{str(config.echo).upper():<15}Echo        - Echo input data to "<RootName>.ech" (flag)
{config.integration_method:<15}Method      - Integration method: {{1: RK4, 2: AB4, or 3: ABM4}} (-)
"{config.time_step}"     DT          - Integration time step (s)
---------------------- DEGREES OF FREEDOM --------------------------------------
{str(config.flap_dof1).upper():<15}FlapDOF1    - First flapwise blade mode DOF (flag)
{str(config.flap_dof2).upper():<15}FlapDOF2    - Second flapwise blade mode DOF (flag)
{str(config.edge_dof).upper():<15}EdgeDOF     - First edgewise blade mode DOF (flag)
{str(config.teeter_dof).upper():<15}TeetDOF    - Rotor-teeter DOF (flag) [unused for 3 blades]
{str(config.drivetrain_dof).upper():<15}DrTrDOF     - Drivetrain rotational-flexibility DOF (flag)
{str(config.generator_dof).upper():<15}GenDOF      - Generator DOF (flag)
{str(config.yaw_dof).upper():<15}YawDOF      - Yaw DOF (flag)
{str(config.fore_aft_tower_dof1).upper():<15}TwFADOF1    - First fore-aft tower bending-mode DOF (flag)
{str(config.fore_aft_tower_dof2).upper():<15}TwFADOF2    - Second fore-aft tower bending-mode DOF (flag)
{str(config.side_to_side_tower_dof1).upper():<15}TwSSDOF1    - First side-to-side tower bending-mode DOF (flag)
{str(config.side_to_side_tower_dof2).upper():<15}TwSSDOF2    - Second side-to-side tower bending-mode DOF (flag)
{str(config.platform_surge_dof).upper():<15}PtfmSgDOF   - Platform horizontal surge translation DOF (flag)
{str(config.platform_sway_dof).upper():<15}PtfmSwDOF   - Platform horizontal sway translation DOF (flag)
{str(config.platform_heave_dof).upper():<15}PtfmHvDOF   - Platform vertical heave translation DOF (flag)
{str(config.platform_roll_dof).upper():<15}PtfmRDOF    - Platform roll tilt rotation DOF (flag)
{str(config.platform_pitch_dof).upper():<15}PtfmPDOF   - Platform pitch tilt rotation DOF (flag)
{str(config.platform_yaw_dof).upper():<15}PtfmYDOF    - Platform yaw rotation DOF (flag)
---------------------- INITIAL CONDITIONS --------------------------------------
{config.out_of_plane_deflection:<15}OoPDefl     - Initial out-of-plane blade-tip displacement (meters)
{config.in_plane_deflection:<15}IPDefl      - Initial in-plane blade-tip deflection (meters)
{config.blade_pitch[0]:<15}BlPitch(1)  - Blade 1 initial pitch (degrees)
{config.blade_pitch[1]:<15}BlPitch(2)  - Blade 2 initial pitch (degrees)
{config.blade_pitch[2]:<15}BlPitch(3)  - Blade 3 initial pitch (degrees) [unused for 2 blades]
{config.teeter_deflection:<15}TeetDefl    - Initial or fixed teeter angle (degrees) [unused for 3 blades]
{config.azimuth_angle:<15}Azimuth     - Initial azimuth angle for blade 1 (degrees)
{round(config.rotor_speed, 2):<15}RotSpeed    - Initial or fixed rotor speed (rpm)
{config.nacelle_yaw:<15}NacYaw      - Initial or fixed nacelle-yaw angle (degrees)
{config.tower_top_fore_aft_disp:<15}TTDspFA     - Initial fore-aft tower-top displacement (meters)
{config.tower_top_side_disp:<15}TTDspSS     - Initial side-to-side tower-top displacement (meters)
{config.platform_surge_disp:<15}PtfmSurge   - Initial horizontal surge translational displacement of platform (meters)
{config.platform_sway_disp:<15}PtfmSway    - Initial horizontal sway translational displacement of platform (meters)
{config.platform_heave_disp:<15}PtfmHeave   - Initial vertical heave translational displacement of platform (meters)
{config.platform_roll_disp:<15}PtfmRoll    - Initial roll tilt rotational displacement of platform (degrees)
{config.platform_pitch_disp:<15}PtfmPitch   - Initial pitch tilt rotational displacement of platform (degrees)
{config.platform_yaw_disp:<15}PtfmYaw     - Initial yaw rotational displacement of platform (degrees)
---------------------- TURBINE CONFIGURATION -----------------------------------
{config.num_blades:<15}NumBl       - Number of blades (-)
{config.tip_radius:<15}TipRad      - The distance from the rotor apex to the blade tip (meters)
{config.hub_radius:<15}HubRad      - The distance from the rotor apex to the blade root (meters)
{config.precone_angles[0]:<15}PreCone(1)  - Blade 1 cone angle (degrees)
{config.precone_angles[1]:<15}PreCone(2)  - Blade 2 cone angle (degrees)
{config.precone_angles[2]:<15}PreCone(3)  - Blade 3 cone angle (degrees) [unused for 2 blades]
{config.hub_center_mass:<15}HubCM       - Distance from rotor apex to hub mass [positive downwind] (meters)
          0   UndSling    - Undersling length [distance from teeter pin to the rotor apex] (meters) [unused for 3 blades]
          0   Delta3      - Delta-3 angle for teetering rotors (degrees) [unused for 3 blades]
          0   AzimB1Up    - Azimuth value to use for I/O when blade 1 points up (degrees)
       -7.1   OverHang    - Distance from yaw axis to rotor apex [3 blades] or teeter pin [2 blades] (meters)
       3.55   ShftGagL    - Distance from rotor apex [3 blades] or teeter pin [2 blades] to shaft strain gages [positive for upwind rotors] (meters)
         -5   ShftTilt    - Rotor shaft tilt angle (degrees)
      2.697   NacCMxn     - Downwind distance from the tower-top to the nacelle CM (meters)
          0   NacCMyn     - Lateral  distance from the tower-top to the nacelle CM (meters)
       2.45   NacCMzn     - Vertical distance from the tower-top to the nacelle CM (meters)
   -3.09528   NcIMUxn     - Downwind distance from the tower-top to the nacelle IMU (meters)
          0   NcIMUyn     - Lateral  distance from the tower-top to the nacelle IMU (meters)
    2.23336   NcIMUzn     - Vertical distance from the tower-top to the nacelle IMU (meters)
       2.75   Twr2Shft    - Vertical distance from the tower-top to the rotor shaft (meters)
     115.63   TowerHt     - Height of tower above ground level [onshore] or MSL [offshore] (meters)
          0   TowerBsHt   - Height of tower base above ground level [onshore] or MSL [offshore] (meters)
          0   PtfmCMxt    - Downwind distance from the ground level [onshore] or MSL [offshore] to the platform CM (meters)
          0   PtfmCMyt    - Lateral distance from the ground level [onshore] or MSL [offshore] to the platform CM (meters)
          0   PtfmCMzt    - Vertical distance from the ground level [onshore] or MSL [offshore] to the platform CM (meters)
          0   PtfmRefzt   - Vertical distance from the ground level [onshore] or MSL [offshore] to the platform reference point (meters)
---------------------- MASS AND INERTIA ----------------------------------------
          0   TipMass(1)  - Tip-brake mass, blade 1 (kg)
          0   TipMass(2)  - Tip-brake mass, blade 2 (kg)
          0   TipMass(3)  - Tip-brake mass, blade 3 (kg) [unused for 2 blades]
   105.52E3   HubMass     - Hub mass (kg) 
 325.6709E3   HubIner     - Hub inertia about rotor axis [3 blades] or teeter axis [2 blades] (kg m^2)
     1500.5   GenIner     - Generator inertia about HSS (kg m^2) 
446.03625E3   NacMass     - Nacelle mass (kg) 
7326.3465E3   NacYIner    - Nacelle inertia about yaw axis (kg m^2) 
          0   YawBrMass   - Yaw bearing mass (kg)
          0   PtfmMass    - Platform mass (kg)
          0   PtfmRIner   - Platform inertia for roll tilt rotation about the platform CM (kg m^2)
          0   PtfmPIner   - Platform inertia for pitch tilt rotation about the platform CM (kg m^2)
          0   PtfmYIner   - Platform inertia for yaw rotation about the platform CM (kg m^2)
---------------------- BLADE ---------------------------------------------------
         40   BldNodes    - Number of blade nodes (per blade) used for analysis (-)
"{config.model.name}_EDBlade.dat"             BldFile(1)  - Name of file containing properties for blade 1 (quoted string)
"{config.model.name}_EDBlade.dat"              BldFile(2)  - Name of file containing properties for blade 2 (quoted string)
"{config.model.name}_EDBlade.dat"              BldFile(3)  - Name of file containing properties for blade 3 (quoted string) [unused for 2 blades]
---------------------- ROTOR-TEETER --------------------------------------------
          0   TeetMod     - Rotor-teeter spring/damper model (0: none, 1: standard, 2: user-defined from routine UserTeet) (switch) [unused for 3 blades]
          0   TeetDmpP    - Rotor-teeter damper position (degrees) [used only for 2 blades and when TeetMod=1]
          0   TeetDmp     - Rotor-teeter damping constant (N-m/(rad/s)) [used only for 2 blades and when TeetMod=1]
          0   TeetCDmp    - Rotor-teeter rate-independent Coulomb-damping moment (N-m) [used only for 2 blades and when TeetMod=1]
          0   TeetSStP    - Rotor-teeter soft-stop position (degrees) [used only for 2 blades and when TeetMod=1]
          0   TeetHStP    - Rotor-teeter hard-stop position (degrees) [used only for 2 blades and when TeetMod=1]
          0   TeetSSSp    - Rotor-teeter soft-stop linear-spring constant (N-m/rad) [used only for 2 blades and when TeetMod=1]
          0   TeetHSSp    - Rotor-teeter hard-stop linear-spring constant (N-m/rad) [used only for 2 blades and when TeetMod=1]
---------------------- DRIVETRAIN ----------------------------------------------
        100   GBoxEff     - Gearbox efficiency (%) 
      50.00   GBRatio     - Gearbox ratio (-) 
 2.317025E9   DTTorSpr    - Drivetrain torsional spring (N-m/rad) X
    9240560   DTTorDmp    - Drivetrain torsional damper (N-m/(rad/s)) X (1.99E5 * .07)
---------------------- FURLING -------------------------------------------------
False         Furling     - Read in additional model properties for furling turbine (flag) [must currently be FALSE)
"unused"      FurlFile    - Name of file containing furling properties (quoted string) [unused when Furling=False]
---------------------- TOWER ---------------------------------------------------
         20   TwrNodes    - Number of tower nodes used for analysis (-)
"{config.model.name}_EDTower.dat"    TwrFile     - Name of file containing tower properties (quoted string)
---------------------- OUTPUT --------------------------------------------------
False         SumPrint    - Print summary data to "<RootName>.sum" (flag)
          1   OutFile     - Switch to determine where output will be placed: (1: in module output file only; 2: in glue code output file only; 3: both) (currently unused)
True          TabDelim    - Use tab delimiters in text tabular output file? (flag) (currently unused)
"ES10.3E2"    OutFmt      - Format used for text tabular output (except time).  Resulting field should be 10 characters. (quoted string) (currently unused)
          0   TStart      - Time to begin tabular output (s) (currently unused)
          1   DecFact     - Decimation factor for tabular output (1: output every time step) (-) (currently unused)
          3   NTwGages    - Number of tower nodes that have strain gages for output [0 to 9] (-)
         5,         10,         15    TwrGagNd    - List of tower nodes that have strain gages [1 to TwrNodes] (-) [unused if NTwGages=0]
          9   NBlGages    - Number of blade nodes that have strain gages for output [0 to 9] (-)
          3, 6, 10, 14, 20, 27, 30, 34, 38    BldGagNd    - List of blade nodes that have strain gages [1 to BldNodes] (-) [unused if NBlGages=0]
              OutList     - The next line(s) contains a list of output parameters.  See OutListParameters.xlsx for a listing of available output channels, (-)
"RootMxb1"    - RootMEdg1 Blade 1 edgewise moment
"RootMyb1"     - RootMFlp1 Blade 1 flapwise moment
"RootMzb1"     - Pitching moment
"Spn1MLxb1"   - local edgewise and flapwise bending moments
"Spn1MLyb1"
"Spn2MLxb1"   - local edgewise and flapwise bending moments
"Spn2MLyb1"
"Spn3MLxb1"   - local edgewise and flapwise bending moments
"Spn3MLyb1"
"Spn4MLxb1"   - local edgewise and flapwise bending moments
"Spn4MLyb1"
"Spn5MLxb1"   - local edgewise and flapwise bending moments
"Spn5MLyb1"
"Spn6MLxb1"   - local edgewise and flapwise bending moments
"Spn6MLyb1"
"Spn7MLxb1"   - local edgewise and flapwise bending moments
"Spn7MLyb1"
"Spn8MLxb1"   - local edgewise and flapwise bending moments
"Spn8MLyb1"
"Spn9MLxb1"   - local edgewise and flapwise bending moments
"Spn9MLyb1"
END
---------------------- NODE OUTPUTS --------------------------------------------
          3   BldNd_BladesOut  - Blades to output
         99   - Blade nodes on each blade (currently unused)
                   OutList             - The next line(s) contains a list of output parameters.  See s for a listing of available output channels, (-)
"ALx"
"ALy"
"ALz"
"RotSpeed"                - Low-speed shaft and high-speed shaft speeds
"GenSpeed"                - Low-speed shaft and high-speed shaft speeds
"TTDspFA"                 - Tower fore-aft and side-to-side displacements and top twist
"TTDspSS"                 - Tower fore-aft and side-to-side displacements and top twist
"TTDspTwst"               - Tower fore-aft and side-to-side displacements and top twist
"YawBrFxp"                - Fore-aft shear, side-to-side shear, and vertical forces at the top of the tower (not rotating with nacelle yaw)
"YawBrFyp"                - Fore-aft shear, side-to-side shear, and vertical forces at the top of the tower (not rotating with nacelle yaw)
"YawBrFzp"                - Fore-aft shear, side-to-side shear, and vertical forces at the top of the tower (not rotating with nacelle yaw)
"YawBrMxp"                - Side-to-side bending, fore-aft bending, and yaw moments at the top of the tower (not rotating with nacelle yaw)
"YawBrMyp"                - Side-to-side bending, fore-aft bending, and yaw moments at the top of the tower (not rotating with nacelle yaw)
"YawBrMzp"                - Side-to-side bending, fore-aft bending, and yaw moments at the top of the tower (not rotating with nacelle yaw)
"TwrBsFxt"                - Fore-aft shear, side-to-side shear, and vertical forces at the base of the tower (mudline)
"TwrBsFyt"                - Fore-aft shear, side-to-side shear, and vertical forces at the base of the tower (mudline)
"TwrBsFzt"                - Fore-aft shear, side-to-side shear, and vertical forces at the base of the tower (mudline)
"TwrBsMxt"                - Side-to-side bending, fore-aft bending, and yaw moments at the base of the tower (mudline)
"TwrBsMyt"                - Side-to-side bending, fore-aft bending, and yaw moments at the base of the tower (mudline)
"TwrBsMzt"                - Side-to-side bending, fore-aft bending, and yaw moments at the base of the tower (mudline)
END of input file (the word "END" must appear in the first 3 columns of this last OutList line)
---------------------------------------------------------------------------------------

"BldPitch1"               - Blade 1 pitch angle
"Azimuth"                 - Blade 1 azimuth angle
"RotTorq"                 - Rotor torque and low-speed shaft 0- and 90-bending moments at the main bearing
"LSSGagMya"               - Rotor torque and low-speed shaft 0- and 90-bending moments at the main bearing
"LSSGagMza"               - Rotor torque and low-speed shaft 0- and 90-bending moments at the main bearing

"RootFxb1 RootFxb2 RootFxb3"                - Out-of-plane shear, in-plane shear, and axial forces at the root of blade 1
"RootFyb1 RootFyb2 RootFyb3"                - Out-of-plane shear, in-plane shear, and axial forces at the root of blade 1
"RootFzb1 RootFzb2 RootFzb3"                - Out-of-plane shear, in-plane shear, and axial forces at the root of blade 1
"RootMxb1 RootMxb2 RootMxb3"                - In-plane bending, out-of-plane bending, and pitching moments at the root of blade 1
"RootMyb1 RootMyb2 RootMyb3"                - In-plane bending, out-of-plane bending, and pitching moments at the root of blade 1
"RootMzb1 RootMzb2 RootMzb3"                - In-plane bending, out-of-plane bending, and pitching moments at the root of blade 1

"TipDxb1 TipDxb2 TipDxb3"
"TipDyb1 TipDyb2 TipDyb3"
"TipDzb1 TipDzb2 TipDzb3"
"TipALxb1 TipALxb2 TipALxb3"
"TipALyb1 TipALyb2 TipALyb3"
"TipALzb1 TipALzb2 TipALzb3"

"OoPDefl1"                - Blade 1 out-of-plane and in-plane deflections and tip twist
"IPDefl1"                 - Blade 1 out-of-plane and in-plane deflections and tip twist
"TwstDefl1"               - Blade 1 out-of-plane and in-plane deflections and tip twist
"""
    # Write the file
    with open(location / f"{config.model.name}_ED.dat", "w") as file:
        file.write(contents)

    return None

def generate_aerodyn_config(location: Path, config: AeroDynConfig):
    """Generate the AeroDyn input file for OpenFAST."""
    contents = f"""------- AERODYN v15 for OpenFAST INPUT FILE -----------------------------------------------
DTU 10MW onshore reference wind turbine v0.1 - OpenFAST v3.5.3
======  General Options  ============================================================================
{str(config.echo).upper():<15}Echo               - Echo the input to "<rootname>.AD.ech"?  (flag)
"{config.dt_aero}"       DTAero             - Time interval for aerodynamic calculations {{or "default"}} (s)
{config.wake_model:<15}WakeMod            - Type of wake/induction model (switch) {{0=none, 1=BEMT, 2=DBEMT}} [WakeMod cannot be 2 when linearizing]
{config.airfoil_aero_model:<15}AFAeroMod          - Type of blade airfoil aerodynamics model (switch) {{1=steady model, 2=Beddoes-Leishman unsteady model}} [AFAeroMod must be 1 when linearizing]
{config.tower_potential_flow:<15}TwrPotent          - Type tower influence on wind based on potential flow around the tower (switch) {{0=none, 1=baseline potential flow, 2=potential flow with Bak correction}}
{config.tower_shadow:<15}TwrShadow          - Calculate tower influence on wind based on downstream tower shadow? (flag)
{str(config.tower_aero).upper():<15}TwrAero           - Calculate tower aerodynamic loads? (flag)
{str(config.frozen_wake).upper():<15}FrozenWake         - Assume frozen wake during linearization? (flag) [used only when WakeMod=1 and when linearizing]
{str(config.cavitation_check).upper():<15}CavitCheck         - Perform cavitation check? (flag) [AFAeroMod must be 1 when CavitCheck=true]
{str(config.buoyancy_effects).upper():<15}Buoyancy           - Include buoyancy effects? (flag)
{str(config.compute_acoustics).upper():<15}CompAA             - Flag to compute AeroAcoustics calculation [only used when WakeMod=1 or 2]
"{config.acoustics_input_file}"       AA_InputFile       - Aeroacoustics input file
======  Environmental Conditions  ===================================================================
{config.air_density:<15.3f}AirDens            - Air density (kg/m^3)
{config.kinematic_viscosity:<15.3E}KinVisc            - Kinematic air viscosity (m^2/s)
{config.speed_of_sound:<15.2f}SpdSound           - Speed of sound (m/s)
{config.atmospheric_pressure:<15.1f}Patm               - Atmospheric pressure (Pa) [used only when CavitCheck=True]
{config.vapor_pressure:<15.1f}Pvap               - Vapour pressure of fluid (Pa) [used only when CavitCheck=True]
======  Blade-Element/Momentum Theory Options  ====================================================== [unused when WakeMod=0]
{config.skewed_wake_model:<15}SkewMod            - Type of skewed-wake correction model (switch) {{1=uncoupled, 2=Pitt/Peters, 3=coupled}} [unused when WakeMod=0]
"{config.skew_factor}"       SkewModFactor      - Constant used in Pitt/Peters skewed wake model {{or "default" is 15/32*pi}} (-) [used only when SkewMod=2; unused when WakeMod=0]
{str(config.tip_loss).upper():<15}TipLoss            - Use the Prandtl tip-loss model? (flag) [unused when WakeMod=0]
{str(config.hub_loss).upper():<15}HubLoss            - Use the Prandtl hub-loss model? (flag) [unused when WakeMod=0]
{str(config.tangential_induction).upper():<15}TanInd             - Include tangential induction in BEMT calculations? (flag) [unused when WakeMod=0]
{str(config.axial_induction_drag).upper():<15}AIDrag             - Include the drag term in the axial-induction calculation? (flag) [unused when WakeMod=0]
{str(config.tangential_induction_drag).upper():<15}TIDrag             - Include the drag term in the tangential-induction calculation? (flag) [unused when WakeMod=0 or TanInd=FALSE]
"{config.induction_tolerance}"     IndToler           - Convergence tolerance for BEMT nonlinear solve residual equation {{or "default"}} (-) [unused when WakeMod=0]
{config.max_iterations:<15}MaxIter            - Maximum number of iteration steps (-) [unused when WakeMod=0]
======  Dynamic Blade-Element/Momentum Theory Options  ============================================== [used only when WakeMod=2]
{config.dynamic_bemt_model:<15}DBEMT_Mod          - Type of dynamic BEMT (DBEMT) model {{1=constant tau1, 2=time-dependent tau1}} (-) [used only when WakeMod=2]
{config.tau1_constant:<15.1f}tau1_const         - Time constant for DBEMT (s) [used only when WakeMod=2 and DBEMT_Mod=1]
======  OLAF -- cOnvecting LAgrangian Filaments (Free Vortex Wake) Theory Options  ================== [used only when WakeMod=3]
"{config.olaf_input_file}"      OLAFInputFileName - Input file for OLAF [used only when WakeMod=3]
======  Beddoes-Leishman Unsteady Airfoil Aerodynamics Options  ===================================== [used only when AFAeroMod=2]
{config.unsteady_aero_model:<15}UAMod              - Unsteady Aero Model Switch (switch) {{1=Baseline model (Original), 2=Gonzalez's variant, 3=Minemma/Pierce variant}} [used only when AFAeroMod=2]
{str(config.f_lookup).upper():<15}FLookup            - Flag for f' lookup or best-fit exponential equations [used only when AFAeroMod=2]
======  Airfoil Information =========================================================================
{config.airfoil_table_mode:<15}AFTabMod           - Interpolation method for multiple airfoil tables
{config.angle_of_attack_column:<15}InCol_Alfa         - The column in the airfoil tables that contains the angle of attack
{config.lift_coefficient_column:<15}InCol_Cl           - The column in the airfoil tables that contains the lift coefficient
{config.drag_coefficient_column:<15}InCol_Cd           - The column in the airfoil tables that contains the drag coefficient
{config.pitching_moment_column:<15}InCol_Cm           - The column in the airfoil tables that contains the pitching-moment coefficient
{config.cpmin_column:<15}InCol_Cpmin        - The column in the airfoil tables that contains the Cpmin coefficient
{config.num_airfoil_files:<15}NumAFfiles         - Number of airfoil files used (-)
"""

    # Add airfoil files
    for file in config.airfoil_files:
        contents += f'"{file}"\n'

    # Rotor/Blade Properties
    contents += f"""======  Rotor/Blade Properties  =====================================================================
{str(config.include_pitching_moment).upper():<15}UseBlCm            - Include aerodynamic pitching moment in calculations?  (flag)
"""

    for i, blade_file in enumerate(config.blade_files, start=1):
        contents += f'"{blade_file}"    ADBlFile({i})        - Name of file containing distributed aerodynamic properties for Blade #{i} (-)\n'

    contents += f"""
======  Tower Influence and Aerodynamics ============================================================= [used only when TwrPotent/=0, TwrShadow=True, or TwrAero=True]
10                     NumTwrNds   - Number of tower nodes used in the analysis  (-) [used only when TwrPotent/=0, TwrShadow=True, or TwrAero=True]
TwrElev        TwrDiam        TwrCd       TwrTI
(m)              (m)           (-)         (-)
  15.0           3.556         1.0        0.1
  28.0           3.556         1.0        0.1
  41.0           3.556         1.0        0.1
  54.0           3.556         1.0        0.1
  67.0           3.556         1.0        0.1
  80.0           3.556         1.0        0.1
  93.0           3.556         1.0        0.1
 106.0           3.556         1.0        0.1
 119.0           3.556         1.0        0.1
 130.1           3.556         1.0        0.1
======  Tower Influence and Aerodynamics ============================================================= [used only when TwrPotent/=0, TwrShadow=True, or TwrAero=True]
TRUE                   SumPrint    - Generate a summary file listing input options and interpolated properties to "<rootname>.AD.sum"?  (flag)
6                      NBlOuts     - Number of blade node outputs [0 - 9] (-)
1, 6, 11, 15, 20, 28   BlOutNd     - Blade nodes whose values will be output  (-)
0                      NTwOuts     - Number of tower node outputs [0 - 9]  (-)
1, 2, 3, 4, 5          TwOutNd     - Tower nodes whose values will be output  (-)
                       OutList     - The next line(s) contains a list of output parameters.  See OutListParameters.xlsx for a listing of available output channels, (-)
"RtAeroFxh"
"RtAeroFyh"
"RtAeroFzh"
"RtAeroMxh"
"RtAeroMyh"
"RtAeroMzh"
"RtVAvgxh"
"RtAeroCp"
"RtTSR"
END of input file (the word "END" must appear in the first 3 columns of this last OutList line)
---------------------------------------------------------------------------------------
"""

    # Write the file
    with open(location / f"{config.model.name}_AD15.dat", "w") as file:
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
    with open(location / f"{config.model.name}_IW.dat", "w") as file:
        file.write(contents)

    return None


if __name__ == "__main__":
    # Define the turbine model and related configurations
    model = TurbineModel()
    fast_config = FastConfig(model)
    elastodyn_config = ElastoDynConfig(model)
    aerodyn_config = AeroDynConfig(model)
    inflow_wind_config = InflowWindConfig(model)

    # Output directory for generated files
    output_dir = PROJECT_ROOT / "solvers" / "aerostructural" / "openfast"
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate configuration files
    generate_fast_config(output_dir, fast_config)
    generate_elastodyn_config(output_dir, elastodyn_config)
    generate_aerodyn_config(output_dir, aerodyn_config)
    generate_inflow_wind_config(output_dir, inflow_wind_config)

    print(f"Configuration files generated in: {output_dir}")
