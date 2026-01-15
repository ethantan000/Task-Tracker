; Task-Tracker Windows Installer Script (NSIS)
; Creates a professional Windows installer with full features
;
; Requirements:
;   - NSIS 3.08 or later
;   - Python executables built with PyInstaller
;   - Electron build completed
;
; Build command:
;   makensis installer.nsi

;--------------------------------
; Includes

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

;--------------------------------
; General Configuration

; Application info
!define APP_NAME "Task-Tracker"
!define APP_VERSION "2.0.0"
!define APP_PUBLISHER "Task-Tracker"
!define APP_DESCRIPTION "Employee Activity Tracking System"
!define APP_WEBSITE "https://github.com/ethantan000/Task-Tracker"

; Installer info
Name "${APP_NAME} ${APP_VERSION}"
OutFile "TaskTracker-Setup-${APP_VERSION}.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallPath"

; Request application privileges
RequestExecutionLevel admin

; Compression
SetCompressor /SOLID lzma
SetCompressorDictSize 32

; Version info
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_DESCRIPTION}"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "LegalCopyright" "Copyright © 2026 ${APP_PUBLISHER}"

;--------------------------------
; Interface Settings

!define MUI_ABORTWARNING
!define MUI_ICON "..\..\WorkMonitor\icon.ico"
!define MUI_UNICON "..\..\WorkMonitor\icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
!define MUI_WELCOMEFINISHPAGE_BITMAP "installer_banner.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "installer_banner.bmp"

; Finish page options
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_NAME}.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME} Dashboard"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Show README"
!define MUI_FINISHPAGE_LINK "Visit project website"
!define MUI_FINISHPAGE_LINK_LOCATION "${APP_WEBSITE}"

;--------------------------------
; Pages

; Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections

; Main application (required)
Section "Task-Tracker Application" SecMain
    SectionIn RO  ; Read-only (required)

    SetOutPath "$INSTDIR"

    ; Copy Electron app files
    File /r "..\electron\dist\win-unpacked\*.*"

    ; Copy Python executables
    SetOutPath "$INSTDIR\resources\bin"
    File "..\pyinstaller\dist\TaskTrackerAPI.exe"
    File "..\pyinstaller\dist\TaskTrackerMonitor.exe"

    ; Copy icon
    SetOutPath "$INSTDIR"
    File "..\..\WorkMonitor\icon.ico"

    ; Create data directories
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\data\.cache"
    CreateDirectory "$INSTDIR\data\.tmp"

    ; Copy documentation
    File "..\..\README.md"
    File "..\..\LICENSE.txt"
    Rename "$INSTDIR\README.md" "$INSTDIR\README.txt"

    ; Write installation info to registry
    WriteRegStr HKLM "Software\${APP_NAME}" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Add to Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "DisplayIcon" "$INSTDIR\icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "URLInfoAbout" "${APP_WEBSITE}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "NoRepair" 1

    ; Calculate and store installation size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "EstimatedSize" "$0"

SectionEnd

; Desktop shortcut (optional)
Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" \
                   "$INSTDIR\${APP_NAME}.exe" \
                   "" \
                   "$INSTDIR\icon.ico" \
                   0 \
                   SW_SHOWNORMAL \
                   "" \
                   "Launch ${APP_NAME} Dashboard"
SectionEnd

; Start Menu shortcuts (optional)
Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"

    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
                   "$INSTDIR\${APP_NAME}.exe" \
                   "" \
                   "$INSTDIR\icon.ico" \
                   0 \
                   SW_SHOWNORMAL \
                   "" \
                   "Launch ${APP_NAME} Dashboard"

    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Work Monitor.lnk" \
                   "$INSTDIR\resources\bin\TaskTrackerMonitor.exe" \
                   "" \
                   "$INSTDIR\icon.ico" \
                   0 \
                   SW_SHOWNORMAL \
                   "" \
                   "Launch Work Monitor"

    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" \
                   "$INSTDIR\Uninstall.exe" \
                   "" \
                   "" \
                   0 \
                   SW_SHOWNORMAL \
                   "" \
                   "Uninstall ${APP_NAME}"

    CreateShortcut "$SMPROGRAMS\${APP_NAME}\README.lnk" \
                   "$INSTDIR\README.txt" \
                   "" \
                   "" \
                   0 \
                   SW_SHOWNORMAL
