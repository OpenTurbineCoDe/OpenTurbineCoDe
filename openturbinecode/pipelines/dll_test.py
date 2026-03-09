# flake8: noqa E501
import ctypes
from ctypes import c_int, c_float, c_double, c_bool, c_char_p, c_char, CDLL, byref, c_void_p, WinDLL, POINTER, create_string_buffer
import numpy as np
from openturbinecode.configs.pathing import PROJECT_ROOT

# Load the DLL
dll_path = PROJECT_ROOT / "apps" / "AeroDyn.dll"
dll = CDLL(dll_path)


"""NOTES:
pointer - 
POINTER - ctypes class that creates a new pointer type. It is used to create pointers to other ctypes types.
create_string_buffer(init_or_size, size=None) - Creates a mutable character buffer. The returned object is a ctypes array of c_char.

c_char_p - Represents the C char * datatype when it points to a zero-terminated string. For a general character pointer, use c_void_p.
c_void_p - Represents the C void * datatype. It is used for raw memory addresses, which are represented as Python integers.
c_wchar_p - Represents the C wchar_t * datatype when it points to a zero-terminated Unicode string.
"""

# Define the argument types for AeroDyn_Inflow_C_Init
dll.AeroDyn_Inflow_C_Init.argtypes = [
    POINTER(c_int),         # ADinputFilePassed - (logical flag as integer)
    POINTER(c_char_p),      # ADinputFileString_C - pointer to a char pointer
    POINTER(c_int),         # ADinputFileStringLength_C - string length (by reference)
    POINTER(c_int),         # IfWinputFilePassed - (logical flag as integer)
    POINTER(c_char_p),      # IfWinputFileString_C - pointer to a char pointer
    POINTER(c_int),         # IfWinputFileStringLength_C - string length (by reference)
    POINTER(c_char),        # OutRootName_C - fixed-length char buffer (by reference)
    POINTER(c_char),        # OutVTKdir_C - fixed-length char buffer (by reference)
    POINTER(c_float),       # gravity_C - real(c_float) (by reference)
    POINTER(c_float),       # defFldDens_C - real(c_float) (by reference)
    POINTER(c_float),       # defKinVisc_C - real(c_float) (by reference)
    POINTER(c_float),       # defSpdSound_C - real(c_float) (by reference)
    POINTER(c_float),       # defPatm_C - real(c_float) (by reference)
    POINTER(c_float),       # defPvap_C - real(c_float) (by reference)
    POINTER(c_float),       # WtrDpth_C - real(c_float) (by reference)
    POINTER(c_float),       # MSL2SWL_C - real(c_float) (by reference)
    POINTER(c_int),         # AeroProjMod_C - integer (by reference)
    POINTER(c_int),         # InterpOrder_C - integer (by reference)
    POINTER(c_double),      # DT_C - real(c_double) (by reference)
    POINTER(c_double),      # TMax_C - real(c_double) (by reference)
    POINTER(c_int),         # storeHHVel - integer flag (by reference)
    POINTER(c_int),         # TransposeDCM_in - integer flag (by reference)
    POINTER(c_int),         # WrVTK_in - integer (by reference)
    POINTER(c_int),         # WrVTK_inType - integer (by reference)
    POINTER(c_float),       # VTKNacDim_in - real(c_float) array (pointer)
    POINTER(c_float),       # VTKHubRad_in - real(c_float) (by reference)
    POINTER(c_int),         # wrOuts_C - integer (by reference)
    POINTER(c_double),      # DT_Outs_C - real(c_double) (by reference)
    POINTER(c_float),       # HubPos_C - real(c_float) array (pointer)
    POINTER(c_double),      # HubOri_C - real(c_double) array (pointer)
    POINTER(c_float),       # NacPos_C - real(c_float) array (pointer)
    POINTER(c_double),      # NacOri_C - real(c_double) array (pointer)
    POINTER(c_int),         # NumBlades_C - integer (by reference)
    POINTER(c_float),       # BldRootPos_C - real(c_float) array (pointer)
    POINTER(c_double),      # BldRootOri_C - real(c_double) array (pointer)
    POINTER(c_int),         # NumMeshPts_C - integer (by reference)
    POINTER(c_float),       # InitMeshPos_C - real(c_float) array (pointer)
    POINTER(c_double),      # InitMeshOri_C - real(c_double) array (pointer)
    POINTER(c_int),         # NumChannels_C - integer (by reference, output)
    POINTER(c_char),        # OutputChannelNames_C - fixed-length char buffer (by reference, output)
    POINTER(c_char),        # OutputChannelUnits_C - fixed-length char buffer (by reference, output)
    POINTER(c_int),         # ErrStat_C - integer (by reference, output)
    POINTER(c_char)         # ErrMsg_C - fixed-length char buffer (by reference, output)
]

