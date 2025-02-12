import yaml
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.configs.pathing import PROJECT_ROOT
from openturbinecode.utils.utilities import calculate_tsr_or_missing
import pandas as pd
import numpy as np


class OpenFASTConfig:
    def __init__(self, model: TurbineModel):
        self.model = model
        self.fast = FastConfig(model)
        self.elastodyn = ElastoDynConfig(model)
        self.aerodyn = AeroDynConfig(model)
        self.inflow_wind = InflowWindConfig(model)

    def write_to_yaml(self, filename):
        """Write the turbine model to a YAML file.

        Args:
            filename (str): The name of the YAML file.
        """
        save_location = PROJECT_ROOT / "solvers" / "aerodynamics" / "turbinesFoam" / filename

        with open(save_location, "w") as file:
            yaml.dump(self.create_dict_for_yaml(), file)

    def create_dict_for_yaml(self):
        """Return the turbine model as a dictionary.

        Returns:
            dict: A dictionary containing the turbine model parameters.
        """
        dict = {"fast": self.fast.__dict__,
                "aerodyn": self.aerodyn.__dict__,
                "elastodyn": self.elastodyn.__dict__,
                "inflow_wind": self.inflow_wind.__dict__}
        return dict

    def read_from_yaml(self, filename):
        """Read the turbine model from a YAML file.

        Args:
            filename (str): The name of the YAML file.
        """
        load_location = PROJECT_ROOT / "solvers" / "aerodynamics" / "turbinesFoam" / filename
        with open(load_location, "r") as file:
            data = yaml.safe_load(file)

        self.fast = FastConfig(self.model)
        self.elastodyn = ElastoDynConfig(self.model)
        self.aerodyn = AeroDynConfig(self.model)
        self.inflow_wind = InflowWindConfig(self.model)

        self.fast.__dict__.update(data["fast"])
        self.elastodyn.__dict__.update(data["elastodyn"])
        self.aerodyn.__dict__.update(data["aerodyn"])
        self.inflow_wind.__dict__.update(data["inflow_wind"])

        return self


class FastConfig:
    def __init__(self, model: TurbineModel):
        self.model = model

        # Simulation Control
        self.t_max = 300.0  # Maximum simulation time [s]
        self.dt = 0.025  # Time step [s]
        self.interp_order = 2  # Interpolation order for I/O time history (1=linear, 2=quadratic)
        self.num_correction = 0  # Number of correction iterations (0=explicit)
        self.dt_ujac = 99999  # Time step between calls to get Jacobians
        self.ujac_scale_factor = 1e6  # Scale factor for the Jacobian calculation

        # Feature switches
        self.elastic = 1  # (1=elastodyn, 2=elastodyn+beamdyn)
        self.inflow = 1  # (0=still air, 1=inflow wind, 2=external inflow)
        self.aero = 2  # (0=aerodyn, 1=aerodyn15, 2=aerodyn14)
        self.servo = 1  # (0=none, 1=servodyn)
        self.hydro = 0  # (0=none, 1=hydrodyn)
        self.sub = 0  # (0=none, 1=subdyn, 2=external platform)
        self.mooring = 0  # (0=none, 1=map++, 2=feamooring, 3=moordyn)
        self.ice = 0  # (0=none, 1=iceflow, 2=icedyn)
        self.mhk = 0  # (0=not mhk, 1=fixed mhk, 2=floating mhk)

        # Environmental conditions
        self.gravity = model.environment.gravity  # Acceleration due to gravity [m/s^2]
        self.air_density = model.fluid.density  # Air density [kg/m^3]
        self.water_density = 0.0  # Water density [kg/m^3]
        self.kinematic_viscosity = model.fluid.kinematic_viscosity  # Kinematic viscosity of air [m^2/s]
        self.speed_sound = model.environment.speed_of_sound  # Speed of sound [m/s]
        self.atm_pressure = model.environment.atmospheric_pressure  # Atmospheric pressure [Pa]
        self.vapor_pressure = model.environment.vapor_pressure  # Vapor pressure [Pa]
        self.water_depth = 0.50  # Water depth [m]
        self.water_level_offset = 0.0   # Offset between water and seal level [m]

        # Input files
        self.elastodyn_file = f"{model.name}_ED.dat"  # Elastodyn input file
        # self.beamdyn_blade_file = [f"{model.name}_BD.dat",
        #                            f"{model.name}_BD.dat",
        #                            f"{model.name}_BD.dat"]
        self.beamdyn_blade_file = ["unused", "unused", "unused"]
        self.inflow_wind_file = f"{model.name}_IW.dat"
        self.aerodyn_file = f"{model.name}_AD15.dat"
        self.servodyn_file = f"{model.name}_SD.dat"
        # self.hydrodyn_file = f"{model.name}_HD.dat"
        self.hydrodyn_file = "unused"
        self.subdyn_file = "unused"
        # self.subdyn_file = f"{model.name}_SUB.dat"
        self.mooring_file = "unused"
        self.icedyn_file = "unused"

        # Output files
        self.sum_print = True  # Print summary data
        self.output_format = "ES13.6E2"

        # Linearization
        self.linearize = False  # Linearization flag. All other options are False if this is False

        # Visualization
        self.wr_vtk = 0  # Write VTK files for visualization
        self.vtk_type = 2  # Type of VTK visualization data (1=surfaces, 2=basic meshes)
        self.vtk_fps = 15.0  # Frames per second for VTK output


