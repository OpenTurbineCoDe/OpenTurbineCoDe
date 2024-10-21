
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
