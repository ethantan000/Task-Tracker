# Task-Tracker Windows Installer - Complete Implementation Guide

**Comprehensive guide for converting the Task-Tracker GitHub repository into a professional Windows installer**

---

## 📋 Executive Summary

This document provides a complete solution for packaging the Task-Tracker full-stack application (Python backend + Next.js frontend + monitoring tool) into a professional Windows installer (`.exe` or `.msi`).

**What's Included:**
- ✅ PyInstaller configurations for Python components
- ✅ Electron wrapper for Next.js dashboard
- ✅ NSIS installer script (professional setup wizard)
- ✅ Inno Setup installer script (alternative)
- ✅ Automated build scripts
- ✅ Testing utilities
- ✅ Complete documentation

**End Result:** `TaskTracker-Setup-2.0.0.exe` - A standalone Windows installer (~80-120 MB) that installs everything users need to run Task-Tracker locally.

---

## 🏗️ Architecture Overview

### Application Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Final Installer Package                   │
│            TaskTracker-Setup-2.0.0.exe (NSIS)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─► Installs to: C:\Program Files\Task-Tracker\
                              ├─► Creates shortcuts (Desktop + Start Menu)
                              ├─► Registers in Control Panel
                              └─► Sets up data directories
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
┌───────────────────┐      ┌───────────────────────┐    ┌─────────────────────┐
│  Task-Tracker.exe │      │  TaskTrackerAPI.exe   │    │TaskTrackerMonitor.exe│
│   (Electron App)  │      │   (FastAPI Backend)   │    │  (Work Monitor)     │
│                   │      │                       │    │                     │
│ - Chromium Browser│◄─────│ - REST API            │    │ - Activity tracking │
│ - Main window     │ HTTP │ - WebSocket server    │    │ - Screenshots       │
│ - Auto-starts API │ 8000 │ - Reads .dat files    │    │ - System tray       │
│ - System tray     │      │ - Serves screenshots  │    │ - Data logging      │
└───────────────────┘      └───────────────────────┘    └─────────────────────┘
        │                              │                              │
        └──────────────────────────────┴──────────────────────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │      Data Storage (.dat)      │
                        │ C:\Program Files\Task-Tracker│
                        │           \data\.cache\       │
                        │           \data\.tmp\         │
                        └──────────────────────────────┘
```

### Build Pipeline

```
Step 1: PyInstaller           Step 2: Electron          Step 3: NSIS/Inno Setup
═══════════════════           ═══════════════           ════════════════════════

api/main.py                   Next.js Dashboard         Electron App
    │                              │                         │
    ▼                              ▼                         ▼
[PyInstaller]                 [npm build]              [electron-builder]
    │                              │                         │
    ▼                              ▼                         ▼
TaskTrackerAPI.exe        .next/ (build)           Task-Tracker.exe
                                                            │
WorkMonitor/                                               │
work_monitor.py                                            ▼
    │                                              ┌─────────────────┐
    ▼                                              │  Final Installer │
[PyInstaller]                                      │   [NSIS/Inno]    │
    │                                              │        │         │
    ▼                                              │        ▼         │
TaskTrackerMonitor.exe  ─────────────────────────►│ TaskTracker-    │
                                                   │ Setup-2.0.0.exe │
                                                   └─────────────────┘
