# Task-Tracker Windows Installer

Complete guide to building a production-ready Windows installer for the Task-Tracker full-stack application.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Step-by-Step Guide](#step-by-step-guide)
5. [Directory Structure](#directory-structure)
6. [Testing](#testing)
7. [Code Signing](#code-signing)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Topics](#advanced-topics)

---

## Overview

This installer system packages the complete Task-Tracker application into a standalone Windows installer:

**Components:**
- **FastAPI Backend** → PyInstaller → `TaskTrackerAPI.exe`
- **Work Monitor** → PyInstaller → `TaskTrackerMonitor.exe`
- **Next.js Dashboard** → Electron → `Task-Tracker.exe` (Desktop app)
- **Final Package** → NSIS/Inno Setup → `TaskTracker-Setup-2.0.0.exe`

**What the installer does:**
- ✅ Installs all components to `C:\Program Files\Task-Tracker\`
- ✅ Creates Start Menu shortcuts
- ✅ Creates Desktop shortcut (optional)
- ✅ Sets up data directories (`data/.cache`, `data/.tmp`)
- ✅ Adds uninstaller to Control Panel
- ✅ Optional: Auto-start with Windows
- ✅ Handles clean uninstallation

---

## Prerequisites

### Required Software

1. **Python 3.10 or later**
   ```bash
   python --version
   # Should output: Python 3.10.x or later
   ```

2. **Node.js 18 or later** with npm
   ```bash
   node --version   # v18.0.0 or later
   npm --version    # 8.0.0 or later
   ```

3. **PyInstaller**
   ```bash
   pip install pyinstaller
   ```

4. **Choose ONE installer builder:**

   **Option A: NSIS (Recommended)**
   - Download from: https://nsis.sourceforge.io/
   - Install and add to PATH
   - Verify: `makensis /VERSION`

   **Option B: Inno Setup**
   - Download from: https://jrsoftware.org/isinfo.php
   - Install and add to PATH
   - Verify: `iscc /?`

### Python Dependencies

Install all Python dependencies:
```bash
pip install -r ../api/requirements.txt
pip install -r ../WorkMonitor/src/requirements.txt
```

### Node.js Dependencies

Install dashboard dependencies:
```bash
cd ../dashboard
npm install
```

---

## Quick Start

**One-command build:**

```batch
# Build everything and create NSIS installer
installer\build_all.bat nsis

# Or with Inno Setup
installer\build_all.bat inno

# Or build both
installer\build_all.bat both
```

This will:
1. ✓ Build Python executables (API + Monitor)
2. ✓ Build Next.js dashboard
3. ✓ Build Electron desktop app
4. ✓ Create Windows installer

**Output:**
- NSIS: `installer/nsis/TaskTracker-Setup-2.0.0.exe`
- Inno Setup: `installer/innosetup/output/TaskTracker-Setup-2.0.0.exe`

---

## Step-by-Step Guide

### Step 1: Build Python Executables

Navigate to the PyInstaller directory and build both executables:

```bash
cd installer/pyinstaller

# Build API Backend
pyinstaller --clean api_backend.spec

# Build Work Monitor
pyinstaller --clean work_monitor.spec
```

**Output:**
- `dist/TaskTrackerAPI.exe` - Backend server executable
- `dist/TaskTrackerMonitor.exe` - Monitoring app executable

**Verify:**
```bash
# Test API
.\dist\TaskTrackerAPI.exe
# Should start server on http://localhost:8000

# Test Monitor (opens GUI)
.\dist\TaskTrackerMonitor.exe
```

### Step 2: Build Next.js Dashboard

Build the production-ready Next.js application:

```bash
cd ../../dashboard

# Install dependencies (if not already done)
npm install

# Build for production
npm run build
```

**Output:**
- `.next/` - Production build
- `out/` - Exported static files (if using static export)

### Step 3: Build Electron Desktop App

Package the dashboard as a native Windows application:

```bash
cd ../installer/electron

# Install dependencies
npm install

# Build Electron app
npm run build
```

**What happens:**
1. Electron builder packages the app
2. Embeds Python executables (`TaskTrackerAPI.exe`, `TaskTrackerMonitor.exe`)
3. Creates `dist/win-unpacked/` with all files
4. May also create a basic NSIS installer (electron-builder default)

**Output:**
- `dist/win-unpacked/Task-Tracker.exe` - Main desktop app
- `dist/Task-Tracker Setup 2.0.0.exe` - Basic installer (electron-builder)

### Step 4: Create Final Installer

#### Option A: NSIS Installer

```bash
cd ../nsis
makensis installer.nsi
```

**Features:**
- Professional installer UI
- Component selection
- Custom pages
- Registry integration
- Full uninstaller

#### Option B: Inno Setup Installer

```bash
cd ../innosetup
iscc installer.iss
```

**Features:**
- Modern wizard-style UI
- Easier scripting
- Better Unicode support
- Built-in code signing support

**Output:**
- `TaskTracker-Setup-2.0.0.exe` - Final installer (50-100 MB)

### Step 5: Test the Installer

Run the test script:
```bash
cd ..
test_executables.bat
```

Or manually:
1. Run the installer on a clean Windows 10/11 machine
2. Test installation with different options
3. Verify shortcuts work
4. Test the application
5. Test uninstallation

---

## Directory Structure

```
installer/
├── README.md                      # This file
├── build_all.bat                  # Complete build script
├── build_python_only.bat          # Build Python executables only
├── test_executables.bat           # Test built executables
│
├── pyinstaller/                   # PyInstaller configurations
│   ├── api_backend.spec           # API backend spec
│   ├── work_monitor.spec          # Monitor spec
│   ├── version_api.txt            # Version info for API
│   ├── version_monitor.txt        # Version info for Monitor
│   └── dist/                      # Build output (created)
│       ├── TaskTrackerAPI.exe
│       └── TaskTrackerMonitor.exe
│
├── electron/                      # Electron wrapper
│   ├── package.json               # Electron config
│   ├── main.js                    # Main process
│   ├── preload.js                 # Preload script
│   ├── README.md                  # Electron docs
│   └── dist/                      # Build output (created)
│       └── win-unpacked/
│           └── Task-Tracker.exe
│
├── nsis/                          # NSIS installer
│   ├── installer.nsi              # NSIS script
│   └── TaskTracker-Setup-2.0.0.exe (created)
│
└── innosetup/                     # Inno Setup installer
    ├── installer.iss              # Inno Setup script
    └── output/
        └── TaskTracker-Setup-2.0.0.exe (created)
```

---

## Testing

### Basic Testing

1. **Test Python executables:**
   ```bash
   # API Backend
   cd installer/pyinstaller/dist
   TaskTrackerAPI.exe
   # Visit http://localhost:8000/docs

   # Work Monitor
   TaskTrackerMonitor.exe
   # Should show system tray icon
   ```

2. **Test Electron app:**
   ```bash
   cd installer/electron/dist/win-unpacked
   Task-Tracker.exe
   # Should start API and show dashboard
   ```

3. **Test installer:**
   - Run `TaskTracker-Setup-2.0.0.exe`
   - Try all installation options
   - Verify shortcuts
   - Launch the application
   - Check Control Panel > Programs
   - Test uninstaller

### Clean Machine Testing

**Critical:** Always test on a clean Windows machine without:
- Python installed
- Node.js installed
- Any development tools

**Recommended test environments:**
- Windows 10 (version 1809+)
- Windows 11
- Both 64-bit

**Test checklist:**
- [ ] Installer runs without admin errors
- [ ] All files install correctly
- [ ] Shortcuts work (Desktop, Start Menu)
- [ ] Application launches successfully
- [ ] API backend starts automatically
- [ ] Monitor can be launched
- [ ] Data is saved to correct location
- [ ] Uninstaller removes all files
- [ ] Uninstaller optionally keeps data

---

## Code Signing

### Why Sign Your Executable?

**Benefits:**
- ✅ Prevents "Unknown Publisher" warnings
- ✅ Improves user trust
- ✅ Reduces antivirus false positives
- ✅ Required for some enterprise deployments

### How to Sign

1. **Get a code signing certificate:**
   - Purchase from: DigiCert, Sectigo, GlobalSign
   - Cost: ~$200-400/year
   - Requires business verification

2. **Sign with SignTool (Windows SDK):**
   ```batch
   signtool sign /f "certificate.pfx" /p "password" /t http://timestamp.digicert.com "TaskTracker-Setup-2.0.0.exe"
   ```

3. **Verify signature:**
   ```batch
   signtool verify /pa "TaskTracker-Setup-2.0.0.exe"
   ```

### Free Alternative (Self-Signing)

**Note:** Self-signed certificates still show warnings but useful for testing.

```batch
# Create self-signed certificate (PowerShell as Admin)
$cert = New-SelfSignedCertificate -Subject "CN=Task-Tracker" -Type CodeSigning -CertStoreLocation Cert:\CurrentUser\My

# Export certificate
Export-Certificate -Cert $cert -FilePath TaskTracker.cer

# Sign
signtool sign /f TaskTracker.cer "TaskTracker-Setup-2.0.0.exe"
```

---

## Troubleshooting

### Issue: "Python not found"

**Cause:** Python not in PATH or not installed

**Solution:**
```bash
# Check Python
python --version

# If not found, install from python.org
# Make sure to check "Add Python to PATH" during installation
```

### Issue: "PyInstaller build fails"

**Common causes:**

1. **Missing dependencies:**
   ```bash
   pip install -r ../api/requirements.txt
   pip install -r ../WorkMonitor/src/requirements.txt
   pip install pyinstaller
   ```

2. **Hidden imports:**
   - Edit `.spec` file and add missing modules to `hiddenimports`

3. **File paths:**
   - Ensure all paths in `.spec` files are correct
   - Use relative paths from the spec file location

### Issue: "Electron build fails"

**Solutions:**

1. **Clean node_modules:**
   ```bash
   cd installer/electron
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check Node version:**
   ```bash
   node --version  # Must be 18+
   ```

3. **Missing Python executables:**
   - Build PyInstaller executables first
   - Verify they exist in `pyinstaller/dist/`

### Issue: "NSIS/Inno Setup not found"

**Solution:**
```batch
# Check if in PATH
makensis /VERSION
iscc /?

# If not found:
# 1. Install NSIS or Inno Setup
# 2. Add installation directory to system PATH
# 3. Restart command prompt
```

### Issue: "Installer shows 'Unknown Publisher' warning"

**Cause:** Executable not code-signed

**Solutions:**
1. Sign with a valid code signing certificate (recommended)
2. Users can bypass by clicking "More info" → "Run anyway"
3. For testing, disable SmartScreen temporarily

### Issue: "Antivirus flags executable as malware"

**Causes:**
- PyInstaller executables often flagged as false positives
- Unsigned executables are suspicious
- Packing/obfuscation techniques trigger heuristics

**Solutions:**
1. **Code sign the executable** (most effective)
2. Submit to antivirus vendors for whitelisting
3. Use VirusTotal to check detection rates
4. Add exception in antivirus software for testing

### Issue: "API doesn't start automatically"

**Debug steps:**

1. **Check if executable exists:**
   ```batch
   dir "C:\Program Files\Task-Tracker\resources\bin\TaskTrackerAPI.exe"
   ```

2. **Test manually:**
   ```batch
   cd "C:\Program Files\Task-Tracker\resources\bin"
   TaskTrackerAPI.exe
   ```

3. **Check Electron logs:**
   - Open DevTools in Electron app
   - Check console for errors

4. **Verify paths in `main.js`:**
   ```javascript
   const apiExePath = path.join(process.resourcesPath, 'bin', 'TaskTrackerAPI.exe');
   console.log('API path:', apiExePath);
   ```

---

## Advanced Topics

### Custom Branding

1. **Replace icon:**
   - Edit `WorkMonitor/icon.ico`
   - Use 256x256 PNG converted to ICO
   - Tools: GIMP, ImageMagick, online converters

2. **Installer splash screen:**
   - Create `installer/nsis/installer_banner.bmp` (164x314 pixels)
   - Update `MUI_WELCOMEFINISHPAGE_BITMAP` in `installer.nsi`

3. **Installer theme:**
   - NSIS: Use Modern UI macros and custom pages
   - Inno Setup: Use custom `WizardImageFile` and `WizardSmallImageFile`

### Silent Installation

**NSIS:**
```batch
TaskTracker-Setup-2.0.0.exe /S
```

**Inno Setup:**
```batch
TaskTracker-Setup-2.0.0.exe /VERYSILENT /SUPPRESSMSGBOXES
```

### Auto-Update Support

To add auto-update capability:

1. **Use Electron's autoUpdater:**
   ```javascript
   const { autoUpdater } = require('electron-updater');

   autoUpdater.checkForUpdatesAndNotify();
   ```

2. **Host updates:**
   - GitHub Releases (free)
   - AWS S3
   - Custom server

3. **Generate update manifests:**
   - electron-builder creates `latest.yml` automatically

### MSI Installer (Advanced)

For enterprise deployments, create an MSI:

1. **Use WiX Toolset:**
   - Download from: https://wixtoolset.org/
   - More complex but full Group Policy support

2. **Or use electron-builder with MSI target:**
   ```json
   "win": {
     "target": ["msi"]
   }
   ```

### Portable Version

Create a portable (no-install) version:

```batch
# With electron-builder
cd installer/electron
npm run build-portable
```

Output: Standalone executable that runs without installation.

---

## File Size Optimization

**Current size:** ~80-120 MB

**Optimization tips:**

1. **Exclude unnecessary files in PyInstaller:**
   ```python
   excludes=[
       'matplotlib',
       'numpy',  # If not used
       'pandas',
       'scipy',
   ]
   ```

2. **Use UPX compression:**
   ```python
   upx=True,
   upx_exclude=[],
   ```

3. **Electron optimization:**
   - Remove unused node_modules
   - Use `asar` archive
   - Exclude dev dependencies

4. **Split into multiple executables:**
   - Main installer: Core app only
   - Optional downloads: Monitor, additional features

---

## Checklist for Release

- [ ] All components build without errors
- [ ] Tested on clean Windows 10 machine
- [ ] Tested on clean Windows 11 machine
- [ ] All shortcuts work correctly
- [ ] Application launches without errors
- [ ] API backend starts automatically
- [ ] Monitor application works
- [ ] Data persists correctly
- [ ] Uninstaller removes all files
- [ ] Uninstaller offers to keep data
- [ ] Executable is code-signed
- [ ] Antivirus scan passes (VirusTotal)
- [ ] Version numbers are correct
- [ ] README and documentation included
- [ ] Release notes prepared
- [ ] Backup of unsigned executable kept

---

## Support

**Issues?**
- GitHub Issues: https://github.com/ethantan000/Task-Tracker/issues
- Check logs in: `C:\Program Files\Task-Tracker\data\.cache\work_monitor.log`

**Documentation:**
- Main README: `../README.md`
- Dashboard README: `../dashboard/README.md`
- API Docs: http://localhost:8000/docs

---

## License

Copyright © 2026 Task-Tracker

See `LICENSE.txt` for details.
