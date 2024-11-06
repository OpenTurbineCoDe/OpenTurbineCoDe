"""This module contains functions to generate axialFlowTurbine files for turbinesFoam.
"""
from pathlib import Path
from openturbinecode.configs.pathing import WSL_ROOT, FOAM_RUN


class TurbineModel:
    def __init__(self):

        # Turbine dimensions
        self.fluid = Fluid()
        self.environment = Environment()
        self.blade = Blade()
        self.rotor = Rotor()
        self.tower = Tower()
        self.hub = Hub()


class Environment:
    def __init__(self):
        # Environmental properties
        self.temperature = 288.15
        self.pressure = 101325
        self.gravity = 9.81


# Default fluid properties
class Fluid:
    def __init__(self):
        # Free stream properties
        self.velocity = 11.4
        self.turbulence_intensity = 0.1
        self.turbulence_length_scale = 0.1

        # Air properties
        self.kinematic_viscosity = 1.5e-5
        self.density = 1.225
        self.dynamic_viscosity = 1.789e-5
        self.thermal_conductivity = 0.0257
        self.specific_heat = 1006
        self.thermal_expansion_coefficient = 0.00343
        self.prandtl_number = 0.71
        self.sutherland_constant = 110.4
        self.sutherland_temperature = 110.4


# Blade geometry
class Blade:
    def __init__(self):
        # Default blade properties
        self.radius = 86.366
        self.tip_speed_ratio = 7
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


# Tower geometry
class Tower:
    def __init__(self):
        self.height = 115.6
        self.radius = 4.15


# Hub geometry
class Hub:
    def __init__(self):
        self.radius = 4.45


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
        self.rotor_start = (-1 * self.rotor_influence, 0, 0)
        self.rotor_end = (self.rotor_influence, 0, 0)
        # Tower cell set
        self.tower_radius = model.tower.radius
        self.tower_base = (0, 0, -1 * model.tower.height)
        self.tower_top = (0, 0, 0)


class fvOptions:
    def __init__(self, model: TurbineModel):
        # Header for axialFlowTurbineAlSourceCoeffs
        self.origin = (0, 0, 0)
        self.axis = (-1, 0, 0)
        self.vertical_direction = (0, 0, 1)
        self.free_stream_velocity = (model.fluid.velocity, 0, 0)
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


model = TurbineModel()
block_mesh = BlockMesh(model)
topo = topoDict(model)
fv = fvOptions(model)


def generate_blockMeshDict(location: Path):
    """Generate the blockMeshDict file for the axialFlowTurbine case.

    Args:
        turbine (AxialTurbine): AxialTurbine object.

    Returns:
        str: blockMeshDict file contents.
    """

    # Define the blockMeshDict file contents
    contents = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  3.0.x                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

// Control volume vertices
vertices
(
    ( {block_mesh.x_upstream}  {block_mesh.y_left}  {block_mesh.z_down} )  // 0
    ( {block_mesh.x_upstream}  {block_mesh.y_right}  {block_mesh.z_down} )  // 1
    ( {block_mesh.x_downstream}  {block_mesh.y_right}  {block_mesh.z_down} )  // 2
    ( {block_mesh.x_downstream}  {block_mesh.y_left}  {block_mesh.z_down} )  // 3
    ( {block_mesh.x_upstream}  {block_mesh.y_left}  {block_mesh.z_up} )  // 4
    ( {block_mesh.x_upstream}  {block_mesh.y_right}  {block_mesh.z_up} )  // 5
    ( {block_mesh.x_downstream}  {block_mesh.y_right}  {block_mesh.z_up} )  // 6
    ( {block_mesh.x_downstream}  {block_mesh.y_left}  {block_mesh.z_up} )  // 7
);

// Control volume blocks
blocks
(
    hex (0 1 2 3 4 5 6 7)
    ( {block_mesh.y_cells} {block_mesh.x_cells} {block_mesh.z_cells} )
    simpleGrading (1 1 1)
);

// Control volume surface patches
boundary
(
    inlet
    {{
        type patch;
        faces
        (
            (2 6 7 3)
        );
    }}

    outlet
    {{
        type patch;
        faces
        (
            (0 4 5 1)
        );
    }}

    walls
    {{
        type wall;
        faces
        (
            (1 5 6 2)
            (4 0 3 7)
        );
    }}

    top
    {{
        type wall;
        faces
        (
            (4 7 6 5)
        );
    }}

    bottom
    {{
        type wall;
        faces
        (
            (0 1 2 3)
        );
    }}
);

edges
(
);

mergePatchPairs
(
);

