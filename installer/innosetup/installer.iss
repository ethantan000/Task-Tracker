; Task-Tracker Windows Installer Script (Inno Setup)
; Alternative to NSIS - simpler syntax, powerful features
;
; Requirements:
;   - Inno Setup 6.2 or later
;   - Python executables built with PyInstaller
;   - Electron build completed
;
; Build command:
;   iscc installer.iss

[Setup]
; Application info
AppName=Task-Tracker
AppVersion=2.0.0
AppVerName=Task-Tracker 2.0.0
AppPublisher=Task-Tracker
AppPublisherURL=https://github.com/ethantan000/Task-Tracker
AppSupportURL=https://github.com/ethantan000/Task-Tracker/issues
AppUpdatesURL=https://github.com/ethantan000/Task-Tracker/releases
DefaultDirName={autopf}\Task-Tracker
DefaultGroupName=Task-Tracker
AllowNoIcons=yes
LicenseFile=..\..\LICENSE.txt
InfoBeforeFile=..\..\README.md
OutputDir=output
OutputBaseFilename=TaskTracker-Setup-2.0.0
SetupIconFile=..\..\WorkMonitor\icon.ico
UninstallDisplayIcon={app}\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0.10240

; Uncomment to require restart after installation
;RestartIfNeededByRun=yes

; Version info
VersionInfoVersion=2.0.0.0
VersionInfoCompany=Task-Tracker
VersionInfoDescription=Task-Tracker Installation
VersionInfoCopyright=Copyright (C) 2026 Task-Tracker
VersionInfoProductName=Task-Tracker
VersionInfoProductVersion=2.0.0

; Disable unnecessary pages
DisableProgramGroupPage=no
DisableReadyPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full"; Description: "Full installation"
Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "main"; Description: "Task-Tracker Application (required)"; Types: full compact custom; Flags: fixed
Name: "shortcuts"; Description: "Desktop and Start Menu Shortcuts"; Types: full
Name: "shortcuts\desktop"; Description: "Desktop Shortcut"; Types: full
Name: "shortcuts\startmenu"; Description: "Start Menu Shortcuts"; Types: full compact
Name: "autostart"; Description: "Auto-start with Windows"; Types: full

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Components: shortcuts\desktop
Name: "quicklaunchicon"; Description: "Create a &Quick Launch icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Main Electron application
Source: "..\electron\dist\win-unpacked\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: main

; Python executables
Source: "..\pyinstaller\dist\TaskTrackerAPI.exe"; DestDir: "{app}\resources\bin"; Flags: ignoreversion; Components: main
Source: "..\pyinstaller\dist\TaskTrackerMonitor.exe"; DestDir: "{app}\resources\bin"; Flags: ignoreversion; Components: main

; Icon
Source: "..\..\WorkMonitor\icon.ico"; DestDir: "{app}"; Flags: ignoreversion; Components: main

; Documentation
Source: "..\..\README.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion isreadme; Components: main
Source: "..\..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: main

[Dirs]
; Create data directories with user write permissions
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\data\.cache"; Permissions: users-modify
Name: "{app}\data\.tmp"; Permissions: users-modify

[Icons]
; Start Menu shortcuts
Name: "{group}\Task-Tracker"; Filename: "{app}\Task-Tracker.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Comment: "Launch Task-Tracker Dashboard"; Components: shortcuts\startmenu
Name: "{group}\Work Monitor"; Filename: "{app}\resources\bin\TaskTrackerMonitor.exe"; WorkingDir: "{app}\resources\bin"; IconFilename: "{app}\icon.ico"; Comment: "Launch Work Monitor"; Components: shortcuts\startmenu
Name: "{group}\Uninstall Task-Tracker"; Filename: "{uninstallexe}"; Components: shortcuts\startmenu
Name: "{group}\README"; Filename: "{app}\README.txt"; Components: shortcuts\startmenu

; Desktop shortcut
Name: "{autodesktop}\Task-Tracker"; Filename: "{app}\Task-Tracker.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Task-Tracker"; Filename: "{app}\Task-Tracker.exe"; Tasks: quicklaunchicon

; Auto-start
Name: "{userstartup}\Task-Tracker"; Filename: "{app}\Task-Tracker.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Parameters: "--minimized"; Components: autostart

[Registry]
; Store installation path
Root: HKLM; Subkey: "Software\Task-Tracker"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Task-Tracker"; ValueType: string; ValueName: "Version"; ValueData: "2.0.0"

[Run]
; Optional: Run after installation
Filename: "{app}\Task-Tracker.exe"; Description: "Launch Task-Tracker Dashboard"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Stop running processes before uninstall
Filename: "{cmd}"; Parameters: "/c taskkill /F /IM ""Task-Tracker.exe"" /T"; Flags: runhidden; RunOnceId: "StopApp"
Filename: "{cmd}"; Parameters: "/c taskkill /F /IM ""TaskTrackerAPI.exe"" /T"; Flags: runhidden; RunOnceId: "StopAPI"
Filename: "{cmd}"; Parameters: "/c taskkill /F /IM ""TaskTrackerMonitor.exe"" /T"; Flags: runhidden; RunOnceId: "StopMonitor"

[UninstallDelete]
; Additional cleanup
Type: filesandordirs; Name: "{app}\resources"
Type: filesandordirs; Name: "{app}\locales"

[Code]
var
  DataDirPage: TInputOptionWizardPage;

{ Custom uninstall data directory handling }
procedure InitializeWizard;
begin
  { Custom pages can be added here if needed }
end;

function InitializeUninstall(): Boolean;
var
  Response: Integer;
begin
  Result := True;

  { Ask user about keeping data }
  Response := MsgBox('Do you want to keep your activity data and screenshots?' + #13#10 + #13#10 +
                     'Select "No" to delete all data (cannot be undone).',
                     mbConfirmation, MB_YESNO);

  if Response = IDNO then
  begin
    { Delete data directories }
    DelTree(ExpandConstant('{app}\data'), True, True, True);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    { Additional cleanup after uninstall }
    DeleteFile(ExpandConstant('{autodesktop}\Task-Tracker.lnk'));
    DeleteFile(ExpandConstant('{userstartup}\Task-Tracker.lnk'));
  end;
end;

{ Check if app is running }
function IsAppRunning(): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('tasklist', '/FI "IMAGENAME eq Task-Tracker.exe" /NH', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    { If tasklist finds the process, ResultCode will be 0 }
    Result := (ResultCode = 0);
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';

  { Check if application is running }
  if IsAppRunning() then
  begin
    Result := 'Task-Tracker is currently running. Please close it and try again.';
    Exit;
  end;

  { Additional pre-install checks can be added here }
end;

{ Check for minimum Windows version }
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  Result := True;
  GetWindowsVersionEx(Version);

  { Require Windows 10 or later }
  if (Version.Major < 10) then
  begin
    MsgBox('Task-Tracker requires Windows 10 or later.', mbError, MB_OK);
    Result := False;
  end;
end;
