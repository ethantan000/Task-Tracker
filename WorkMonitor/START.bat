@echo off
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

:: Check if required packages are installed
python -c "import PIL, pystray, psutil, schedule" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Required packages not found!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

:: Launch Work Monitor in background using pythonw (windowless Python)
:: The application will run independently in system tray
start "" pythonw src\work_monitor.py

:: Exit immediately - the app now runs independently
exit
