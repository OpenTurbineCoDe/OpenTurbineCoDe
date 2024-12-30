"""This script contains the options for the AeroDyn standalone solver. It parses
the turbine model and creates the necessary configuration files for the solver.

The AeroDyn standalone solver is a standalone version of the AeroDyn module from
the FAST software suite. It is used to simulate the aerodynamic behavior of a
wind turbine.

IMPORTANT:
-----------
The solver requires the following general configuration files:
- AeroDynDriver.inp: Contains the simulation input parameters and turbine geometry / motion.
- AeroDyn.dat: Contains the Aerodyn specific model options as well as BEMT options.
- InflowWind.dat (optional, flagged): Contains the inflow wind conditions.
- ./AeroData/Section.dat: Contains the airfoil data for the blades.
"""

import yaml
import pandas as pd
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.configs.pathing import PROJECT_ROOT
from openturbinecode.utils.utilities import calculate_tsr_or_missing


class AeroDynStandaloneOptions:
    def __init__(self, model: TurbineModel):
        self.model = model
        self.aerodyn_input = AeroDynInputConfig(model)
        self.aerodyn = AeroDynConfig(model)
        self.inflow_wind = InflowWindConfig(model)

    def write_to_yaml(self, filename):
        """Write the AeroDyn model to a YAML file.

        Args:
            filename (str): The name of the YAML file.
        """
        save_location = PROJECT_ROOT / "solvers" / "aerodynamics" / "aerodyn" / filename

        with open(save_location, "w") as file:
            yaml.dump(self.create_dict_for_yaml(), file)

    def create_dict_for_yaml(self):
        """Return the AeroDyn model as a dictionary.

        Returns:
            dict: A dictionary containing the turbine model parameters.
        """
        dict = {"aerodyn_standalone": self.aerodyn_input.__dict__,
                "aerodyn": self.aerodyn.__dict__,
                "inflow_wind": self.inflow_wind.__dict__}
        return dict

    def read_from_yaml(self, filename):
        """Read the AeroDyn model from a YAML file.

        Args:
            filename (str): The name of the YAML file.
        """
        load_location = PROJECT_ROOT / "solvers" / "aerodynamics" / "aerodyn" / filename
        with open(load_location, "r") as file:
            data = yaml.safe_load(file)

        self.aerodyn_input = AeroDynInputConfig(self.model)
        self.aerodyn = AeroDynConfig(self.model)
        self.inflow_wind = InflowWindConfig(self.model)

        self.aerodyn_input.__dict__.update(data["aerodyn_standalone"])
        self.aerodyn.__dict__.update(data["aerodyn"])
        self.inflow_wind.__dict__.update(data["inflow_wind"])

        return self


class AeroDynInputConfig:
    def __init__(self, model: TurbineModel):
        self.model = model

        # Simulation Control
        self.mhk_system: int = 0  # Flag for Marine HydroKinetic system
        self.t_max = 10.0  # Maximum simulation time [s]
        self.dt = 0.025  # Time step [s]
        self.analysis_type = 1  # (1: multiple turbines, 2: one turbine, 3: one, combined case)

        # Environmental Conditions
        self.air_density: float = model.fluid.density  # Working fluid density (kg/m^3)
        self.kinematic_viscosity: float = model.fluid.kinematic_viscosity  # Kinematic air viscosity (m^2/s)
        self.speed_of_sound: float = model.environment.speed_of_sound  # Speed of sound (m/s)
        self.atmospheric_pressure: float = model.environment.atmospheric_pressure  # Atmospheric pressure (Pa)
        self.vapor_pressure: float = model.environment.vapor_pressure  # Vapor pressure of fluid (Pa)
        self.water_depth = 0.0  # Water depth (m)

        # Inflow Data
        self.comp_inflow = 0  # Used to select inflow data (0=steady, 1=InflowWind)
        self.inflow_wind_file = f"{"unused" if self.comp_inflow == 0 else f"{model.name}_IW.dat"}"  # InflowWind file
        self.horizontal_wind_speed = model.fluid.velocity  # Horizontal wind speed [m/s]
        self.wind_ref_height = model.fluid.reference_height  # Reference height for horizontal wind speed [m]
        self.power_law_exp = model.fluid.power_law_exponent  # Power law exponent

        # Turbine Configuration
        self.num_turbines = 1  # May be used in multiple turbine analysis

        # Turbine Geometry
        self.basic_hawt_format = True  # Flag for basic Horizontal-Axis WT format
        self.num_blades = model.rotor.n_blades  # Number of blades
        self.hub_radius = model.hub.radius  # Distance from rotor apex to blade root [m]
        self.hub_height = model.tower.height + model.hub.radius  # Distance from base to hub mass [m]
        self.hub_overhang = model.hub.overhang  # Distance from hub mass to rotor plane [m]

        # Turbine Motion
        self.motion_type = model.nacelle.motion  # Type of motion (0=rigid, 1=sinusoidal, 2=arbitrary)
        self.nacelle_yaw = model.nacelle.yaw  # Nacelle yaw angle [deg]
        if model.blade.rotor_speed == 0:
            self.rotor_speed: float = calculate_tsr_or_missing(tsr=model.blade.tip_speed_ratio,
                                                               freestream_velocity=model.fluid.velocity,
                                                               radius=model.blade.radius)
        else:
            self.rotor_speed: float = model.blade.rotor_speed

        self.shaft_tilt: float = model.rotor.tilt_angle  # Shaft tilt angle [deg]
        self.blade_pitch = model.blade.pitch_angle  # Blade pitch angle [deg]
        self.blade_precone = -1 * model.rotor.blade_precone_angle  # Blade precone angle [deg]

        # Time-dependent analysis
        self.timeseries_file = "ad_TimeseriesInput.csv"
        # Input files
        self.elastodyn_file = f"{model.name}_ED.dat"  # Elastodyn input file
        self.beamdyn_blade_file = [f"{model.name}_BD.dat",
                                   f"{model.name}_BD.dat",
                                   f"{model.name}_BD.dat"]

        self.aerodyn_file = f"{model.name}_AD15.dat"

        # Output Settings
        # skip for now

        # Linearization
        # skip for now

        # Visualization
        # skip for now


