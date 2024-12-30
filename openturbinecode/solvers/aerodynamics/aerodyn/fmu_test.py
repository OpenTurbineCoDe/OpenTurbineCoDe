from fmpy import simulate_fmu
import numpy as np


def main():
    # Define FMU path
    fmu_path = "AeroDynSlave.fmu"

    # Define simulation inputs
    inputs = np.array([
        (0.0, 1.0, 2.0, 3.0, 0.1, 0.2, 0.3, 0.01, 0.02, 0.03),  # Initial inputs
    ], dtype=[
        ('time', np.float64),
        ('position_1', np.float64), ('position_2', np.float64), ('position_3', np.float64),
        ('velocity_1', np.float64), ('velocity_2', np.float64), ('velocity_3', np.float64),
        ('orientation_1', np.float64), ('orientation_2', np.float64), ('orientation_3', np.float64)
    ])

    # inputs = np.array([
    #     (0.0, 1.0),  # At time 0.0, test_input is 1.0
    # ], dtype=[('time', np.float64), ('test_input', np.float64)])

    # Simulate the FMU
    result = simulate_fmu(
        filename=fmu_path,
        start_time=0.0,
        stop_time=10.0,  # Simulation runtime
        input=inputs,  # Pass simulation inputs
        output_interval=10.0
    )

    # Print the inputs for verification
    print("Simulation Inputs:")
    for row in inputs:
        print(row)

    # Print the results
    print("\nSimulation Results:")
    for time in result['time']:
        print(f"Time: {time:.2f}")


if __name__ == "__main__":
    main()
