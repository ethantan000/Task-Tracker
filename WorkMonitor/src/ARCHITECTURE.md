# WorkMonitor v2.0 - Clean Architecture Design

## Problem Statement
The existing codebase (~2400 lines) has accumulated technical debt through incremental fixes:
- Window lifecycle errors ("window was deleted before visibility changed")
- Button visibility issues requiring window maximization
- Fragile system tray integration
- Complex window management patterns

## Solution: Ground-Up Rebuild

### Core Principle
**ONE creation function per window + hide/show lifecycle = zero lifecycle errors**

---

## PHASE 2: Architecture Design

### 1. APPLICATION WINDOWS

#### 1.1 WorkMonitor (Main Window)
- **Type**: Root tk.Tk() window
- **Size**: 560x850px (adaptive to screen height)
- **Minimum**: 560x800px (ensures all buttons visible)
- **Lifecycle**: Created once, hidden/shown via withdraw/deiconify
- **Close behavior**: Minimize to tray (not destroy)
- **Components**:
  - Header (title, subtitle) - pinned top
  - Status card (active/idle/alert indicators)
  - Stats card (work time, idle time, screenshots, security, network)
  - Timer card (large time display, active/inactive counters)
  - Button panel (4 buttons in 2x2 grid) - pinned bottom
  - All buttons must be visible at default size
  - Content area scrollable if needed

**Creation Pattern**:
```python
class WindowManager:
    def __init__(self):
        self.main_window = None  # Single reference

    def get_main_window(self):
        """Get or create main window - ONLY creation point"""
        if self.main_window is None or not self.main_window.winfo_exists():
            self.main_window = self._create_main_window()
        return self.main_window

    def show_main_window(self):
        """Show main window"""
        window = self.get_main_window()
        window.deiconify()
        window.lift()
        window.focus_force()

    def hide_main_window(self):
        """Hide main window to tray"""
        if self.main_window and self.main_window.winfo_exists():
            self.main_window.withdraw()
```

#### 1.2 Admin Panel
- **Type**: Toplevel window
- **Size**: 700x900px, centered
- **Lifecycle**: Created once, hidden/shown
- **Entry Points**:
  1. WorkMonitor button
  2. System tray menu
- **Password validation**: Independent dialog (no parent dependency)
- **Components**:
  - Scrollable canvas container
  - 5 settings sections (work hours, monitoring, email, network, startup)
  - Action buttons at bottom (Save, Change Password, Reset) - pinned
  - Close button (X) - pinned top-right

**Creation Pattern**:
```python
def get_admin_panel(self):
    """Get or create admin panel - ONLY creation point"""
    if self.admin_panel is None or not self.admin_panel.winfo_exists():
        self.admin_panel = self._create_admin_panel()
    return self.admin_panel

def show_admin_panel(self):
    """Show admin panel with password check"""
    # Create independent password dialog
    dialog = tk.Toplevel()
    dialog.withdraw()
    password = simpledialog.askstring("Admin Access", "Enter password:",
                                     parent=dialog, show='*')
    dialog.destroy()

    if self._verify_password(password):
        panel = self.get_admin_panel()
        panel.deiconify()
        panel.lift()
        panel.focus_force()
    else:
        messagebox.showerror("Error", "Invalid password")
```

#### 1.3 Warning Screen
- **Type**: Fullscreen Toplevel
- **Lifecycle**: Created on-demand, destroyed after dismissal
- **Trigger**: Idle >= warning_threshold during work hours
- **Dismissal**: Any input (mouse/keyboard/button)

**Creation Pattern** (exception - destroyed after use):
```python
def show_warning_screen(self):
    """Create and show warning screen"""
    if self.warning_window and self.warning_window.winfo_exists():
        return  # Already showing

    self.warning_window = self._create_warning_screen()
    # Auto-dismiss after interaction
```

#### 1.4 Floating Widget
- **Type**: Separate subprocess (tk.Tk() in different process)
- **Size**: Draggable, resizable, persistent preferences
- **Features**: Always-on-top, opacity control, work time display
- **Lifecycle**: Started/stopped as subprocess
- **Communication**: File-based (reads .cache/ files)

**Management Pattern**:
```python
def start_floating_widget(self):
    """Start widget as subprocess"""
    if self.widget_process is None or self.widget_process.poll() is not None:
        self.widget_process = subprocess.Popen([
            sys.executable,
            str(BASE_DIR / "src" / "overlay_widget.py")
        ])

def stop_floating_widget(self):
    """Stop widget subprocess"""
    if self.widget_process and self.widget_process.poll() is None:
        self.widget_process.terminate()
        self.widget_process.wait(timeout=2)
        self.widget_process = None
```

