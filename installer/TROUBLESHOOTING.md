# Task-Tracker Installer Troubleshooting Guide

Common issues and solutions when building or using the Task-Tracker Windows installer.

---

## Build Issues

### 1. PyInstaller: "Module not found" errors

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Install all dependencies first
pip install -r ../api/requirements.txt
pip install -r ../WorkMonitor/src/requirements.txt
pip install pyinstaller

# Verify installation
pip list | findstr fastapi
```

**If still failing:**
Add to `hiddenimports` in the `.spec` file:
```python
hiddenimports = [
    'fastapi',
    'uvicorn',
    # ... add missing module here
]
```

---

### 2. PyInstaller: "Failed to execute script" when running EXE

**Causes:**
- Missing data files
- Missing hidden imports
- Path issues

**Debug:**
```bash
# Run with console output to see errors
# Change in .spec file:
console=True  # instead of False

# Rebuild
pyinstaller --clean your_spec.spec
```

**Check logs:**
```bash
# Run executable and check error
cd installer/pyinstaller/dist
TaskTrackerAPI.exe
# Read error messages
```

---

### 3. Electron: Build fails with "Cannot find module"

**Error:**
```
Error: Cannot find module 'electron'
```

**Solution:**
```bash
cd installer/electron

# Clean install
rmdir /s /q node_modules
del package-lock.json
npm install

# Verify electron
npm list electron
```

---

### 4. Electron: "Python executables not found"

**Error in build:**
```
Cannot copy file: pyinstaller/dist/TaskTrackerAPI.exe
```

**Solution:**
```bash
# Build Python executables FIRST
cd installer/pyinstaller
pyinstaller --clean api_backend.spec
pyinstaller --clean work_monitor.spec

# Verify they exist
dir dist\*.exe

# Then build Electron
cd ..\electron
npm run build
```

---

### 5. NSIS: "Invalid command" or syntax errors

**Error:**
```
Error: Invalid command MUI_PAGE_WELCOME
```

**Causes:**
- NSIS version too old
- Missing MUI2 include

**Solution:**
```bash
# Check NSIS version
makensis /VERSION
# Must be 3.08 or later

# If too old, download latest from:
# https://nsis.sourceforge.io/Download

# Verify MUI2 is included in script:
!include "MUI2.nsh"
```

---

### 6. Inno Setup: "File not found" errors

**Error:**
```
Error: Source file not found: ..\electron\dist\win-unpacked\*
```

**Causes:**
- Electron not built yet
- Wrong relative paths

**Solution:**
```bash
# Build Electron first
cd installer/electron
npm run build

# Verify files exist
dir dist\win-unpacked

# Check paths in installer.iss are correct
# They should be relative to the .iss file location
```

---

## Runtime Issues

### 7. Application: "API connection failed"

**Symptoms:**
- Dashboard shows "Unable to connect"
- Empty data in UI

**Debug:**

1. **Check if API is running:**
   ```bash
   # Open Task Manager
   # Look for "TaskTrackerAPI.exe"
   ```

2. **Test API manually:**
   ```bash
   # Open browser
   http://localhost:8000/api/health
   # Should return: {"status":"ok"}
   ```

3. **Check firewall:**
   ```bash
   # Windows Firewall might block port 8000
   # Add exception:
   netsh advfirewall firewall add rule name="Task-Tracker API" dir=in action=allow protocol=TCP localport=8000
   ```

4. **Check logs:**
   ```
   C:\Program Files\Task-Tracker\data\.cache\work_monitor.log
   ```

---

### 8. Monitor: "Access denied" or "Permission errors"

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'C:\\Program Files\\Task-Tracker\\data\\.cache\\...'
```

**Cause:**
- Insufficient permissions to write to Program Files

**Solution:**

**Option 1: Run as Administrator**
```bash
# Right-click shortcut → Run as administrator
```

**Option 2: Change data directory**

Edit `main.js`:
```javascript
// Use AppData instead of Program Files
const dataDirPath = path.join(app.getPath('appData'), 'Task-Tracker', 'data');
```

Rebuild Electron app.

**Option 3: Fix permissions (installer already does this)**
```bash
# Manually fix (as admin):
icacls "C:\Program Files\Task-Tracker\data" /grant Users:(OI)(CI)M
```

---

### 9. WebSocket: "Connection refused"

**Symptoms:**
- Real-time updates don't work
- Console shows WebSocket errors

**Debug:**

1. **Check API is running:**
   ```bash
   netstat -an | findstr 8000
   # Should show LISTENING
   ```

2. **Test WebSocket manually:**
   ```bash
   # Install wscat
   npm install -g wscat

   # Test connection
   wscat -c ws://localhost:8000/ws/activity
   ```