```

---

## 📂 Complete File Structure

After implementation, your repository will have:

```
Task-Tracker/
├── installer/                              # NEW - All installer files
│   ├── README.md                           # Main installer documentation
│   ├── QUICK_START.md                      # 5-minute quickstart guide
│   ├── TROUBLESHOOTING.md                  # Detailed troubleshooting
│   ├── WINDOWS_INSTALLER_COMPLETE_GUIDE.md # This file
│   │
│   ├── build_all.bat                       # Main build script (automated)
│   ├── build_python_only.bat               # Build Python executables only
│   ├── test_executables.bat                # Test built executables
│   │
│   ├── pyinstaller/                        # Python → EXE configs
│   │   ├── api_backend.spec                # API backend PyInstaller spec
│   │   ├── work_monitor.spec               # Monitor PyInstaller spec
│   │   ├── version_api.txt                 # Version info for API
│   │   ├── version_monitor.txt             # Version info for Monitor
│   │   └── dist/                           # Output (created during build)
│   │       ├── TaskTrackerAPI.exe          # ← Built API executable
│   │       └── TaskTrackerMonitor.exe      # ← Built Monitor executable
│   │
│   ├── electron/                           # Next.js → Desktop app
│   │   ├── package.json                    # Electron config + dependencies
│   │   ├── main.js                         # Electron main process (app logic)
│   │   ├── preload.js                      # Preload script (security)
│   │   ├── README.md                       # Electron-specific docs
│   │   └── dist/                           # Output (created during build)
│   │       └── win-unpacked/               # Unpacked Electron app
│   │           └── Task-Tracker.exe        # ← Main desktop app
│   │
│   ├── nsis/                               # NSIS installer (recommended)
│   │   ├── installer.nsi                   # NSIS installer script
│   │   └── TaskTracker-Setup-2.0.0.exe     # ← Final installer (created)
│   │
│   └── innosetup/                          # Inno Setup installer (alternative)
│       ├── installer.iss                   # Inno Setup script
│       └── output/
│           └── TaskTracker-Setup-2.0.0.exe # ← Final installer (created)
│
├── api/                                    # Existing - FastAPI backend
│   ├── main.py                             # Entry point for API
│   └── requirements.txt                    # Python dependencies
│
├── dashboard/                              # Existing - Next.js frontend
│   ├── app/                                # Next.js pages
│   ├── components/                         # React components
│   ├── package.json                        # Node dependencies
│   └── .next/                              # Build output (created)
│
├── WorkMonitor/                            # Existing - Monitoring app
│   ├── src/
│   │   ├── work_monitor.py                 # Entry point for monitor
│   │   ├── email_reports.py                # Email functionality
│   │   └── overlay_widget.py               # Overlay widget
│   ├── icon.ico                            # Application icon
│   └── .cache/                             # Data storage (runtime)
│
├── LICENSE.txt                             # License file
└── README.md                               # Main project README
```

---

## 🚀 Implementation Steps

### Step 1: Repository Setup (5 minutes)

```batch
# Clone the repository
git clone https://github.com/ethantan000/Task-Tracker
cd Task-Tracker

# Create installer directory (if you're setting this up manually)
# (Already created if you're following this guide)
mkdir installer
cd installer
```

### Step 2: Install Prerequisites (10 minutes)

**Required software:**

1. **Python 3.10+**
   ```batch
   # Download from: https://www.python.org/downloads/
   # During installation, check "Add Python to PATH"

   # Verify
   python --version
   pip --version
   ```

2. **Node.js 18+**
   ```batch
   # Download from: https://nodejs.org/
   # Install LTS version

   # Verify
   node --version
   npm --version
   ```

3. **PyInstaller**
   ```batch
   pip install pyinstaller
   ```

4. **NSIS (or Inno Setup)**

   **Option A: NSIS (Recommended)**
   ```batch
   # Download from: https://nsis.sourceforge.io/Download
   # Install and add to PATH

   # Or with Chocolatey:
   choco install nsis

   # Verify
   makensis /VERSION
   ```

   **Option B: Inno Setup**
   ```batch
   # Download from: https://jrsoftware.org/isdl.php
   # Install and add to PATH

   # Verify
   iscc /?
   ```

### Step 3: Automated Build (10 minutes)

**The easy way - one command builds everything:**

```batch
cd installer
build_all.bat nsis
```

This script will:
1. ✓ Install Python dependencies
2. ✓ Build API backend with PyInstaller → `TaskTrackerAPI.exe`
3. ✓ Build Work Monitor with PyInstaller → `TaskTrackerMonitor.exe`
4. ✓ Install Node dependencies
5. ✓ Build Next.js dashboard → `.next/`
6. ✓ Build Electron desktop app → `Task-Tracker.exe`
7. ✓ Create NSIS installer → `TaskTracker-Setup-2.0.0.exe`

**Output locations:**
- Python EXEs: `installer/pyinstaller/dist/`
- Electron app: `installer/electron/dist/win-unpacked/`
- **Final installer: `installer/nsis/TaskTracker-Setup-2.0.0.exe`** ← This is what you distribute!

### Step 4: Manual Build (Alternative)

If you prefer to build components individually:

**4a. Build Python Executables**
```batch
cd installer/pyinstaller

