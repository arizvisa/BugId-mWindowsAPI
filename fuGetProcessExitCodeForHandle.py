from .mDefines import STILL_ACTIVE;
from .mFunctions import POINTER;
from .mTypes import DWORD;
from .mDLLs import KERNEL32;
from .fbIsProcessRunningForHandle import fbIsProcessRunningForHandle;
from .fThrowError import fThrowError;

def fuGetProcessExitCodeForHandle(hProcess):
  dwExitCode = DWORD();
  KERNEL32.GetExitCodeProcess(hProcess, POINTER(dwExitCode)) \
      or fThrowError("GetExitCodeProcess(0x%08X, ...)" % (hProcess,));
  uExitCode = dwExitCode.value;
  if uExitCode == STILL_ACTIVE and fbIsProcessRunningForHandle(hProcess):
    # The process is still running.
    return None;
  return uExitCode;