3. **Check antivirus/firewall:**
   - Some antivirus block WebSocket connections
   - Temporarily disable to test

4. **Check browser console:**
   - Open DevTools (F12)
   - Look for WebSocket errors
   - Verify correct URL

---

### 10. Screenshots: "No screenshots displayed"

**Causes:**
- Monitor not running
- Incorrect screenshot directory
- Permission issues

**Debug:**

1. **Check if monitor is running:**
   ```bash
   tasklist | findstr TaskTrackerMonitor.exe
   ```

2. **Check screenshot directory:**
   ```bash
   dir "C:\Program Files\Task-Tracker\data\.tmp"
   # Should contain .png files
   ```

3. **Check API can access files:**
   ```bash
   # Visit in browser
   http://localhost:8000/api/screenshots/today
   # Should return JSON with screenshot list
   ```

---

## Installation Issues

### 11. Installer: "Windows protected your PC"

**Message:**
```
Windows protected your PC
Microsoft Defender SmartScreen prevented an unrecognized app from starting
```

**Cause:**
- Executable not code-signed
- Normal for new/unsigned software

**User solution:**
1. Click "More info"
2. Click "Run anyway"

**Developer solution:**
1. Get a code signing certificate
2. Sign the executable
3. Build reputation over time

---

### 12. Installer: "Not a valid Win32 application"

**Error:**
```
installer.exe is not a valid Win32 application
```

**Causes:**
- Corrupted download
- Wrong architecture (32-bit vs 64-bit)
- Incomplete build

**Solution:**
```bash
# Rebuild installer
cd installer/nsis
del TaskTracker-Setup-*.exe
makensis installer.nsi

# Verify file
# Should be ~80-120 MB
dir TaskTracker-Setup-*.exe
```

---

### 13. Installer: "Cannot create directory"

**Error during installation:**
```
Cannot create directory: C:\Program Files\Task-Tracker
```

**Cause:**
- Insufficient permissions
- Directory already exists with locked files

**Solution:**

1. **Run installer as Administrator:**
   - Right-click installer.exe
   - Select "Run as administrator"

2. **Close running application:**
   - Close Task-Tracker if running
   - End processes in Task Manager

3. **Uninstall previous version:**
   - Control Panel → Programs
   - Uninstall Task-Tracker
   - Try installation again

---

### 14. Uninstaller: "Some files could not be removed"

**Warning during uninstall:**
```
Some files could not be removed. You may need to remove them manually.
```

**Causes:**
- Application still running
- Files in use by another process

**Solution:**

1. **Stop all processes:**
   ```bash
   taskkill /F /IM Task-Tracker.exe
   taskkill /F /IM TaskTrackerAPI.exe
   taskkill /F /IM TaskTrackerMonitor.exe
   ```

2. **Wait a moment:**
   ```bash
   timeout /t 5
   ```

3. **Re-run uninstaller:**
   ```bash
   "C:\Program Files\Task-Tracker\Uninstall.exe"
   ```

4. **Manual cleanup if needed:**
   ```bash
   rmdir /s "C:\Program Files\Task-Tracker"
   rmdir /s "%APPDATA%\Task-Tracker"
   ```

---

## Performance Issues

### 15. High CPU usage

**Symptoms:**
- Task-Tracker uses >50% CPU
- System slows down

**Causes:**
- Monitor taking screenshots too frequently
- API polling too fast
- Memory leak

**Debug:**

1. **Check which process:**
   ```bash
   # Open Task Manager
   # Sort by CPU
   # Identify: Task-Tracker.exe, TaskTrackerAPI.exe, or TaskTrackerMonitor.exe
   ```

2. **Check screenshot frequency:**
   - Default: Every 60 seconds
   - If too high, edit config

3. **Check WebSocket polling:**
   - Default: Every 5 seconds
   - Edit in `main.py`:
     ```python
     await asyncio.sleep(5)  # Increase to 10 or 30
     ```

---

### 16. High memory usage

**Symptoms:**
- Task-Tracker uses >1 GB RAM
- System runs out of memory

**Causes:**
- Too many screenshots in memory
- Memory leak in Electron
- Large data files

**Solution:**

1. **Clear old screenshots:**
   ```bash
   # Delete old screenshots (>30 days)
   del /q "C:\Program Files\Task-Tracker\data\.tmp\*.png"
   ```

2. **Restart application:**
   ```bash
   taskkill /F /IM Task-Tracker.exe
   # Launch again
   ```

3. **Reduce screenshot resolution:**
   - Edit monitor config
   - Reduce quality or resolution

---

## Antivirus Issues

