#!/bin/bash

###############################################################################
# WorkMonitor Startup Script (Linux/macOS)
#
# Usage: ./start.sh
#
# This script starts the WorkMonitor application in the background.
# The app will run in the system tray.
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  WorkMonitor - Starting"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python not found!"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${GREEN}[OK]${NC} Python found: $($PYTHON_CMD --version)"

# Check if required packages are installed
echo "[*] Checking required packages..."
$PYTHON_CMD -c "import PIL, pystray, psutil, schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Required packages not found!"
    echo "Please run: ./install.sh"
    echo "Or manually install: pip install pillow pystray schedule psutil"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} All packages installed"

# Create directories if they don't exist
mkdir -p .cache .tmp

# Check if already running
if [ -f ".cache/app.lock" ]; then
    PID=$(cat .cache/app.lock 2>/dev/null)
    if [ ! -z "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}[WARNING]${NC} WorkMonitor is already running (PID: $PID)"
        echo "If this is incorrect, delete .cache/app.lock and try again"
        exit 0
    else
        # Stale lock file, remove it
        rm -f .cache/app.lock
    fi
fi

# Launch Work Monitor
echo "[*] Starting WorkMonitor..."

# On Linux, we need an X display for tkinter
if [ -z "$DISPLAY" ]; then
    echo -e "${YELLOW}[WARNING]${NC} No DISPLAY environment variable set"
    echo "WorkMonitor requires a graphical environment (X11/Wayland)"
    echo "If you're running headless, this won't work"
fi

# Start in background
nohup $PYTHON_CMD src/work_monitor.py > .cache/app.log 2>&1 &
PID=$!

# Give it a moment to start
sleep 2

# Check if it's still running
if ps -p $PID > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} WorkMonitor started successfully (PID: $PID)"
    echo ""
    echo "The application is now running in the system tray."
    echo ""
    echo "To view logs: tail -f .cache/app.log"
    echo "To stop: pkill -f work_monitor.py"
    echo ""
else
    echo -e "${RED}[ERROR]${NC} Failed to start WorkMonitor"
    echo "Check .cache/app.log for details:"
    tail -20 .cache/app.log
    exit 1
fi

echo "=========================================="
