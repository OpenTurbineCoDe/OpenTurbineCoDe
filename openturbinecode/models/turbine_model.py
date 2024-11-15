"""This module contains the TurbineModel base class. It contains the default
turbine model parameters and can be superclassed to create custom turbine models.

It also contains methods for reading and writing the turbine model to a YAML file.
This way YAML files are generated based on the default / superclassed turbine model
and can be used as input for the OpenTurbineCode solvers.
"""

import yaml
from openturbinecode.configs.pathing import PROJECT_ROOT


class TurbineModel:
    def __init__(self):

        # Turbine dimensions
        self.fluid = Fluid()
        self.environment = Environment()
        self.blade = Blade()
        self.rotor = Rotor()
        self.tower = Tower()
        self.hub = Hub()

    def write_to_yaml(self, filename):
        """Write the turbine model to a YAML file.

        Args:
            filename (str): The name of the YAML file.
        """
        with open(filename, "w") as file:
            yaml.dump(self.create_dict_for_yaml(), file)

    def create_dict_for_yaml(self):
        """Return the turbine model as a dictionary.

        Returns:
            dict: A dictionary containing the turbine model parameters.
        """
        dict = {"fluid": self.fluid.__dict__,
                "environment": self.environment.__dict__,
                "blade": self.blade.__dict__,
                "rotor": self.rotor.__dict__,
                "tower": self.tower.__dict__,
                "hub": self.hub.__dict__}
        return dict

    def read_from_yaml(self, filename):
        """Read the turbine model from a YAML file.

        Args:
            filename (str): The name of the YAML file.
        """
        with open(filename, "r") as file:
            data = yaml.safe_load(file)

        self.fluid = Fluid()
        self.environment = Environment()
        self.blade = Blade()
        self.rotor = Rotor()
        self.tower = Tower()
        self.hub = Hub()

        self.fluid.__dict__.update(data["fluid"])
        self.environment.__dict__.update(data["environment"])
        self.blade.__dict__.update(data["blade"])
        self.rotor.__dict__.update(data["rotor"])
        self.tower.__dict__.update(data["tower"])
        self.hub.__dict__.update(data["hub"])

        return self


# Default environmental properties
class Environment:
    def __init__(self):
        # Environmental properties
        self.temperature = 288.15  # (K) 15 degrees Celsius
        self.pressure = 101325  # (Pa) Standard atmospheric pressure
        self.gravity = 9.81  # (m/s^2) Standard gravity

    def read_from_yaml(self, filename):
        with open(filename, "r") as file:
            data = yaml.safe_load(file)

        if "environment" in data:
            self.__dict__.update(data["environment"])

        return self


# Default fluid properties
class Fluid:
    def __init__(self):
        # Free stream properties
        self.velocity = 11.4  # (m/s)
        self.turbulence_intensity = 0.1  # (%)
        self.turbulence_length_scale = 0.1  # (-)

        # Air properties
        self.kinematic_viscosity = 1.5e-5  # (m^2/s)
        self.density = 1.225  # (kg/m^3)
        self.dynamic_viscosity = 1.789e-5  # (kg/m/s)
        self.thermal_conductivity = 0.0257  # (W/m/K)
        self.specific_heat = 1006  # (J/kg/K)
        self.thermal_expansion_coefficient = 0.00343  # (1/K)
        self.prandtl_number = 0.71  # (-)
        self.sutherland_constant = 110.4  # (K)
        self.sutherland_temperature = 110.4  # (K)

    def read_from_yaml(self, filename):
        with open(filename, "r") as file:
            data = yaml.safe_load(file)

        field = "fluid"

        if field in data:
            self.__dict__.update(data[field])

        return self


# Blade geometry
class Blade:
    def __init__(self):
        # Default blade properties
        self.radius = 86.366  # (m)
        self.tip_speed_ratio = 7  # (-)
        self.profiles = ["Cylinder",
                         "FFA_W3_600",
                         "FFA_W3_480",
                         "FFA_W3_360",
                         "FFA_W3_301",
                         "FFA_W3_241"]
        self.blade_profiles = [0, 0,
                               1, 1, 1,
                               2, 2,
                               3, 3,
                               4, 4, 4,
                               5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                               5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                               5, 5, 5, 5, 5, 5, 5, 5]


class Rotor:
    def __init__(self):
        # Default rotor properties
        self.n_blades = 3

    def read_from_yaml(self, filename):
        with open(filename, "r") as file:
            data = yaml.safe_load(file)

        field = "rotor"

        if field in data:
            self.__dict__.update(data[field])

        return self


# Tower geometry
class Tower:
    def __init__(self):
        self.height = 115.6  # (m)
        self.radius = 4.15  # (m)

    def read_from_yaml(self, filename):
        with open(filename, "r") as file:
            data = yaml.safe_load(file)

        field = "tower"

        if field in data:
            self.__dict__.update(data[field])

        return self


# Hub geometry
class Hub:
    def __init__(self):
        self.radius = 4.45  # (m)

    def read_from_yaml(self, filename):
        with open(filename, "r") as file:
            data = yaml.safe_load(file)

        field = "hub"

        if field in data:
            self.__dict__.update(data[field])

        return self


if __name__ == "__main__":
    default_path = PROJECT_ROOT / "models" / "defaults"

    # Create a new turbine model
    model = TurbineModel()

    # Write the default yaml
    model.write_to_yaml(default_path / "turbine_model.yaml")

    # Read the default yaml
    model.read_from_yaml(default_path / "turbine_model.yaml")
