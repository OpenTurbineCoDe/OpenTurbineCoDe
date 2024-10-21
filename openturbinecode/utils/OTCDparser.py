import numpy as np
import csv


def OFparse(outfile, nodeR=[]):
    # Reading the csv output
    _ = open(outfile)  # Formerly ofh, switched to _ because currently unused.

    head = np.genfromtxt(outfile, delimiter='\t', skip_header=6, dtype="|U20", autostrip=True, max_rows=1)
    data = np.genfromtxt(outfile, delimiter='\t', skip_header=8, dtype="float", autostrip=True)

    # Identifying the rows of interest
    i = 0
    ifN0 = np.nan
    ifT0 = np.nan
    iPwr = np.nan
    iThr = np.nan
    iTrq = np.nan

    # Assigns a numerical value of i for each parameter, corresponding
    # to the column number where the values of that parameter are located.
    for str in head:
        # if "B1N1Fn" in str:  #in the frame of the root chord
        # if "AB1N001Fn" in str:  #in the frame of the root chord
        if "AB1N001Fx" in str:  # in the frame of the rotor plane
            ifN0 = i
        # elif "B1N1Ft" in str:
        # if "AB1N001Ft" in str:
        if "AB1N001Fy" in str:
            ifT0 = i
        elif "RtAeroPwr" in str:
            iPwr = i
        elif "RtAeroFxh" in str:
            iThr = i
        elif "RtAeroMxh" in str:
            iTrq = i
        i += 1

    fN = np.zeros(max(len(nodeR), 1))
    fT = np.zeros(max(len(nodeR), 1))
    pwr = np.nan

    # Time averaging the results for each spanwise station
    if np.isnan(ifN0) or np.isnan(ifT0) or len(nodeR) == 0:
        fN = np.nan*fN
        fT = np.nan*fT
        print('WARNING: did not find fN or fT in OF outputs. Output will be NaN.')
    else:
        for i in range(len(nodeR)):
            fN[i] = np.mean(data[0:, ifN0+i])
            fT[i] = np.mean(data[0:, ifT0+i])

    if not np.isnan(iPwr):
        pwr = np.mean(data[0:, iPwr])  # TG 7/27 Includes the last datapoint

    # Rough estimates of the torque/thrust using
    if np.isnan(iThr):
        thrust = np.trapz(fN, nodeR)
        print('WARNING: did not find thrust in OF outputs. Integrating the loads as an estimate.')
    else:
        thrust = np.mean(data[0:, iThr])  # TG 7/27 Includes the last datapoint

    if np.isnan(iTrq):
        torque = np.trapz(fT*np.array(nodeR), nodeR)
        print('WARNING: did not find torque in OF outputs. Integrating the loads as an estimate.')
    else:
        torque = np.mean(data[0:, iTrq])  # TG 7/27 Includes last datapoint

    return thrust, torque, pwr, fN, fT  # could do better with the finer exports


def UAEHparse(outfile):
    # Reading the csv output
    ofh = open(outfile)

    thrust = np.nan
    torque = np.nan
    pwr = np.nan
    thr_std = np.nan
    trq_std = np.nan
    pwr_std = np.nan
    for row in csv.reader(ofh, delimiter=','):
        if len(row) <= 1:
            continue
        # estimated with a gross integration of the pressure loads
        if row[0] == '815':
            thrust = float(row[10])
            thr_std = float(row[13])
        # LSSTQCOR: low speed shaft torque strain gauge - more accurate than the estimated aero torque
        if row[0] == '819':
            torque = float(row[10])
            trq_std = float(row[13])
        # power based on LSSTQCOR
        if row[0] == '822':
            pwr = float(row[10])*1e3
            pwr_std = float(row[13])*1e3
    ofh.close()

    return thrust, torque, pwr, thr_std, trq_std, pwr_std


def getLiftDistribution(testcase):
    dicty = {}
    f = open(testcase, 'r')
    lines = [line.rstrip('\n') for line in f]
    f.close()
    vars_slice = lines[1].replace('Variables = ', '').split('" "')
    nodes = int(lines[3].replace('I=   ', ''))

    print('found %i nodes in the file\n' % nodes)

    for i in range(len(vars_slice)):
        vars_slice[i] = vars_slice[i].replace('"', '')
    vars_slice[-1] = vars_slice[-1].rstrip(' ')

    for i in range(len(vars_slice)):
        dicty[vars_slice[i]] = []
        for j in range(nodes):
            dicty[vars_slice[i]].append(float(lines[5+j+(nodes*i)]))
    return dicty