### 17. Antivirus blocks or deletes executable

**Symptoms:**
- Installer won't run
- Executable disappears after creation
- "Threat detected" warnings

**Causes:**
- False positive (common with PyInstaller)
- Unsigned executable
- Packing detected as malicious

**Solutions:**

1. **Code sign the executable** (best solution)
   ```bash
   signtool sign /f cert.pfx /p password installer.exe
   ```

2. **Add exception in antivirus:**
   - Windows Defender: Settings → Virus & threat protection → Manage settings → Add exclusion
   - Add: `C:\Program Files\Task-Tracker\`

3. **Submit to antivirus vendors:**
   - VirusTotal: Upload and check detection
   - Submit false positive reports

4. **Test with different antivirus:**
   - Some are more aggressive than others

---

## Data Issues

### 18. Data not persisting / lost data

**Symptoms:**
- Activity data resets
- Statistics show zero
- Screenshots missing

**Causes:**
- Wrong data directory
- Permissions issues
- Data files corrupted

**Debug:**

1. **Check data directory:**
   ```bash
   dir "C:\Program Files\Task-Tracker\data\.cache"
   # Should contain .dat files
   ```

2. **Check file contents:**
   ```bash
   # Data files are base64 encoded
   # Should not be 0 bytes
   dir "C:\Program Files\Task-Tracker\data\.cache\*.dat"
   ```

3. **Check API reads correctly:**
   ```bash
   http://localhost:8000/api/activity/today
   # Should return activity data
   ```

4. **Verify monitor is writing:**
   ```bash
   # Watch directory for changes
   # Run monitor for 1 minute
   # Check if .dat files update
   ```

---

## Network Issues

### 19. Port already in use

**Error:**
```
[Errno 10048] Address already in use
```

**Cause:**
- Another application using port 8000

**Solution:**

1. **Find what's using port 8000:**
   ```bash
   netstat -ano | findstr :8000
   # Note the PID
   ```

2. **Kill the process:**
   ```bash
   taskkill /F /PID <PID>
   ```

3. **Change port (if needed):**
   - Edit `api/main.py`:
     ```python
     uvicorn.run(app, host="0.0.0.0", port=8001)
     ```
   - Edit `installer/electron/main.js`:
     ```javascript
     const API_PORT = 8001;
     ```
   - Rebuild

---

### 20. Localhost not accessible

**Symptoms:**
- Can't connect to http://localhost:8000
- Dashboard shows connection errors

**Debug:**

1. **Try 127.0.0.1 instead:**
   ```bash
   http://127.0.0.1:8000/api/health
   ```

2. **Check hosts file:**
   ```bash
   notepad C:\Windows\System32\drivers\etc\hosts
   # Ensure: 127.0.0.1    localhost
   ```

3. **Check firewall:**
   ```bash
   # Temporarily disable to test
   netsh advfirewall set allprofiles state off
   # Remember to re-enable!
   ```

---

## Advanced Debugging

### Enable Debug Mode

**For API:**
Edit `api/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # Change from INFO
```

**For Electron:**
Edit `installer/electron/main.js`:
```javascript
mainWindow.webContents.openDevTools();  // Uncomment this line
```

**For Monitor:**
Edit `WorkMonitor/src/work_monitor.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # Change from ERROR
```

Rebuild all components.

---

### Collect Logs

```batch
# Create support bundle
mkdir support_logs
copy "C:\Program Files\Task-Tracker\data\.cache\work_monitor.log" support_logs\
copy "%APPDATA%\Task-Tracker\logs\*" support_logs\

# Compress and send
tar -czf support_logs.zip support_logs\
```

---

## Getting Help

If you can't resolve the issue:

1. **Check GitHub Issues:**
   https://github.com/ethantan000/Task-Tracker/issues

2. **Create new issue with:**
   - Full error message
   - Steps to reproduce
   - Windows version
   - Logs (if available)
   - Screenshots

3. **Include system info:**
   ```batch
   systeminfo > system_info.txt
   ```

---

## Common Quick Fixes

**Try these first:**

```batch
# 1. Restart all components
taskkill /F /IM Task-Tracker.exe
taskkill /F /IM TaskTrackerAPI.exe
taskkill /F /IM TaskTrackerMonitor.exe
timeout /t 3
"C:\Program Files\Task-Tracker\Task-Tracker.exe"

# 2. Run as administrator
# Right-click shortcut → Run as administrator

# 3. Check Windows updates
# Settings → Update & Security → Check for updates

# 4. Reinstall
# Uninstall from Control Panel
# Delete: C:\Program Files\Task-Tracker
# Run installer again
```

---

**Still having issues?** File a GitHub issue with full details!
