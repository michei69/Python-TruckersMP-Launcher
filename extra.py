import ctypes

WORD = ctypes.c_ushort
DWORD = ctypes.c_ulong
LPBYTE = ctypes.POINTER(ctypes.c_ubyte)
LPTSTR = ctypes.POINTER(ctypes.c_char)
HANDLE = ctypes.c_void_p
LPCTSTR = ctypes.POINTER(ctypes.c_char)
class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("nLength",                         DWORD),
                ("lpSecurityDescriptor",            ctypes.wintypes.LPVOID),
                ("bInheritHandle",                  ctypes.wintypes.BOOL)]
LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)
LPTHREAD_START_ROUTINE = ctypes.wintypes.LPVOID
class STARTUPINFO(ctypes.Structure):
    _fields_ = [
    ("cb", DWORD),
    ("lpReserved", LPTSTR),
    ("lpDesktop", LPTSTR),
    ("lpTitle", LPTSTR),
    ("dwX", DWORD),
    ("dwY", DWORD),
    ("dwXSize", DWORD),
    ("dwYSize", DWORD),
    ("dwXCountChars", DWORD),
    ("dwYCountChars", DWORD),
    ("dwFillAttribute",DWORD),
    ("dwFlags", DWORD),
    ("wShowWindow", WORD),
    ("cbReserved2", WORD),
    ("lpReserved2", LPBYTE),
    ("hStdInput", HANDLE),
    ("hStdOutput", HANDLE),
    ("hStdError", HANDLE),
    ]
    def __init__(self, **kwds):
        self.cb = ctypes.sizeof(self)
        super(STARTUPINFO, self).__init__(**kwds)

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
    ("hProcess", HANDLE),
    ("hThread", HANDLE),
    ("dwProcessId", DWORD),
    ("dwThreadId", DWORD),
    ]