// ************************************************************************* //
"""

    # Write the blockMeshDict file
    with open(location / "system" / "blockMeshDict", "w") as file:
        file.write(contents)

    return None


def generate_topoSetDict(location: Path):
    """Generate the topoSetDict file for the axialFlowTurbine case.

    Args:
        turbine (AxialTurbine): AxialTurbine object.

    Returns:
        str: topoSetDict file contents.
    """
    # Define the topoSetDict file contents
    contents = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  3.0.x                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

actions
(
    // Turbine rotor cell set
    {{
        name 	turbine;
        type	cellSet;
        action	new;
        source	cylinderToCell;
        sourceInfo
        {{
            type    cylinder;
            // Starting at the blade root along Z-axis and ending at the rotor apex
            p1      ({topo.rotor_start[0]} {topo.rotor_start[1]} {-1 * topo.rotor_start[2]});
            p2      ({topo.rotor_end[0]} {topo.rotor_end[1]} {topo.rotor_end[2]});
            radius  {topo.rotor_radius};
        }}
    }}

    // Tower cell set
    {{
        name 	turbine;
        type	cellSet;
        action	add;
        source	cylinderToCell;
        sourceInfo
        {{
            // Starting and ending tower points
            type    cylinder;
            p1      ({topo.tower_base[0]} {topo.tower_base[1]} {topo.tower_base[2]});
            p2      ({topo.tower_top[0]} {topo.tower_top[1]} {topo.tower_top[2]});
            radius  {topo.tower_radius};          // Approximate tower radius
        }}
    }}

    // Convert cellSet to cellZone for fvOptions
    {{
        name    turbine;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        sourceInfo
        {{
            set turbine;
        }}
    }}
);


// ************************************************************************* //
"""
    with open(location / "system" / "topoSetDict", "w") as file:
        file.write(contents)

    return None


def generate_fvOptions(location: Path, fv_options: fvOptions):
    """Generate the fvOptions file for the axialFlowTurbine case using the fvOptions object."""

    def write_header():
        return """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  6                                     |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvOptions;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""

    def write_turbine_base():
        return f"""turbine
{{
    type            axialFlowTurbineALSource;
    active          on;

    axialFlowTurbineALSourceCoeffs
    {{
        fieldNames          (U);
        selectionMode       cellSet;
        cellSet             turbine;
        origin              {str(fv_options.origin).replace(",", "")};
        axis                {str(fv_options.axis).replace(",", "")};
        verticalDirection   {str(fv_options.vertical_direction).replace(",", "")};
        freeStreamVelocity  {str(fv_options.free_stream_velocity).replace(",", "")};
        tipSpeedRatio       {fv_options.tip_speed_ratio};
        rotorRadius         {fv_options.rotor_radius};

        dynamicStall
        {{
            active          off;
            dynamicStallModel LeishmanBeddoes;
        }}

        endEffects
        {{
            active          on;
            endEffectsModel Glauert; // Glauert || Shen || liftingLine
            GlauertCoeffs
            {{
                tipEffects  on;
                rootEffects on;
            }}
            ShenCoeffs
            {{
                c1          0.125;
                c2          21;
                tipEffects  on;
                rootEffects on;
            }}
        }}

"""

    def write_blades():
        blade_str = "        blades\n        {\n"
        for idx in range(1, fv_options.num_blades + 1):
            blade_str += f"""            blade{idx}
            {{
                writePerf           true;
                writeElementPerf    true;
                nElements           {fv_options.num_blade_elements};
                elementProfiles
                (
"""
            for profile in fv_options.blade_profile:
                blade_str += f"                    {profile}\n"
            blade_str += "                );\n"
            # Azimuthal offset for additional blade
            if idx > 1:
                blade_str += f"                azimuthalOffset {(idx - 1) * 120.0};\n"
            # Always write reference to elementData file
            blade_str += """                elementData
                (
                    #include "elementData"
                );\n"""
            blade_str += "            }\n"
        blade_str += "        }\n"
        return blade_str

    def write_tower():
        return f"""        tower
        {{
            includeInTotalDrag  {"true" if fv_options.include_tower_drag else "false"};
            nElements   {fv_options.num_tower_elements};
            elementProfiles ({fv_options.tower_profile});
            elementData
            (
""" + "\n".join([f"                {data}" for data in fv_options.tower_element_data]) + "\n            );\n        }\n"

    def write_hub():
        return f"""        hub
        {{
            nElements   {fv_options.num_hub_elements};
            elementProfiles ({fv_options.hub_profile});
            elementData
            (
""" + "\n".join([f"                {data}" for data in fv_options.hub_element_data]) + "\n            );\n        }\n"

    def write_profile_data():
        profile_str = "        profileData\n        {\n"
        for profile_name in fv_options.profile_data:
            profile_str += f"""            {profile_name}
            {{
                data (#include "../../resources/foilData/{profile_name}");
            }}\n"""
        profile_str += "        }\n"
        return profile_str

    # Combine all sections to form the full contents of the fvOptions file
    contents = (
        write_header() +
        write_turbine_base() +
        write_blades() +
        write_tower() +
        write_hub() +
        write_profile_data() +
        "    }\n}\n\n// ************************************************************************* //\n"
    )

    # Write the contents to the fvOptions file
    with open(location / "system" / "fvOptions", "w") as file:
        file.write(contents)


if __name__ == "__main__":
    case_dir = WSL_ROOT / FOAM_RUN / "test_case"
    generate_blockMeshDict(case_dir)
    generate_topoSetDict(case_dir)
    generate_fvOptions(case_dir, fv)
