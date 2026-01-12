"""
Work Monitor Overlay Widget
- Always on top, draggable, resizable
- Shows work time, idle status, anti-cheat status
- Recording indicator with live updates
- Customizable opacity and size
- Right-click settings menu
- Keyboard shortcuts and mouse wheel controls

USAGE:
------
* DRAG: Click and drag anywhere on the widget to move it
* RESIZE: Drag the resize grip (◢) in the bottom-right corner to resize
* OPACITY:
  - Mouse wheel: Scroll up/down over the widget to adjust opacity
  - Keyboard: Press + or - to increase/decrease opacity
  - Menu: Right-click → Opacity → Select preset value (30%, 50%, 70%, 85%, 100%)
* COLLAPSE: Click the arrow button (▼/▲) or double-click the work time to minimize
* SETTINGS MENU: Right-click anywhere on the widget to access:
  - Opacity presets
  - Collapse/Expand toggle
  - Reset Size (restore default size)
  - Reset Position (move back to bottom-right corner)
  - Save Settings (preferences auto-save every 5 seconds)
* KEYBOARD SHORTCUTS:
  - +/= : Increase opacity by 5%
  - - : Decrease opacity by 5%
  - ESC : Manually save preferences
  - Double-click work time: Toggle collapse

All preferences (position, size, opacity, collapsed state) are automatically saved
and restored when the widget is restarted.

Copyright (c) 2025 Enkhtamir Enkhdavaa
Contact: me@tamir.cc | enkhtamir.com
"""

import tkinter as tk
from tkinter import Menu
import json
import base64
from pathlib import Path
from datetime import datetime

def decode_data(encoded_str):
    """Decode base64 data to JSON"""
    try:
        json_str = base64.b64decode(encoded_str.encode()).decode()
        return json.loads(json_str)
    except:
        return None

def get_log_filename(date_str):
    """Generate obfuscated log filename from date"""
    encoded = base64.b64encode(date_str.encode()).decode().replace('=', '').replace('/', '_')
    return f"d{encoded}.dat"

