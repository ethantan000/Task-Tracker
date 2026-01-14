# WorkMonitor Startup Guide

This guide explains how to install and start WorkMonitor on different operating systems.

---

## Quick Start by Platform

### **Windows Users**

1. **Install:**
   ```cmd
   INSTALL.bat
   ```

2. **Start:**
   ```cmd
   START.bat
   ```

### **Linux/macOS Users**

1. **Install:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. **Start:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

---

## Why START.bat Doesn't Work on Linux

**The Issue:**
- `START.bat` is a **Windows batch file** (`.bat` extension)
- Batch files use Windows-specific commands (`@echo off`, `start`, `pythonw`, etc.)
- Linux/macOS use **bash scripts** (`.sh` extension) with different syntax

**The Solution:**
- We've created equivalent **Linux/macOS scripts** (`install.sh`, `start.sh`)
- Use the appropriate script for your operating system

---

## Detailed Instructions

### Windows Installation

#### Step 1: Install Python
- Download from [python.org](https://python.org)
- **Important:** Check "Add Python to PATH" during installation

#### Step 2: Install WorkMonitor
```cmd
cd WorkMonitor
INSTALL.bat
```

This will:
- ✓ Check Python installation
- ✓ Install required packages (pillow, pystray, schedule, psutil)
- ✓ Create data directories (`.cache`, `.tmp`)

#### Step 3: Start WorkMonitor
```cmd
START.bat
```

This will:
- ✓ Check Python and packages
- ✓ Launch WorkMonitor in the background (system tray)
- ✓ Exit immediately (app runs independently)

---

### Linux/macOS Installation

#### Step 1: Install Python (if not already installed)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip
```

**macOS (with Homebrew):**
```bash
brew install python3
```

#### Step 2: Install WorkMonitor
```bash
cd WorkMonitor
chmod +x install.sh
./install.sh
```

This will:
- ✓ Check Python installation
- ✓ Install required packages
- ✓ Create data directories
- ✓ Make scripts executable

#### Step 3: Start WorkMonitor
```bash
./start.sh
```

This will:
- ✓ Check Python and packages
- ✓ Launch WorkMonitor in the background
- ✓ Show PID and status

**Note:** Requires a graphical environment (X11/Wayland). Won't work on headless servers.

---

## Troubleshooting

### Problem: "Python not found"

**Solution:**
- Make sure Python 3.7+ is installed
- On Linux: `python3 --version`
- On Windows: `python --version`
- If not installed, follow Step 1 above

---

### Problem: "Required packages not found"

**Solution:**
Run the install script again:
- Windows: `INSTALL.bat`
- Linux/macOS: `./install.sh`

Or manually install:
```bash
pip install pillow pystray schedule psutil
```

---

### Problem: START.bat does nothing on Linux

**Cause:** You're using a Windows batch file on Linux

**Solution:** Use the Linux script instead:
```bash
./start.sh
```

---

### Problem: "Permission denied" on Linux

**Cause:** Script is not executable

**Solution:**
```bash
chmod +x install.sh start.sh
./start.sh
```

---

### Problem: "No DISPLAY environment variable"

**Cause:** Running on a headless server or without GUI

**Solution:**
- WorkMonitor requires a graphical environment (uses tkinter GUI)
- Install on a desktop Linux system with X11 or Wayland
- Or use VNC/remote desktop to access GUI

---

### Problem: App crashes immediately

**Check the logs:**

**Windows:**
- Look in `.cache\app.log`

**Linux/macOS:**
```bash
tail -f .cache/app.log
```

Common issues:
- Missing DashboardServer (fixed in latest version)
- Missing icon.ico file
- Python package version conflicts

---

### Problem: "WorkMonitor is already running"

**Cause:** Another instance is running or stale lock file

**Solution:**

**Windows:**
```cmd
taskkill /F /IM pythonw.exe
del .cache\app.lock
START.bat
```

**Linux/macOS:**
```bash
pkill -f work_monitor.py
rm .cache/app.lock
./start.sh
```

---

## What's Changed (Recent Updates)

### ✅ Fixed: DashboardServer Removal

The old built-in dashboard server has been **removed** and replaced with:
- **FastAPI backend** in `/api` directory
- **Next.js dashboard** in `/dashboard` directory

**What this means:**
- WorkMonitor (the monitoring app) runs independently
- The web dashboard is now a separate service
- Much better performance and modern UI

**To use the new dashboard:**

1. **Start WorkMonitor** (as explained above)

2. **Start the API backend:**
   ```bash
   cd api
   pip install -r requirements.txt
   python main.py
   ```
   (Runs on http://localhost:8000)

3. **Start the Next.js dashboard:**
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```
   (Runs on http://localhost:3000)

---

## Default Credentials

**Admin Password:** `admin123`

⚠️ **Important:** Change this in the Admin Panel after first login!

---

## File Locations

```
WorkMonitor/
├── START.bat          # Windows startup script
├── INSTALL.bat        # Windows install script
├── start.sh           # Linux/macOS startup script
├── install.sh         # Linux/macOS install script
├── icon.ico           # Application icon
├── src/
│   ├── work_monitor.py      # Main application
│   ├── overlay_widget.py    # Overlay widget
│   └── email_reports.py     # Email reporting
├── .cache/            # Data storage (created automatically)
│   ├── d*.dat         # Daily activity logs
│   ├── sys.dat        # Configuration
│   ├── app.lock       # Lock file (prevents multiple instances)
│   └── app.log        # Application logs
└── .tmp/              # Screenshots (created automatically)
```

---

## System Requirements

### Windows
- Windows 7 or later (64-bit recommended)
- Python 3.7+
- 100MB disk space

### Linux
- Any modern Linux distribution with X11/Wayland
- Python 3.7+
- 100MB disk space
- Desktop environment (GNOME, KDE, XFCE, etc.)

### macOS
- macOS 10.13 or later
- Python 3.7+
- 100MB disk space

---

## Getting Help

If you encounter issues:

1. **Check the logs:** `.cache/app.log`
2. **Review this guide:** Common issues covered above
3. **Check Python version:** Must be 3.7+
4. **Reinstall packages:** Run install script again
5. **Open an issue:** [GitHub Issues](https://github.com/ethantan000/Task-Tracker/issues)

---

## Advanced Usage

### Running on Startup (Auto-start)

**Windows:**
1. Press `Win+R`, type `shell:startup`, press Enter
2. Create a shortcut to `START.bat` in the Startup folder

**Linux (systemd):**
Create `~/.config/systemd/user/workmonitor.service`:
```ini
[Unit]
Description=WorkMonitor Activity Tracker

[Service]
Type=simple
ExecStart=/path/to/WorkMonitor/start.sh
Restart=on-failure

[Install]
WantedBy=default.target
```

Then:
```bash
systemctl --user enable workmonitor
systemctl --user start workmonitor
```

**macOS (launchd):**
Create `~/Library/LaunchAgents/com.workmonitor.app.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.workmonitor.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/WorkMonitor/start.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.workmonitor.app.plist
```

---

## Summary

- ✅ **Windows:** Use `START.bat`
- ✅ **Linux/macOS:** Use `start.sh`
- ✅ **Always run install script first**
- ✅ **Dashboard is now a separate service** (FastAPI + Next.js)
- ✅ **Check logs if issues occur:** `.cache/app.log`

Happy monitoring! 🎯
