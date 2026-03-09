import ctypes
from ctypes import c_int, c_float, c_double, c_bool, c_char_p, CDLL, create_string_buffer
from openturbinecode.configs.pathing import PROJECT_ROOT

# Load the DLL using WinDLL for stdcall convention
dll_path = PROJECT_ROOT / "apps" / "AeroDyn.dll"
dll = CDLL(dll_path)

# Define the argument list for the minimal example
dll.AeroDyn_Inflow_C_Init.argtypes = [
    c_bool,                # ADinputFilePassed
    ctypes.c_void_p,       # ADinputFileString_C
    c_int,                 # ADinputFileStringLength_C
    c_bool,                # IfWinputFilePassed
    ctypes.c_void_p,       # IfWinputFileString_C
    c_int,                 # IfWinputFileStringLength_C
    c_char_p               # OutRootName_C
]

# Initialize the arguments
ADinputFilePassed = c_bool(False)
ADinputFileString = create_string_buffer(b"Test Input File", 1024)  # Ensure buffer size is non-zero
ADinputFileStringLength = c_int(len(ADinputFileString.value))
IfWinputFilePassed = c_bool(False)
IfWinputFileString = create_string_buffer(b"Test Wind Input File", 1024)  # Ensure buffer size is non-zero
IfWinputFileStringLength = c_int(len(IfWinputFileString.value))
OutRootName = b"TestOutput"

# Use byref to pass pointers explicitly for c_void_p arguments
print("Calling AeroDyn_Inflow_C_Init() with minimal arguments using WinDLL...")
dll.AeroDyn_Inflow_C_Init(
    ADinputFilePassed,
    ctypes.cast(ctypes.byref(ADinputFileString), ctypes.c_void_p),  # Explicit cast to c_void_p
    ADinputFileStringLength,
    IfWinputFilePassed,
    ctypes.cast(ctypes.byref(IfWinputFileString), ctypes.c_void_p),  # Explicit cast to c_void_p
    IfWinputFileStringLength,
    OutRootName
)
print("Call succeeded with minimal arguments using WinDLL.")
