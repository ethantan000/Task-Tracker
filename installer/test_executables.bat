@echo off
:: Quick test script for the built executables
:: Tests if they launch without errors

setlocal

set PYINSTALLER_DIR=%~dp0pyinstaller\dist
set ELECTRON_DIR=%~dp0electron\dist\win-unpacked

echo ========================================
echo Testing Built Executables
echo ========================================
echo.

:: Test API Backend
echo [1/3] Testing API Backend...
if not exist "%PYINSTALLER_DIR%\TaskTrackerAPI.exe" (
    echo ERROR: TaskTrackerAPI.exe not found
    goto end
)

echo Starting API server (will run for 5 seconds)...
start "API Test" "%PYINSTALLER_DIR%\TaskTrackerAPI.exe"
timeout /t 5 /nobreak >nul

:: Check if it's running
tasklist | findstr /i "TaskTrackerAPI.exe" >nul
if errorlevel 1 (
    echo WARNING: API server not running. Check logs for errors.
) else (
    echo SUCCESS: API server is running
    taskkill /F /IM TaskTrackerAPI.exe /T >nul 2>&1
)
echo.

:: Test Work Monitor
echo [2/3] Testing Work Monitor...
if not exist "%PYINSTALLER_DIR%\TaskTrackerMonitor.exe" (
    echo ERROR: TaskTrackerMonitor.exe not found
    goto end
)

echo Starting Work Monitor (will run for 5 seconds)...
start "Monitor Test" "%PYINSTALLER_DIR%\TaskTrackerMonitor.exe"
timeout /t 5 /nobreak >nul

:: Check if it's running
tasklist | findstr /i "TaskTrackerMonitor.exe" >nul
if errorlevel 1 (
    echo WARNING: Work Monitor not running. Check for GUI window.
) else (
    echo SUCCESS: Work Monitor is running
    taskkill /F /IM TaskTrackerMonitor.exe /T >nul 2>&1
)
echo.

:: Test Electron App
echo [3/3] Testing Electron Application...
if not exist "%ELECTRON_DIR%\Task-Tracker.exe" (
    echo WARNING: Electron app not found. May not be built yet.
    goto end
)

echo Starting Electron app (will run for 5 seconds)...
start "Electron Test" "%ELECTRON_DIR%\Task-Tracker.exe"
timeout /t 5 /nobreak >nul

tasklist | findstr /i "Task-Tracker.exe" >nul
if errorlevel 1 (
    echo WARNING: Electron app not running. Check for errors.
) else (
    echo SUCCESS: Electron app is running
    taskkill /F /IM Task-Tracker.exe /T >nul 2>&1
)
echo.

:end
echo ========================================
echo Test Complete
echo ========================================
echo.
echo Note: This is a basic launch test only.
echo For full testing, install the complete package
echo and verify all features manually.
echo.

pause
