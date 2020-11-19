# ================================================
# External python imports
# ================================================
import argparse
import numpy as np
import os
import matplotlib.pyplot as plt

# ================================================
# Input arguments
# ================================================

parser = argparse.ArgumentParser()
parser.add_argument("--procs", help="number of processors", type=int, default=4)
parser.add_argument("--output", help="Output directory", type=str, default="Outputs")
parser.add_argument("--configuration", help="WT Configuration", type=str, default="DTU_10MW")
parser.add_argument("--hifimesh", help="CFD mesh level - [0,1,2,3,4]", type=int, default=3)
parser.add_argument("--V", help="Inflow wind speed", type=float, default=8.0)
parser.add_argument("--tsrlist", help="Prescribed tip speed ratio", type=float, default=[7.8], nargs="+")
parser.add_argument("--restart", help="Name of the restart file", type=str, default=None)
args = parser.parse_args()

baseDir = os.path.dirname(os.path.abspath(__file__))
path_to_case = os.path.join(baseDir, args.configuration, "original/")

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


# ================================================
# High-Fidelity runs with ADflow
# ================================================

hifi_torque = []
hifi_cp = []
hifi_file = os.path.join(path_to_case, "ADflow/Wrapped_hifi_Analysis.py")
for tsr in args.tsrlist:  # Looping over a range of input tip speed ratios
    args.tsr = tsr
    exec(compile(open(hifi_file, "rb").read(), hifi_file, "exec"))  # Running the ADflow runscript

    # Extracting performance information
    torque = funcs[f"{ap.name}_mx"]
    cp, pwr, rpm, om, tip_speed = WT_performance(args.V, spanRef, areaRef, rho[0], tsr, torque)

    hifi_torque.append(torque)
    hifi_cp.append(cp)


# ================================================
# Low-Fidelity runs with AeroDyn / CCBlade
# ================================================
for tsr in args.tsrlist:
    print(f"Low-fi output for tsr={tsr}")


# ================================================
# Plotting the results
# ================================================

if MPI.COMM_WORLD.rank == 0:
    print(hifi_torque)
    print(hifi_cp)

    f, ax = plt.subplots(figsize=(10, 7.5))
    plt.plot(args.tsrlist, hifi_cp, label="High Fidelity", marker="o")
    # plt.plot(args.tsr, lofi_cp, label='Low Fidelity', marker="o")
    # ax.set_xlim(0, -40)
    plt.title("Multifidelity study", fontsize=18)
    plt.xlabel(r"TSR", fontsize=16)
    plt.ylabel(r"$C_p$", fontsize=16)
    plt.grid()
    plt.tick_params(axis="both", labelsize=16)
    plt.legend(loc="upper left", fontsize=16)
    # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    # plt.xticks(N, N_list)
    f.tight_layout()
    plt.savefig(f"{outputDirectory}/Multifidelity_comparison.pdf")
    # plt.show()