# API Backend
pyinstaller --clean api_backend.spec

# Work Monitor
pyinstaller --clean work_monitor.spec

# Check output
dir dist\*.exe
```

**4b. Build Next.js Dashboard**
```batch
cd ../../dashboard

# Install dependencies
npm install

# Build production version
npm run build
```

**4c. Build Electron Desktop App**
```batch
cd ../installer/electron

# Install dependencies
npm install

# Build for Windows
npm run build
```

**4d. Create Installer**

**With NSIS:**
```batch
cd ../nsis
makensis installer.nsi
```

**With Inno Setup:**
```batch
cd ../innosetup
iscc installer.iss
```

### Step 5: Test the Installer (5 minutes)

**Quick test:**
```batch
cd installer
test_executables.bat
```

**Full test (recommended):**
1. Copy `TaskTracker-Setup-2.0.0.exe` to a clean Windows 10/11 machine
2. Run the installer
3. Choose installation options
4. Launch Task-Tracker from Start Menu
5. Verify dashboard loads
6. Verify API is responding at http://localhost:8000
7. Test Work Monitor (from Start Menu)
8. Test uninstallation

---

## 🎯 Key Features Implemented

### PyInstaller Specifications

**API Backend (`api_backend.spec`):**
- ✅ Bundles FastAPI + Uvicorn
- ✅ Includes all WebSocket dependencies
- ✅ Embeds required data files
- ✅ Console mode for logging
- ✅ Custom icon and version info
- ✅ Optimized with UPX compression
- ✅ Excludes unnecessary packages (matplotlib, numpy)

**Work Monitor (`work_monitor.spec`):**
- ✅ Bundles tkinter GUI
- ✅ Includes PIL, pystray, psutil
- ✅ Embeds icon and helper modules
- ✅ Windowed mode (no console)
- ✅ Custom icon and version info
- ✅ Optimized size

### Electron Wrapper

**Main Process (`main.js`):**
- ✅ Manages application lifecycle
- ✅ Auto-starts API backend
- ✅ Creates main window with dashboard
- ✅ System tray integration
- ✅ Optional Work Monitor launcher
- ✅ Automatic data directory creation
- ✅ Development/production mode handling
- ✅ Graceful shutdown

**Preload Script (`preload.js`):**
- ✅ Secure IPC bridge
- ✅ Exposes only necessary APIs
- ✅ Context isolation

**Package Configuration (`package.json`):**
- ✅ Electron-builder setup
- ✅ Windows-specific settings
- ✅ Embeds Python executables
- ✅ NSIS configuration
- ✅ Icon and version info

### NSIS Installer

**Features:**
- ✅ Professional Modern UI
- ✅ License agreement page
- ✅ Component selection
- ✅ Custom installation directory
- ✅ Desktop shortcut (optional)
- ✅ Start Menu shortcuts
- ✅ Auto-start with Windows (optional)
- ✅ Creates data directories with proper permissions
- ✅ Registry integration
- ✅ Add/Remove Programs entry
- ✅ Full uninstaller with data preservation option
- ✅ Checks for existing installation
- ✅ Validates Windows version
- ✅ Stops running processes before install/uninstall

### Inno Setup Installer

**Features (alternative to NSIS):**
- ✅ Modern wizard UI
- ✅ Similar features to NSIS
- ✅ Easier scripting syntax
- ✅ Better Unicode support
- ✅ Built-in code signing support
- ✅ Pascal scripting for advanced logic
- ✅ Custom uninstall logic

---

## 📦 What Gets Installed

When users run `TaskTracker-Setup-2.0.0.exe`:

### File Structure
```
C:\Program Files\Task-Tracker\
├── Task-Tracker.exe              # Main application (Electron)
├── icon.ico                       # Application icon
├── README.txt                     # Documentation
├── LICENSE.txt                    # License
├── Uninstall.exe                  # Uninstaller
│
├── resources\                     # Electron resources
│   ├── app.asar                   # Packaged app
│   └── bin\                       # Python executables
│       ├── TaskTrackerAPI.exe     # Backend server
│       └── TaskTrackerMonitor.exe # Monitoring tool
│
├── locales\                       # Electron locales
├── swiftshader\                   # GPU emulation
│
└── data\                          # User data
    ├── .cache\                    # Activity logs (.dat files)
    └── .tmp\                      # Screenshots (.png files)
