from .mDefines import *;
from .mFunctions import *;
from .mTypes import *;
from .mDLLs import KERNEL32;
from .fThrowError import fThrowError;

def fbIsProcessRunningForHandle(hProcess):
  uWaitForSingleObjectResult = KERNEL32.WaitForSingleObject(hProcess, 0);
  if uWaitForSingleObjectResult == WAIT_TIMEOUT:
    # If the process is running, waiting for it for 0 seconds will timeout.
    return True;
  if uWaitForSingleObjectResult == WAIT_OBJECT_0:
    # If the process is no longer running, waiting for it for 0 seconds will succeed.
    return False;
  fThrowError("WaitForSingleObject(0x%08X, 0) = 0x%08X" % (hProcess, uWaitForSingleObjectResult));
