"""
Work Monitor Overlay Widget
- Always on top, draggable
- Shows work time, idle status, anti-cheat status
- Recording indicator with live updates

Copyright (c) 2025 Enkhtamir Enkhdavaa
Contact: me@tamir.cc | enkhtamir.com
"""

import tkinter as tk
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

        # Semi-transparent (0.75 = 75% visible)
        self.root.attributes('-alpha', 0.75)

        # Position: bottom-right corner (above taskbar)
        self.position_widget()

        # Dark semi-transparent frame
        self.frame = tk.Frame(self.root, bg='#1a1a2e', padx=10, pady=6)
        self.frame.pack()

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

        # Bind drag to all elements
        for widget in [self.frame, self.top_frame, self.time_label,
                       self.stats_frame, self.idle_label, self.clock_label,
                       self.rec_dot, self.rec_label, self.anticheat_label,
                       self.screenshots_label]:
            widget.bind('<Button-1>', self.start_drag)
            widget.bind('<B1-Motion>', self.do_drag)

        # Data directory (parent folder, since we're in src/)
        self.data_dir = Path(__file__).parent.parent / ".cache"
        self.config_file = self.data_dir / "sys.dat"

        # Blink state
        self.blink_on = True

        # Start updating
        self.update_display()
        self.blink_recording()

    def position_widget(self):
        """Position in bottom-right corner"""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - 200
        y = screen_h - 140
        self.root.geometry(f'+{x}+{y}')

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_x
        y = self.root.winfo_y() + event.y - self.drag_y
        self.root.geometry(f'+{x}+{y}')

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
        now = datetime.now().strftime("%H:%M")
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

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    widget = OverlayWidget()
    widget.run()