class ElastoDynConfig:
    def __init__(self, model: TurbineModel):
        self.model = model

        # Simulation control
        self.echo: bool = False  # Echo input data to <RootName>.ech (flag)
        self.integration_method: int = 3  # Integration method: {1: RK4, 2: AB4, or 3: ABM4}
        self.time_step: str = "DEFAULT"  # Integration time step (s)

        # Degrees of freedom
        self.flap_dof1: bool = False  # First flapwise blade mode DOF
        self.flap_dof2: bool = False  # Second flapwise blade mode DOF
        self.edge_dof: bool = False  # First edgewise blade mode DOF
        self.teeter_dof: bool = False  # Rotor-teeter DOF (unused for 3 blades)
        self.drivetrain_dof: bool = False  # Drivetrain rotational-flexibility DOF
        self.generator_dof: bool = False  # Generator DOF
        self.yaw_dof: bool = False  # Yaw DOF
        self.fore_aft_tower_dof1: bool = False  # First fore-aft tower bending-mode DOF
        self.fore_aft_tower_dof2: bool = False  # Second fore-aft tower bending-mode DOF
        self.side_to_side_tower_dof1: bool = False  # First side-to-side tower bending-mode DOF
        self.side_to_side_tower_dof2: bool = False  # Second side-to-side tower bending-mode DOF
        self.platform_surge_dof: bool = False  # Platform horizontal surge DOF
        self.platform_sway_dof: bool = False  # Platform horizontal sway DOF
        self.platform_heave_dof: bool = False  # Platform vertical heave DOF
        self.platform_roll_dof: bool = False  # Platform roll tilt DOF
        self.platform_pitch_dof: bool = False  # Platform pitch tilt DOF
        self.platform_yaw_dof: bool = False  # Platform yaw DOF

        # Environmental conditions for v300
        self.gravity: float = model.environment.gravity  # Acceleration due to gravity (m/s^2)

        # Initial conditions
        self.out_of_plane_deflection: float = 0.0  # Initial out-of-plane blade-tip deflection (m)
        self.in_plane_deflection: float = 0.0  # Initial in-plane blade-tip deflection (m)
        self.blade_pitch: list[float] = [model.blade.pitch_angle,
                                         model.blade.pitch_angle,
                                         model.blade.pitch_angle]  # Blade initial pitch angles (degrees)
        self.teeter_deflection: float = 0.0  # Initial or fixed teeter angle (degrees)
        self.azimuth_angle: float = 0.0  # Initial azimuth angle for blade 1 (degrees)
        # Initial or fixed rotor speed (rpm)
        if model.blade.rotor_speed is None:
            model.blade.rotor_speed = calculate_tsr_or_missing(tsr=model.blade.tip_speed_ratio,
                                                               freestream_velocity=model.fluid.velocity,
                                                               radius=model.blade.radius)
        self.rotor_speed: float = np.round(model.blade.rotor_speed, 2)
        self.nacelle_yaw: float = 0.0  # Initial or fixed nacelle-yaw angle (degrees)
        self.tower_top_fore_aft_disp: float = 0.0  # Initial fore-aft tower-top displacement (m)
        self.tower_top_side_disp: float = 0.0  # Initial side-to-side tower-top displacement (m)
        self.platform_surge_disp: float = 0.0  # Initial horizontal surge translational displacement (m)
        self.platform_sway_disp: float = 0.0  # Initial horizontal sway translational displacement (m)
        self.platform_heave_disp: float = 0.0  # Initial vertical heave translational displacement (m)
        self.platform_roll_disp: float = 0.0  # Initial roll tilt rotational displacement (degrees)
        self.platform_pitch_disp: float = 0.0  # Initial pitch tilt rotational displacement (degrees)
        self.platform_yaw_disp: float = 0.0  # Initial yaw rotational displacement (degrees)

        # Turbine configuration
        self.num_blades: int = model.rotor.n_blades  # Number of blades
        self.tip_radius: float = model.blade.radius  # Distance from the rotor apex to blade tip (m)
        self.hub_radius: float = model.hub.radius  # Distance from the rotor apex to blade root (m)
        self.precone_angles: list[float] = [model.rotor.blade_precone_angle * x for x in [1, 1, 1]]  # for blade (deg)
        self.hub_center_mass: float = 0.15  # Distance from rotor apex to hub mass (m)
        self.undersling_length: float = 0.0  # Distance from teeter pin to underpin axis (m)
        self.azimuth_b1_up: float = 0.0  # Azimuth angle for blade 1 in upwind configuration (deg)
        self.overhang: float = -10.86  # Distance from rotor apex to blade root in downwind direction (m)
        self.shaft_tilt: float = model.rotor.tilt_angle  # Rotor shaft tilt angle (degrees)
        self.nacelle_cm: list[float] = [4.375, 0.0, 6.285]  # Nacelle center of mass (m)
        self.nacelle_imu: list[float] = [4.375, 0, 6.285]
        self.tower_to_shaft: float = 7.163  # Vertical distance from tower-top to rotor shaft (m)
        self.tower_height: float = model.tower.height  # Height of tower above ground level (m)
        self.base_tower_height: float = 13.93  # Height of tower base above ground level (m)
        self.platform_cm: list[float] = [0.0, 0.0, 0.0]  # Platform center of mass (m)
        self.platform_vert_ref: float = 0.0  # Platform reference point (m)

        # Mass and inertia
        self.tip_mass: list[float] = [0.0 for _ in range(3)]  # Blade tip mass (kg)
        self.hub_mass: float = 442573.0  # Hub mass (kg)
        self.hub_inertia: float = 7341300  # Hub inertia about rotor axis (kg*m^2)
        self.generator_inertia: float = 0  # Generator inertia about HSS (kg*m^2)
        self.nacelle_mass: float = 479960  # Nacelle mass (kg)
        self.nacelle_yaw_inertia: float = 42486734  # Nacelle inertia about yaw axis (kg*m^2)
        self.yaw_bearing_mass: float = 31899.0  # Yaw bearing mass (kg)
        self.platform_mass: float = 0.0  # Platform mass (kg)
        self.platform_inertia: list[float] = [0.0, 0.0, 0.0]  # Platform inertia roll-pitch-yaw (kg*m^2)

        # Blade properties
        self.num_blade_nodes: int = 100  # Number of blade nodes used for analysis
        self.blade_files: list[str] = [
            f"{model.name}_EDBlade.dat",
            f"{model.name}_EDBlade.dat",
            f"{model.name}_EDBlade.dat",
        ]  # Blade input files

        # Rotor-teeter
        self.teeter_mode: int = 0  # Rotor-teeter spring/damper model (unused for 3 blades)
        self.teeter_damping: float = 0.0  # Rotor-teeter damping constant (N*m/(rad/s))

        # Drivetrain
        self.gearbox_efficiency: float = 100.0  # Gearbox efficiency (%)
        self.gear_ratio: float = 1.0  # Gearbox ratio
        self.torsional_spring: float = 8.235e15  # Drivetrain torsional spring (N*m/rad)
        self.torsional_damper: float = 6.215e15  # Drivetrain torsional damper (N*m/(rad/s))

        # Tower
        self.num_tower_nodes: int = 21  # Number of tower nodes
        self.tower_file: str = f"{model.name}_EDTower.dat"  # Tower input file

        self.output = [
            "Azimuth",
            "BldPitch1",
            "GenSpeed",
            "RotSpeed",
            "IPDefl1",
            "OoPDefl1",
            "RootMxb1",
            "RootMyb1",
            "TipDxb1",
            "TipDyb1",
            "NcIMUTAxs",
            "NcIMUTAys",
            "NcIMUTAzs",
            "RotTorq",
            "RotThrust",
            "TwrBsMxt",
            "TwrBsMyt",
            "TwrBsMzt",
            "YawBrFxp",
            "YawBrFyp",
            "YawBrFzp",
            "YawBrMxp",
            "YawBrMyp",
            "YawBrMzp",
            "TwrBsFzt",
            "NacYaw",
            "PtfmSurge",
            "PtfmSway",
            "PtfmHeave",
            "PtfmRoll",
            "PtfmPitch",
            "PtfmYaw",
            "YawBrTDxt",
            "YawBrTDyt"
        ]

    def validate(self):
        """Perform validation checkson the configuration."""
        if not (1 <= self.num_blades <= 3):
            raise ValueError("Number of blades must be between 1 and 3.")
        if self.teeter_dof and self.num_blades != 2:
            raise ValueError("Teeter DOF is only valid for 2-bladed rotors.")

    def to_dict(self):
        """Convert the configuration to a dictionary."""
        return self.__dict__