class AeroDynConfig:
    def __init__(self, model: TurbineModel):
        self.model = model

        # General Solver Options
        self.echo: bool = False  # Echo the input to "<rootname>.AD.ech"
        self.dt_aero: str = "default"  # Time interval for aerodynamic calculations
        self.wake_model: int = 1  # Type of wake/induction model {0=none, 1=BEMT, 2=DBEMT}
        self.airfoil_aero_model: int = 1  # Type of blade airfoil aerodynamics model {1=steady, 2=unsteady}
        self.tower_potential_flow: int = 0  # Twr influence based on potential flow {0=none,1=baseline,2=correction}
        self.tower_shadow: int = 0  # Tower influence based on downstream shadow {0=none, 1=included}
        self.tower_aero: bool = False  # Calculate tower aerodynamic loads?
        self.frozen_wake: bool = False  # Assume frozen wake during linearization?
        self.cavitation_check: bool = False  # Perform cavitation check?
        self.buoyancy_effects: bool = False  # Include buoyancy effects?
        self.compute_acoustics: bool = False  # Compute AeroAcoustics calculations?
        self.acoustics_input_file: str = "unused"  # Aeroacoustics input file

        # Environmental Conditions
        self.air_density: float = model.fluid.density  # Air density (kg/m^3)
        self.kinematic_viscosity: float = model.fluid.kinematic_viscosity  # Kinematic air viscosity (m^2/s)
        self.speed_of_sound: float = model.environment.speed_of_sound  # Speed of sound (m/s)
        self.atmospheric_pressure: float = model.environment.atmospheric_pressure  # Atmospheric pressure (Pa)
        self.vapor_pressure: float = model.environment.vapor_pressure  # Vapor pressure of fluid (Pa)

        # Blade-Element/Momentum Theory Options
        self.skewed_wake_model: int = 1  # Type of skewed-wake correction model
        self.skew_factor: str = "default"  # Skew model factor
        self.tip_loss: bool = False  # Use Prandtl tip-loss model?
        self.hub_loss: bool = False  # Use Prandtl hub-loss model?
        self.tangential_induction: bool = False  # Include tangential induction?
        self.axial_induction_drag: bool = False  # Include drag term in axial-induction calculation?
        self.tangential_induction_drag: bool = False  # Include drag term in tangential-induction calculation?
        self.induction_tolerance: str = "Default"  # Convergence tolerance for BEMT residual equation
        self.max_iterations: int = 200  # Maximum number of iterations for BEMT solve

        # Dynamic Blade-Element/Momentum Theory Options
        self.dynamic_bemt_model: int = 2  # Type of dynamic BEMT model
        self.tau1_constant: float = 4.0  # Time constant for DBEMT

        # OLAF -- Convecting Lagrangian Filaments Options
        self.olaf_input_file: str = "unused"  # Input file for OLAF

        # Beddoes-Leishman Unsteady Airfoil Aerodynamics Options
        self.unsteady_aero_model: int = 1  # Unsteady Aero Model Switch
        self.f_lookup: bool = True  # Flag for f' lookup or best-fit exponential equations

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
        self.tower_data = pd.DataFrame([
            [0.000E+00, 8.300E+00, 1.0000E+00, 0.0, 1.0],
            [1.150E+01, 8.022E+00, 1.0000E+00, 0.0, 1.0],
            [2.300E+01, 7.743E+00, 1.0000E+00, 0.0, 1.0],
            [3.450E+01, 7.465E+00, 1.0000E+00, 0.0, 1.0],
            [4.600E+01, 7.186E+00, 1.0000E+00, 0.0, 1.0],
            [5.750E+01, 6.908E+00, 1.0000E+00, 0.0, 1.0],
            [6.900E+01, 6.629E+00, 1.0000E+00, 0.0, 1.0],
            [8.050E+01, 6.351E+00, 1.0000E+00, 0.0, 1.0],
            [9.200E+01, 6.072E+00, 1.0000E+00, 0.0, 1.0],
            [1.035E+02, 5.794E+00, 1.0000E+00, 0.0, 1.0],
            [1.156E+02, 5.500E+00, 1.0000E+00, 0.0, 1.0],
        ], columns=["TwrElev", "TwrDiam", "TwrCd", "TwrTI", "TwrCb"])

        # Output Options
        self.blade_node_outputs: list = range(2, len(model.blade.profiles), 2)
        self.tower_node_outputs: list = []
        self.outputs: list = ['RtAeroPwr', 'RtAeroCp', 'RtAeroCq', 'RtAeroCt',
                              'RtAeroFxh', 'RtAeroFyh', 'RtAeroFzh',
                              'RtAeroMxh', 'RtAeroMyh', 'RtAeroMzh',
                              'B1AeroMx', 'B1AeroMy', 'B1AeroMz']

        # Node Outputs
        self.node_outputs: list = ["VUndx", "VUndy", "VUndz", "Ft", "Fn", "Fy", "Fx", "Ct", "Cn", "Cy", "Cx", "Alpha"]

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
        self.wind_vzi_list: list[float] = [12.0]  # Z coordinates for velocity points (m)

        # Parameters for Steady Wind Conditions
        self.h_wind_speed: float = model.fluid.velocity  # Horizontal wind speed (m/s)
        self.ref_height: float = 120.0  # Reference height for horizontal wind speed (m)
        self.power_law_exp: float = 0.1429  # Power law exponent

        # Parameters for Uniform Wind File
        self.uniform_filename: str = "experimentwind.hhwind"  # Uniform wind time series filename
        self.uniform_ref_height: float = 119.0  # Reference height for uniform wind (m)
        self.ref_length: float = 100.0  # Reference length for linear shear

        # Parameters for Binary TurbSim Full-Field Files
        self.turbsim_filename: str = "Wind/90m_12mps_twr.bts"  # Full field wind file name

        # Parameters for Binary Bladed-style Full-Field Files
        self.bladed_rootname: str = "Wind/90m_12mps_twr"  # Rootname of full-field wind file
        self.tower_file: bool = False  # Does the wind file have a tower file?

        # Parameters for HAWC-format Binary Files
        self.hawc_file_u: str = "wasp\\Output\\basic_5u.bin"  # U-component fluctuating wind file
        self.hawc_file_v: str = "wasp\\Output\\basic_5v.bin"  # V-component fluctuating wind file
        self.hawc_file_w: str = "wasp\\Output\\basic_5w.bin"  # W-component fluctuating wind file
        self.hawc_nx: int = 64  # Number of grid points in x direction
        self.hawc_ny: int = 32  # Number of grid points in y direction
        self.hawc_nz: int = 32  # Number of grid points in z direction
        self.hawc_dx: float = 16.0  # Distance between points in x direction (m)
        self.hawc_dy: float = 3.0  # Distance between points in y direction (m)
        self.hawc_dz: float = 3.0  # Distance between points in z direction (m)
        self.hawc_ref_height: float = 90.0  # Reference height for HAWC (m)

        # Scaling Parameters for Turbulence
        self.scale_method: int = 2  # Turbulence scaling method
        self.scale_factor_x: float = 1.0  # Scaling factor in x direction
        self.scale_factor_y: float = 1.0  # Scaling factor in y direction
        self.scale_factor_z: float = 1.0  # Scaling factor in z direction
        self.sigma_x: float = 1.2  # Std deviation for x direction turbulence
        self.sigma_y: float = 0.8  # Std deviation for y direction turbulence
        self.sigma_z: float = 0.2  # Std deviation for z direction turbulence

        # Mean Wind Profile Parameters (HAWC files)
        self.u_ref: float = 11.4  # Mean wind speed at reference height (m/s)
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
    options = AeroDynStandaloneOptions(root_directory="output")
