from itertools import product
from pathlib import Path
import numpy as np
# Turbine model class
from openturbinecode.models.turbine_model import TurbineModel
# Openfast specific modules
from openturbinecode.solvers.aerostructural.openfast import utils as openfast_util
from openturbinecode.solvers.aerodynamics.aerodyn import utils as aerodyn_util
from openturbinecode.configs.pathing import OPENFAST_RUN, AERODYN_RUN, PROJECT_ROOT
# Openfast post-processing
from openturbinecode.postprocessing import pp_openfast

BOOL_RUN_CASE = True
BOOL_POST_PROCESS = False


def update_turbine_model(turbine_model, param_dict):
    """
    Update the TurbineModel instance with parameter values.

    Args:
        turbine_model (TurbineModel): Instance of the TurbineModel class.
        param_dict (dict): Dictionary of parameters to update.
            Keys should be in the format '<component>.<attribute>', e.g., 'fluid.velocity'.
    """
    for param, value in param_dict.items():
        component, attribute = param.split(".", 1)
        if hasattr(turbine_model, component):
            sub_component = getattr(turbine_model, component)
            if hasattr(sub_component, attribute):
                setattr(sub_component, attribute, value)
            else:
                raise AttributeError(f"'{component}' does not have an attribute '{attribute}'")
        else:
            raise AttributeError(f"TurbineModel does not have a component '{component}'")


def parametric_analysis(turbine_model, param_ranges, output_base_dir, solver):
    """
    Perform a two-level parametric analysis using OpenFAST.

    Args:
        turbine_model (TurbineModel): An instance of the TurbineModel class.
        param_ranges (dict): Dictionary of parameters and their ranges, e.g.,
            {
                "fluid.velocity": [8.0, 10.0, 12.0],
                "rotor.n_blades": [2, 3]
            }
        output_base_dir (str): Base directory to store simulation cases and results.
    """
    # Create the output base directory
    Path(output_base_dir).mkdir(parents=True, exist_ok=True)

    # Extract parameter names and ranges
    param_names = list(param_ranges.keys())
    param_values = list(param_ranges.values())

    # Iterate through all combinations of parameters
    for param_combination in product(*param_values):
        # Update turbine model with the current parameter values
        param_dict = dict(zip(param_names, param_combination))
        update_turbine_model(turbine_model, param_dict)

        # Create a unique case directory name based on the parameter combination
        case_name = "_".join([f"{param.split('.')[-1]}_{value}" for param, value in param_dict.items()])
        case_dir = Path(output_base_dir) / case_name

        # Run the OpenFAST case
        match solver:
            case "openfast":
                print(f"Running case: {case_name} with parameters: {param_dict}")
                openfast_util.run_openfast_case(str(case_dir), model=turbine_model)
            case "aerodyn":
                print(f"Running case: {case_name} with parameters: {param_dict}")
                aerodyn_util.run_aerodyn_case(case_dir, model=turbine_model)


if __name__ == "__main__":
    # Output base directory
    solver = "aerodyn"
    if solver == "openfast":
        output_dir = OPENFAST_RUN / "parametric_analysis"
    elif solver == "aerodyn":

        output_dir = AERODYN_RUN / "parametric_analysis"

    analysis_num = 1
    match analysis_num:
        case 1:
            # Define parameter ranges for analysis
            model_name = "DTU_10MW"
            param_ranges = {
                "fluid.velocity": [8.0, 11.0, 14.0],  # Horizontal windspeed (m/s)
                "blade.tip_speed_ratio": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # Tip speed ratio
            }
        case 2:
            # Define parameter ranges for analysis
            model_name = "DTU_10MW"
            param_ranges = {
                "blade.pitch_angle": [-10.0, -5.0, 0.0, 5.0, 10.0],  # Blade angle (deg)
                "blade.tip_speed_ratio": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # Tip speed ratio
            }
        case 202:
            # FOCAL-1 Validation LC 1.1
            model_name = "IEA_15MW"
            param_ranges = {
                "fluid.velocity": [12.83],  # Horizontal windspeed (m/s)
                "blade.pitch_angle": [0.0],  # Blade pitch angle (deg)
                "blade.rotor_speed": np.around(np.linspace(3, 10, 15), decimals=1).tolist()  # Tip speed ratio
            }
        case 206:
            # FOCAL-1 Validation LC 1.2
            model_name = "IEA_15MW"
            param_ranges = {
                "fluid.velocity": [12.83],  # Horizontal windspeed (m/s)
                "blade.pitch_angle": [10.0],  # Blade pitch angle (deg)
                "blade.rotor_speed": np.around(np.linspace(3, 10, 15), decimals=1).tolist()  # Tip speed ratio
            }
        case 402:
            # FOCAL-1 Validation LC 1.2
            model_name = "IEA_15MW"
            param_ranges = {
                "fluid.velocity": [18.39],  # Horizontal windspeed (m/s)
                "blade.pitch_angle": [9.0],  # Blade pitch angle (deg)
                "blade.rotor_speed": np.around(np.linspace(3, 10, 15), decimals=1).tolist()  # Tip speed ratio
            }
        case 406:
            # FOCAL-1 Validation LC 1.2
            model_name = "IEA_15MW"
            param_ranges = {
                "fluid.velocity": [18.39],  # Horizontal windspeed (m/s)
                "blade.pitch_angle": [15.0],  # Blade pitch angle (deg)
                "blade.rotor_speed": np.around(np.linspace(3, 10, 15), decimals=1).tolist()  # Tip speed ratio
            }
        case _:
            raise ValueError(f"Analysis number {analysis_num} is not supported.")
            exit()

    # Build a string using the analysis_number with leading zeros and followed by based on param_range keys
    param_str = f"{str(analysis_num).zfill(3)}_" + "_".join([f"{param}_{len(values)}" for param, values in param_ranges.items()])  # noqa: E501
    output_dir_run = output_dir / model_name / f"{param_str}"

    if BOOL_RUN_CASE:
        # Example turbine model
        model = TurbineModel(name=model_name)
        model.read_from_yaml(PROJECT_ROOT / "models" / "defaults" / f"{model_name}.yaml")

        # Perform the analysis
        parametric_analysis(turbine_model=model,
                            param_ranges=param_ranges,
                            output_base_dir=output_dir_run,
                            solver="aerodyn")

    if BOOL_POST_PROCESS:
        # Post-process the results
        parametric_data = pp_openfast.get_parametric_analysis_data(output_dir_run)

        # Possible channels: "RtAeroCp", "RtAeroCt", "RtAeroCq", "RtAeroFxh", "RtAeroFyh", "RtAeroFzh"

        response_channel_plots = ['RtAeroPwr', 'RtAeroCp', 'RtAeroCq', 'RtAeroCt', 'Thrust', 'Torque',
                                  'RtAeroFxh', 'RtAeroFyh', 'RtAeroFzh',
                                  'RtAeroMxh', 'RtAeroMyh', 'RtAeroMzh',
                                  'B1AeroMx', 'B1AeroMy', 'B1AeroMz']
        # Plot parametric response
        for response_channel in response_channel_plots:
            pp_openfast.plot_parametric_response(parametric_data,
                                                 response_channel=response_channel,
                                                 dependent="rotor_speed",
                                                 output_dir=output_dir_run / "plots")
