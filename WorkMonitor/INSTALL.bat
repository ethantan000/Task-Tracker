@echo off
title Work Monitor - Installation
color 0A
cd /d "%~dp0"

echo ====================================================
echo       Work Monitor - Installation
echo ====================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Install from https://python.org
    echo Check "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo [OK] Python found!

:: Install packages
echo [*] Installing packages...
echo     - Pillow (PIL)
echo     - pystray
echo     - schedule
echo     - psutil
echo.
python -m pip install pillow pystray schedule psutil --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages
    pause
    exit /b 1
)
echo [OK] Packages installed!

:: Create directories
if not exist ".cache" mkdir .cache
if not exist ".tmp" mkdir .tmp
echo [OK] Directories ready!

echo.
echo ====================================================
echo       Installation Complete!
echo ====================================================
echo.
echo Admin password: admin123
echo.
echo Double-click START.bat to run the program.
echo.
pause
