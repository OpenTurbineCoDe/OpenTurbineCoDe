# flake8: noqa: E501
from pathlib import Path
from openturbinecode.configs.pathing import PROJECT_ROOT
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.solvers.aerostructural.openfast.options import (
    FastConfig, ElastoDynConfig, AeroDynConfig, InflowWindConfig
)
from . import fast, elastodyn, aerodyn, inflow

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
    fast.generate_fast_config(output_dir, fast_config)
    elastodyn.generate_elastodyn_config(output_dir, elastodyn_config)
    aerodyn.generate_aerodyn_config(output_dir, aerodyn_config)
    inflow.generate_inflow_wind_config(output_dir, inflow_wind_config)

    print(f"Configuration files generated in: {output_dir}")