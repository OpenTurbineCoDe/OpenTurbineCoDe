from fmpy import simulate_fmu
import numpy as np

PRECONE = 0.0
BLADE_PITCH = 0.0


def main():
    # Define FMU path
    fmu_path = "AeroDynSlave.fmu"

    # Define simulation inputs for blade geometry
    # IEA-15 has no precone
    input_data = np.array([
        [0.0,               # time
         0.0, 0.0, 0.0,     # blade 1 origin
         PRECONE, 0.0, BLADE_PITCH,    # blade 1 azimuth, precone, pitch
         0.0,               # blade 1 hub radius
         0.0, 0.0, 120.0,   # blade 2 origin
         PRECONE, 0.0, BLADE_PITCH,    # blade 2 azimuth, precone, pitch
         0.0,               # blade 2 hub radius
         0.0, 0.0, 240.0,   # blade 3 origin
         PRECONE, 0.0, BLADE_PITCH,    # blade 3 azimuth, precone, pitch
         0.0]               # blade 3 hub radius
    ], dtype=np.float64)

    # Define the column names for the input variables
    input_variables = [
        'time',
        'blade_origin_x_1', 'blade_origin_y_1', 'blade_origin_z_1',
        'blade_orientation_azimuth_1', 'blade_orientation_precone_1', 'blade_orientation_pitch_1',
        'blade_hub_radius_1',
        'blade_origin_x_2', 'blade_origin_y_2', 'blade_origin_z_2',
        'blade_orientation_azimuth_2', 'blade_orientation_precone_2', 'blade_orientation_pitch_2',
        'blade_hub_radius_2',
        'blade_origin_x_3', 'blade_origin_y_3', 'blade_origin_z_3',
        'blade_orientation_azimuth_3', 'blade_orientation_precone_3', 'blade_orientation_pitch_3',
        'blade_hub_radius_3',
    ]

    # Convert to structured array for simulation
    inputs = np.rec.fromarrays(input_data.T, names=input_variables)

    # Simulate the FMU
    result = simulate_fmu(
        filename=fmu_path,
        start_time=0.0,
        stop_time=10.0,
        input=inputs,
        output_interval=10.0,
        debug_logging=True
    )

    # Print the inputs for verification
    print("Simulation Inputs:")
    for row in input_data:
        print(row)

    # Print the results
    print("\nSimulation Results:")
    print(result)


if __name__ == "__main__":
    main()
