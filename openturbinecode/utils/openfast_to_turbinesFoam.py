"""This module assists in the conversion of OpenFAST files to TurbinesFoam files.
"""
from pathlib import Path
import pandas as pd
from openturbinecode.configs.pathing import PROJECT_ROOT


OPENFAST_MODEL_DIR: Path = PROJECT_ROOT / "models" / "DTU_10MW" / "Madsen2019" / "OpenFAST"
TURBINESFOAM_MODEL_DIR: Path = PROJECT_ROOT / "models" / "DTU_10MW" / "Madsen2019" / "turbinesFoam"

CONVERT_AIRFOILS = False
CONVERT_BLADE = True


def extract_openfast_airfoil_data(filename):
    """Extracts the airfoil data from an OpenFAST airfoil file.

    Args:
        filename (str): Name of file

    Returns:
        Pandas DataFrame: DataFrame of aerodynamic data.
    """
    aero_data_started = False
    aero_data_lines = []

    with open(OPENFAST_MODEL_DIR / "AeroData" / f"{filename}.dat", 'r') as file:
        for line in file:
            line = line.strip()

            # Start collecting aerodynamics data after finding the line with 'Alpha Cl Cd Cm'
            if "Alpha" and "Cl" and "Cd" and "Cm" in line:
                aero_data_started = True  # Trigger data collection
                next(file)  # Skip the units header line
                continue

            # Collect aerodynamic data lines
            if aero_data_started:
                parts = line.split()
                if len(parts) == 4:
                    aero_data_lines.append([float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])])

    # Convert to DataFrame
    aerodynamics_df = pd.DataFrame(aero_data_lines, columns=["Alpha (deg)", "Cl", "Cd", "Cm"])

    return aerodynamics_df


def write_turbinesFoam_airfoil_file(filename, aerodynamics_df):
    with open(TURBINESFOAM_MODEL_DIR / "airfoildata" / filename, 'w') as file:
        # Write header
        file.write(f"// {filename}\n")
        file.write("//   alpha   C_l    C_d\n")

        # Write data rows in the specified format
        for _, row in aerodynamics_df.iterrows():
            alpha = int(row["Alpha (deg)"])  # Convert Alpha to integer for formatting
            cl = round(row["Cl"], 3)         # Limit Cl to 3 decimal places
            cd = round(row["Cd"], 4)         # Limit Cd to 4 decimal places
            file.write(f"    ({alpha:<4} {cl:<6} {cd})\n")

    return None


def convert_airfoil_file(filename):
    """Converts an airfoil file from OpenFAST to TurbinesFoam file format.

    Args:
        filename (str): Name of file to convert.
    """
    print(f"Converting airfoil file: {filename}")

    # Extract the airfoil data
    aerodynamics_df = extract_openfast_airfoil_data(filename)

    # Write the airfoil file in TurbinesFoam format
    write_turbinesFoam_airfoil_file(filename, aerodynamics_df)

    print(f"Airfoil file {filename} converted successfully.")


def extract_openfast_blade_properties(filename):
    """Extracts the elementData from an OpenFAST elementData file.

    Args:
        filename (str): Name of file

    Returns:
        Pandas DataFrame: DataFrame of element data.
    """
    element_data_lines = []
    blade_data_found = False

    with open(OPENFAST_MODEL_DIR / filename, 'r') as file:
        for line in file:
            line = line.strip()

            # Start collecting aerodynamics data after finding the line with 'Alpha Cl Cd Cm'
            # BlSpn     BlCrvAC    BlSwpAC    BlCrvAng    BlTwist    BlChord    BlAFID
            if "BlSpn" and "BlCrvAC" and "BlSwpAC" and "BlCrvAng" in line:
                blade_data_found = True  # Trigger data collection
                next(file)  # Skip the units header line
                continue

            # Collect element data lines
            if blade_data_found:
                parts = line.split()
                if len(parts) == 6:
                    all_data = [int(parts[0]), float(parts[1]), float(parts[2]),
                                float(parts[3]), float(parts[4]), float(parts[5])]
                    element_data_lines.append(all_data)

    # Convert to DataFrame
    columns = ["Span", "CurveAC", "SweepAC", "CurveAngle", "Twist", "Chord", "AirfoilID"]
    elementData_df = pd.DataFrame(element_data_lines, columns=columns)

    return elementData_df


def write_turbinesFoam_elementData_file(filename, elementData_df):
    with open(TURBINESFOAM_MODEL_DIR / "elementData" / filename, 'w') as file:
        # Write header
        file.write("// Blade element data\n")
        file.write("// axialDistance, radius, azimuth, chord, chordMount, twist\n")

        # Write data rows in the specified format
        for _, row in elementData_df.iterrows():
            axial_distance = round(0, 1)
            radius = round(row["Span"], 3)
            azimuth = round(0, 1)
            chord = round(row["Chord"], 3)
            chord_mount = round(0.25, 2)
            twist = round(row["Twist"], 3)
            file.write(f"    ({axial_distance:<4} {radius:<6} {azimuth:<6} {chord} {chord_mount} {twist})\n")

    return None


def convert_elementData_file(openfast_filename, turbinesFoam_filename):
    """Converts an elementData file from OpenFAST to TurbinesFoam file format.

    Args:
        filename (str): Name of file to convert.
    """
    print(f"Converting elementData file: {openfast_filename}")

    # Extract the elementData
    elementData_df = extract_openfast_blade_properties(openfast_filename)

    # Write the elementData file in TurbinesFoam format
    write_turbinesFoam_elementData_file(turbinesFoam_filename, elementData_df)

    print(f"ElementData file {openfast_filename} converted successfully.")


if __name__ == "__main__":
    if CONVERT_AIRFOILS:
        # Convert all airfoil files
        airfoil_files = ["Cylinder", "FFA_W3_241", "FFA_W3_301", "FFA_W3_360", "FFA_W3_480", "FFA_W3_600"]

        # Convert each airfoil file
        for airfoil_file in airfoil_files:
            convert_airfoil_file(airfoil_file)

    # Create elementData file
    if CONVERT_BLADE:
        openfast_filename = "DTU_10MW_ADBlade.dat"
        turbinesFoam_filename = "elementData"
        convert_elementData_file(openfast_filename, turbinesFoam_filename)
