# sample code taken from AeroelasticSE example in WEIS

import sys
import os
import platform
import numpy as np

try:
    # from weis.aeroelasticse.runfast_pywrapper   import runfast_pywrapper, runfast_pywrapper_batch
    # from weis.aeroelasticse.CaseGen_IEC         import CaseGen_IEC    Commented out by TG 6/29
    from ROSCO_toolbox.ofTools.case_gen.CaseGen_IEC import CaseGen_IEC  # TG 6/29
    # the casegen_iec module no longer exists under aeroelasticse -- that's an old version of weis. an updated version of the module is under rosco.    TG
    # from wisdem.commonse.mpi_tools              import mpi
except ImportError as err:
    _has_aeroelasticse = False
else:
    _has_aeroelasticse = True


"""
Definition of a decorator to be used on every function that requires the sprcific module
"""


def requires_aeroelasticse(function):
    def check_requirement(*args, **kwargs):
        if _has_aeroelasticse == False:
            raise ImportError("AeroelasticSE is required to do this.")
        function(*args, *kwargs)
    return check_requirement


@requires_aeroelasticse
def generateDLC(path, turb_data, DLC_list, n_ws, n_seeds, TMax):

    # ==================== DEFINITIONS  =====================================

    # File management
    # mydir = os.path.dirname(os.path.realpath(__file__))  # get path to this file
    # fname_wt_input = mydir + os.sep + "IEA-10-198-RWT.yaml"

    # #location of servodyn lib (./local of weis)
    # #run_dir1            = "/fslhome/dcaprace/ATLANTIS/soft/python_modules/WEIS/" # os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ) ) ) + os.sep
    # run_dir1            = "/Users/dg/Documents/BYU/devel/Python/WEIS"
    # run_dir2            = run_dir1 + "/examples/01_aeroelasticse/"

    # ==================== PART 2 =====================================
    # Unsteady loading computation from DLCs

    # Turbine inputs
    iec = CaseGen_IEC()
    # Wind class I, II, III, IV
    iec.Turbine_Class = turb_data["assembly"]["turbine_class"]
    # Turbulence class 'A', 'B', or 'C'
    iec.Turbulence_Class = turb_data["assembly"]["turbulence_class"]
    # Rotor diameter to size the wind grid
    iec.D = turb_data["assembly"]["rotor_diameter"]
    # Hub height to size the wind grid
    iec.z_hub = turb_data["assembly"]["hub_height"]
    cut_in = turb_data["control"]["supervisory"]["Vin"]    # Cut in wind speed
    # Cut out wind speed
    cut_out = turb_data["control"]["supervisory"]["Vout"]
    Vrated = turb_data["control"]["supervisory"]["Vrated"]   # Rated wind speed

    # n_ws                    = 3    # Number of wind speed bins
    # TMax                    = 1.    # Length of wind grids and OpenFAST simulations, suggested 720 s

    # Start of the transient for DLC with a transient, e.g. DLC 1.4
    Ttrans = max([0., TMax - 60.])
    # Start of the recording of the channels of OpenFAST
    TStart = max([0., TMax - 600.])

    # #TODO: we already defined vel range and stuff in the turbine yaml... can we use that here too?
    # # Initial conditions to start the OpenFAST runs
    # u_ref     = np.arange(3.,26.) # Wind speed
    # pitch_ref = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5058525323662666, 5.253759185225932, 7.50413344606208, 9.310153958810268, 10.8972969450052, 12.412247669440042, 13.883219268525659, 15.252012626933068, 16.53735488246438, 17.76456777500061, 18.953261878035104, 20.11055307762722, 21.238680277668898, 22.30705111326602, 23.455462501156205] # Pitch values in deg
    # omega_ref = [2.019140272160114, 2.8047214918577925, 3.594541645994511, 4.359025795823625, 5.1123509774611025, 5.855691196288371, 6.589281196735111, 7.312788026081227, 7.514186181824161, 7.54665511646938, 7.573823812448151, 7.600476033113538, 7.630243938880304, 7.638301051122195, 7.622050377183605, 7.612285710588359, 7.60743945212863, 7.605865650155881, 7.605792924227456, 7.6062185247519825, 7.607153933765292, 7.613179734210654, 7.606737845170748] # Rotor speeds in rpm

    iec.init_cond = {}
    # iec.init_cond[("ElastoDyn","RotSpeed")]        = {'U':u_ref}
    # iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = omega_ref
    # iec.init_cond[("ElastoDyn","BlPitch1")]        = {'U':u_ref}
    # iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = pitch_ref
    # iec.init_cond[("ElastoDyn","BlPitch2")]        = iec.init_cond[("ElastoDyn","BlPitch1")]
    # iec.init_cond[("ElastoDyn","BlPitch3")]        = iec.init_cond[("ElastoDyn","BlPitch1")]
    # # iec.init_cond[("HydroDyn","WaveHs")]           = {'U':[3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 40, 50]}
    # # iec.init_cond[("HydroDyn","WaveHs")]['val']    = [1.101917033, 1.101917033, 1.179052649, 1.315715154, 1.536867124, 1.835816514, 2.187994638, 2.598127096, 3.061304068, 3.617035443, 4.027470219, 4.51580671, 4.51580671, 6.98, 10.7]
    # # iec.init_cond[("HydroDyn","WaveTp")]           = {'U':[3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 40, 50]}
    # # iec.init_cond[("HydroDyn","WaveTp")]['val']    = [8.515382435, 8.515382435, 8.310063688, 8.006300889, 7.6514231, 7.440581338, 7.460834063, 7.643300307, 8.046899942, 8.521314105, 8.987021024, 9.451641026, 9.451641026, 11.7, 14.2]
    # # iec.init_cond[("HydroDyn","PtfmSurge")]        = {'U':[3., 15., 25.]}
    # # iec.init_cond[("HydroDyn","PtfmSurge")]['val'] = [4., 15., 10.]
    # # iec.init_cond[("HydroDyn","PtfmPitch")]        = {'U':[3., 15., 25.]}
    # # iec.init_cond[("HydroDyn","PtfmPitch")]['val'] = [-1., 3., 1.3]
    # # iec.init_cond[("HydroDyn","PtfmHeave")]        = {'U':[3., 25.]}
    # # iec.init_cond[("HydroDyn","PtfmHeave")]['val'] = [0.5,0.5]

    # Process DLC inputs

    wind_speeds = np.linspace(int(cut_in), int(cut_out), int(n_ws))
    iec.dlc_inputs = {}
    iec.dlc_inputs['DLC'] = DLC_list
    iec.dlc_inputs['U'] = []
    iec.dlc_inputs['Seeds'] = []
    iec.dlc_inputs['Yaw'] = []

    for DLC in DLC_list:
        # VELOCITY
        if DLC == 1.4 or DLC == 5.1:
            iec.dlc_inputs['U'].append([Vrated - 2., Vrated, Vrated + 2.])
        elif DLC >= 6.1 and DLC <= 6.3:
            iec.dlc_inputs['U'].append([])
        else:
            iec.dlc_inputs['U'].append(wind_speeds)

        # SEED
        if DLC == 0 or DLC >= 1.4 and DLC <= 1.5:
            iec.dlc_inputs['Seeds'].append([])  # deterministic
        else:
            # number of seeds, probabilistic
            iec.dlc_inputs['Seeds'].append([n_seeds])

        # YAW
        iec.dlc_inputs['Yaw'].append([])

    iec.PC_MaxRat = 2.  # ??

    # #example multiple:
    # iec.dlc_inputs['DLC']   = [1.1, 1.3, 1.4, 1.5, 5.1, 6.1, 6.3]
    # iec.dlc_inputs['U']     = [wind_speeds, wind_speeds,[Vrated - 2., Vrated, Vrated + 2.],wind_speeds, [Vrated - 2., Vrated, Vrated + 2., cut_out], [], []]
    # iec.dlc_inputs['Seeds'] = [[1],[1],[],[],[1],[1],[1]]
    # # iec.dlc_inputs['Seeds'] = [range(1,7), range(1,7),[],[], range(1,7), range(1,7), range(1,7)]
    # iec.dlc_inputs['Yaw']   = [[], [], [], [], [], [], []]
    # iec.PC_MaxRat           = 2. #??
    # #only power curve:
    # wind_speeds = [18]
    # iec.dlc_inputs = {}
    # iec.dlc_inputs['DLC']   = [1.1]
    # iec.dlc_inputs['U']     = [wind_speeds]
    # iec.dlc_inputs['Seeds'] = [[1]]
    # # iec.dlc_inputs['Seeds'] = [range(1,7), range(1,7),[],[], range(1,7), range(1,7), range(1,7)]
    # iec.dlc_inputs['Yaw']   = [[]]

    iec.TStart = Ttrans
    iec.TMax = TMax    # wind file length
    # '+','-','both': sign for transient events in EDC, EWS
    iec.transient_dir_change = 'both'
    # 'v','h','both': vertical or horizontal shear for EWS
    iec.transient_shear_orientation = 'both'

    # # Management of parallelization
    # if MPI:
    #     from wisdem.commonse.mpi_tools import map_comm_heirarchical, subprocessor_loop, subprocessor_stop
    #     n_OF_runs = 0
    #     for i in range(len(iec.dlc_inputs['DLC'])):
    #         # Number of wind speeds
    #         if iec.dlc_inputs['DLC'][i] == 1.4: # assuming 1.4 is run at [V_rated-2, V_rated, V_rated] and +/- direction change
    #             if iec.dlc_inputs['U'][i] == []:
    #                 n_U = 6
    #             else:
    #                 n_U = len(iec.dlc_inputs['U'][i]) * 2
    #         elif iec.dlc_inputs['DLC'][i] == 5.1: # assuming 5.1 is run at [V_rated-2, V_rated, V_rated]
    #             if iec.dlc_inputs['U'][i] == []:
    #                 n_U = 3
    #             else:
    #                 n_U = len(iec.dlc_inputs['U'][i])
    #         elif iec.dlc_inputs['DLC'][i] in [6.1, 6.3]: # assuming V_50 for [-8, 8] deg yaw error
    #             if iec.dlc_inputs['U'][i] == []:
    #                 n_U = 2
    #             else:
    #                 n_U = len(iec.dlc_inputs['U'][i])
    #         else:
    #             n_U = len(iec.dlc_inputs['U'][i])
    #         # Number of seeds
    #         if iec.dlc_inputs['DLC'][i] == 1.4: # not turbulent
    #             n_Seeds = 1
    #         else:
    #             n_Seeds = len(iec.dlc_inputs['Seeds'][i])
    #         n_OF_runs += n_U*n_Seeds
    #         available_cores = MPI.COMM_WORLD.Get_size()
    #         n_parallel_OFruns = np.min([available_cores - 1, n_OF_runs])
    #         comm_map_down, comm_map_up, color_map = map_comm_heirarchical(1, n_parallel_OFruns)
    #         sys.stdout.flush()

    case_inputs = {}
    # case_inputs ... pass info to tweak your OF simu if required. Not to be mistaken for the initial conditions.

    # Naming, file management, etc
    iec.wind_dir = path + os.sep + 'DLCs/wind'
    iec.case_name_base = 'iea10mw'
    iec.cores = 1

    iec.debug_level = 2

    iec.parallel_windfile_gen = False
    iec.mpi_run = False
    iec.run_dir = path + os.sep + 'DLCs/iea15mw'

    # Parallel file generation with MPI

    rank = 0
    if rank == 0:
        case_list, case_name_list, dlc_list = iec.execute(
            case_inputs=case_inputs)

        # print(case_name_list)
        # print(case_list)
        # print(dlc_list)

        for case in case_name_list:
            print("Generated " + case)

    sys.stdout.flush()
    sys.stdout.flush()