# Initialize arguments

# Default fixed-length for strings (from template)
default_str_c_len = 1025

#------------------------------------------------------------------
# Flags for input file passing – use integers (1=True, 0=False)
ADinputFilePassed = c_int(0)      # e.g., 0 if not passing file contents
IfWinputFilePassed = c_int(0)       # same here

#------------------------------------------------------------------
# Input file strings – these will be built from your string arrays in adi_init.
# For now we initialize them as empty.
ADinputFileString = c_char_p(b"")
ADinputFileStringLength = c_int(0)

IfWinputFileString = c_char_p(b"")
IfWinputFileStringLength = c_int(0)

#------------------------------------------------------------------
# Output file name buffers – pad the string to default_str_c_len
OutRootName = create_string_buffer("TestOutput".ljust(default_str_c_len).encode('utf-8'), default_str_c_len)
OutVTKdir   = create_string_buffer("".ljust(default_str_c_len).encode('utf-8'), default_str_c_len)

#------------------------------------------------------------------
# Environmental parameters
gravity     = c_float(9.80665)      # gravitational acceleration (m/s^2)
defFldDens  = c_float(1.225)          # air density (kg/m^3)
defKinVisc  = c_float(1.464e-05)      # kinematic viscosity (m^2/s)
defSpdSound = c_float(335.0)          # speed of sound (m/s)
defPatm     = c_float(103500.0)       # atmospheric pressure (Pa)
defPvap     = c_float(1700.0)         # vapor pressure (Pa)
WtrDpth     = c_float(0.0)            # water depth (m)
MSL2SWL     = c_float(0.0)            # offset (m)

#------------------------------------------------------------------
# Other scalar parameters
AeroProjMod = c_int(1)
InterpOrder = c_int(1)              # default interpolation order: 1 (linear)
DT          = c_double(0.1)
TMax        = c_double(600.0)

# Flags and VTK parameters – using integers for flags
storeHHVel    = c_int(1)
TransposeDCM_in = c_int(1)
WrVTK_in      = c_int(0)
WrVTK_inType  = c_int(1)
WrVTK_DT      = c_double(0.0)

# VTKNacDim array – use the template defaults
VTKNacDim_in_np = np.array([-2.5, -2.5, 0, 10, 5, 5], dtype=np.float32)
VTKNacDim_in_ptr = VTKNacDim_in_np.ctypes.data_as(POINTER(c_float))
VTKHubRad_in = c_float(1.5)

wrOuts = c_int(0)
DT_Outs = c_double(0.0)

#------------------------------------------------------------------
# Hub and nacelle positions and orientations
HubPos_np = np.zeros(3, dtype=np.float32)
HubPos_ptr = HubPos_np.ctypes.data_as(POINTER(c_float))

HubOri_np = np.eye(3, dtype=np.float64).flatten()
HubOri_ptr = HubOri_np.ctypes.data_as(POINTER(c_double))

NacPos_np = np.zeros(3, dtype=np.float32)
NacPos_ptr = NacPos_np.ctypes.data_as(POINTER(c_float))

NacOri_np = np.eye(3, dtype=np.float64).flatten()
NacOri_ptr = NacOri_np.ctypes.data_as(POINTER(c_double))

#------------------------------------------------------------------
# Blade and mesh arrays
NumBlades = c_int(3)
NumMeshPts = c_int(5)

BldRootPos_np = np.zeros(3 * NumBlades.value, dtype=np.float32)
BldRootPos_ptr = BldRootPos_np.ctypes.data_as(POINTER(c_float))

BldRootOri_np = np.zeros(9 * NumBlades.value, dtype=np.float64)
BldRootOri_ptr = BldRootOri_np.ctypes.data_as(POINTER(c_double))

InitMeshPos_np = np.zeros(3 * NumMeshPts.value, dtype=np.float32)
InitMeshPos_ptr = InitMeshPos_np.ctypes.data_as(POINTER(c_float))

