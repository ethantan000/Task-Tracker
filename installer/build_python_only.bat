@echo off
:: Build only the Python executables
:: Useful for quick testing or when Electron build is not needed

setlocal

set PYINSTALLER_DIR=%~dp0pyinstaller
set ROOT_DIR=%~dp0..

echo ========================================
echo Building Python Executables Only
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    exit /b 1
)

:: Install dependencies
echo Installing Python dependencies...
pip install pyinstaller
pip install -r "%ROOT_DIR%\api\requirements.txt"
pip install -r "%ROOT_DIR%\WorkMonitor\src\requirements.txt"
echo.

:: Build
cd /d "%PYINSTALLER_DIR%"

echo Building API Backend...
pyinstaller --clean api_backend.spec
if errorlevel 1 (
    echo ERROR: Failed to build API backend
    exit /b 1
)
echo.

echo Building Work Monitor...
pyinstaller --clean work_monitor.spec
if errorlevel 1 (
    echo ERROR: Failed to build Work Monitor
    exit /b 1
)
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executables created:
dir dist\*.exe
echo.
echo Location: %PYINSTALLER_DIR%\dist\
echo.

pause