class OverlayWidget:
    def __init__(self):
        self.root = tk.Tk()

        # Remove title bar and borders
        self.root.overrideredirect(True)

        # Always on top of everything
        self.root.attributes('-topmost', True)

        # Data directory (parent folder, since we're in src/)
        self.data_dir = Path(__file__).parent.parent / ".cache"
        self.config_file = self.data_dir / "sys.dat"
        self.prefs_file = self.data_dir / "widget_prefs.json"

        # Load user preferences
        self.prefs = self.load_preferences()
        self.opacity = self.prefs.get('opacity', 0.75)
        self.collapsed = self.prefs.get('collapsed', False)

        # Set opacity
        self.root.attributes('-alpha', self.opacity)

        # Position: bottom-right corner (above taskbar) or saved position
        self.position_widget()

        # Dark semi-transparent frame
        self.frame = tk.Frame(self.root, bg='#1a1a2e', padx=10, pady=6)
        self.frame.pack(fill='both', expand=True)

        # Top row: Recording indicator
        self.top_frame = tk.Frame(self.frame, bg='#1a1a2e')
        self.top_frame.pack(fill='x', pady=(0, 4))

        self.rec_dot = tk.Label(
            self.top_frame,
            text="\u25CF",  # Solid circle
            font=('Arial', 10),
            fg='#ff0000',
            bg='#1a1a2e'
        )
        self.rec_dot.pack(side='left')

        self.rec_label = tk.Label(
            self.top_frame,
            text=" REC",
            font=('Consolas', 9, 'bold'),
            fg='#ff0000',
            bg='#1a1a2e'
        )
        self.rec_label.pack(side='left')

        # Minimize button (middle)
        self.minimize_btn = tk.Label(
            self.top_frame,
            text=" \u25BC ",  # Down arrow
            font=('Arial', 8),
            fg='#888888',
            bg='#1a1a2e',
            cursor='hand2'
        )
        self.minimize_btn.pack(side='left', padx=5)
        self.minimize_btn.bind('<Button-1>', lambda e: self.toggle_collapse())

        # Anti-cheat status (right side of top row)
        self.anticheat_label = tk.Label(
            self.top_frame,
            text="Anti-Cheat: ON",
            font=('Consolas', 9),
            fg='#4CAF50',
            bg='#1a1a2e'
        )
        self.anticheat_label.pack(side='right')

        # Separator line
        self.sep = tk.Frame(self.frame, bg='#333333', height=1)
        self.sep.pack(fill='x', pady=4)

        # Work time display (main)
        self.time_label = tk.Label(
            self.frame,
            text="Work: 0:00:00",
            font=('Consolas', 16, 'bold'),
            fg='#4CAF50',
            bg='#1a1a2e'
        )
        self.time_label.pack()

        # Stats row
        self.stats_frame = tk.Frame(self.frame, bg='#1a1a2e')
        self.stats_frame.pack(fill='x', pady=(4, 0))

        self.idle_label = tk.Label(
            self.stats_frame,
            text="Idle: 0m",
            font=('Consolas', 9),
            fg='#ff9800',
            bg='#1a1a2e'
        )
        self.idle_label.pack(side='left')

        self.clock_label = tk.Label(
            self.stats_frame,
            text="00:00",
            font=('Consolas', 9),
            fg='#888888',
            bg='#1a1a2e'
        )
        self.clock_label.pack(side='right')

        # Screenshots count
        self.screenshots_label = tk.Label(
            self.frame,
            text="Screenshots: 0",
            font=('Consolas', 9),
            fg='#2196F3',
            bg='#1a1a2e'
        )
        self.screenshots_label.pack(pady=(2, 0))

        # Resize grip (bottom-right corner)
        self.resize_grip = tk.Label(
            self.frame,
            text="\u25E2",  # Lower-right corner symbol
            font=('Arial', 10),
            fg='#555555',
            bg='#1a1a2e',
            cursor='size_nw_se'
        )
        self.resize_grip.pack(side='right', anchor='se')
        self.resize_grip.bind('<Button-1>', self.start_resize)
        self.resize_grip.bind('<B1-Motion>', self.do_resize)

        # Bind drag to all elements (except resize grip)
        self.drag_widgets = [self.frame, self.top_frame, self.time_label,
                             self.stats_frame, self.idle_label, self.clock_label,
                             self.rec_dot, self.rec_label, self.anticheat_label,
                             self.screenshots_label, self.minimize_btn]
        for widget in self.drag_widgets:
            widget.bind('<Button-1>', self.start_drag)
            widget.bind('<B1-Motion>', self.do_drag)

        # Bind right-click for settings menu
        self.root.bind('<Button-3>', self.show_settings_menu)

        # Bind mouse wheel for opacity
        self.root.bind('<MouseWheel>', self.adjust_opacity_wheel)  # Windows/Mac
        self.root.bind('<Button-4>', self.adjust_opacity_wheel)    # Linux scroll up
        self.root.bind('<Button-5>', self.adjust_opacity_wheel)    # Linux scroll down

        # Bind keyboard shortcuts
        self.root.bind('<plus>', lambda e: self.adjust_opacity(0.05))
        self.root.bind('<minus>', lambda e: self.adjust_opacity(-0.05))
        self.root.bind('<equal>', lambda e: self.adjust_opacity(0.05))  # + without shift
        self.root.bind('<KP_Add>', lambda e: self.adjust_opacity(0.05))  # Numpad +
        self.root.bind('<KP_Subtract>', lambda e: self.adjust_opacity(-0.05))  # Numpad -
        self.root.bind('<Escape>', lambda e: self.save_preferences())

        # Double-click to collapse/expand
        self.time_label.bind('<Double-Button-1>', lambda e: self.toggle_collapse())

        # Blink state
        self.blink_on = True

        # Resize tracking
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_width = 0
        self.resize_start_height = 0

        # Apply collapsed state if saved
        if self.collapsed:
            self.apply_collapsed_state()

        # Start updating
        self.update_display()
        self.blink_recording()

    def load_preferences(self):
        """Load user preferences from file"""
        try:
            if self.prefs_file.exists():
                with open(self.prefs_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_preferences(self):
        """Save user preferences to file"""
        try:
            # Get current position
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            w = self.root.winfo_width()
            h = self.root.winfo_height()

            self.prefs = {
                'opacity': self.opacity,
                'position': {'x': x, 'y': y},
                'size': {'width': w, 'height': h},
                'collapsed': self.collapsed
            }

            self.data_dir.mkdir(exist_ok=True)
            with open(self.prefs_file, 'w') as f:
                json.dump(self.prefs, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def position_widget(self):
        """Position widget using saved position or default to bottom-right corner"""
        self.root.update_idletasks()

        # Try to use saved position and size
        saved_pos = self.prefs.get('position', {})
        saved_size = self.prefs.get('size', {})

        if saved_pos and saved_size:
            x = saved_pos.get('x')
            y = saved_pos.get('y')
            w = saved_size.get('width')
            h = saved_size.get('height')
            if all(v is not None for v in [x, y, w, h]):
                self.root.geometry(f'{w}x{h}+{x}+{y}')
                return

        # Default position: bottom-right corner
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - 280
        y = screen_h - 180
        self.root.geometry(f'+{x}+{y}')

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f'+{x}+{y}')

    def start_resize(self, event):
        """Start resizing from corner"""
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.resize_start_width = self.root.winfo_width()
        self.resize_start_height = self.root.winfo_height()

    def do_resize(self, event):
        """Resize the widget"""
        delta_x = event.x_root - self.resize_start_x
        delta_y = event.y_root - self.resize_start_y

        new_width = max(150, self.resize_start_width + delta_x)
        new_height = max(80, self.resize_start_height + delta_y)

        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.geometry(f'{new_width}x{new_height}+{x}+{y}')

    def adjust_opacity(self, delta):
        """Adjust opacity by delta amount"""
        self.opacity = max(0.1, min(1.0, self.opacity + delta))
        self.root.attributes('-alpha', self.opacity)
        self.save_preferences()

    def adjust_opacity_wheel(self, event):
        """Adjust opacity with mouse wheel"""
        # Windows/Mac use event.delta, Linux uses event.num
        if hasattr(event, 'delta'):
            delta = 0.05 if event.delta > 0 else -0.05
        else:
            delta = 0.05 if event.num == 4 else -0.05

        self.adjust_opacity(delta)

    def toggle_collapse(self):
        """Toggle between collapsed and expanded view"""
        self.collapsed = not self.collapsed

        if self.collapsed:
            self.apply_collapsed_state()
        else:
            # Show all elements
            self.sep.pack(fill='x', pady=4)
            self.time_label.pack()
            self.stats_frame.pack(fill='x', pady=(4, 0))
            self.screenshots_label.pack(pady=(2, 0))
            self.resize_grip.pack(side='right', anchor='se')
            self.minimize_btn.config(text=" \u25BC ")  # Down arrow

        self.save_preferences()

    def apply_collapsed_state(self):
        """Apply collapsed state (hide most elements)"""
        self.sep.pack_forget()
        self.time_label.pack_forget()
        self.stats_frame.pack_forget()
        self.screenshots_label.pack_forget()
        self.resize_grip.pack_forget()
        self.minimize_btn.config(text=" \u25B2 ")  # Up arrow

    def show_settings_menu(self, event):
        """Show right-click settings menu"""
        menu = Menu(self.root, tearoff=0, bg='#2a2a3e', fg='#ffffff',
                    activebackground='#4a4a5e', activeforeground='#ffffff')

        # Opacity submenu
        opacity_menu = Menu(menu, tearoff=0, bg='#2a2a3e', fg='#ffffff',
                           activebackground='#4a4a5e', activeforeground='#ffffff')
        for opacity_val in [0.3, 0.5, 0.7, 0.85, 1.0]:
            label = f"{int(opacity_val * 100)}%"
            if abs(self.opacity - opacity_val) < 0.05:
                label = f"• {label}"
            opacity_menu.add_command(
                label=label,
                command=lambda v=opacity_val: self.set_opacity(v)
            )

        menu.add_cascade(label="Opacity", menu=opacity_menu)
        menu.add_separator()
        menu.add_command(label="Collapse/Expand", command=self.toggle_collapse)
        menu.add_separator()
        menu.add_command(label="Reset Size", command=self.reset_size)
        menu.add_command(label="Reset Position", command=self.reset_position)
        menu.add_separator()
        menu.add_command(label="Save Settings", command=self.save_preferences)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def set_opacity(self, value):
        """Set opacity to specific value"""
        self.opacity = value
        self.root.attributes('-alpha', self.opacity)
        self.save_preferences()

    def reset_size(self):
        """Reset widget to default size"""
        self.root.geometry('')  # Clear size to let it auto-size
        self.root.update_idletasks()
        self.save_preferences()

    def reset_position(self):
        """Reset widget to default bottom-right position"""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - 280
        y = screen_h - 180
        self.root.geometry(f'+{x}+{y}')
        self.save_preferences()

    def blink_recording(self):
        """Blink the recording indicator"""
        self.blink_on = not self.blink_on
        if self.blink_on:
            self.rec_dot.config(fg='#ff0000')
            self.rec_label.config(fg='#ff0000')
        else:
            self.rec_dot.config(fg='#661111')
            self.rec_label.config(fg='#661111')

        # Blink every 500ms
        self.root.after(500, self.blink_recording)

    def read_config(self):
        """Read config for anti-cheat status (base64 encoded)"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    encoded = f.read()
                    data = decode_data(encoded)
                    if data:
                        return data
        except:
            pass
        return {}

    def read_work_data(self):
        """Read today's work data from log file (base64 encoded)"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = self.data_dir / get_log_filename(date_str)

            if log_file.exists():
                with open(log_file, 'r') as f:
                    encoded = f.read()
                    data = decode_data(encoded)
                    if data:
                        return data
        except:
            pass
        return {}

    def format_time(self, seconds):
        """Format seconds as H:MM:SS"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h}:{m:02d}:{s:02d}"

    def update_display(self):
        """Update the display with current data"""
        data = self.read_work_data()
        config = self.read_config()

        work_secs = data.get('work_seconds', 0)
        idle_secs = data.get('idle_seconds', 0)
        suspicious_secs = data.get('suspicious_seconds', 0)
        screenshots = len(data.get('screenshots', []))
        suspicious_count = len(data.get('suspicious_events', []))

        # Check if currently idle (idle period is active)
        current_idle_start = data.get('current_idle_start')
        is_idle = current_idle_start is not None

        if is_idle:
            # Calculate current idle duration
            try:
                idle_start_time = datetime.fromisoformat(current_idle_start)
                current_idle_secs = (datetime.now() - idle_start_time).total_seconds()
                idle_str = self.format_time(current_idle_secs)
                self.time_label.config(text=f"IDLE: {idle_str}", fg='#e74c3c', bg='#4a1a1a')
                self.frame.config(bg='#4a1a1a')
                for w in [self.top_frame, self.rec_dot, self.rec_label,
                         self.anticheat_label, self.stats_frame, self.idle_label,
                         self.clock_label, self.screenshots_label]:
                    w.config(bg='#4a1a1a')
            except:
                self.time_label.config(text="IDLE", fg='#e74c3c', bg='#4a1a1a')
        else:
            # Update work time
            work_str = self.format_time(work_secs)
            self.time_label.config(text=f"Work: {work_str}", bg='#1a1a2e')

            # Reset background to normal
            self.frame.config(bg='#1a1a2e')
            for w in [self.top_frame, self.rec_dot, self.rec_label,
                     self.anticheat_label, self.stats_frame, self.idle_label,
                     self.clock_label, self.screenshots_label]:
                w.config(bg='#1a1a2e')

            # Color based on hours worked
            hours = work_secs / 3600
            if hours >= 8:
                self.time_label.config(fg='#2196F3')  # Blue - done!
            elif hours >= 4:
                self.time_label.config(fg='#4CAF50')  # Green - good progress
            else:
                self.time_label.config(fg='#ff9800')  # Orange - keep going

        # Total idle time today
        idle_mins = int(idle_secs // 60)
        self.idle_label.config(text=f"Idle: {idle_mins}m", fg='#e74c3c' if is_idle else '#ff9800')

        # Current time
        now = datetime.now().strftime("%I:%M %p")
        self.clock_label.config(text=now)

        # Screenshots
        self.screenshots_label.config(text=f"Screenshots: {screenshots}")

        # Anti-cheat status
        anticheat_on = config.get('anticheat_enabled', True)
        if anticheat_on:
            if suspicious_count > 0 or suspicious_secs > 60:
                # Alerts detected
                self.anticheat_label.config(
                    text=f"Anti-Cheat: {suspicious_count} ALERT",
                    fg='#e91e63'
                )
            else:
                self.anticheat_label.config(
                    text="Anti-Cheat: ON",
                    fg='#4CAF50'
                )
        else:
            self.anticheat_label.config(
                text="Anti-Cheat: OFF",
                fg='#888888'
            )

        # Update every second
        self.root.after(1000, self.update_display)

    def on_close(self):
        """Handle window close event"""
        self.save_preferences()
        self.root.destroy()

    def run(self):
        """Run the widget main loop"""
        # Save preferences on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Auto-save preferences periodically (every 5 seconds)
        def auto_save():
            self.save_preferences()
            self.root.after(5000, auto_save)

        auto_save()
        self.root.mainloop()


if __name__ == "__main__":
    widget = OverlayWidget()
    widget.run()
