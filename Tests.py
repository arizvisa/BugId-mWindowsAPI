import os, sys, subprocess;

sModuleFolderPath = os.path.dirname(os.path.abspath(__file__));
sBaseFolderPath = os.path.dirname(sModuleFolderPath);
sys.path.extend([
  sBaseFolderPath,
  sModuleFolderPath,
  os.path.join(sModuleFolderPath, "modules"),
]);

from mWindowsAPI import *;

if __name__ == "__main__":
  # Test console functions
  uTestColor = 0x0A; # Bright green
  hStdOut = KERNEL32.GetStdHandle(STD_OUTPUT_HANDLE);
  oConsoleScreenBufferInfo = CONSOLE_SCREEN_BUFFER_INFO();
  assert KERNEL32.GetConsoleScreenBufferInfo(hStdOut, PCONSOLE_SCREEN_BUFFER_INFO(oConsoleScreenBufferInfo)), \
      "GetConsoleScreenBufferInfo(0x%08X, ...) => Error 0x%08X" % \
      (hStdOut, KERNEL32.GetLastError());
  uOriginalColor = oConsoleScreenBufferInfo.wAttributes & 0xFF;
  assert KERNEL32.SetConsoleTextAttribute(hStdOut, uTestColor), \
      "SetConsoleTextAttribute(0x%08X, 0x%02X) => Error 0x%08X" % \
      (hStdOut, uTestColor, KERNEL32.GetLastError());
  print "This should be green";
  assert KERNEL32.SetConsoleTextAttribute(hStdOut, uOriginalColor), \
      "SetConsoleTextAttribute(0x%08X, 0x%02X) => Error 0x%08X" % \
      (hStdOut, uOriginalColor, KERNEL32.GetLastError());
  
  # Test process functions
  oNotepadProcess = subprocess.Popen("notepad.exe");
  print "* Started notepad process %d..." % oNotepadProcess.pid;
  # fdsProcessesExecutableName_by_uId (make sure notepad.exe is included)
  dsProcessesExecutableName_by_uId = fdsProcessesExecutableName_by_uId();
  sProcessesExecutableName = dsProcessesExecutableName_by_uId.get(oNotepadProcess.pid);
  assert sProcessesExecutableName, \
      "Notepad.exe process %d not found in process list!" % oNotepadProcess.pid;
  assert sProcessesExecutableName == "notepad.exe", \
      "Notepad.exe process %d is reported to run %s" % sProcessesExecutableName;
  # fuGetProcessIntegrityLevelForId
  uProcessIntegrityLevel = fuGetProcessIntegrityLevelForId(oNotepadProcess.pid);
  assert uProcessIntegrityLevel is not None, \
      "Notepad.exe process %d integrity level could not be determined!" % oNotepadProcess.pid;
  print "  + IntegrityLevel = 0x%X." % uProcessIntegrityLevel;
  # fbTerminateProcessForId
  fbTerminateProcessForId(oNotepadProcess.pid);
  assert oNotepadProcess.poll() != None, \
      "Notepad.exe was not terminated!";
  # fdsProcessesExecutableName_by_uId (make sure notepad.exe is removed)
  assert oNotepadProcess.pid not in fdsProcessesExecutableName_by_uId(), \
      "Notepad.exe is still reported to exist after being terminated!?";
  print "  + Terminated.";
