#!/bin/bash

###############################################################################
# WorkMonitor Installation Script (Linux/macOS)
#
# Usage: ./install.sh
#
# This script installs all required Python packages for WorkMonitor.
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  WorkMonitor - Installation"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python not found!"
    echo ""
    echo "Please install Python 3.7+ first:"
    echo "  • Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  • macOS: brew install python3"
    echo "  • Fedora: sudo dnf install python3"
    echo "  • Or download from: https://python.org"
    echo ""
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
PIP_CMD="pip3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo -e "${GREEN}[OK]${NC} Python found: $($PYTHON_CMD --version)"

# Check pip
if ! command -v $PIP_CMD &> /dev/null; then
    echo -e "${YELLOW}[WARNING]${NC} pip not found, attempting to install..."
    $PYTHON_CMD -m ensurepip --default-pip || {
        echo -e "${RED}[ERROR]${NC} Failed to install pip"
        echo "Please install pip manually:"
        echo "  • Ubuntu/Debian: sudo apt install python3-pip"
        echo "  • macOS: curl https://bootstrap.pypa.io/get-pip.py | python3"
        exit 1
    }
fi

echo -e "${GREEN}[OK]${NC} pip found: $($PIP_CMD --version)"

# Install required packages
echo ""
echo "[*] Installing required packages..."
echo "    • Pillow (PIL) - Image processing"
echo "    • pystray - System tray icon"
echo "    • schedule - Task scheduling"
echo "    • psutil - System monitoring"
echo ""

# Install packages
$PIP_CMD install --user pillow pystray schedule psutil

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}[OK]${NC} All packages installed successfully!"
else
    echo ""
    echo -e "${RED}[ERROR]${NC} Failed to install some packages"
    echo "Try running with sudo or checking your internet connection"
    exit 1
fi

# Create directories
echo ""
echo "[*] Creating data directories..."
mkdir -p .cache .tmp
echo -e "${GREEN}[OK]${NC} Directories created"

# Make scripts executable
chmod +x start.sh 2>/dev/null || true
echo -e "${GREEN}[OK]${NC} Scripts are executable"

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "Default admin password: admin123"
echo ""
echo "To start WorkMonitor:"
echo "  ./start.sh"
echo ""
echo "Note: This application requires a graphical environment (X11/Wayland)"
echo ""