InitMeshOri_np=np.zeros(9*NumMeshPts.value, dtype=np.float64)
InitMeshOri_ptr = InitMeshOri_np.ctypes.data_as(POINTER(c_double))

#------------------------------------------------------------------
# OUTPUTS
NumChannels = c_int(0)
NumChannels_ptr = byref(NumChannels)

# Output channel names and units – using fixed buffer sizes (template uses 20*8000 bytes)
OutputChannelNames = create_string_buffer(20 * 8000)
OutputChannelUnits = create_string_buffer(20 * 8000)

ErrStat = c_int(0)
ErrStat_ptr = byref(ErrStat)

ErrMsg = create_string_buffer(1025)

# Call the function
print("Calling AeroDyn_Inflow_C_Init()...")
result = dll.AeroDyn_Inflow_C_Init(
    byref(ADinputFilePassed),             # POINTER(c_int): AD input file flag
    byref(ADinputFileString),             # POINTER(c_char_p): AD input file as string
    byref(ADinputFileStringLength),       # POINTER(c_int): AD input file string length
    byref(IfWinputFilePassed),            # POINTER(c_int): IfW input file flag
    byref(IfWinputFileString),            # POINTER(c_char_p): IfW input file as string
    byref(IfWinputFileStringLength),      # POINTER(c_int): IfW input file string length
    OutRootName,                          # POINTER(c_char): OutRootName buffer
    OutVTKdir,                            # POINTER(c_char): OutVTKdir buffer
    byref(gravity),                       # POINTER(c_float): gravity
    byref(defFldDens),                    # POINTER(c_float): defFldDens
    byref(defKinVisc),                    # POINTER(c_float): defKinVisc
    byref(defSpdSound),                   # POINTER(c_float): defSpdSound
    byref(defPatm),                       # POINTER(c_float): defPatm
    byref(defPvap),                       # POINTER(c_float): defPvap
    byref(WtrDpth),                       # POINTER(c_float): WtrDpth
    byref(MSL2SWL),                       # POINTER(c_float): MSL2SWL
    byref(AeroProjMod),                   # POINTER(c_int): AeroProjMod
    byref(InterpOrder),                   # POINTER(c_int): InterpOrder
    byref(DT),                            # POINTER(c_double): DT
    byref(TMax),                          # POINTER(c_double): TMax
    byref(storeHHVel),                    # POINTER(c_int): storeHHVel flag
    byref(TransposeDCM_in),               # POINTER(c_int): TransposeDCM_in flag
    byref(WrVTK_in),                      # POINTER(c_int): WrVTK_in
    byref(WrVTK_inType),                  # POINTER(c_int): WrVTK_inType
    VTKNacDim_in_ptr,                     # POINTER(c_float): VTKNacDim array
    byref(VTKHubRad_in),                  # POINTER(c_float): VTKHubRad
    byref(wrOuts),                        # POINTER(c_int): wrOuts flag
    byref(DT_Outs),                       # POINTER(c_double): DT_Outs
    HubPos_ptr,                           # POINTER(c_float): HubPos array
    HubOri_ptr,                           # POINTER(c_double): HubOri array
    NacPos_ptr,                           # POINTER(c_float): NacPos array
    NacOri_ptr,                           # POINTER(c_double): NacOri array
    byref(NumBlades),                     # POINTER(c_int): NumBlades
    BldRootPos_ptr,                       # POINTER(c_float): BldRootPos array
    BldRootOri_ptr,                       # POINTER(c_double): BldRootOri array
    byref(NumMeshPts),                    # POINTER(c_int): NumMeshPts
    InitMeshPos_ptr,                      # POINTER(c_float): InitMeshPos array
    InitMeshOri_ptr,                      # POINTER(c_double): InitMeshOri array
    byref(NumChannels),                   # POINTER(c_int): number of channels (output)
    OutputChannelNames,                   # POINTER(c_char): output channel names buffer
    OutputChannelUnits,                   # POINTER(c_char): output channel units buffer
    ErrStat_ptr,                          # POINTER(c_int): error status (output)
    ErrMsg                                # POINTER(c_char): error message buffer (output)
)


# Check results
print(f"ErrStat: {ErrStat.value}")
print(f"ErrMsg: {ErrMsg.value.decode()}")
