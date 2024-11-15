import yaml
from openturbinecode.models.turbine_model import TurbineModel
from openturbinecode.configs.pathing import PROJECT_ROOT


class turbineFoamAxialFlowOptions:
    def __init__(self, model: TurbineModel):
        self.model = model
        self.block_mesh = BlockMesh(model)
        self.topo_dict = topoDict(model)
        self.fv_options = fvOptions(model)
        self.hex_mesh_dict = HexMeshDict(model)

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
        dict = {"block_mesh": self.block_mesh.__dict__,
                "topo_dict": self.topo_dict.__dict__,
                "fv_options": self.fv_options.__dict__,
                "hex_mesh_dict": self.hex_mesh_dict.__dict__}
        return dict

    def read_from_yaml(self, filename):
        """Read the turbine model from a YAML file.

        Args:
            filename (str): The name of the YAML file.
        """
        load_location = PROJECT_ROOT / "solvers" / "aerodynamics" / "turbinesFoam" / filename
        with open(load_location, "r") as file:
            data = yaml.safe_load(file)

        self.block_mesh = BlockMesh(self.model)
        self.topo_dict = topoDict(self.model)
        self.fv_options = fvOptions(self.model)
        self.hex_mesh_dict = HexMeshDict(self.model)

        self.block_mesh.__dict__.update(data["block_mesh"])
        self.topo_dict.__dict__.update(data["topo_dict"])
        self.fv_options.__dict__.update(data["fv_options"])
        self.hex_mesh_dict.__dict__.update(data["hex_mesh_dict"])

        return self


class BlockMesh:
    def __init__(self, model: TurbineModel):
        diameter = 2 * model.blade.radius

        self.x_cells = 96
        self.y_cells = 32
        self.z_cells = 24

        self.x_upstream = 7 * diameter
        self.x_downstream = -4 * diameter
        self.z_up = 1.5 * diameter
        self.z_down = -1.5 * diameter
        self.y_left = -1.5 * diameter
        self.y_right = 1.5 * diameter


class topoDict:
    def __init__(self, model: TurbineModel):
        # Turbine rotor cell set
        self.rotor_radius = model.blade.radius
        self.rotor_influence = 1  # Rotor-disc region of influence in x-direction
        self.rotor_start = [-1 * self.rotor_influence, 0, 0]
        self.rotor_end = [self.rotor_influence, 0, 0]
        # Tower cell set
        self.tower_radius = model.tower.radius
        self.tower_base = [0, 0, -1 * model.tower.height]
        self.tower_top = [0, 0, 0]


class fvOptions:
    def __init__(self, model: TurbineModel):
        # Header for axialFlowTurbineAlSourceCoeffs
        self.origin = [0, 0, 0]
        self.axis = [-1, 0, 0]
        self.vertical_direction = [0, 0, 1]
        self.free_stream_velocity = [model.fluid.velocity, 0, 0]
        self.tip_speed_ratio = model.blade.tip_speed_ratio
        self.rotor_radius = model.blade.radius

        # Blade profile data - Converts profile indices to profile names
        blade_profiles = []
        for profile in model.blade.blade_profiles:
            blade_profiles.append(f"{model.blade.profiles[profile]}")
        self.blade_profile = blade_profiles

        # Blade information (default for 3 blades at the moment)
        self.num_blades = model.rotor.n_blades
        self.num_blade_elements = int(2 * (len(self.blade_profile) - 1))

        # Blade Profile Information
        self.profile_data = list(set(self.blade_profile))  # Gets only unique values

        # Tower information
        self.include_tower_drag = False
        self.num_tower_elements = 6
        self.tower_profile = "Cylinder"

        # Default tower properties
        self.include_in_total_drag = True

        # Write element data in the form of (0, radius, height), radius is constant
        element_data = []
        for idx in range(self.num_tower_elements+1):
            radius = model.tower.radius
            height = -1 * ((self.num_tower_elements - idx) / self.num_tower_elements) * model.tower.height
            element_data.append(f"({"0"} {height} {radius} )")
        self.tower_element_data = element_data

        # Hub information
        self.num_hub_elements = 1
        self.hub_profile = "Cylinder"
        # Axial distance, hub height, diameter
        self.hub_element_data = [f"(0 0 {model.hub.radius} {model.hub.radius})",
                                 f"(0 {-1 * model.hub.radius} {model.hub.radius})"]


