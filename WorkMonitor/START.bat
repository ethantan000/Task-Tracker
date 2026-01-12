@echo off
title Work Monitor - Starting...
color 0A
cd /d "%~dp0"

echo ====================================================
echo       Work Monitor - Starting
echo ====================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

:: Check if required packages are installed
python -c "import PIL, pystray, psutil, schedule" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Required packages not found!
    echo Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

echo [*] Starting Work Monitor...
echo.
echo The application will run in system tray.
echo Right-click the tray icon to access settings.
echo.
echo Close this window to stop the monitor.
echo ====================================================
echo.

:: Run with python (not pythonw) so we can see error messages
python src\work_monitor.py

:: If we get here, the program exited
echo.
echo ====================================================
echo Work Monitor has stopped.
echo ====================================================
pause