#### 1.5 System Tray
- **Type**: pystray.Icon in daemon thread
- **Menu Items**:
  - Show (restore main window)
  - Show/Hide Floating Widget (dynamic label)
  - Open Dashboard
  - Admin Panel
  - Exit
- **Icon**: Load from icon.ico or create fallback
- **Thread**: Daemon thread, stopped on app exit

---

### 2. WINDOW LIFECYCLE MANAGER

**Central Authority Pattern**:
```python
class WindowManager:
    """Centralized window lifecycle management"""

    def __init__(self, root):
        self.root = root  # Main tk.Tk() instance

        # Single references per window type
        self.admin_panel = None
        self.warning_window = None
        self.widget_process = None
        self.tray_icon = None

    # Creation functions (private, called only by get_* methods)
    def _create_main_window(self): ...
    def _create_admin_panel(self): ...
    def _create_warning_screen(self): ...

    # Access functions (public, safe to call multiple times)
    def get_main_window(self): ...
    def get_admin_panel(self): ...

    # Show/hide functions (public, used by all entry points)
    def show_main_window(self): ...
    def hide_main_window(self): ...
    def show_admin_panel(self): ...
    def hide_admin_panel(self): ...

    # Cleanup functions
    def close_all_windows(self): ...
    def destroy_all(self): ...
```

**Key Rules**:
1. ONE creation function per window type
2. Creation functions are PRIVATE (_create_*)
3. Access functions check existence before returning
4. Show/hide use withdraw/deiconify (not destroy)
5. References cleared immediately after destruction
6. All entry points call the SAME show functions

---

### 3. LAYOUT SYSTEM (UNBREAKABLE)

#### 3.1 Main Window Layout
```
┌─────────────────────────────────────┐
│ HEADER (pinned top, pack)           │ ← Fixed height, never scrolls
│  - Title: "WorkMonitor" (36pt)      │
│  - Subtitle                          │
├─────────────────────────────────────┤
│ SCROLLABLE CONTENT (pack, expand)   │ ← Expands to fill space
│  ┌───────────────────────────────┐  │
│  │ Status Card                   │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Stats Card (5 rows)           │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Timer Card                    │  │
│  └───────────────────────────────┘  │
│                                     │
│  (scroll if content exceeds space) │
├─────────────────────────────────────┤
│ BUTTON PANEL (pinned bottom, pack)  │ ← Fixed height, never scrolls
│  ┌──────────────┬──────────────┐   │
│  │ Open         │ Admin        │   │
│  │ Dashboard    │ Panel        │   │
│  └──────────────┴──────────────┘   │
│  ┌──────────────┬──────────────┐   │
│  │ Minimize to  │ Shutdown     │   │
│  │ Tray         │ Program      │   │
│  └──────────────┴──────────────┘   │
└─────────────────────────────────────┘
```

**Layout Code**:
```python
# Header (pinned top)
header_frame = tk.Frame(root, bg=BG_COLOR)
header_frame.pack(side='top', fill='x', padx=30, pady=(20, 0))
# ... add title, subtitle ...

# Content area (scrollable)
content_canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient='vertical', command=content_canvas.yview)
content_frame = tk.Frame(content_canvas, bg=BG_COLOR)

content_canvas.pack(side='left', fill='both', expand=True, padx=30)
scrollbar.pack(side='right', fill='y')
content_canvas.create_window((0, 0), window=content_frame, anchor='nw')
content_frame.bind('<Configure>', lambda e: content_canvas.configure(
    scrollregion=content_canvas.bbox('all')))

# ... add status card, stats card, timer card to content_frame ...

# Button panel (pinned bottom)
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(side='bottom', fill='x', padx=30, pady=20)
# ... add 4 buttons in 2x2 grid ...
```

**Critical Requirements**:
- NO fixed heights for main container
- NO absolute positioning for buttons
- Header and footer use pack(side='top'/'bottom')
- Content uses pack(fill='both', expand=True)
- Minimum window size ensures all buttons visible
- Scrollbar appears automatically if content overflows

