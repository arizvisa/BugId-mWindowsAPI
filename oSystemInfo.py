from .mDefines import MAX_PATH, PROCESSOR_ARCHITECTURE_AMD64, PROCESSOR_ARCHITECTURE_INTEL;
from .mDLLs import KERNEL32;
from .mFunctions import POINTER, WSTR;
from .mRegistry import cRegistryValue;
from .mTypes import SYSTEM_INFO;

def fsHKLMValue(sKeyName, sValueName):
  oRegistryValue = cRegistryValue.foGet(sHiveName = "HKLM", sKeyName = sKeyName, sValueName = sValueName);
  if not oRegistryValue:
    oRegistryValue = cRegistryValue.foGet(sHiveName = "HKLM", sKeyName = sKeyName, sValueName = sValueName, uRegistryBits = 64);
  assert oRegistryValue, \
      "Cannot read HKLM\%s\%s" % (sKeyName, sValueName);
  assert oRegistryValue.sTypeName == "REG_SZ", \
      r"Expected HKLM\%s\%s to be REG_SZ, got %s" % (sKeyName, sValueName, oRegistryValue.sType);
  return oRegistryValue.xValue;

class cSystemInfo(object):
  def __init__(oSelf):
    oSystemInfo = SYSTEM_INFO();
    KERNEL32.GetNativeSystemInfo(POINTER(oSystemInfo));
    oSelf.sOSISA = {
      PROCESSOR_ARCHITECTURE_INTEL: "x86",
      PROCESSOR_ARCHITECTURE_AMD64: "x64",
    }.get(oSystemInfo.wProcessorArchitecture);
    assert oSelf.sOSISA is not None, \
        "Unknown processor architecture 0x%X" % oSystemInfo.wProcessorArchitecture;
    oSelf.uPageSize = oSystemInfo.dwPageSize;
    oSelf.uMinimumApplicationAddress = oSystemInfo.lpMinimumApplicationAddress;
    oSelf.uMaximumApplicationAddress = oSystemInfo.lpMaximumApplicationAddress;
    oSelf.uNumberOfProcessors = oSystemInfo.dwNumberOfProcessors;
    oSelf.uAllocationAddressGranularity = oSystemInfo.dwAllocationGranularity;
    
    oSelf.__sOSName = None;
    oSelf.__sOSReleaseId = None;
    oSelf.__sOSBuild = None;
    oSelf.__sOSPath = None;
    oSelf.__sSystemName = None;
    oSelf.__sUniqueSystemId = None;
  
  @property
  def sOSName(oSelf):
    if not oSelf.__sOSName:
      oSelf.__sOSName = fsHKLMValue(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName");
    return oSelf.__sOSName;

  @property
  def sOSReleaseId(oSelf):
    if not oSelf.__sOSReleaseId:
      try:
        oSelf.__sOSReleaseId = fsHKLMValue(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ReleaseId");
      except AssertionError:
        oSelf.__sOSReleaseId = "0"
    return oSelf.__sOSReleaseId;
  @property
  def uReleaseId(oSelf):
    return long(oSelf.sOSReleaseId);

  @property
  def sOSBuild(oSelf):
    if not oSelf.__sOSBuild:
      oSelf.__sOSBuild = fsHKLMValue(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "CurrentBuild");
    return oSelf.__sOSBuild;
  @property
  def uOSBuild(oSelf):
    return long(oSelf.sOSBuild);
  
  @property
  def sOSPath(oSelf):
    if oSelf.__sOSPath is None:
      sBuffer = WSTR(MAX_PATH);
      uPathSize = KERNEL32.GetWindowsDirectoryW(sBuffer, MAX_PATH);
      uPathSize > 0 \
          or fThrowError("GetWindowsDirectoryW(..., 0x%X)" % (MAX_PATH,));
      oSelf.__sPath = sBuffer.value;
    return oSelf.__sPath;
  
  @property
  def sSystemName(oSelf):
    if not oSelf.__sSystemName:
      oSelf.__sSystemName = fsHKLMValue(r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName", "ComputerName");
    return oSelf.__sSystemName;
  
  @property
  def sUniqueSystemId(oSelf):
    if not oSelf.__sUniqueSystemId:
      oSelf.__sUniqueSystemId = fsHKLMValue(r"SOFTWARE\Microsoft\Cryptography", "MachineGuid");
    return oSelf.__sUniqueSystemId;
  
  @property
  def sOSVersion(oSelf):
    return "%s release %s, build %s %s in %s" % \
        (oSelf.sOSName, oSelf.sOSReleaseId, oSelf.sOSBuild, oSelf.sOSISA, oSelf.sOSPath);

oSystemInfo = cSystemInfo();