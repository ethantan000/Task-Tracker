# Quick Start Guide - Windows Installer

**5-minute guide to building the Task-Tracker Windows installer**

---

## ⚡ Prerequisites (One-time setup)

Install these first (if not already installed):

```batch
# 1. Python 3.10+
python --version

# 2. Node.js 18+
node --version

# 3. NSIS (choose one of these methods)
# Method A: Download installer from https://nsis.sourceforge.io/
# Method B: Using Chocolatey
choco install nsis

# 4. PyInstaller
pip install pyinstaller
```

---

## 🚀 Build in 3 Steps

### Step 1: Clone and Navigate

```batch
git clone https://github.com/ethantan000/Task-Tracker
cd Task-Tracker\installer
```

### Step 2: Run Build Script

```batch
# This builds everything and creates the installer
build_all.bat nsis
```

**Wait 5-10 minutes** while it:
- ✓ Builds Python executables
- ✓ Builds Next.js dashboard
- ✓ Builds Electron app
- ✓ Creates NSIS installer

### Step 3: Get Your Installer

```batch
cd nsis
dir TaskTracker-Setup-*.exe
```

**Your installer is ready!** 🎉

---

## 📦 What You Get

- **File:** `TaskTracker-Setup-2.0.0.exe` (~80-120 MB)
- **What it installs:**
  - Desktop application with dashboard
  - Background API server
  - Work monitoring tool
  - Start menu shortcuts
  - Desktop shortcut (optional)

---

## ✅ Test It

```batch
# Test the installer
TaskTracker-Setup-2.0.0.exe

# Or test just the executables
cd ..\pyinstaller\dist
TaskTrackerAPI.exe        # Starts API on localhost:8000
TaskTrackerMonitor.exe    # Opens monitoring tool
```

---

## 🆘 If Something Goes Wrong

### "Python not found"
```batch
python --version  # If fails, install Python from python.org
```

### "makensis not found"
```batch
# Install NSIS from https://nsis.sourceforge.io/
# Or use Inno Setup instead:
build_all.bat inno
```

### "Build failed"
```batch
# Try building Python only first
build_python_only.bat

# Check logs for errors
type pyinstaller\build\api_backend\warn-api_backend.txt
```

### "Still stuck?"
See `TROUBLESHOOTING.md` for detailed solutions.

---

## 📚 Next Steps

- **Customize:** Edit `nsis/installer.nsi` for branding
- **Sign it:** Get a code signing certificate to remove warnings
- **Distribute:** Upload to GitHub Releases or your website
- **Document:** Add release notes and changelog

---

## 🔧 Individual Component Builds

If you need to build components separately:

```batch
# Python executables only
build_python_only.bat

# Electron app only
cd electron
npm install
npm run build

# NSIS installer only
cd ..\nsis
makensis installer.nsi

# Inno Setup installer only
cd ..\innosetup
iscc installer.iss
```

---

## 📂 Output Locations

After building, find your files here:

| Component | Location |
|-----------|----------|
| API Executable | `installer/pyinstaller/dist/TaskTrackerAPI.exe` |
| Monitor Executable | `installer/pyinstaller/dist/TaskTrackerMonitor.exe` |
| Electron App | `installer/electron/dist/win-unpacked/` |
| NSIS Installer | `installer/nsis/TaskTracker-Setup-2.0.0.exe` |
| Inno Installer | `installer/innosetup/output/TaskTracker-Setup-2.0.0.exe` |

---

## 🎯 Build Options

```batch
# Build with NSIS (recommended)
build_all.bat nsis

# Build with Inno Setup
build_all.bat inno

# Build both
build_all.bat both

# Test executables
test_executables.bat
```

---

## 💡 Pro Tips

1. **Clean builds:** Delete `dist/` folders before rebuilding
2. **Test on VM:** Always test installer on a clean Windows VM
3. **Sign your app:** Eliminates "Unknown Publisher" warnings
4. **Check antivirus:** Scan with VirusTotal before distributing
5. **Version bump:** Update version in all files before release

---

## 📖 Full Documentation

- **Complete guide:** `README.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`
- **Electron docs:** `electron/README.md`

---

## ⏱️ Typical Build Times

- Python executables: 2-3 minutes
- Next.js build: 1-2 minutes
- Electron build: 2-4 minutes
- NSIS installer: 30 seconds
- **Total: 5-10 minutes** ⚡

---

**Questions?** Open an issue on GitHub!

**Ready to build?** Run `build_all.bat nsis` and grab a coffee ☕
