@echo off
:: Task-Tracker Complete Build Script for Windows
:: This script builds all components and creates the final installer
::
:: Requirements:
::   - Python 3.10+ with pip
::   - Node.js 18+ with npm
::   - PyInstaller: pip install pyinstaller
::   - NSIS 3.08+ OR Inno Setup 6.2+ installed and in PATH
::
:: Usage:
::   build_all.bat [nsis|inno|both]
::   Default: nsis

setlocal enabledelayedexpansion

:: Configuration
set INSTALLER_TYPE=%1
if "%INSTALLER_TYPE%"=="" set INSTALLER_TYPE=nsis

set ROOT_DIR=%~dp0..
set INSTALLER_DIR=%~dp0
set PYINSTALLER_DIR=%INSTALLER_DIR%pyinstaller
set ELECTRON_DIR=%INSTALLER_DIR%electron
set API_DIR=%ROOT_DIR%\api
set DASHBOARD_DIR=%ROOT_DIR%\dashboard
set WORKMONITOR_DIR=%ROOT_DIR%\WorkMonitor

echo ========================================
echo Task-Tracker Windows Installer Builder
echo ========================================
echo.
echo Root Directory: %ROOT_DIR%
echo Installer Type: %INSTALLER_TYPE%
echo.

:: Check Python
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    exit /b 1
)
python --version
echo.

:: Check Node.js
echo [2/7] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found in PATH
    exit /b 1
)
node --version
npm --version
echo.

:: Install PyInstaller
echo [3/7] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    exit /b 1
)
echo.

:: Build Python executables
echo [4/7] Building Python executables with PyInstaller...
cd /d "%PYINSTALLER_DIR%"

echo Building API Backend...
pyinstaller --clean api_backend.spec
if errorlevel 1 (
    echo ERROR: Failed to build API backend
    exit /b 1
)

echo Building Work Monitor...
pyinstaller --clean work_monitor.spec
if errorlevel 1 (
    echo ERROR: Failed to build Work Monitor
    exit /b 1
)

echo Python executables built successfully:
dir dist\*.exe
echo.

:: Build Next.js frontend
echo [5/7] Building Next.js dashboard...
cd /d "%DASHBOARD_DIR%"

echo Installing dashboard dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dashboard dependencies
    exit /b 1
)

echo Building dashboard...
call npm run build
if errorlevel 1 (
    echo ERROR: Failed to build dashboard
    exit /b 1
)

:: For Electron, we need to export as static if using static serving
:: Or keep it as a server bundle
echo.

:: Build Electron application
echo [6/7] Building Electron desktop application...
cd /d "%ELECTRON_DIR%"

echo Installing Electron dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install Electron dependencies
    exit /b 1
)

echo Building Electron app with electron-builder...
call npm run build
if errorlevel 1 (
    echo ERROR: Failed to build Electron app
    exit /b 1
)

echo Electron app built successfully
echo.

:: Create final installer
echo [7/7] Creating Windows installer...

if /i "%INSTALLER_TYPE%"=="nsis" goto build_nsis
if /i "%INSTALLER_TYPE%"=="inno" goto build_inno
if /i "%INSTALLER_TYPE%"=="both" goto build_both

:build_nsis
echo Building NSIS installer...
cd /d "%INSTALLER_DIR%\nsis"
makensis installer.nsi
if errorlevel 1 (
    echo WARNING: NSIS build failed or makensis not found
    echo Please install NSIS from https://nsis.sourceforge.io/
) else (
    echo NSIS installer created successfully
    dir TaskTracker-Setup-*.exe
)
if /i "%INSTALLER_TYPE%"=="both" goto build_inno_continue
goto end

:build_inno
echo Building Inno Setup installer...
cd /d "%INSTALLER_DIR%\innosetup"
iscc installer.iss
if errorlevel 1 (
    echo WARNING: Inno Setup build failed or iscc not found
    echo Please install Inno Setup from https://jrsoftware.org/isinfo.php
) else (
    echo Inno Setup installer created successfully
    dir output\TaskTracker-Setup-*.exe
)
goto end

:build_both
goto build_nsis

:build_inno_continue
echo.
echo Building Inno Setup installer...
cd /d "%INSTALLER_DIR%\innosetup"
iscc installer.iss
if errorlevel 1 (
    echo WARNING: Inno Setup build failed or iscc not found
) else (
    echo Inno Setup installer created successfully
    dir output\TaskTracker-Setup-*.exe
)

:end
echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Test the installer on a clean Windows machine
echo   2. Sign the executable with a code signing certificate
echo   3. Test antivirus compatibility
echo   4. Create release notes
echo.
echo Installers location:
echo   NSIS:       %INSTALLER_DIR%\nsis\
echo   Inno Setup: %INSTALLER_DIR%\innosetup\output\
echo   Electron:   %ELECTRON_DIR%\dist\
echo.

pause
