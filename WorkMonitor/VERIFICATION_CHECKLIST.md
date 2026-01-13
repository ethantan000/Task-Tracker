# WorkMonitor v2.0 - Verification Checklist

## CRITICAL VERIFICATION TESTS

This checklist MUST be completed before considering the rebuild successful.

---

## ✅ PHASE 6: VERIFICATION

### 1. Window Lifecycle Tests

#### Main Window
- [ ] Application launches successfully from START.bat
- [ ] Main window appears with correct size (560x850)
- [ ] Window can be minimized to tray
- [ ] Window can be restored from tray (Show menu item)
- [ ] Window can be minimized/restored multiple times without errors
- [ ] No "window was deleted" errors occur

#### Admin Panel
- [ ] **CRITICAL:** Admin panel opens from WorkMonitor button
  - Click "Admin Panel" button
  - Enter password: `admin123`
  - Panel should appear centered at 700x900
- [ ] **CRITICAL:** Admin panel opens from system tray menu
  - Minimize to tray
  - Right-click tray icon → "Admin Panel"
  - Enter password: `admin123`
  - Panel should appear even when main window is hidden
- [ ] Admin panel can be opened/closed multiple times
- [ ] Settings can be modified and saved
- [ ] Password can be changed successfully
- [ ] Data can be reset successfully
- [ ] No errors when opening panel with main window hidden (in tray)

#### Warning Screen
- [ ] Warning screen appears when idle > warning_threshold during work hours
- [ ] Warning screen is fullscreen and red
- [ ] Warning screen can be dismissed with "I'm Back" button
- [ ] Warning screen can be dismissed with any key press
- [ ] Warning screen can be dismissed with mouse click

#### Floating Widget
- [ ] Floating widget starts when toggled (tray menu or future button)
- [ ] Widget shows work time correctly
- [ ] Widget has "X" close button that works
- [ ] Widget closes automatically when app exits
- [ ] Widget can be toggled on/off multiple times

---

### 2. Layout Tests

#### Button Visibility
- [ ] **CRITICAL:** All 4 buttons visible at default window size (560x850)
  - "Open Dashboard" (blue)
  - "Admin Panel" (purple)
  - "Minimize to Tray" (outlined)
  - "Shutdown Program" (red)
- [ ] **CRITICAL:** All 4 buttons visible at minimum size (560x800)
- [ ] Buttons remain visible when resizing window
- [ ] No vertical scrolling required to see buttons at default size

#### Content Scrolling
- [ ] Content area scrolls if window is made very small
- [ ] Header stays fixed at top when scrolling
- [ ] Buttons stay fixed at bottom when scrolling
- [ ] Scrollbar appears only when needed

#### Admin Panel Layout
- [ ] All 5 settings sections are visible
- [ ] Content scrolls if window is resized smaller
- [ ] Action buttons stay pinned at bottom
- [ ] Title bar stays pinned at top

---

### 3. System Tray Tests

#### Tray Icon
- [ ] Tray icon appears when minimized
- [ ] Tray icon has correct image (or fallback)
- [ ] Tray icon tooltip shows "WorkMonitor"

#### Tray Menu
- [ ] "Show" menu item restores main window
- [ ] "Show/Hide Floating Widget" toggles widget
- [ ] "Open Dashboard" opens dashboard.html in browser
- [ ] "Admin Panel" shows password dialog and opens panel
- [ ] "Exit" closes app completely with confirmation

#### Tray Behavior
- [ ] Main window can be restored from tray multiple times
- [ ] Admin panel works when opened from tray
- [ ] App continues running in background when in tray
- [ ] Closing terminal does NOT close app (if launched from START.bat)

---

### 4. System Behavior Tests

#### Single Instance
- [ ] Running START.bat twice shows "already running" error
- [ ] Only one instance can run at a time
- [ ] Lock file (app.lock) is created on start
- [ ] Lock file is removed on clean exit