```

### Registry Keys
```
HKLM\Software\Task-Tracker\
├── InstallPath = "C:\Program Files\Task-Tracker"
└── Version = "2.0.0"

HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Task-Tracker\
├── DisplayName = "Task-Tracker"
├── DisplayVersion = "2.0.0"
├── Publisher = "Task-Tracker"
├── UninstallString = "C:\Program Files\Task-Tracker\Uninstall.exe"
└── EstimatedSize = [calculated]
```

### Shortcuts Created
```
Desktop\
└── Task-Tracker.lnk (optional)

Start Menu\Programs\Task-Tracker\
├── Task-Tracker.lnk
├── Work Monitor.lnk
├── README.lnk
└── Uninstall Task-Tracker.lnk

Startup\ (optional)
└── Task-Tracker.lnk (auto-start)
```

---

## 🧪 Testing Checklist

### Pre-Distribution Testing

- [ ] **Build succeeds without errors**
  - [ ] PyInstaller builds complete
  - [ ] Electron build completes
  - [ ] Installer creation succeeds

- [ ] **Executables work standalone**
  - [ ] TaskTrackerAPI.exe starts and responds
  - [ ] TaskTrackerMonitor.exe launches GUI
  - [ ] Task-Tracker.exe opens dashboard

- [ ] **Installer testing**
  - [ ] Runs without admin errors
  - [ ] All options work (custom dir, shortcuts, etc.)
  - [ ] Files install correctly
  - [ ] Registry keys created
  - [ ] Shortcuts work

- [ ] **Application testing**
  - [ ] Dashboard loads correctly
  - [ ] API responds at localhost:8000
  - [ ] Real-time updates work (WebSocket)
  - [ ] Screenshots display
  - [ ] Monitor tracks activity
  - [ ] Data persists correctly

- [ ] **Uninstaller testing**
  - [ ] Removes all files
  - [ ] Offers to keep data
  - [ ] Cleans up registry
  - [ ] Removes shortcuts

- [ ] **Security testing**
  - [ ] VirusTotal scan (antivirus check)
  - [ ] SmartScreen status
  - [ ] Firewall compatibility

- [ ] **Clean machine testing**
  - [ ] Windows 10 (version 1809+)
  - [ ] Windows 11
  - [ ] Without Python installed
  - [ ] Without Node.js installed
  - [ ] Without admin rights (if possible)

---

## 🔒 Code Signing (Recommended)

### Why Sign?

**Unsigned installer:**
```
⚠️ Windows protected your PC
   Windows Defender SmartScreen prevented an unrecognized app
   Publisher: Unknown Publisher