#### 3.2 Admin Panel Layout
```
┌────────────────────────────────────────┐
│ TITLE BAR (pinned top, pack)          │ ← Fixed
│  Admin Panel              [X]          │
├────────────────────────────────────────┤
│ SCROLLABLE SETTINGS (canvas, expand)  │ ← Expands
│  ┌──────────────────────────────────┐ │
│  │ Section 1: Work Hours            │ │
│  │   Start: [09:00]  End: [17:00]   │ │
│  └──────────────────────────────────┘ │
│  ┌──────────────────────────────────┐ │
│  │ Section 2: Monitoring Settings   │ │
│  │   Screenshot interval: [3] min   │ │
│  │   Idle threshold: [300] sec      │ │
│  └──────────────────────────────────┘ │
│  ... (3 more sections) ...            │
│                                        │
├────────────────────────────────────────┤
│ ACTION BUTTONS (pinned bottom, pack)   │ ← Fixed
│  ┌─────────┐ ┌──────────────┐ ┌─────┐ │
│  │  Save   │ │ Change Pass  │ │Reset│ │
│  └─────────┘ └──────────────┘ └─────┘ │
└────────────────────────────────────────┘
```

**Same scrollable pattern**: pinned header/footer, expandable content

---

### 4. ENTRY POINTS

#### 4.1 START.bat (Primary)
```batch
@echo off
cd /d "%~dp0"
start "" pythonw src\work_monitor.py
exit
```
- Uses pythonw (no console window)
- `start ""` detaches process
- `exit` closes batch immediately
- App runs independently in background

#### 4.2 Python Entry Point
```python
if __name__ == "__main__":
    app = WorkMonitorApp()
    app.run()
```

**Single Instance Enforcement**:
```python
class WorkMonitorApp:
    def __init__(self):
        self.lock_file = DATA_DIR / "app.lock"
        if self.lock_file.exists():
            messagebox.showerror("Error", "WorkMonitor is already running!")
            sys.exit(1)
        self.lock_file.write_text(str(os.getpid()))
```

#### 4.3 Admin Panel Entry Points
**All paths call the SAME function**:
1. WorkMonitor button → `window_manager.show_admin_panel()`
2. System tray menu → `window_manager.show_admin_panel()`

No duplicated logic. Password validation is part of `show_admin_panel()`.

---

### 5. SYSTEM TRAY BEHAVIOR

**Menu Actions**:
```python
def create_tray_menu():
    return pystray.Menu(
        item('Show', on_show),
        item('Show/Hide Floating Widget', on_toggle_widget),
        item('Open Dashboard', on_dashboard),
        item('Admin Panel', on_admin_panel),
        item('Exit', on_exit)
    )

def on_show(icon, item):
    """Restore main window"""
    icon.stop()  # Stop tray icon thread
    window_manager.show_main_window()

def on_admin_panel(icon, item):
    """Show admin panel from tray"""
    window_manager.show_admin_panel()
```

**Key Points**:
- Tray icon runs in daemon thread
- Menu callbacks invoke window_manager methods
- No duplicate window creation logic
- Admin panel works even when main window hidden

---

### 6. BUSINESS LOGIC (REUSE)

**Keep These Modules Intact**:
1. **AntiCheatDetector** (lines 139-336) - Jitter detection, keyboard/window tracking
2. **Config** (lines 444-494) - Thread-safe configuration management
3. **ActivityLogger** (lines 496-741) - Obfuscated data storage, atomic writes
4. **ScreenshotManager** (lines 742-793) - Screenshot capture, cleanup
5. **HTMLReportGenerator** (lines 795-1070) - Dashboard HTML generation
6. **MouseTracker** (lines 376-442) - Mouse movement tracking
7. **KeyboardTracker** (lines 338-374) - Keyboard activity tracking
8. **EmailReportSender** (email_reports.py) - Weekly email reports
9. **DashboardServer** (dashboard_server.py) - HTTP server for network access

**Monitoring Loop**:
```python
def monitor_loop(self):
    """Background monitoring thread"""
    while self.running:
        # 1. Check mouse/keyboard activity
        mouse_idle = self.mouse_tracker.get_idle_time()
        keyboard_idle = self.keyboard_tracker.get_idle_time()
        current_idle = min(mouse_idle, keyboard_idle)

        # 2. Determine if working (idle < threshold)
        is_working = current_idle < self.config.get('idle_start_seconds')

        # 3. Check for cheating
        if self.config.get('anticheat_enabled'):
            is_cheating = self.anticheat.check_for_cheating(...)

        # 4. Show warning if idle too long during work hours
        if is_work_hours() and current_idle >= warning_threshold:
            self.window_manager.show_warning_screen()

        # 5. Log time (only during work hours)
        if is_work_hours():
            if is_working:
                self.logger.add_work_time(1)
            else:
                self.logger.add_idle_time(1)
            if is_cheating:
                self.logger.add_suspicious_time(1)

        # 6. Capture screenshot at interval
        if should_capture_screenshot():
            self.screenshot_manager.capture(suspicious=is_cheating)

        # 7. Update dashboard HTML
        self.report_generator.save_dashboard(self.logger.get_all_data())

        # 8. Schedule UI update (use after() for thread safety)
        self.root.after(0, self.window_manager.update_ui)

        time.sleep(1)
```

