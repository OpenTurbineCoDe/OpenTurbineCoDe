import numpy as np
import matplotlib.pyplot as plt


def WT_performance(V, span, A, rho, tsr, torque):
    tip_speed = tsr * V
    om = tip_speed / span
    rpm = om / (2 * np.pi) * 60

    pwr = torque * om
    cp = pwr / (0.5 * rho * V ** 3 * A)
    return cp, pwr, rpm, om, tip_speed


# tsr = [6, 7.8, 8, 9, 10, 11]
rpm = [5.140594353281056, 6.682772659265372, 6.854125804374741, 7.710891529921582, 8.567657255468426, 9.424422981015269]
torque_tsr_aero = [
    6486324.515557441,
    6177710.636690566,
    6118368.157031173,
    5762388.798192269,
    5383884.229969542,
    4970668.212413302,
]
torque_tsr_aero = [i / 6177710.636690566 * 100 for i in torque_tsr_aero]

torque_tsr_as = [
    6466181.68889197,
    6089781.464942027,
    6022126.314603662,
    5642901.570431805,
    5233110.354232096,
    4788045.0081259515,
]
torque_tsr_as = [i / 6177710.636690566 * 100 for i in torque_tsr_as]

span = [0.9, 0.95, 1, 1.05, 1.1]
torque_span_aero = [5070841.690466099, 5624674.827432943, 6192015.250241273, 6771008.30635636, 7358283.154983968]
torque_span_aero = [i / 6192015.250241273 * 100 for i in torque_span_aero]
torque_span_as = [5036017.931075935, 5562770.714669893, 6089781.464942027, 6600057.569262839, 7091336.621986912]
torque_span_as = [i / 6192015.250241273 * 100 for i in torque_span_as]

pitch = [0, 2, 4, 5, 6, 7]  # , 8]
# pitch_aero = [0, 2, 4, 6, 7, 8]
torque_pitch_aero = [
    6192015.250241273,
    6953432.990313784,
    7554436.754475241,
    7782917.222971912,
    7948377.75517264,
    8006502.140278728,
    # 7774801.5885043545,
]
torque_pitch_aero = [i / 6192015.250241273 * 100 for i in torque_pitch_aero]
torque_pitch_as = [
    6089781.464942027,
    6878438.9956290545,
    7503391.97690941,
    7742389.247932378,
    7917333.687112423,
    7995488.400889516,
    # 7888155.883263865,
]
torque_pitch_as = [i / 6192015.250241273 * 100 for i in torque_pitch_as]

f, ax = plt.subplots(figsize=(10, 7.5))
# for i in range(len(torque)):
#     if i <= 3:
#         sty = "--"
#     else:
#         sty = "-"
#     plt.plot(tsr[i], cp[i], label=labels[i], marker="o", linestyle=sty)
plt.plot(rpm, torque_tsr_aero, label="Aero-only", marker="o")
plt.plot(rpm, torque_tsr_as, label="Aerostructural", marker="o")
# ax.set_xlim(0, -40)
plt.title("Aero vs Aerostructural analysis", fontsize=18)
plt.xlabel(r"Rpm", fontsize=16)
plt.ylabel(r"Torque $[\%]$", fontsize=16)
plt.grid()
plt.tick_params(axis="both", labelsize=16)
plt.legend(loc="lower left", fontsize=16)
# ax.xaxis.set_major_locator(MaxNLocator(integer=True))
# plt.xticks(N, N_list)
f.tight_layout()
# plt.savefig("param_study_tsr.pdf")
# plt.show()

f, ax = plt.subplots(figsize=(10, 7.5))
plt.plot(span, torque_span_aero, label="Aero-only", marker="o")
plt.plot(span, torque_span_as, label="Aerostructural", marker="o")
# ax.set_xlim(0, -40)
plt.title("Aero vs Aerostructural analysis", fontsize=18)
plt.xlabel(r"Normalized span", fontsize=16)
plt.ylabel(r"Torque $[\%]$", fontsize=16)
plt.grid()
plt.tick_params(axis="both", labelsize=16)
plt.legend(loc="upper left", fontsize=16)
# ax.xaxis.set_major_locator(MaxNLocator(integer=True))
# plt.xticks(N, N_list)
f.tight_layout()
# plt.savefig("param_study_span.pdf")
# plt.show()

f, ax = plt.subplots(figsize=(10, 7.5))
plt.plot(pitch, torque_pitch_aero, label="Aero-only", marker="o")
plt.plot(pitch, torque_pitch_as, label="Aerostructural", marker="o")
# ax.set_xlim(0, -40)
plt.title("Aero vs Aerostructural analysis", fontsize=18)
plt.xlabel(r"Pitch [$^\circ$]", fontsize=16)
plt.ylabel(r"Torque $[\%]$", fontsize=16)
plt.grid()
plt.tick_params(axis="both", labelsize=16)
plt.legend(loc="upper left", fontsize=16)
# ax.xaxis.set_major_locator(MaxNLocator(integer=True))
# plt.xticks(N, N_list)
f.tight_layout()
# plt.savefig("param_study_pitch.pdf")
plt.show()
