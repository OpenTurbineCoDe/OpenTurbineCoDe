import os
import re
import pandas as pd


def extract_thrust_torque(file_path):
    """Extract Time, Thrust, and Torque from an AeroDyn .out file."""
    records = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                if re.match(r'^\s*\d+\.\d+', line):
                    parts = line.strip().split()
                    if len(parts) >= 29:
                        try:
                            time = float(parts[0])
                            thrust = float(parts[22])  # RtAeroFxh
                            torque = float(parts[25])  # RtAeroMxh
                            power = float(parts[18])  # RtAeroPwr
                            records.append((time, thrust, torque, power))
                        except ValueError:
                            continue
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return records


def parse_parametric_folder(folder_name):
    """Extract pitch_angle and tip_speed_ratio from folder name."""
    match = re.search(r'pitch_angle_([-+]?[0-9]*\.?[0-9]+)_tip_speed_ratio_([-+]?[0-9]*\.?[0-9]+)', folder_name)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None


def walk_and_process(root_dir):
    """Walk through the directory, process .out files, and collect parametric data."""
    summary = []

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.out'):
                full_path = os.path.join(subdir, file)
                folder = os.path.basename(os.path.normpath(subdir))
                pitch_angle, tip_speed_ratio = parse_parametric_folder(folder)

                if pitch_angle is not None and tip_speed_ratio is not None:
                    records = extract_thrust_torque(full_path)
                    if records:
                        thrusts = [r[1] for r in records]
                        torques = [r[2] for r in records]
                        summary.append({
                            "pitch_angle": pitch_angle,
                            "tip_speed_ratio": tip_speed_ratio,
                            "mean_thrust_N": sum(thrusts) / len(thrusts),
                            "mean_torque_Nm": sum(torques) / len(torques),
                            "mean_power_W": sum(r[3] for r in records) / len(records),
                            "case_path": full_path
                        })

    return pd.DataFrame(summary)


# === Example Usage ===
if __name__ == "__main__":
    root = r"E:\Wright\Solvers\aerodynamics\aerodyn\run\parametric_analysis\DTU_10MW\003_blade.pitch_angle_1_blade.tip_speed_ratio_10"
    df = walk_and_process(root)
    df.sort_values(["pitch_angle", "tip_speed_ratio"], inplace=True)
    print(df)

    # Optional: save to CSV
    df.to_csv("parametric_thrust_torque_summary.csv", index=False)