SectionEnd

; Auto-start with Windows (optional)
Section /o "Auto-start with Windows" SecAutoStart
    CreateShortcut "$SMSTARTUP\${APP_NAME}.lnk" \
                   "$INSTDIR\${APP_NAME}.exe" \
                   "" \
                   "$INSTDIR\icon.ico" \
                   0 \
                   SW_SHOWMINIMIZED
SectionEnd

; Visual C++ Runtime (optional, if needed)
Section "Microsoft Visual C++ Runtime" SecVCRuntime
    ; Check if already installed
    ClearErrors
    ReadRegStr $0 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" "Installed"
    ${If} ${Errors}
        ; Not installed, include the redistributable
        ; Note: You'll need to download and include vcredist_x64.exe
        ; File "vcredist_x64.exe"
        ; ExecWait '"$INSTDIR\vcredist_x64.exe" /quiet /norestart'
        ; Delete "$INSTDIR\vcredist_x64.exe"

        DetailPrint "Visual C++ Runtime may be required. Please install manually if needed."
    ${Else}
        DetailPrint "Visual C++ Runtime already installed"
    ${EndIf}
SectionEnd

;--------------------------------
; Section Descriptions

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} \
        "Core application files (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} \
        "Creates a shortcut on the desktop"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} \
        "Creates shortcuts in the Start Menu"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecAutoStart} \
        "Automatically start ${APP_NAME} when Windows starts"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecVCRuntime} \
        "Install Microsoft Visual C++ Runtime (may be required)"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller Section

Section "Uninstall"
    ; Stop any running processes
    DetailPrint "Stopping running processes..."
    nsExec::ExecToLog 'taskkill /F /IM "${APP_NAME}.exe" /T'
    nsExec::ExecToLog 'taskkill /F /IM "TaskTrackerAPI.exe" /T'
    nsExec::ExecToLog 'taskkill /F /IM "TaskTrackerMonitor.exe" /T'
    Sleep 1000

    ; Remove files and directories
    RMDir /r "$INSTDIR\resources"
    RMDir /r "$INSTDIR\locales"
    Delete "$INSTDIR\*.*"

    ; Ask user if they want to keep data files
    MessageBox MB_YESNO|MB_ICONQUESTION \
        "Do you want to keep your activity data and screenshots?$\n$\n\
         Select 'No' to delete all data (cannot be undone)." \
        /SD IDYES IDYES KeepData

    ; Delete data if user chose to
    RMDir /r "$INSTDIR\data"

    KeepData:

    ; Remove installation directory if empty
    RMDir "$INSTDIR"

    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    Delete "$SMSTARTUP\${APP_NAME}.lnk"

    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"

    DetailPrint "Uninstallation complete"

SectionEnd

;--------------------------------
; Functions

; Check for existing installation
Function .onInit
    ; Check if already installed
    ReadRegStr $0 HKLM "Software\${APP_NAME}" "InstallPath"
    ${If} $0 != ""
        MessageBox MB_YESNO|MB_ICONQUESTION \
            "${APP_NAME} is already installed at:$\n$\n\
             $0$\n$\n\
             Do you want to uninstall the previous version?" \
            /SD IDYES IDYES Uninstall IDNO Cancel

        Uninstall:
            ExecWait '"$0\Uninstall.exe" /S _?=$0'
            Goto Continue

        Cancel:
            Abort

        Continue:
    ${EndIf}

    ; Check Windows version (require Windows 10 or later)
    ${If} ${AtLeastWin10}
        ; OK
    ${Else}
        MessageBox MB_OK|MB_ICONSTOP \
            "${APP_NAME} requires Windows 10 or later."
        Abort
    ${EndIf}
FunctionEnd

; Cleanup on installation abort
Function .onInstFailed
    DetailPrint "Installation failed. Cleaning up..."
FunctionEnd

; Post-installation tasks
Function .onInstSuccess
    DetailPrint "Installation completed successfully!"
FunctionEnd