class AeroDynConfig:
    def __init__(self, model: TurbineModel):
        self.model = model

        # General Options
        self.echo: bool = False  # Echo the input to "<rootname>.AD.ech"
        self.dt_aero: str = "default"  # Time interval for aerodynamic calculations
        self.wake_model: int = 1  # Type of wake/induction model {0=none, 1=BEMT, 2=DBEMT}
        self.airfoil_aero_model: int = 1  # Type of blade airfoil aerodynamics model {1=steady, 2=unsteady (Beddoes-Leishman)}
        self.tower_potential_flow: int = 1  # Tower influence based on potential flow {0=none, 1=baseline, 2=Bak correction}
        self.tower_shadow: int = 1  # Tower influence based on downstream shadow {0=none, 1=included}
        self.tower_aero: bool = True  # Calculate tower aerodynamic loads?
        self.frozen_wake: bool = False  # Assume frozen wake during linearization?
        self.cavitation_check: bool = False  # Perform cavitation check?
        self.buoyancy_effects: bool = False  # Include buoyancy effects?
        self.compute_acoustics: bool = False  # Compute AeroAcoustics calculations?
        self.acoustics_input_file: str = "unused"  # Aeroacoustics input file

        # Environmental Conditions
        self.air_density: float = 1.225  # Air density (kg/m^3)
        self.kinematic_viscosity: float = model.fluid.kinematic_viscosity  # Kinematic air viscosity (m^2/s)
        self.speed_of_sound: float = model.environment.speed_of_sound  # Speed of sound (m/s)
        self.atmospheric_pressure: float = 103500.0  # Atmospheric pressure (Pa)
        self.vapor_pressure: float = 1700.0  # Vapor pressure of fluid (Pa)
        self.fluid_depth: float = 0.5  # Fluid depth (m)

        # Blade-Element/Momentum Theory Options
        self.skewed_wake_model: int = 2  # ype of skewed-wake correction model (switch) {1=uncoupled, 2=Pitt/Peters, 3=coupled} [unused when WakeMod=0 or 3]
        self.skew_factor: str = "default"  # Skew model factor
        self.tip_loss: bool = True  # Use Prandtl tip-loss model?
        self.hub_loss: bool = True  # Use Prandtl hub-loss model?
        self.tangential_induction: bool = True  # Include tangential induction?
        self.axial_induction_drag: bool = True  # Include drag term in axial-induction calculation?
        self.tangential_induction_drag: bool = True  # Include drag term in tangential-induction calculation?
        self.induction_tolerance: str = "default"  # Convergence tolerance for BEMT residual equation
        self.max_iterations: int = 500  # Maximum number of iterations for BEMT solve

        # Dynamic Blade-Element/Momentum Theory Options
        self.dynamic_bemt_model: int = 2  # Type of dynamic BEMT model
        self.tau1_constant: float = 2  # Time constant for DBEMT

        # OLAF -- Convecting Lagrangian Filaments Options
        self.olaf_input_file: str = "unused"  # Input file for OLAF

        # Beddoes-Leishman Unsteady Airfoil Aerodynamics Options
        self.unsteady_aero_model: int = 3  # Unsteady Aero Model Switch (switch) {1=Baseline model (Original), 2=Gonzalez's variant (changes in Cn,Cc,Cm), 3=Minnema/Pierce variant (changes in Cc and Cm)} [used only when AFAeroMod=2]
        self.f_lookup: bool = True  # Flag for f' lookup or best-fit exponential equations
        self.ua_radius: list[float] = [0.25, 0.95]  # Radius for unsteady aerodynamics stall (m)

        # Airfoil Information
        self.airfoil_table_mode: int = 1  # Interpolation method for airfoil tables
        self.angle_of_attack_column: int = 1  # Column in airfoil tables for angle of attack
        self.lift_coefficient_column: int = 2  # Column in airfoil tables for lift coefficient
        self.drag_coefficient_column: int = 3  # Column in airfoil tables for drag coefficient
        self.pitching_moment_column: int = 4  # Column in airfoil tables for pitching moment
        self.cpmin_column: int = 0  # Column in airfoil tables for Cpmin (0 if not used)
        self.airfoil_files: list[str] = model.blade.profiles  # Airfoil file names
        self.num_airfoil_files: int = len(self.airfoil_files)  # Number of airfoil files used

        # Rotor/Blade Properties
        self.include_pitching_moment: bool = True  # Include aerodynamic pitching moment in calculations?
        self.blade_files: list[str] = [
            f"{model.name}_ADBlade.dat",
            f"{model.name}_ADBlade.dat",
            f"{model.name}_ADBlade.dat",
        ]  # Distributed aerodynamic properties for each blade

        # Hub Properties
        # self.hub_volume: float = 7.2  # Hub volume (m^3)
        # self.hub_center_of_buoyancy_x = 0.2222  # Hub center of buoyancy in x direction (m)
        self.hub_volume: float = 0
        self.hub_center_of_buoyancy_x = 0

        # Nacelle Properties
        # self.nacelle_volume: float = 38.6  # Nacelle volume (m^3)
        # self.nacelle_center_of_buoyancy_b = 0.43  # Position of nac. center of buoy from yaw bearing in nacelle coords
        self.nacelle_volume: float = 0
        self.nacelle_center_of_buoyancy_b = 0

        # Tail Fin Properties
        self.tail_fin_aero: bool = False  # Include tail fin aerodynamics?
        self.tail_fin_file: str = "unused"  # Tail fin aerodynamic properties file

        # Tower Influence and Aerodynamics
        self.tower_data = pd.DataFrame(model.tower.data, columns=["TwrElev", "TwrDiam", "TwrCd", "TwrTI", "TwrCb"])

        # Output Options
        self.blade_node_outputs: list = list(range(1, 10))
        self.tower_node_outputs: list = []
        # Outputs list for Rotor Aerodynamics
        self.outputs: list = ['RtAeroPwr', 'RtAeroCp', 'RtAeroCq', 'RtAeroCt', 'RtTSR',
                              'RtAeroFxh', 'RtAeroFyh', 'RtAeroFzh',
                              'RtAeroMxh', 'RtAeroMyh', 'RtAeroMzh']

    def validate(self):
        """Perform validation checks on the configuration."""
        if not (0 <= self.wake_model <= 2):
            raise ValueError("Wake model must be 0 (none), 1 (BEMT), or 2 (DBEMT).")
        if self.airfoil_aero_model not in {1, 2}:
            raise ValueError("Airfoil aerodynamics model must be 1 (steady) or 2 (unsteady).")

    def to_dict(self):
        """Convert the configuration to a dictionary."""
        return self.__dict__