```

**Signed installer:**
```
✓ Do you want to allow this app to make changes?
  Publisher: Task-Tracker (Verified)
  [Yes] [No]
```

### How to Sign

1. **Get a code signing certificate ($200-400/year)**
   - DigiCert: https://www.digicert.com/code-signing/
   - Sectigo: https://sectigo.com/ssl-certificates-tls/code-signing
   - GlobalSign: https://www.globalsign.com/en/code-signing-certificate

2. **Install Windows SDK (includes SignTool)**
   ```batch
   # Download from: https://developer.microsoft.com/windows/downloads/windows-sdk/
   ```

3. **Sign the installer**
   ```batch
   signtool sign ^
     /f "path\to\certificate.pfx" ^
     /p "certificate_password" ^
     /t http://timestamp.digicert.com ^
     /fd sha256 ^
     /d "Task-Tracker" ^
     "TaskTracker-Setup-2.0.0.exe"
   ```

4. **Verify signature**
   ```batch
   signtool verify /pa "TaskTracker-Setup-2.0.0.exe"

   # Or right-click file → Properties → Digital Signatures
   ```

### Alternative: Self-Signing (Testing Only)

```powershell
# Create self-signed cert (PowerShell as Admin)
$cert = New-SelfSignedCertificate `
    -Subject "CN=Task-Tracker" `
    -Type CodeSigning `
    -CertStoreLocation Cert:\CurrentUser\My

# Export certificate
$password = ConvertTo-SecureString -String "password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath TaskTracker.pfx -Password $password

# Sign
signtool sign /f TaskTracker.pfx /p password TaskTracker-Setup-2.0.0.exe
```

**Note:** Self-signed certificates still show warnings but useful for internal testing.

---

## 🛠️ Customization

### Change Application Icon

1. Replace `WorkMonitor/icon.ico` with your icon
2. Rebuild all components
3. Icon will be used for:
   - Executables
   - Installer
   - Shortcuts
   - System tray

### Change Application Name

1. **In PyInstaller specs** (`api_backend.spec`, `work_monitor.spec`):
   ```python
   name='YourAppName',
   ```

2. **In Electron** (`package.json`):
   ```json
   "productName": "Your App Name",
   "build": {
     "appId": "com.yourcompany.yourapp"
   }
   ```

3. **In NSIS** (`installer.nsi`):
   ```nsis
   !define APP_NAME "Your App Name"
   ```

4. **In Inno Setup** (`installer.iss`):
   ```ini
   AppName=Your App Name
   ```

### Change Installation Directory

**NSIS:**
```nsis
InstallDir "$PROGRAMFILES64\YourAppName"
```

**Inno Setup:**
```ini
DefaultDirName={autopf}\YourAppName
```

### Add Custom Installer Pages

**NSIS example:**
```nsis
Page custom CustomPageFunction
```

**Inno Setup example:**
```pascal
[Code]
procedure InitializeWizard;
begin
  // Add custom page here
end;
```

### Change Data Directory Location

**Recommended:** Use AppData instead of Program Files:

Edit `installer/electron/main.js`:
```javascript
const dataDirPath = path.join(app.getPath('appData'), 'Task-Tracker', 'data');
const screenshotsDirPath = path.join(app.getPath('appData'), 'Task-Tracker', 'screenshots');
```

This avoids permission issues on Windows.

---

## 📊 Troubleshooting Common Issues

See `TROUBLESHOOTING.md` for detailed solutions. Quick fixes:

### Build fails
```batch
# Clean everything and rebuild
cd installer/pyinstaller
rmdir /s /q build dist
cd ..\electron
rmdir /s /q dist node_modules
npm install
cd ..
build_all.bat nsis
```

### "Module not found" in PyInstaller
```python
# Add to hiddenimports in .spec file
hiddenimports = [
    'your_missing_module',
]
```