class HexMeshDict:
    def __init__(self, model: TurbineModel):
        # Which steps to run
        self.casellated_mesh = True
        self.snap = True
        self.addLayers = False

        # Geometry definitions for meshing
        self.turbine_type = "searchableCylinder"
        self.turbine_point1 = [-1, 0, 0]
        self.turbine_point2 = [1, 0, 0]
        self.turbine_radius = model.blade.radius

        self.tower_type = "searchableCylinder"
        self.tower_point1 = [0, 0, -115.6]  # Tower base to top
        self.tower_point2 = [0, 0, 0]  # Half the tower diameter

        self.turb_zone = "searchableBox"
        self.minimum = [-120, -120, -115.6]  # Domain bounds to encomposs blade and tower
        self.maximum = [120, 120, 115.6]  # Domain bounds to encomposs blade and tower

        # Castellated Mesh Controls
        self.max_local_cells = 500000
        self.max_global_cells = 10000000
        self.min_refinement_cells = 0
        self.max_load_unbalance = 0.10
        self.n_cells_between_levels = 1  # Number of buffer layers between different levels

        # Explicit feature edge refinement
        # None for now

        # Surface based refinement
        # None for now

        # Region-wise refinement
        # None for now

        # Mesh selection
        # None for now

        # Snap controls
        self.nSmoothPatch = 5  # Number of patch smoothing iterations
        self.tolerance = 2.0  # Maximum distance from surface to snap
        self.nSolveIter = 40  # Number of mesh displacement relaxation iterations
        self.nRelaxIter = 10  # Maximum number of snapping relaxation iterations

        # Feature snapping
        self.nFeatureSnapIter = 10
        self.implicit_feature_snap = True
        self.explicit_feature_snap = True
        self.multi_region_feature_snap = False

        # Layer addition controls
        self.relativeSize = True
        self.expansion_ratio = 1.0
        self.final_layer_thickness = 0.3
        self.min_thickness = 0.25
        self.n_grow = 0

        # Advanced settings
        self.feature_angle = 60
        self.n_relaxation_iterations = 5
        self.n_smooth_surface_normals = 1
        self.n_smooth_thickness = 10
        self.max_face_thickness_ratio = 0.5
        self.max_thickness_to_medial_ratio = 0.3
        self.min_median_axis_angle = 90
        self.n_buffer_cells_no_extrude = 0
        self.n_layer_iteration = 50
        self.n_relaxed_iteration = 20

        # Mesh quality controls
        self.maxNoneOrtho = 70
        self.max_boundary_skewness = 20
        self.max_internal_skewness = 5
        self.max_concave = 80
        self.minVol = 1e-13
        self.min_tet_quality = 1e-30
        self.min_area = -1
        self.min_twist = 0.05
        self.minDeterminant = 0.001
        self.min_face_weight = 0.05
        self.min_volume_ratio = 0.01
        self.min_triangle_twist = -1
        self.n_smooth_scale = 4
        self.error_reduction = 0.75
        self.max_non_orthogonal = 75


if __name__ == "__main__":
    default_path = PROJECT_ROOT / "models" / "defaults"
    model = TurbineModel()
    model.read_from_yaml(default_path / "turbine_model.yaml")

    options = turbineFoamAxialFlowOptions(model)
    options.write_to_yaml("turbineFoamAxialFlowOptions.yaml")

    options.read_from_yaml("turbineFoamAxialFlowOptions.yaml")