class InflowWindConfig:
    def __init__(self, model: TurbineModel):
        self.model = model
        # General Options
        self.echo: bool = False  # Echo input data to <RootName>.ech
        self.wind_type: int = 1  # Wind file type (1=steady; 2=uniform; etc.)
        self.propagation_dir: float = 0.0  # Direction of wind propagation (degrees)
        self.upflow_angle: float = 0.0  # Upflow angle (degrees)
        self.use_cubic_interpolation: bool = False  # Use cubic interpolation for velocity in time?
        self.num_velocity_points: int = 1  # Number of points to output the wind velocity
        self.wind_vxi_list: list[float] = [0.0]  # X coordinates for velocity points (m)
        self.wind_vyi_list: list[float] = [0.0]  # Y coordinates for velocity points (m)
        self.wind_vzi_list: list[float] = [150.0]  # Z coordinates for velocity points (m)

        # Parameters for Steady Wind Conditions
        self.h_wind_speed: float = model.fluid.velocity  # Horizontal wind speed (m/s)
        self.ref_height: float = 150.0  # Reference height for horizontal wind speed (m)
        self.ref_length: float = 125.0  # Reference length for linear shear (m)
        self.power_law_exp: float = 0.12  # Power law exponentS

        # Parameters for Uniform Wind File
        self.uniform_filename: str = "none"  # Uniform wind time series filename
        self.uniform_ref_height: float = 150.0  # Reference height for uniform wind (m)
        self.ref_length: float = 240.0  # Reference length for linear shear

        # Parameters for Binary TurbSim Full-Field Files
        self.turbsim_filename: str = "none"  # Full field wind file name

        # Parameters for Binary Bladed-style Full-Field Files
        self.bladed_rootname: str = "none"  # Rootname of full-field wind file
        self.tower_file: bool = False  # Does the wind file have a tower file?

        # Parameters for HAWC-format Binary Files
        self.hawc_file_u: str = "none"  # U-component fluctuating wind file
        self.hawc_file_v: str = "none"  # V-component fluctuating wind file
        self.hawc_file_w: str = "none"  # W-component fluctuating wind file
        self.hawc_nx: int = 64  # Number of grid points in x direction
        self.hawc_ny: int = 32  # Number of grid points in y direction
        self.hawc_nz: int = 32  # Number of grid points in z direction
        self.hawc_dx: float = 16.0  # Distance between points in x direction (m)
        self.hawc_dy: float = 3.0  # Distance between points in y direction (m)
        self.hawc_dz: float = 3.0  # Distance between points in z direction (m)
        self.hawc_ref_height: float = 150.0  # Reference height for HAWC (m)

        # Scaling Parameters for Turbulence
        self.scale_method: int = 2  # Turbulence scaling method
        self.scale_factor_x: float = 1.0  # Scaling factor in x direction
        self.scale_factor_y: float = 1.0  # Scaling factor in y direction
        self.scale_factor_z: float = 1.0  # Scaling factor in z direction
        self.sigma_x: float = 1.2  # Std deviation for x direction turbulence
        self.sigma_y: float = 0.8  # Std deviation for y direction turbulence
        self.sigma_z: float = 0.2  # Std deviation for z direction turbulence

        # Mean Wind Profile Parameters (HAWC files)
        self.u_ref: float = model.fluid.velocity  # Mean wind speed at reference height (m/s)
        self.wind_profile_type: int = 2  # Wind profile type (0=constant; 1=logarithmic; 2=power law)
        self.power_law_exp_hawc: float = 0.2  # Power law exponent
        self.surface_roughness: float = 0.03  # Surface roughness length (m)
        self.x_offset: float = 0.0  # Initial offset in x direction

        # LIDAR Parameters
        self.lidar_sensor_type: int = 0  # Lidar configuration
        self.lidar_num_pulse_gates: int = 0  # Number of lidar measurement gates
        self.lidar_pulse_spacing: float = 30.0  # Distance between range gates (m)
        self.lidar_num_beams: int = 0  # Number of lidar measurement beams
        self.lidar_focal_distance_x: float = -200.0  # Focal distance in x direction (m)
        self.lidar_focal_distance_y: float = 0.0  # Focal distance in y direction (m)
        self.lidar_focal_distance_z: float = 0.0  # Focal distance in z direction (m)
        self.lidar_rotor_apex_offset: list[float] = [0.0, 0.0, 0.0]  # Rotor apex offset (x, y, z)
        self.lidar_ref_speed: float = 17.0  # Reference wind speed for lidar (m/s)
        self.measurement_interval: float = 0.25  # Time between measurements (s)
        self.lidar_radial_velocity: bool = False  # Return radial component (True) or x direction (False)
        self.consider_hub_motion: bool = True  # Flag to consider hub motion's impact on lidar

        # Output Options
        self.sum_print: bool = False  # Print summary data
        self.output_list: list[str] = [
            "Wind1VelX",  # X-direction wind velocity
            "Wind1VelY",  # Y-direction wind velocity
            "Wind1VelZ",  # Z-direction wind velocity
        ]

    def validate(self):
        """Perform validation checks on the configuration."""
        if not (0 <= self.wind_type <= 6):
            raise ValueError("Wind type must be between 0 and 6.")
        if self.scale_method not in {0, 1, 2}:
            raise ValueError("Scale method must be 0 (none), 1 (direct), or 2 (calculated).")

    def to_dict(self):
        """Convert the configuration to a dictionary."""
        return self.__dict__


if __name__ == "__main__":
    options = OpenFASTOptions(root_directory="output")
    options.write_all_configs()