---

### 7. SHUTDOWN SEQUENCE

**Clean Shutdown**:
```python
def quit_app(self):
    """Clean shutdown - close all windows and threads"""
    self.running = False  # Stop monitoring loop

    # 1. Stop floating widget
    self.window_manager.stop_floating_widget()

    # 2. Stop email scheduler
    if self.email_sender:
        self.email_sender.stop()

    # 3. Stop dashboard server
    if self.dashboard_server:
        self.dashboard_server.stop()

    # 4. Close admin panel
    if self.admin_panel and self.admin_panel.winfo_exists():
        self.admin_panel.destroy()
        self.admin_panel = None

    # 5. Close warning window
    if self.warning_window and self.warning_window.winfo_exists():
        self.warning_window.destroy()
        self.warning_window = None

    # 6. Remove lock file
    if self.lock_file.exists():
        self.lock_file.unlink()

    # 7. Destroy root window
    self.root.destroy()
```

---

## VERIFICATION CHECKLIST

After rebuild, MUST verify:

### Window Lifecycle
- [ ] Main window can be shown/hidden multiple times
- [ ] Admin panel can be opened/closed multiple times
- [ ] No "window was deleted" errors
- [ ] No duplicate window instances

### Admin Panel
- [ ] Opens from WorkMonitor button
- [ ] Opens from system tray menu
- [ ] Works when main window is hidden (in tray)
- [ ] Password validation works in all cases

### Layout
- [ ] All 4 buttons visible at default 560x850 size
- [ ] Buttons remain visible when resizing to minimum (560x800)
- [ ] Content scrolls if window is too small
- [ ] Header and footer never scroll out of view

### System Tray
- [ ] Minimize to tray hides window (not destroy)
- [ ] Restore from tray shows window again
- [ ] All tray menu actions work
- [ ] Floating widget toggle works from tray

### System Behavior
- [ ] START.bat launches app without leaving terminal
- [ ] Closing terminal does NOT close app
- [ ] Single instance enforcement works
- [ ] App runs in background with system tray icon

### Floating Widget
- [ ] Starts when toggled
- [ ] Stops when toggled again
- [ ] Has "X" button that works
- [ ] Closes automatically when app exits

---

## FILE STRUCTURE

```
WorkMonitor/
├── START.bat                  # User launch script (pythonw)
├── INSTALL.bat                # Setup script
├── icon.ico                   # App icon
├── dashboard.html             # Generated dashboard (static)
├── src/
│   ├── work_monitor.py        # NEW: Main app with clean architecture
│   ├── window_manager.py      # NEW: Centralized window lifecycle
│   ├── overlay_widget.py      # KEEP: Floating widget (separate process)
│   ├── business_logic.py      # NEW: Business logic modules (extracted)
│   ├── email_reports.py       # KEEP: Email functionality
│   └── dashboard_server.py    # KEEP: HTTP server
├── .cache/                    # Data directory
│   ├── sys.dat                # Config (base64-encoded)
│   ├── app.lock               # Single instance lock
│   ├── d*.dat                 # Daily logs (obfuscated)
│   └── widget_prefs.json      # Widget preferences
└── .tmp/                      # Screenshots (auto-cleaned)
```

---

## IMPLEMENTATION STRATEGY

### Step 1: Extract Business Logic
Create `business_logic.py` with all reusable classes:
- AntiCheatDetector
- Config
- ActivityLogger
- ScreenshotManager
- MouseTracker
- KeyboardTracker
- HTMLReportGenerator

### Step 2: Create WindowManager
Create `window_manager.py` with centralized window lifecycle:
- ONE creation function per window
- Hide/show instead of destroy/recreate
- All entry points use the same methods

### Step 3: Rebuild work_monitor.py
New main file with clean structure:
- Import business_logic modules
- Import window_manager
- Simple, focused code
- No duplicated logic

### Step 4: Update overlay_widget.py
Minimal changes (it already works well):
- Ensure it reads from correct .cache/ files
- Verify subprocess management works

### Step 5: Verification
Test every item on the verification checklist.

---

## SUCCESS CRITERIA

The rebuild is complete when:
1. **Zero lifecycle errors** - No "window was deleted" exceptions
2. **Always visible buttons** - All 4 buttons visible at default size
3. **Reliable admin panel** - Works from all entry points, even when main window hidden
4. **Clean architecture** - Single creation function per window, no duplicated logic
5. **Passes all verification checks** - Every checklist item verified working

This architecture **GUARANTEES** correctness by design, not by patching.