### API doesn't start
```javascript
// Enable debug logging in main.js
console.log('API path:', apiExePath);
console.log('API exists:', fs.existsSync(apiExePath));
```

### Port already in use
```batch
# Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /F /PID [PID]
```

### Antivirus blocks executable
- Sign the executable (best solution)
- Add exception in antivirus
- Submit false positive report to vendor

---

## 📈 Distribution

### Release Checklist

- [ ] Version numbers updated in all files
- [ ] Code signed
- [ ] Tested on clean Windows 10/11
- [ ] VirusTotal scan clean
- [ ] README and docs updated
- [ ] Release notes written
- [ ] Backup of unsigned executable kept

### Where to Host

1. **GitHub Releases** (Recommended)
   ```batch
   # Create release
   git tag v2.0.0
   git push origin v2.0.0

   # Upload installer to GitHub Releases
   ```

2. **Direct download**
   - Upload to your website
   - Use CDN for faster downloads
   - Provide checksum (SHA256)

3. **Auto-update**
   - Implement electron-updater
   - Host on GitHub Releases or S3
   - Automatic updates for users

### Provide These Files

- `TaskTracker-Setup-2.0.0.exe` - Main installer
- `TaskTracker-Setup-2.0.0.exe.sha256` - Checksum
- `RELEASE_NOTES.md` - What's new
- `INSTALL.txt` - Installation instructions

---

## 💰 Size Optimization

**Current size:** ~80-120 MB

### Reduce Size

1. **PyInstaller excludes:**
   ```python
   excludes=[
       'matplotlib', 'numpy', 'pandas',  # If not needed
       'scipy', 'pytest', 'IPython',
   ]
   ```

2. **UPX compression:**
   ```python
   upx=True,
   ```

3. **Electron optimization:**
   ```json
   "asar": true,
   "compression": "maximum"
   ```

4. **Remove unused dependencies:**
   ```batch
   npm prune --production
   ```

### Expected sizes:
- TaskTrackerAPI.exe: ~20-30 MB
- TaskTrackerMonitor.exe: ~25-35 MB
- Task-Tracker.exe: ~80-100 MB (includes Chromium)
- Final installer: ~80-120 MB (compressed)

---

## 🎓 Learning Resources

### PyInstaller
- Docs: https://pyinstaller.org/en/stable/
- Spec files: https://pyinstaller.org/en/stable/spec-files.html

### Electron
- Docs: https://www.electronjs.org/docs/latest
- electron-builder: https://www.electron.build/

### NSIS
- Docs: https://nsis.sourceforge.io/Docs/
- Examples: https://nsis.sourceforge.io/Examples/

### Inno Setup
- Docs: https://jrsoftware.org/ishelp/
- Examples: https://jrsoftware.org/isinfo.php

---

## 📞 Support

**Need help?**
1. Check `TROUBLESHOOTING.md`
2. Read `QUICK_START.md` for basic issues
3. Search GitHub Issues
4. Open a new issue with:
   - Error message (full text)
   - Build logs
   - Windows version
   - Steps to reproduce

---

## ✅ Summary

You now have a **complete, production-ready Windows installer system** that:

1. ✅ Bundles all components (API, Monitor, Dashboard)
2. ✅ Creates a professional installer with UI
3. ✅ Handles installation, shortcuts, and uninstallation
4. ✅ Works on clean Windows machines (no dependencies)
5. ✅ Includes comprehensive documentation
6. ✅ Supports code signing and customization
7. ✅ Provides testing and troubleshooting guides

**To build:**
```batch
cd installer
build_all.bat nsis
```

**To distribute:**
```batch
# Sign it
signtool sign TaskTracker-Setup-2.0.0.exe

# Upload to GitHub Releases or your website
```

**That's it!** 🎉

---

**Repository:** https://github.com/ethantan000/Task-Tracker
**License:** MIT (see LICENSE.txt)
**Version:** 2.0.0
