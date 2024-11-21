
import numpy as np
import os
import json

# =============================================================
# Performance function to postproduce High-Fidelity results
# =============================================================


def WT_performance(V, span, A, rho, tsr, torque):
    tip_speed = tsr * V
    om = tip_speed / span
    rpm = om / (2 * np.pi) * 60

    pwr = torque * om
    cp = pwr / (0.5 * rho * V ** 3 * A)
    return cp, pwr, rpm, om, tip_speed


def read_config():
    current_dir = os.path.dirname(__file__)

    with open(os.path.join(current_dir, '../config.json')) as file:
        config = json.load(file)

    return config


def calculate_tsr_or_missing(**kwargs):
    """
    Calculate the missing component for TSR (Tip Speed Ratio) using the formula:
    TSR = (rotor_speed * radius) / freestream_velocity

    Arguments should include any two of the following as keyword arguments:
    - radius (float): Rotor radius (meters)
    - rotor_speed (float): Rotor angular velocity (rpm)
    - freestream_velocity (float): Freestream velocity (m/s)
    - tsr (float): Tip Speed Ratio (unitless)

    Returns:
        float: The calculated missing component.
    """
    if 'rotor_speed' in kwargs:
        # Convert rotor speed from RPM to radians/second
        kwargs['rotor_speed'] = kwargs['rotor_speed'] * (2 * 3.14159 / 60)

    if 'radius' not in kwargs:
        if 'rotor_speed' in kwargs and 'freestream_velocity' in kwargs and 'tsr' in kwargs:
            return (kwargs['tsr'] * kwargs['freestream_velocity']) / kwargs['rotor_speed']
        else:
            raise ValueError("To calculate radius, provide rotor_speed, freestream_velocity, and TSR.")
    elif 'rotor_speed' not in kwargs:
        if 'radius' in kwargs and 'freestream_velocity' in kwargs and 'tsr' in kwargs:
            return (kwargs['tsr'] * kwargs['freestream_velocity']) / kwargs['radius'] * (60 / (2 * 3.14159))
        else:
            raise ValueError("To calculate rotor_speed, provide radius, freestream_velocity, and TSR.")
    elif 'freestream_velocity' not in kwargs:
        if 'radius' in kwargs and 'rotor_speed' in kwargs and 'tsr' in kwargs:
            return (kwargs['rotor_speed'] * kwargs['radius']) / kwargs['tsr']
        else:
            raise ValueError("To calculate freestream_velocity, provide radius, rotor_speed, and TSR.")
    elif 'tsr' not in kwargs:
        if 'radius' in kwargs and 'rotor_speed' in kwargs and 'freestream_velocity' in kwargs:
            return (kwargs['rotor_speed'] * kwargs['radius']) / kwargs['freestream_velocity']
        else:
            raise ValueError("To calculate TSR, provide radius, rotor_speed, and freestream_velocity.")
    else:
        raise ValueError("Provide only three inputs to solve for the missing component.")


if __name__ == "__main__":
    # Example usage
    radius = 89.167  # meters
    tip_speed_ratio = 10  # RPM
    freestream_velocity = 14  # m/s

    rotor_speed = calculate_tsr_or_missing(radius=radius, tsr=tip_speed_ratio, freestream_velocity=freestream_velocity)
    print(f"Rotor Speed: {rotor_speed}")
