from simulatortofmu import SimulatorToFMU

SimulatorToFMU(
    simulator_path="python aerodyn_fmu_controller.py",
    fmu_name="AeroDynController",
    inputs={
        "wind_speed": "Real",
        "pitch_angle": "Real"
    },
    outputs={
        "aero_force": "Real"
    },
    description="FMU for controlling AeroDyn from Python"
)
