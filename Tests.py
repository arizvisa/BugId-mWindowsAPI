import os, sys, subprocess, threading, time;

sModuleFolderPath = os.path.dirname(os.path.abspath(__file__));
sBaseFolderPath = os.path.dirname(sModuleFolderPath);
sys.path.extend([
  sBaseFolderPath,
  sModuleFolderPath,
  os.path.join(sModuleFolderPath, "modules"),
]);

from mWindowsAPI import *;

if __name__ == "__main__":
  # Test registry access
  print "* Testing Registry access...";
  # cWindowsVersion uses foGetRegistryValue
  print "  Windows version: %s" %  oWindowsVersion;
  print "* Testing oSystemInfo...";
  # Test oSystemInfo
  print "  Windows ISA:     %s" % oSystemInfo.sOSISA;
  print "  Processors:      %d" % oSystemInfo.uNumberOfProcessors;
  print "  Address range:   0x%08X - 0x%08X" % (oSystemInfo.uMinimumApplicationAddress, oSystemInfo.uMaximumApplicationAddress);
  print "  Page size:       0x%X" % oSystemInfo.uPageSize;
  print "  Allocation granularity: 0x%X" % oSystemInfo.uAllocationAddressGranularity;
  
  # Test console functions
  print "* Testing KERNEL32 console functions...";
  hStdOut = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE);
  oConsoleScreenBufferInfo = CONSOLE_SCREEN_BUFFER_INFO();
  assert KERNEL32.GetConsoleScreenBufferInfo(hStdOut, PCONSOLE_SCREEN_BUFFER_INFO(oConsoleScreenBufferInfo)), \
      "GetConsoleScreenBufferInfo(0x%08X, ...) => Error 0x%08X" % \
      (hStdOut, KERNEL32.GetLastError());
  print "  Console buffer size (WxH): %d x %d" % (oConsoleScreenBufferInfo.dwSize.X, oConsoleScreenBufferInfo.dwSize.Y);
  print "  Console window size (WxH): %d x %d" % (oConsoleScreenBufferInfo.dwMaximumWindowSize.X, oConsoleScreenBufferInfo.dwMaximumWindowSize.Y);
  uOriginalColor = oConsoleScreenBufferInfo.wAttributes & 0xFF;
  uTestColor = (uOriginalColor & 0xF0) | 0x0A; # Bright green foreground, keep same background.
  assert KERNEL32.SetConsoleTextAttribute(hStdOut, uTestColor), \
      "SetConsoleTextAttribute(0x%08X, 0x%02X) => Error 0x%08X" % \
      (hStdOut, uTestColor, KERNEL32.GetLastError());
  print "  * This should be green.";
  assert KERNEL32.SetConsoleTextAttribute(hStdOut, uOriginalColor), \
      "SetConsoleTextAttribute(0x%08X, 0x%02X) => Error 0x%08X" % \
      (hStdOut, uOriginalColor, KERNEL32.GetLastError());
  
  print "* Testing process functions...";
  # Test process functions
  sTestApplicationPath = os.getenv("ComSpec");
  oTestProcess = subprocess.Popen(sTestApplicationPath);
  print "  + Started test process %d..." % oTestProcess.pid;
  try:
    print "  * Testing fSuspendProcessForId...";
    fSuspendProcessForId(oTestProcess.pid);
    # cProcessInformation
    print "  * Testing cProcessInformation...";
    oProcessInformation = cProcessInformation.foGetForId(oTestProcess.pid);
    print "    + ISA = %s" % repr(oProcessInformation.sISA);
    print "    + Binary start address = 0x%08X" % oProcessInformation.uBinaryStartAddress;
    print "    + Binary Path = %s" % repr(oProcessInformation.sBinaryPath);
    print "    + Command line = %s" % repr(oProcessInformation.sCommandLine);
    # cVirtualAllocation
    oBinaryVirtualAllocation = cVirtualAllocation(oTestProcess.pid, oProcessInformation.uBinaryStartAddress);
    assert oBinaryVirtualAllocation.bAllocated, \
        "Expected memory to be allocated at address 0x%08X" % oProcessInformation.uBinaryStartAddress;
    assert oBinaryVirtualAllocation.uStartAddress == oProcessInformation.uBinaryStartAddress, \
        "Expected binary virtual allocation to start at address 0x%08X, not 0x%08X" % \
          (oProcessInformation.uBinaryStartAddress, oBinaryVirtualAllocation.uStartAddress);
    print "    + There are 0x%X bytes of memory allocated at address 0x%08X." % \
        (oBinaryVirtualAllocation.uSize, oBinaryVirtualAllocation.uStartAddress);
    
    # fdsProcessesExecutableName_by_uId (make sure test process binary is included)
    print "  * Testing fdsProcessesExecutableName_by_uId...";
    dsProcessesExecutableName_by_uId = fdsProcessesExecutableName_by_uId();
    sProcessesExecutableName = dsProcessesExecutableName_by_uId.get(oTestProcess.pid);
    assert sProcessesExecutableName, \
        "Test process id %d/0x%X not found in process list!" % (oTestProcess.pid, oTestProcess.pid);
    assert sProcessesExecutableName.lower() == os.path.basename(sTestApplicationPath).lower(), \
        "Text process %d/0x%X is reported to run %s" % (oTestProcess.pid, sProcessesExecutableName);
    # fuGetProcessIntegrityLevelForId
    print "  * Testing fuGetProcessIntegrityLevelForId...";
    uProcessIntegrityLevel = fuGetProcessIntegrityLevelForId(oTestProcess.pid);
    assert uProcessIntegrityLevel is not None, \
        "Test process %d/0x%X integrity level could not be determined!" % (oTestProcess.pid, oTestProcess.pid);
    print "    + IntegrityLevel = 0x%X." % uProcessIntegrityLevel;
    # fuGetProcessMemoryUsage
    # cVirtualAllocation.foCreateInProcessForId()
    # cVirtualAllocation.fAllocate()
    # cVirtualAllocation.fFree()
    print "  * Testing Memory management functions...";
    uProcessMemoryUsage = fuGetProcessMemoryUsage(oTestProcess.pid);
    print "    + Memory usage = 0x%X." % uProcessMemoryUsage;
    uMemoryAllocationSize = 0x1230000;
    oVirtualAllocation = cVirtualAllocation.foCreateInProcessForId(oTestProcess.pid, uMemoryAllocationSize, bReserved = True);
    oVirtualAllocation.fDump();
    assert oVirtualAllocation is not None, \
        "Attempt to reserve 0x%X bytes failed" % uMemoryAllocationSize;
    assert oVirtualAllocation.uSize == uMemoryAllocationSize, \
        "Attempted to reserve 0x%X bytes, but got 0x%X" % (uMemoryAllocationSize, oVirtualAllocation.uSize);
    uProcessMemoryUsageAfterReservation = fuGetProcessMemoryUsage(oTestProcess.pid);
    print "    + Memory usage after reserving 0x%X bytes = 0x%X." % \
        (oVirtualAllocation.uSize, uProcessMemoryUsageAfterReservation);
    assert uProcessMemoryUsageAfterReservation >= uProcessMemoryUsage, \
        "Process memory usage was expected to be at least 0x%X after reservation, but is 0x%X" % \
        (uProcessMemoryUsage, uProcessMemoryUsageAfterReservation);
    oVirtualAllocation.fAllocate();
    oVirtualAllocation.fDump();
    uProcessMemoryUsageAfterAllocation = fuGetProcessMemoryUsage(oTestProcess.pid);
    print "    + Memory usage after allocating 0x%X bytes = 0x%X." % \
        (oVirtualAllocation.uSize, uProcessMemoryUsageAfterAllocation);
    assert uProcessMemoryUsageAfterAllocation >= uProcessMemoryUsageAfterReservation + uMemoryAllocationSize, \
        "Process memory usage was expected to be 0x%X after allocation, but is 0x%X" % \
        (uProcessMemoryUsage + uMemoryAllocationSize, uProcessMemoryUsageAfterAllocation);
    oVirtualAllocation.fFree();
    oVirtualAllocation.fDump();
    uProcessMemoryUsageAfterFree = fuGetProcessMemoryUsage(oTestProcess.pid);
    print "    + Memory usage after freeing memory = 0x%X." % uProcessMemoryUsageAfterFree;
    assert uProcessMemoryUsageAfterFree >= uProcessMemoryUsage, \
        "Process memory usage was expected to be at least 0x%X after free, but is 0x%X" % \
        (uProcessMemoryUsage, uProcessMemoryUsageAfterFree);

    # cJobObject
    print "  * Testing cJobObject...";
    oJobObject = cJobObject(oTestProcess.pid);
    oJobObject.fSetMaxTotalMemoryUse(uProcessMemoryUsageAfterFree + uMemoryAllocationSize / 2);
    oVirtualAllocation = cVirtualAllocation.foCreateInProcessForId(oTestProcess.pid, uMemoryAllocationSize);
    assert oVirtualAllocation is None, \
        "Attempt to allocate 0x%X bytes succeeded despite JobObject memory allocation limits" % uMemoryAllocationSize;
    print "    + JobObject memory limits applied correctly.";
    
    # fbTerminateProcessForId
    print "  * Testing fbTerminateProcessForId...";
    fbTerminateProcessForId(oTestProcess.pid);
    assert oTestProcess.poll() != None, \
        "Test process was not terminated!";
    # fdsProcessesExecutableName_by_uId (make sure test process is removed)
    assert oTestProcess.pid not in fdsProcessesExecutableName_by_uId(), \
        "Test process is still reported to exist after being terminated!?";
    print "  + Test process was terminated.";
    
    # TODO: add test for fbTerminateThreadForId, fDebugBreakProcessForId, fSuspendProcessForId, \
    # fuCreateThreadInProcessForIdAndAddress and fSendCtrlCToProcessForId.
    # This will require attaching a debugger to the process to determine a thread id, resume the application, or catch
    # the exceptions these functions throw.
    
    # cPipe
    print "* Testing cPipe...";
    def fTestPipe(oPipe):
      sWrittenBytes = "test\0test\x7f\x80\xff";
      oPipe.fWriteBytes(sWrittenBytes + "\n");
      sReadBytes = oPipe.fsReadLine();
      assert sReadBytes == sWrittenBytes, \
          "Expected %s, got %s" % (repr(sWrittenBytes), repr(sReadBytes));
      oPipe.fWriteBytes(sWrittenBytes + "\r\n");
      sReadBytes = oPipe.fsReadLine();
      assert sReadBytes == sWrittenBytes, \
          "Expected %s, got %s" % (repr(sWrittenBytes), repr(sReadBytes));
      oPipe.fWriteBytes(sWrittenBytes);
      oPipe.fClose(bInput = True);
      sReadBytes = oPipe.fsReadBytes(len(sWrittenBytes));
      assert sReadBytes == sWrittenBytes, \
          "Expected %s, got %s" % (repr(sWrittenBytes), repr(sReadBytes));
      sReadBytes = oPipe.fsReadBytes(len(sWrittenBytes));
      assert sReadBytes == "", \
          "Read %s after closing pipe for write" % repr(sReadBytes);
      oPipe.fClose();
      sReadBytes = oPipe.fsReadBytes(len(sWrittenBytes));
      assert sReadBytes == "", \
          "Read %s from a completely closed pipe" % repr(sReadBytes);
      try:
        oPipe.fWriteBytes("test");
      except IOError:
        pass;
      else:
        raise AssertionError("Should not be able to write to a closed pipe!");
    fTestPipe(cPipe());
    print "  * Testing cPipe with non-inheritable handles...";
    fTestPipe(cPipe(bInheritableInput = False, bInheritableOutput = False));
    # cConsoleProcess, fSuspendProcessForId
    print "* Testing cConsoleProcess...";
    sExpectedOutput = "Test";
    oConsoleProcess = cConsoleProcess.foCreateForBinaryPathAndArguments(
      os.environ.get("ComSpec"),
      ["/K", "ECHO %s&ECHO OFF" % sExpectedOutput],
    );
    sExpectedOutput += "\r\n";
    print "  * Reading process output...";
    sActualOutput = oConsoleProcess.oStdOutPipe.fsReadBytes(len(sExpectedOutput));
    assert sActualOutput == sExpectedOutput, \
        "Expected %s, got %s" % (repr(sExpectedOutput), repr(sActualOutput));
    # Suspend the process to test for a known issue: attempting to close handles on a
    # suspended process will hang until the process is resumed or killed.
    fSuspendProcessForId(oConsoleProcess.uId);
    def fPipeReadingThread():
      print "  * Reading end of console process output in thread...";
      sBytesRead = oConsoleProcess.oStdOutPipe.fsReadBytes();
      assert sBytesRead == "", \
          "Expected %s, got %s" % (repr(""), repr(sBytesRead));
    oReadThread = threading.Thread(target = fPipeReadingThread);
    oReadThread.start();
    def fKillProcessThread():
      time.sleep(1);
      print "  * Terminating console process...";
      fbTerminateProcessForId(oConsoleProcess.uId);
    oKillProcessThread = threading.Thread(target = fKillProcessThread);
    oKillProcessThread.start();
    print "  * Closing pipes...";
    # This will hang until the process is killed...
    oConsoleProcess.fClose();
    print "  * Waiting for kill process thread...";
    oKillProcessThread.join();
    print "  * Waiting for end of console process output in thread...";
    oReadThread.join();
    print "  * Reading end of output...";
    sReadBytes = oConsoleProcess.oStdOutPipe.fsReadBytes(1);
    assert sReadBytes == "", \
        "Read %s from a completely closed pipe" % repr(sReadBytes);
  except:
    oTestProcess.terminate();
    oTestProcess.wait();
    raise;