#### Batch File Launch
- [ ] START.bat launches app successfully
- [ ] START.bat exits immediately (doesn't stay open)
- [ ] Terminal window closes after launch
- [ ] App continues running after terminal closes
- [ ] App icon appears in system tray

#### Process Management
- [ ] App runs as background process (no console window)
- [ ] Floating widget runs as separate subprocess
- [ ] Email scheduler runs (if enabled)
- [ ] Dashboard server runs (if enabled)

---

### 5. Business Logic Tests

#### Time Tracking
- [ ] Work time increments during work hours
- [ ] Idle time increments when user is idle
- [ ] Work time does NOT increment outside work hours
- [ ] Idle periods are tracked with start/end times
- [ ] Timer display updates every second

#### Screenshots
- [ ] Screenshots are captured at configured interval
- [ ] Screenshots are ONLY captured during work hours
- [ ] Screenshots are ONLY captured when user is working (not idle)
- [ ] Screenshots are saved to .tmp/ directory
- [ ] Suspicious screenshots are marked correctly

#### Anti-Cheat
- [ ] Jitter/jiggler patterns are detected
- [ ] Keyboard inactivity is tracked
- [ ] Window changes are tracked
- [ ] Cheat score is calculated correctly
- [ ] Suspicious events are logged

#### Dashboard
- [ ] Dashboard HTML is generated and updated
- [ ] Daily tab shows correct stats
- [ ] Weekly/Monthly/Yearly tabs work
- [ ] Screenshots are visible in dashboard
- [ ] Idle periods are listed correctly

---

### 6. UI Update Tests

#### Real-Time Updates
- [ ] Status indicator changes between Active/Idle
- [ ] Work hours label shows "During/Outside Work Hours"
- [ ] Work time updates every second
- [ ] Idle time updates every second
- [ ] Screenshot count increments
- [ ] Security status shows "Verified" or "⚠️ Suspicious Activity"
- [ ] Timer displays in HH:MM:SS format
- [ ] Inactive time shows current idle duration

#### UI Responsiveness
- [ ] UI remains responsive during monitoring
- [ ] No lag or freezing
- [ ] Buttons respond immediately to clicks
- [ ] Window can be resized smoothly

---

### 7. Error Handling Tests

#### Window Errors
- [ ] No TclError exceptions in logs
- [ ] No "window was deleted" errors
- [ ] No "window not found" errors
- [ ] No stale window reference errors

#### Configuration Errors
- [ ] Invalid config values are handled gracefully
- [ ] Missing config file creates default config
- [ ] Corrupted config file recreates default
- [ ] Config saves are atomic (no data loss)

#### Screenshot Errors
- [ ] Failed screenshots don't crash app
- [ ] Missing screenshot directory is recreated
- [ ] Disk full errors are logged

---

### 8. Shutdown Tests

#### Clean Shutdown
- [ ] "Shutdown Program" button shows confirmation dialog
- [ ] Confirming shutdown closes all windows
- [ ] Floating widget is terminated
- [ ] Email scheduler is stopped
- [ ] Dashboard server is stopped
- [ ] Lock file is removed
- [ ] No zombie processes remain

#### Emergency Shutdown
- [ ] Force closing window (X button) minimizes to tray
- [ ] Killing process from Task Manager cleans up properly
- [ ] Lock file is removed on process kill

---

## 🔍 REGRESSION TESTS (Previously Broken Features)

These were specifically mentioned as broken in the old version:

### Admin Panel from Tray
- [ ] ✅ **FIXED:** Admin panel opens successfully from tray menu
- [ ] ✅ **FIXED:** No "window was deleted before visibility changed" error
- [ ] ✅ **FIXED:** Password dialog works when main window is hidden

### Button Visibility
- [ ] ✅ **FIXED:** All 4 buttons visible without maximizing window
- [ ] ✅ **FIXED:** Default window height (850px) shows all content
- [ ] ✅ **FIXED:** Minimum height (800px) ensures buttons visible

### Window Lifecycle
- [ ] ✅ **FIXED:** Windows can be shown/hidden multiple times
- [ ] ✅ **FIXED:** No duplicate window instances
- [ ] ✅ **FIXED:** Clean references to all windows

---

## 📊 ACCEPTANCE CRITERIA

The rebuild is **SUCCESSFUL** when:

1. ✅ **Zero lifecycle errors** - No Tkinter window exceptions
2. ✅ **Always visible buttons** - All 4 buttons visible at default size
3. ✅ **Reliable admin panel** - Works from all entry points (button + tray)
4. ✅ **Clean architecture** - One creation function per window
5. ✅ **All verification tests pass** - Every checkbox above is checked

---

## 🧪 TESTING PROCEDURE

### Quick Test (5 minutes)
1. Run START.bat
2. Verify all 4 buttons are visible
3. Click "Admin Panel" → enter password → verify panel opens
4. Minimize to tray
5. Right-click tray → "Admin Panel" → enter password → verify panel opens
6. Exit app

### Full Test (20 minutes)
1. Complete entire checklist above
2. Run app for 10 minutes and monitor for errors
3. Check logs for any exceptions
4. Verify business logic (time tracking, screenshots)
5. Test all entry points and edge cases

---

## 📝 TEST RESULTS

Date: _______________
Tester: _______________

### Summary
- Total Tests: ___ / ___
- Passed: ___
- Failed: ___
- Blocked: ___

### Critical Issues Found
1.
2.
3.

### Non-Critical Issues Found
1.
2.
3.

### Sign-Off
- [ ] All critical tests passed
- [ ] No P0/P1 bugs remain
- [ ] Ready for production

Approved by: _______________
Date: _______________

---

## 🚀 DEPLOYMENT CHECKLIST

Before deploying to production:

- [ ] All verification tests pass
- [ ] No errors in work_monitor.log
- [ ] Old work_monitor.py backed up to work_monitor_old.py
- [ ] New work_monitor.py is active
- [ ] START.bat uses new version
- [ ] Documentation updated (ARCHITECTURE.md)
- [ ] Git commit created with changes
- [ ] PR created and reviewed

---

## 📚 RELATED DOCUMENTS

- `ARCHITECTURE.md` - Clean architecture design document
- `work_monitor.py` - New implementation (v2.0)
- `work_monitor_old.py` - Original implementation (backup)
- `.cache/work_monitor.log` - Application error log

---

**Version:** 2.0
**Last Updated:** 2026-01-13
**Status:** Ready for Verification
