"""
Work Monitor - Employee Activity Tracking System
Tracks mouse activity, captures screenshots, and generates reports.
Includes anti-cheat detection for mouse jigglers and fake activity.

Copyright (c) 2025 Enkhtamir Enkhdavaa
Contact: me@tamir.cc | enkhtamir.com
"""

import os
import sys
import json
import time
import hashlib
import threading
import base64
import logging
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from pathlib import Path
import ctypes
from ctypes import wintypes
import math
import statistics
from collections import deque
import psutil
from email_reports import EmailReportSender
from dashboard_server import DashboardServer

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent / ".cache" / "work_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import required packages
try:
    from PIL import ImageGrab
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "pystray"])
    from PIL import ImageGrab, Image, ImageDraw
    import pystray
    from pystray import MenuItem as item

# Constants
APP_NAME = "WorkMonitor"
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent  # Go up from src/
DATA_DIR = BASE_DIR / ".cache"
SCREENSHOTS_DIR = BASE_DIR / ".tmp"
CONFIG_FILE = DATA_DIR / "sys.dat"
LOG_FILE = DATA_DIR / "app.dat"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Data encoding helpers
def encode_data(data):
    """Encode JSON data to base64"""
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()

def decode_data(encoded_str):
    """Decode base64 data to JSON"""
    try:
        json_str = base64.b64decode(encoded_str.encode()).decode()
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Failed to decode data: {e}")
        return None

def get_log_filename(date_str):
    """Generate obfuscated log filename from date"""
    encoded = base64.b64encode(date_str.encode()).decode().replace('=', '').replace('/', '_')
    return f"d{encoded}.dat"

def date_from_log_filename(filename):
    """Extract date from obfuscated log filename"""
    try:
        if filename.startswith('d') and filename.endswith('.dat'):
            encoded = filename[1:-4].replace('_', '/')
            # Add padding back
            padding = 4 - len(encoded) % 4
            if padding != 4:
                encoded += '=' * padding
            return base64.b64decode(encoded.encode()).decode()
    except (ValueError, UnicodeDecodeError) as e:
        logger.error(f"Failed to decode filename '{filename}': {e}")
    return None

# Default configuration
DEFAULT_CONFIG = {
    "work_start_hour": 9,
    "work_start_minute": 0,
    "work_end_hour": 17,
    "work_end_minute": 0,
    "screenshot_interval_minutes": 3,
    "idle_start_seconds": 300,        # Start counting as idle after 5 minutes
    "warning_screen_seconds": 360,    # Show red warning after 6 minutes
    "admin_password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
    "screenshot_retention_days": 14,
    # Anti-cheat settings
    "anticheat_enabled": True,
    "min_movement_distance": 50,  # Minimum pixels mouse must move to count as real activity
    "jitter_detection_window": 30,  # Seconds to analyze for jitter patterns
    "max_jitter_regularity": 0.85,  # Max regularity score (0-1) before flagging as jitter
    "require_keyboard_activity": True,  # Require some keyboard input
    "keyboard_check_interval": 300,  # Seconds - must have keyboard activity within this window
    "require_window_changes": True,  # Require active window to change occasionally
    "window_change_interval": 600,  # Seconds - must change windows within this interval
    # Email report settings
    "email_enabled": False,
    "email_to": "",
    "email_from": "",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "",
    "smtp_password": "",
    "smtp_use_tls": True,
    # Network dashboard settings
    "dashboard_server_enabled": False,
    "dashboard_port": 8080,
    # Autostart settings
    "autostart_enabled": True,
}


class AntiCheatDetector:
    """Detect mouse jigglers, fake activity, and cheating attempts"""

    def __init__(self, config):
        self.config = config
        # Movement history for pattern detection
        self.movement_history = deque(maxlen=100)  # (timestamp, x, y, distance)
        self.interval_history = deque(maxlen=50)   # Time between movements
        self.distance_history = deque(maxlen=50)   # Movement distances

        # Keyboard tracking
        self.last_keyboard_time = time.time()
        self.keyboard_count = 0

        # Window tracking
        self.last_window_change = time.time()
        self.last_window_title = ""
        self.window_change_count = 0

        # Cheat detection state
        self.is_cheating = False
        self.cheat_reason = ""
        self.cheat_score = 0  # 0-100, higher = more suspicious
        self.suspicious_events = deque(maxlen=50)  # Log of suspicious activity

    def calculate_distance(self, pos1, pos2):
        """Calculate distance between two points"""
        return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

    def add_movement(self, old_pos, new_pos, timestamp):
        """Record a mouse movement for analysis"""
        if old_pos is None:
            return

        distance = self.calculate_distance(old_pos, new_pos)
        self.movement_history.append((timestamp, new_pos[0], new_pos[1], distance))
        self.distance_history.append(distance)

        # Calculate interval from last movement
        if len(self.movement_history) >= 2:
            prev_time = self.movement_history[-2][0]
            interval = timestamp - prev_time
            self.interval_history.append(interval)

    def detect_jitter_pattern(self):
        """Detect if movements follow a jitter/oscillating pattern"""
        if len(self.movement_history) < 10:
            return False, 0, ""

        # Get recent movements
        recent = list(self.movement_history)[-20:]

        # Check 1: Very small movements (jiggler typically moves 1-5 pixels)
        distances = [m[3] for m in recent]
        avg_distance = statistics.mean(distances) if distances else 0

        if avg_distance < self.config.get('min_movement_distance'):
            # Small movements detected - check for regularity

            # Check 2: Regular intervals (jigglers move at fixed intervals)
            if len(self.interval_history) >= 5:
                intervals = list(self.interval_history)[-10:]
                if len(intervals) >= 3:
                    try:
                        interval_std = statistics.stdev(intervals)
                        interval_mean = statistics.mean(intervals)
                        # Coefficient of variation - low = very regular
                        if interval_mean > 0:
                            cv = interval_std / interval_mean
                            regularity = 1 - min(cv, 1)  # 0=random, 1=perfectly regular

                            if regularity > self.config.get('max_jitter_regularity'):
                                return True, regularity * 100, f"Regular micro-movements detected (regularity: {regularity:.1%})"
                    except statistics.StatisticsError as e:
                        logger.error(f"Failed to calculate interval statistics: {e}")

            # Check 3: Oscillating pattern (back and forth)
            if len(recent) >= 6:
                x_positions = [m[1] for m in recent]
                y_positions = [m[2] for m in recent]

                # Check for alternating directions
                x_changes = [x_positions[i+1] - x_positions[i] for i in range(len(x_positions)-1)]
                y_changes = [y_positions[i+1] - y_positions[i] for i in range(len(y_positions)-1)]

                # Count direction changes
                x_reversals = sum(1 for i in range(len(x_changes)-1) if x_changes[i] * x_changes[i+1] < 0)
                y_reversals = sum(1 for i in range(len(y_changes)-1) if y_changes[i] * y_changes[i+1] < 0)

                total_reversals = x_reversals + y_reversals
                max_reversals = len(x_changes) - 1 + len(y_changes) - 1

                if max_reversals > 0:
                    reversal_rate = total_reversals / max_reversals
                    # High reversal rate = oscillating pattern
                    if reversal_rate > 0.7:
                        return True, reversal_rate * 100, f"Oscillating mouse pattern detected (reversal rate: {reversal_rate:.1%})"

        return False, 0, ""

    def detect_no_keyboard(self):
        """Check if keyboard activity is missing for too long"""
        if not self.config.get('require_keyboard_activity'):
            return False, ""

        elapsed = time.time() - self.last_keyboard_time
        threshold = self.config.get('keyboard_check_interval')

        if elapsed > threshold:
            return True, f"No keyboard activity for {int(elapsed)}s (threshold: {threshold}s)"
        return False, ""

    def detect_no_window_change(self):
        """Check if active window hasn't changed"""
        if not self.config.get('require_window_changes'):
            return False, ""

        elapsed = time.time() - self.last_window_change
        threshold = self.config.get('window_change_interval')

        if elapsed > threshold:
            return True, f"Same window for {int(elapsed)}s (threshold: {threshold}s)"
        return False, ""

    def record_keyboard_activity(self):
        """Record keyboard activity"""
        self.last_keyboard_time = time.time()
        self.keyboard_count += 1

    def check_active_window(self):
        """Check and record active window changes"""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            current_title = buf.value

            if current_title != self.last_window_title:
                self.last_window_title = current_title
                self.last_window_change = time.time()
                self.window_change_count += 1
                return True
        except (OSError, AttributeError) as e:
            logger.error(f"Failed to get active window: {e}")
        return False

    def analyze(self):
        """Run all cheat detection and return result"""
        if not self.config.get('anticheat_enabled'):
            return False, 0, "Anti-cheat disabled"

        issues = []
        total_score = 0

        # Check for jitter/jiggler
        is_jitter, jitter_score, jitter_reason = self.detect_jitter_pattern()
        if is_jitter:
            issues.append(jitter_reason)
            total_score += jitter_score * 0.5  # Weight: 50%

        # Check for no keyboard
        no_keyboard, kb_reason = self.detect_no_keyboard()
        if no_keyboard:
            issues.append(kb_reason)
            total_score += 30  # Fixed penalty

        # Check for no window changes
        no_window, win_reason = self.detect_no_window_change()
        if no_window:
            issues.append(win_reason)
            total_score += 20  # Fixed penalty

        self.cheat_score = min(100, total_score)
        self.is_cheating = self.cheat_score >= 50
        self.cheat_reason = "; ".join(issues) if issues else "None"

        # Log suspicious activity
        if self.is_cheating:
            self.suspicious_events.append({
                "time": datetime.now().isoformat(),
                "score": self.cheat_score,
                "reasons": issues
            })

        return self.is_cheating, self.cheat_score, self.cheat_reason

    def get_status(self):
        """Get current anti-cheat status"""
        return {
            "is_cheating": self.is_cheating,
            "score": self.cheat_score,
            "reason": self.cheat_reason,
            "keyboard_last": time.time() - self.last_keyboard_time,
            "window_last": time.time() - self.last_window_change,
            "suspicious_count": len(self.suspicious_events)
        }


class KeyboardTracker:
    """Track keyboard activity using Windows API"""

    def __init__(self, anticheat=None):
        self.anticheat = anticheat
        self.last_key_state = {}
        self.key_count = 0
        self.last_activity = time.time()

    def check_activity(self):
        """Check for any keyboard activity"""
        try:
            # Check common keys (letters, numbers, space, enter, etc.)
            keys_to_check = list(range(0x08, 0x5B)) + list(range(0x60, 0x88))  # VK codes

            for vk in keys_to_check:
                state = ctypes.windll.user32.GetAsyncKeyState(vk)
                was_pressed = self.last_key_state.get(vk, 0)

                # Key was just pressed (bit 0 = pressed since last call)
                if state & 0x0001 and not (was_pressed & 0x0001):
                    self.key_count += 1
                    self.last_activity = time.time()
                    if self.anticheat:
                        self.anticheat.record_keyboard_activity()

                self.last_key_state[vk] = state

            return self.key_count
        except (OSError, AttributeError) as e:
            logger.error(f"Failed to check keyboard state: {e}")
            return 0

    def get_idle_seconds(self):
        """Get seconds since last keyboard activity"""
        return time.time() - self.last_activity


class MouseTracker:
    """Track mouse position using Windows API with anti-cheat integration"""

    class POINT(ctypes.Structure):
        _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

    def __init__(self, config=None):
        self.last_position = None
        self.last_move_time = time.time()
        self.config = config
        self.anticheat = AntiCheatDetector(config) if config else None
        self.total_distance = 0
        self.real_activity = True  # False if cheating detected

    def get_position(self):
        """Get current mouse position"""
        pt = self.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)

    def has_moved(self):
        """Check if mouse has moved since last check"""
        current_pos = self.get_position()
        current_time = time.time()

        if self.last_position is None:
            self.last_position = current_pos
            return True

        moved = current_pos != self.last_position
        if moved:
            # Record movement for anti-cheat analysis
            if self.anticheat:
                self.anticheat.add_movement(self.last_position, current_pos, current_time)
                self.anticheat.check_active_window()

            # Calculate distance
            distance = math.sqrt(
                (current_pos[0] - self.last_position[0])**2 +
                (current_pos[1] - self.last_position[1])**2
            )
            self.total_distance += distance

            self.last_position = current_pos
            self.last_move_time = current_time

        return moved

    def is_real_activity(self):
        """Check if current activity is genuine (not a jiggler)"""
        if not self.anticheat:
            return True

        is_cheating, score, reason = self.anticheat.analyze()
        self.real_activity = not is_cheating
        return self.real_activity

    def get_idle_seconds(self):
        """Get seconds since last mouse movement"""
        return time.time() - self.last_move_time

    def get_cheat_status(self):
        """Get anti-cheat status"""
        if self.anticheat:
            return self.anticheat.get_status()
        return {"is_cheating": False, "score": 0, "reason": "Anti-cheat not initialized"}


class Config:
    """Configuration manager with thread safety"""

    def __init__(self):
        self._lock = threading.Lock()
        self.config = self.load()

    def load(self):
        """Load configuration from file (base64 encoded)"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    encoded = f.read()
                    loaded = decode_data(encoded)
                    if loaded:
                        return {**DEFAULT_CONFIG, **loaded}
            except (IOError, OSError) as e:
                logger.error(f"Failed to load config from {CONFIG_FILE}: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def save(self):
        """Save configuration to file using atomic write (base64 encoded)"""
        with self._lock:
            try:
                # Atomic write: write to temp file, then rename
                temp_file = CONFIG_FILE.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    f.write(encode_data(self.config))
                temp_file.replace(CONFIG_FILE)
            except (IOError, OSError) as e:
                logger.error(f"Failed to save config: {e}")

    def get(self, key):
        with self._lock:
            return self.config.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        with self._lock:
            self.config[key] = value
        self.save()

    def verify_password(self, password):
        """Verify admin password"""
        return hashlib.sha256(password.encode()).hexdigest() == self.config.get("admin_password_hash")

    def set_password(self, new_password):
        """Set new admin password"""
        self.config["admin_password_hash"] = hashlib.sha256(new_password.encode()).hexdigest()
        self.save()


class ActivityLogger:
    """Log and track activity data with thread safety"""

    def __init__(self):
        self._lock = threading.Lock()
        self.today_log = self.load_today()

    def get_today_file(self):
        """Get today's log file path (obfuscated name)"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return DATA_DIR / get_log_filename(date_str)

    def load_today(self):
        """Load today's activity log (base64 encoded)"""
        log_file = self.get_today_file()
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    encoded = f.read()
                    data = decode_data(encoded)
                    if data:
                        return data
            except (IOError, OSError) as e:
                logger.error(f"Failed to load today's log from {log_file}: {e}")

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "work_seconds": 0,
            "idle_seconds": 0,
            "overtime_seconds": 0,
            "suspicious_seconds": 0,
            "screenshots": [],
            "sessions": [],
            "current_session_start": None,
            "suspicious_events": [],
            "keyboard_activity_count": 0,
            "window_change_count": 0,
            "idle_periods": [],
            "current_idle_start": None
        }

    def save(self):
        """Save today's log using atomic write (base64 encoded)"""
        with self._lock:
            try:
                log_file = self.get_today_file()
                # Atomic write: write to temp file, then rename
                temp_file = log_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    f.write(encode_data(self.today_log))
                temp_file.replace(log_file)
            except (IOError, OSError) as e:
                logger.error(f"Failed to save activity log: {e}")

    def add_work_time(self, seconds):
        """Add work time (only during office hours)"""
        with self._lock:
            self.today_log["work_seconds"] += seconds
        self.save()

    def add_idle_time(self, seconds):
        """Add idle time"""
        with self._lock:
            self.today_log["idle_seconds"] += seconds
        self.save()

    def add_screenshot(self, filepath, is_suspicious=False):
        """Record screenshot"""
        with self._lock:
            self.today_log["screenshots"].append({
                "time": datetime.now().isoformat(),
                "path": str(filepath),
                "suspicious": is_suspicious
            })
        self.save()

    def add_suspicious_time(self, seconds, reason=""):
        """Add time flagged as suspicious activity"""
        with self._lock:
            self.today_log["suspicious_seconds"] += seconds
            if reason:
                self.today_log["suspicious_events"].append({
                    "time": datetime.now().isoformat(),
                    "duration": seconds,
                    "reason": reason
                })
        self.save()

    def update_activity_counts(self, keyboard_count, window_count):
        """Update keyboard and window activity counts"""
        with self._lock:
            self.today_log["keyboard_activity_count"] = keyboard_count
            self.today_log["window_change_count"] = window_count
        self.save()

    def start_idle_period(self):
        """Mark the start of an idle period (person left)"""
        with self._lock:
            if self.today_log.get("current_idle_start") is None:
                self.today_log["current_idle_start"] = datetime.now().isoformat()
        self.save()

    def end_idle_period(self):
        """Mark the end of an idle period (person returned)"""
        with self._lock:
            if self.today_log.get("current_idle_start") is not None:
                start_time = self.today_log["current_idle_start"]
                end_time = datetime.now().isoformat()
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.now()
                duration_seconds = (end_dt - start_dt).total_seconds()

                if duration_seconds > 60:  # Only log if > 1 minute
                    if "idle_periods" not in self.today_log:
                        self.today_log["idle_periods"] = []
                    self.today_log["idle_periods"].append({
                        "left": start_time,
                        "returned": end_time,
                        "duration_seconds": duration_seconds
                    })
                self.today_log["current_idle_start"] = None
        self.save()

    def get_idle_periods(self):
        """Get list of idle periods with formatted times"""
        periods = []
        with self._lock:
            idle_periods = self.today_log.get("idle_periods", []).copy()

        for period in idle_periods:
            try:
                left_dt = datetime.fromisoformat(period["left"])
                returned_dt = datetime.fromisoformat(period["returned"])
                duration_mins = int(period["duration_seconds"] / 60)
                periods.append({
                    "left": left_dt.strftime("%I:%M:%S %p"),
                    "returned": returned_dt.strftime("%I:%M:%S %p"),
                    "duration": f"{duration_mins} min"
                })
            except (ValueError, KeyError, TypeError) as e:
                logger.error(f"Failed to format idle period {period}: {e}")
        return periods

    @staticmethod
    def load_date(date_str):
        """Load log for a specific date (base64 encoded)"""
        log_file = DATA_DIR / get_log_filename(date_str)
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    encoded = f.read()
                    return decode_data(encoded)
            except (IOError, OSError) as e:
                logger.error(f"Failed to load log for date {date_str}: {e}")
        return None

    @staticmethod
    def get_week_summary():
        """Get summary for current week (Mon-Sun)"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        return ActivityLogger.get_date_range_summary(start_of_week, today)

    @staticmethod
    def get_month_summary():
        """Get summary for current month"""
        today = datetime.now()
        start_of_month = today.replace(day=1)
        return ActivityLogger.get_date_range_summary(start_of_month, today)

    @staticmethod
    def get_year_summary():
        """Get summary for current year"""
        today = datetime.now()
        start_of_year = today.replace(month=1, day=1)
        return ActivityLogger.get_date_range_summary(start_of_year, today)

    @staticmethod
    def get_date_range_summary(start_date, end_date):
        """Get summary for a date range"""
        total_work = 0
        total_idle = 0
        total_overtime = 0
        total_suspicious = 0
        total_screenshots = 0
        daily_data = []

        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            log = ActivityLogger.load_date(date_str)
            if log:
                work_h = log.get("work_seconds", 0) / 3600
                idle_h = log.get("idle_seconds", 0) / 3600
                overtime_h = log.get("overtime_seconds", 0) / 3600
                suspicious_h = log.get("suspicious_seconds", 0) / 3600
                screenshots = len(log.get("screenshots", []))

                total_work += work_h
                total_idle += idle_h
                total_overtime += overtime_h
                total_suspicious += suspicious_h
                total_screenshots += screenshots

                daily_data.append({
                    "date": date_str,
                    "day_name": current.strftime("%A"),
                    "work_hours": work_h,
                    "idle_hours": idle_h,
                    "overtime_hours": overtime_h,
                    "suspicious_hours": suspicious_h,
                    "screenshots": screenshots
                })
            current += timedelta(days=1)

        return {
            "work_hours": total_work,
            "idle_hours": total_idle,
            "overtime_hours": total_overtime,
            "suspicious_hours": total_suspicious,
            "real_work_hours": max(0, total_work - total_suspicious),
            "screenshot_count": total_screenshots,
            "days_worked": len([d for d in daily_data if d["work_hours"] > 0]),
            "daily_data": daily_data,
            "avg_work_per_day": total_work / max(1, len([d for d in daily_data if d["work_hours"] > 0]))
        }

    def get_summary(self):
        """Get today's summary"""
        suspicious_hours = self.today_log.get("suspicious_seconds", 0) / 3600
        return {
            "date": self.today_log["date"],
            "work_hours": self.today_log["work_seconds"] / 3600,
            "idle_hours": self.today_log["idle_seconds"] / 3600,
            "overtime_hours": self.today_log["overtime_seconds"] / 3600,
            "suspicious_hours": suspicious_hours,
            "total_hours": (self.today_log["work_seconds"] + self.today_log["overtime_seconds"]) / 3600,
            "real_work_hours": max(0, (self.today_log["work_seconds"] / 3600) - suspicious_hours),
            "screenshot_count": len(self.today_log["screenshots"]),
            "suspicious_count": len(self.today_log.get("suspicious_events", [])),
            "keyboard_count": self.today_log.get("keyboard_activity_count", 0),
            "window_changes": self.today_log.get("window_change_count", 0),
            "idle_periods": self.get_idle_periods()
        }


class ScreenshotManager:
    """Handle screenshot capture and cleanup"""

    def __init__(self, config):
        self.config = config

    def capture(self):
        """Capture screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename

        try:
            screenshot = ImageGrab.grab()
            screenshot.save(filepath, "PNG")
            return filepath
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None

    def cleanup_old(self):
        """Remove screenshots and logs older than retention period"""
        retention_days = self.config.get("screenshot_retention_days")
        cutoff = datetime.now() - timedelta(days=retention_days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        removed_screenshots = 0
        removed_logs = 0

        # Clean old screenshots
        for file in SCREENSHOTS_DIR.glob("screenshot_*.png"):
            try:
                date_str = file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y%m%d")
                if file_date < cutoff:
                    file.unlink()
                    removed_screenshots += 1
            except (ValueError, IndexError, OSError) as e:
                logger.error(f"Failed to clean screenshot {file}: {e}")

        # Clean old log files
        for file in DATA_DIR.glob("d*.dat"):
            try:
                date_str = date_from_log_filename(file.name)
                if date_str and date_str < cutoff_str:
                    file.unlink()
                    removed_logs += 1
            except OSError as e:
                logger.error(f"Failed to clean log file {file}: {e}")

        return removed_screenshots + removed_logs


class HTMLReportGenerator:
    """Generate HTML reports with Daily/Weekly/Monthly/Yearly views"""

    @staticmethod
    def generate_dashboard(summary, config, screenshots_today=None, logger=None):
        """Generate main dashboard HTML with all views"""
        # Convert work hours to 12-hour format with AM/PM
        work_start_dt = datetime.now().replace(hour=config.get('work_start_hour'), minute=config.get('work_start_minute'))
        work_end_dt = datetime.now().replace(hour=config.get('work_end_hour'), minute=config.get('work_end_minute'))
        work_start = work_start_dt.strftime("%I:%M %p")
        work_end = work_end_dt.strftime("%I:%M %p")

        # Get period summaries
        week_summary = ActivityLogger.get_week_summary()
        month_summary = ActivityLogger.get_month_summary()
        year_summary = ActivityLogger.get_year_summary()

        # Helper function to generate screenshot thumbnails
        def generate_screenshots_html(screenshots_list, max_count=20):
            html = ""
            if screenshots_list:
                for ss in screenshots_list[-max_count:]:
                    ss_time = datetime.fromisoformat(ss['time']).strftime("%Y-%m-%d %I:%M %p")
                    ss_path = ss.get('path', '')
                    suspicious = ss.get('suspicious', False)
                    border_style = 'border: 2px solid #e91e63;' if suspicious else 'border: 2px solid #333;'
                    html += f'''<a href="file:///{ss_path.replace(chr(92), '/')}" target="_blank" class="screenshot-thumb" style="{border_style}" title="{ss_time}">
                        <img src="file:///{ss_path.replace(chr(92), '/')}" alt="{ss_time}">
                        <span>{ss_time.split(' ')[1]}</span>
                    </a>\n'''
            return html

        # Screenshots HTML - clickable links
        screenshots_html = ""
        if screenshots_today:
            for ss in screenshots_today[-20:]:  # Show last 20
                ss_time = datetime.fromisoformat(ss['time']).strftime("%I:%M:%S %p")
                ss_path = ss.get('path', '')
                suspicious = ss.get('suspicious', False)
                border_style = 'border: 2px solid #e91e63;' if suspicious else 'border: 2px solid #333;'
                screenshots_html += f'''<a href="file:///{ss_path.replace(chr(92), '/')}" target="_blank" class="screenshot-thumb" style="{border_style}" title="{ss_time}">
                    <img src="file:///{ss_path.replace(chr(92), '/')}" alt="{ss_time}">
                    <span>{ss_time}</span>
                </a>\n'''

        # Idle periods HTML (for detailed view)
        idle_periods = summary.get('idle_periods', [])
        idle_periods_html = ""
        for period in idle_periods:
            idle_periods_html += f'''<tr>
                <td>{period['left']}</td>
                <td>{period['returned']}</td>
                <td>{period['duration']}</td>
            </tr>'''

        # Helper to generate day breakdown with collapsible screenshots
        def generate_day_breakdown(daily_data, max_screenshots=10):
            html = ""
            for day in daily_data:
                day_log = ActivityLogger.load_date(day['date'])
                day_screenshots = day_log.get('screenshots', []) if day_log else []
                day_screenshots_html = generate_screenshots_html(day_screenshots[-max_screenshots:], max_screenshots) if day_screenshots else '<span style="opacity:0.5;">No screenshots</span>'
                day_id = day['date'].replace('-', '')

                html += f'''
                <div class="day-section">
                    <button class="day-header-btn" onclick="toggleDetails('day-{day_id}')">
                        <span class="day-name">{day['day_name']} - {day['date']}</span>
                        <span class="day-stats">Work: {day['work_hours']:.1f}h | Idle: {day['idle_hours']:.1f}h | Screenshots: {len(day_screenshots)} ▼</span>
                    </button>
                    <div id="day-{day_id}" class="day-screenshots-collapsible">
                        {day_screenshots_html}
                    </div>
                </div>'''
            return html

        # Weekly breakdown HTML with screenshots per day
        weekly_breakdown_html = generate_day_breakdown(week_summary.get('daily_data', []), 10)

        # Monthly breakdown HTML with screenshots per day
        monthly_breakdown_html = generate_day_breakdown(month_summary.get('daily_data', []), 6)

        # Pre-calculate conditional strings to avoid f-string nesting issues
        idle_periods_count_text = "No idle periods" if not idle_periods else f"{len(idle_periods)} periods"
        idle_periods_content = '<p style="opacity:0.6;">No idle periods recorded today</p>' if not idle_periods_html else f'''
                <table>
                    <tr><th>Left At</th><th>Returned At</th><th>Duration</th></tr>
                    {idle_periods_html}
                </table>
                '''
        screenshots_content = screenshots_html if screenshots_html else '<p style="opacity:0.6;">No screenshots yet today</p>'
        weekly_daily_content = '<p style="opacity:0.6;">No data yet this week</p>' if not weekly_breakdown_html else weekly_breakdown_html
        monthly_daily_content = '<p style="opacity:0.6;">No data yet this month</p>' if not monthly_breakdown_html else monthly_breakdown_html

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>Work Monitor Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); min-height: 100vh; color: #fff; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 25px; background: rgba(255,255,255,0.1); border-radius: 20px; }}
        .header h1 {{ font-size: 2.2em; margin-bottom: 8px; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .header-btn {{ display: inline-block; padding: 10px 20px; color: #fff; text-decoration: none; border-radius: 20px; font-size: 0.9em; margin: 5px; transition: opacity 0.2s; }}
        .header-btn:hover {{ opacity: 0.8; }}
        .tabs {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }}
        .tab {{ padding: 12px 30px; background: rgba(255,255,255,0.1); border: none; color: #fff; border-radius: 25px; cursor: pointer; font-size: 1em; transition: all 0.3s; }}
        .tab:hover, .tab.active {{ background: linear-gradient(90deg, #00d2ff, #3a7bd5); }}
        .tab-content {{ display: none; }} .tab-content.active {{ display: block; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .stat-card {{ background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; text-align: center; transition: transform 0.3s; }}
        .stat-card:hover {{ transform: translateY(-3px); }}
        .stat-value {{ font-size: 2.2em; font-weight: bold; margin: 8px 0; }}
        .stat-label {{ font-size: 0.95em; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; }}
        .stat-sublabel {{ font-size: 0.8em; opacity: 0.6; margin-top: 5px; }}
        .work {{ border-left: 4px solid #4CAF50; }} .work .stat-value {{ color: #4CAF50; }}
        .idle {{ border-left: 4px solid #ff9800; }} .idle .stat-value {{ color: #ff9800; }}
        .after-hours {{ border-left: 4px solid #e91e63; }} .after-hours .stat-value {{ color: #e91e63; }}
        .suspicious {{ border-left: 4px solid #9c27b0; }} .suspicious .stat-value {{ color: #9c27b0; }}
        .section {{ background: rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; margin-bottom: 20px; }}
        .section h2 {{ margin-bottom: 15px; color: #3a7bd5; font-size: 1.3em; }}
        .collapsible {{ cursor: pointer; padding: 15px 20px; background: rgba(255,255,255,0.05); border: none; color: #fff; width: 100%; text-align: left; font-size: 1.1em; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
        .collapsible:hover {{ background: rgba(255,255,255,0.1); }}
        .collapsible-content {{ display: none; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; margin-bottom: 15px; }}
        .collapsible-content.show {{ display: block; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ color: #3a7bd5; font-weight: 600; }}
        .screenshot-item {{ background: rgba(255,255,255,0.05); padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; display: inline-block; margin-right: 10px; }}
        .screenshot-thumb {{ display: inline-block; margin: 5px; text-decoration: none; border-radius: 8px; overflow: hidden; transition: transform 0.2s; }}
        .screenshot-thumb:hover {{ transform: scale(1.05); }}
        .screenshot-thumb img {{ width: 120px; height: 70px; object-fit: cover; display: block; }}
        .screenshot-thumb span {{ display: block; background: rgba(0,0,0,0.7); color: #fff; font-size: 10px; padding: 4px; text-align: center; }}
        .day-section {{ background: rgba(255,255,255,0.05); border-radius: 10px; margin-bottom: 10px; overflow: hidden; }}
        .day-header-btn {{ display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 12px 15px; background: rgba(255,255,255,0.03); border: none; color: #fff; cursor: pointer; transition: background 0.2s; }}
        .day-header-btn:hover {{ background: rgba(255,255,255,0.08); }}
        .day-name {{ font-size: 1em; font-weight: bold; color: #00d2ff; }}
        .day-stats {{ font-size: 0.85em; color: #888; }}
        .day-screenshots-collapsible {{ display: none; padding: 10px 15px; flex-wrap: wrap; gap: 5px; }}
        .day-screenshots-collapsible.show {{ display: flex; }}
        .footer {{ text-align: center; margin-top: 30px; opacity: 0.6; font-size: 0.85em; }}
        .status-indicator {{ display: inline-block; width: 10px; height: 10px; background: #4CAF50; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        .summary-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .day-row {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 8px; }}
        .day-row:hover {{ background: rgba(255,255,255,0.08); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="status-indicator"></span>Work Monitor Dashboard</h1>
            <div style="opacity: 0.8;">Office Hours: {work_start} - {work_end}</div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('daily')">Daily</button>
            <button class="tab" onclick="showTab('weekly')">Weekly</button>
            <button class="tab" onclick="showTab('monthly')">Monthly</button>
            <button class="tab" onclick="showTab('yearly')">Yearly</button>
        </div>

        <!-- DAILY TAB -->
        <div id="daily" class="tab-content active">
            <h2 style="text-align:center; margin-bottom:20px; color:#00d2ff;">{summary['date']}</h2>
            <div class="stats-grid">
                <div class="stat-card work"><div class="stat-label">Work Time</div><div class="stat-value">{summary['work_hours']:.2f}h</div><div class="stat-sublabel">{int(summary['work_hours'] * 60)} min</div></div>
                <div class="stat-card idle"><div class="stat-label">Idle Time</div><div class="stat-value">{summary['idle_hours']:.2f}h</div><div class="stat-sublabel">{int(summary['idle_hours'] * 60)} min</div></div>
                <div class="stat-card suspicious"><div class="stat-label">Suspicious</div><div class="stat-value">{summary.get('suspicious_hours', 0):.2f}h</div><div class="stat-sublabel">{summary.get('suspicious_count', 0)} alerts</div></div>
                <div class="stat-card" style="border-left: 4px solid #2196F3;"><div class="stat-label">Real Work</div><div class="stat-value" style="color:#2196F3;">{summary.get('real_work_hours', summary['work_hours']):.2f}h</div></div>
            </div>
            <div class="stats-grid">
                <div class="stat-card" style="border-left: 4px solid #00bcd4;"><div class="stat-label">Keystrokes</div><div class="stat-value" style="color:#00bcd4;">{summary.get('keyboard_count', 0):,}</div></div>
                <div class="stat-card" style="border-left: 4px solid #8bc34a;"><div class="stat-label">Window Switches</div><div class="stat-value" style="color:#8bc34a;">{summary.get('window_changes', 0)}</div></div>
                <div class="stat-card" style="border-left: 4px solid #ff5722;"><div class="stat-label">Screenshots</div><div class="stat-value" style="color:#ff5722;">{summary['screenshot_count']}</div></div>
            </div>

            <button class="collapsible" onclick="toggleDetails('idle-details')">
                <span>Idle Periods (Left / Returned)</span>
                <span>{idle_periods_count_text}</span>
            </button>
            <div id="idle-details" class="collapsible-content">
                {idle_periods_content}
            </div>

            <button class="collapsible" onclick="toggleDetails('screenshots-details')">
                <span>Recent Screenshots</span>
                <span>{summary['screenshot_count']} total</span>
            </button>
            <div id="screenshots-details" class="collapsible-content">
                {screenshots_content}
            </div>
        </div>

        <!-- WEEKLY TAB -->
        <div id="weekly" class="tab-content">
            <h2 style="text-align:center; margin-bottom:20px; color:#00d2ff;">This Week</h2>
            <div class="stats-grid">
                <div class="stat-card work"><div class="stat-label">Total Work</div><div class="stat-value">{week_summary['work_hours']:.1f}h</div><div class="stat-sublabel">{week_summary['days_worked']} days worked</div></div>
                <div class="stat-card idle"><div class="stat-label">Total Idle</div><div class="stat-value">{week_summary['idle_hours']:.1f}h</div></div>
                <div class="stat-card suspicious"><div class="stat-label">Suspicious</div><div class="stat-value">{week_summary['suspicious_hours']:.1f}h</div></div>
                <div class="stat-card" style="border-left: 4px solid #2196F3;"><div class="stat-label">Avg/Day</div><div class="stat-value" style="color:#2196F3;">{week_summary['avg_work_per_day']:.1f}h</div></div>
            </div>
            <div class="section">
                <h2>Daily Breakdown</h2>
                {weekly_daily_content}
            </div>
        </div>

        <!-- MONTHLY TAB -->
        <div id="monthly" class="tab-content">
            <h2 style="text-align:center; margin-bottom:20px; color:#00d2ff;">This Month</h2>
            <div class="stats-grid">
                <div class="stat-card work"><div class="stat-label">Total Work</div><div class="stat-value">{month_summary['work_hours']:.1f}h</div><div class="stat-sublabel">{month_summary['days_worked']} days worked</div></div>
                <div class="stat-card idle"><div class="stat-label">Total Idle</div><div class="stat-value">{month_summary['idle_hours']:.1f}h</div></div>
                <div class="stat-card suspicious"><div class="stat-label">Suspicious</div><div class="stat-value">{month_summary['suspicious_hours']:.1f}h</div></div>
                <div class="stat-card" style="border-left: 4px solid #2196F3;"><div class="stat-label">Real Work</div><div class="stat-value" style="color:#2196F3;">{month_summary['real_work_hours']:.1f}h</div></div>
            </div>
            <div class="section">
                <h2>Daily Breakdown</h2>
                {monthly_daily_content}
            </div>
        </div>

        <!-- YEARLY TAB -->
        <div id="yearly" class="tab-content">
            <h2 style="text-align:center; margin-bottom:20px; color:#00d2ff;">This Year ({datetime.now().year})</h2>
            <div class="stats-grid">
                <div class="stat-card work"><div class="stat-label">Total Work</div><div class="stat-value">{year_summary['work_hours']:,.0f}h</div><div class="stat-sublabel">{year_summary['days_worked']} days worked</div></div>
                <div class="stat-card idle"><div class="stat-label">Total Idle</div><div class="stat-value">{year_summary['idle_hours']:,.0f}h</div></div>
                <div class="stat-card suspicious"><div class="stat-label">Suspicious</div><div class="stat-value">{year_summary['suspicious_hours']:,.0f}h</div></div>
                <div class="stat-card" style="border-left: 4px solid #2196F3;"><div class="stat-label">Real Work</div><div class="stat-value" style="color:#2196F3;">{year_summary['real_work_hours']:,.0f}h</div></div>
            </div>
            <div class="section">
                <div class="summary-row"><span>Real Work Hours:</span><span style="color:#4CAF50;">{year_summary['real_work_hours']:.0f}h</span></div>
                <div class="summary-row"><span>Average per Day:</span><span>{year_summary['avg_work_per_day']:.1f}h</span></div>
                <div class="summary-row"><span>Total Screenshots:</span><span>{year_summary['screenshot_count']}</span></div>
            </div>
        </div>

        <div class="footer">
            <p>Work Monitor v1.0 | Auto-refreshes every 30 seconds</p>
            <p style="margin-top:5px;">&copy; 2025 Enkhtamir Enkhdavaa | <a href="https://enkhtamir.com" style="color:#3a7bd5;">enkhtamir.com</a></p>
        </div>
    </div>

    <script>
        function showTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }}
        function toggleDetails(id) {{
            var el = document.getElementById(id);
            el.classList.toggle('show');
        }}
    </script>
</body>
</html>'''
        return html

    @staticmethod
    def save_dashboard(summary, config, logger):
        """Save dashboard HTML file"""
        screenshots_today = logger.today_log.get("screenshots", [])
        html = HTMLReportGenerator.generate_dashboard(summary, config, screenshots_today)
        dashboard_path = BASE_DIR / "dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return dashboard_path


class AdminPanel(tk.Toplevel):
    """Admin configuration panel with Apple-inspired design"""

    def __init__(self, parent, config, logger=None, email_sender=None, dashboard_server=None):
        super().__init__(parent)
        self.config = config
        self.logger = logger
        self.email_sender = email_sender
        self.dashboard_server = dashboard_server
        self.title("Settings - WorkMonitor")
        self.geometry("700x900")
        self.configure(bg='#f5f5f7')
        self.resizable(True, True)
        self.minsize(700, 900)

        self.create_widgets()

    def create_widgets(self):
        """Create admin panel widgets with modern, sectioned design"""
        # Main scrollable container
        canvas = tk.Canvas(self, bg='#f5f5f7', highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f5f7')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True, padx=30, pady=30)
        scrollbar.pack(side='right', fill='y')

        # Title
        title = tk.Label(scrollable_frame, text="Settings",
                        font=('SF Pro Display', 26, 'bold'),
                        bg='#f5f5f7', fg='#1d1d1f')
        title.pack(pady=(0, 30))

        # SECTION 1: Work Hours
        self._create_section(scrollable_frame, "Work Hours", "Configure your daily work schedule")
        work_card = self._create_card(scrollable_frame)

        hours_frame = tk.Frame(work_card, bg='#ffffff')
        hours_frame.pack(fill='x', pady=8)

        # Start time
        start_label = tk.Label(hours_frame, text="Start Time", font=('SF Pro Text', 13),
                              bg='#ffffff', fg='#86868b')
        start_label.pack(side='left')

        start_inputs = tk.Frame(hours_frame, bg='#ffffff')
        start_inputs.pack(side='right')

        self.start_hour = tk.Entry(start_inputs, font=('SF Pro Text', 13), width=4,
                                   relief='solid', bd=1)
        self.start_hour.insert(0, str(self.config.get('work_start_hour')))
        self.start_hour.pack(side='left', padx=2)
        tk.Label(start_inputs, text=":", bg='#ffffff', font=('SF Pro Text', 13)).pack(side='left')
        self.start_minute = tk.Entry(start_inputs, font=('SF Pro Text', 13), width=4,
                                     relief='solid', bd=1)
        self.start_minute.insert(0, str(self.config.get('work_start_minute')))
        self.start_minute.pack(side='left', padx=2)

        # End time
        end_frame = tk.Frame(work_card, bg='#ffffff')
        end_frame.pack(fill='x', pady=8)

        end_label = tk.Label(end_frame, text="End Time", font=('SF Pro Text', 13),
                            bg='#ffffff', fg='#86868b')
        end_label.pack(side='left')

        end_inputs = tk.Frame(end_frame, bg='#ffffff')
        end_inputs.pack(side='right')

        self.end_hour = tk.Entry(end_inputs, font=('SF Pro Text', 13), width=4,
                                relief='solid', bd=1)
        self.end_hour.insert(0, str(self.config.get('work_end_hour')))
        self.end_hour.pack(side='left', padx=2)
        tk.Label(end_inputs, text=":", bg='#ffffff', font=('SF Pro Text', 13)).pack(side='left')
        self.end_minute = tk.Entry(end_inputs, font=('SF Pro Text', 13), width=4,
                                   relief='solid', bd=1)
        self.end_minute.insert(0, str(self.config.get('work_end_minute')))
        self.end_minute.pack(side='left', padx=2)

        # SECTION 2: Monitoring Settings
        self._create_section(scrollable_frame, "Monitoring", "Configure activity tracking parameters")
        monitoring_card = self._create_card(scrollable_frame)

        self._create_input_row(monitoring_card, "Screenshot Interval", "minutes",
                               'screenshot_interval_minutes', self)
        self._create_input_row(monitoring_card, "Idle Threshold", "seconds",
                               'idle_start_seconds', self, 'idle_start')
        self._create_input_row(monitoring_card, "Warning Screen", "seconds",
                               'warning_screen_seconds', self, 'warning_screen')

        # SECTION 3: Email Reports
        self._create_section(scrollable_frame, "Email Reports", "Weekly activity reports via email")
        email_card = self._create_card(scrollable_frame)

        self.email_enabled = tk.BooleanVar(value=self.config.get('email_enabled'))
        enable_check = tk.Checkbutton(email_card, text="Enable Weekly Email Reports (Fridays 5:30 PM)",
                                      variable=self.email_enabled, bg='#ffffff',
                                      font=('SF Pro Text', 13), fg='#1d1d1f',
                                      activebackground='#ffffff', selectcolor='#f5f5f7')
        enable_check.pack(anchor='w', pady=8)

        self._create_input_row(email_card, "Recipient Email", "", 'email_to', self)
        self._create_input_row(email_card, "SMTP Server", "", 'smtp_server', self)
        self._create_input_row(email_card, "SMTP Port", "", 'smtp_port', self)
        self._create_input_row(email_card, "SMTP Username", "", 'smtp_username', self)

        # Password field (special handling)
        pwd_frame = tk.Frame(email_card, bg='#ffffff')
        pwd_frame.pack(fill='x', pady=8)
        tk.Label(pwd_frame, text="SMTP Password", font=('SF Pro Text', 13),
                bg='#ffffff', fg='#86868b').pack(side='left')
        self.smtp_password = tk.Entry(pwd_frame, font=('SF Pro Text', 13), show='*',
                                      relief='solid', bd=1, width=20)
        self.smtp_password.insert(0, str(self.config.get('smtp_password')))
        self.smtp_password.pack(side='right')

        # Test email button in card
        test_email_btn = tk.Button(email_card, text="Send Test Email",
                                   command=self.send_test_email,
                                   bg='#007aff', fg='white', font=('SF Pro Text', 12, 'bold'),
                                   relief='flat', bd=0, padx=20, pady=10,
                                   cursor='hand2', activebackground='#0051d5')
        test_email_btn.pack(pady=(12, 8))

        # SECTION 4: Network Dashboard
        self._create_section(scrollable_frame, "Network Access", "Remote dashboard accessibility")
        network_card = self._create_card(scrollable_frame)

        self.dashboard_server_enabled = tk.BooleanVar(value=self.config.get('dashboard_server_enabled'))
        network_check = tk.Checkbutton(network_card, text="Enable Network Access to Dashboard",
                                       variable=self.dashboard_server_enabled, bg='#ffffff',
                                       font=('SF Pro Text', 13), fg='#1d1d1f',
                                       activebackground='#ffffff', selectcolor='#f5f5f7')
        network_check.pack(anchor='w', pady=8)

        self._create_input_row(network_card, "Dashboard Port", "", 'dashboard_port', self)

        if self.dashboard_server and self.dashboard_server.is_running():
            url = self.dashboard_server.get_access_url()
            if url:
                url_frame = tk.Frame(network_card, bg='#e8f5e9', relief='flat', bd=0)
                url_frame.pack(fill='x', pady=8)
                tk.Label(url_frame, text=f"✓ Active at: {url}",
                        bg='#e8f5e9', fg='#2e7d32',
                        font=('SF Pro Text', 12, 'bold')).pack(padx=12, pady=8)

        # SECTION 5: Startup Settings
        self._create_section(scrollable_frame, "Startup", "Application launch behavior")
        startup_card = self._create_card(scrollable_frame)

        self.autostart_enabled = tk.BooleanVar(value=self.config.get('autostart_enabled'))
        autostart_check = tk.Checkbutton(startup_card, text="Start automatically with Windows",
                                        variable=self.autostart_enabled, bg='#ffffff',
                                        font=('SF Pro Text', 13), fg='#1d1d1f',
                                        activebackground='#ffffff', selectcolor='#f5f5f7')
        autostart_check.pack(anchor='w', pady=8)

        # Show current autostart status
        current_status = check_autostart_enabled()
        status_color = '#e8f5e9' if current_status else '#fff3e0'
        status_text_color = '#2e7d32' if current_status else '#e65100'
        status_text = "✓ Currently enabled in Windows startup" if current_status else "○ Currently disabled in Windows startup"

        status_frame = tk.Frame(startup_card, bg=status_color, relief='flat', bd=0)
        status_frame.pack(fill='x', pady=8)
        tk.Label(status_frame, text=status_text,
                bg=status_color, fg=status_text_color,
                font=('SF Pro Text', 11)).pack(padx=12, pady=6)

        # Action Buttons Section
        buttons_frame = tk.Frame(scrollable_frame, bg='#f5f5f7')
        buttons_frame.pack(fill='x', pady=(30, 0))

        # Primary actions
        primary_row = tk.Frame(buttons_frame, bg='#f5f5f7')
        primary_row.pack(fill='x', pady=(0, 10))

        save_btn = tk.Button(primary_row, text="Save Settings", command=self.save_settings,
                            bg='#34c759', fg='white', font=('SF Pro Text', 13, 'bold'),
                            relief='flat', bd=0, padx=30, pady=14,
                            cursor='hand2', activebackground='#2da94a')
        save_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))

        pwd_btn = tk.Button(primary_row, text="Change Password", command=self.change_password,
                           bg='#007aff', fg='white', font=('SF Pro Text', 13, 'bold'),
                           relief='flat', bd=0, padx=30, pady=14,
                           cursor='hand2', activebackground='#0051d5')
        pwd_btn.pack(side='left', expand=True, fill='x', padx=(5, 0))

        # Danger zone
        reset_btn = tk.Button(buttons_frame, text="Reset All Data", command=self.reset_all,
                             bg='#ff3b30', fg='white', font=('SF Pro Text', 13, 'bold'),
                             relief='flat', bd=0, padx=30, pady=14,
                             cursor='hand2', activebackground='#d62f25')
        reset_btn.pack(fill='x')

    def _create_section(self, parent, title, subtitle):
        """Create a section header"""
        section_frame = tk.Frame(parent, bg='#f5f5f7')
        section_frame.pack(fill='x', pady=(20, 12))

        tk.Label(section_frame, text=title, font=('SF Pro Display', 20, 'bold'),
                bg='#f5f5f7', fg='#1d1d1f').pack(anchor='w')
        tk.Label(section_frame, text=subtitle, font=('SF Pro Text', 13),
                bg='#f5f5f7', fg='#86868b').pack(anchor='w', pady=(2, 0))

    def _create_card(self, parent):
        """Create a card container"""
        card = tk.Frame(parent, bg='#ffffff', relief='flat', bd=0)
        card.pack(fill='x', pady=(0, 20))

        inner = tk.Frame(card, bg='#ffffff')
        inner.pack(fill='x', padx=20, pady=16)
        return inner

    def _create_input_row(self, parent, label, unit, config_key, obj, attr_name=None):
        """Create an input row with label and entry"""
        row = tk.Frame(parent, bg='#ffffff')
        row.pack(fill='x', pady=8)

        label_text = f"{label} ({unit})" if unit else label
        tk.Label(row, text=label_text, font=('SF Pro Text', 13),
                bg='#ffffff', fg='#86868b').pack(side='left')

        entry = tk.Entry(row, font=('SF Pro Text', 13), relief='solid', bd=1, width=20)
        entry.insert(0, str(self.config.get(config_key)))
        entry.pack(side='right')

        # Store reference
        if attr_name:
            setattr(obj, attr_name, entry)
        else:
            setattr(obj, config_key.replace('_', ''), entry)

    def save_settings(self):
        try:
            self.config.set('work_start_hour', int(self.start_hour.get()))
            self.config.set('work_start_minute', int(self.start_minute.get()))
            self.config.set('work_end_hour', int(self.end_hour.get()))
            self.config.set('work_end_minute', int(self.end_minute.get()))
            self.config.set('screenshot_interval_minutes', int(self.screenshotintervalminutes.get()))
            self.config.set('idle_start_seconds', int(self.idle_start.get()))
            self.config.set('warning_screen_seconds', int(self.warning_screen.get()))

            # Save email settings
            self.config.set('email_enabled', self.email_enabled.get())
            self.config.set('email_to', self.emailto.get())
            self.config.set('email_from', self.smtpusername.get())  # Use SMTP username as from address
            self.config.set('smtp_server', self.smtpserver.get())
            self.config.set('smtp_port', int(self.smtpport.get()))
            self.config.set('smtp_username', self.smtpusername.get())
            self.config.set('smtp_password', self.smtp_password.get())

            # Save network dashboard settings
            self.config.set('dashboard_server_enabled', self.dashboard_server_enabled.get())
            self.config.set('dashboard_port', int(self.dashboardport.get()))

            # Save autostart settings and apply changes
            autostart_setting = self.autostart_enabled.get()
            self.config.set('autostart_enabled', autostart_setting)

            # Apply autostart changes to Windows registry
            if autostart_setting:
                success = setup_autostart()
                if not success:
                    messagebox.showwarning("Warning", "Settings saved but autostart setup failed.\n\nCheck permissions and try again.")
            else:
                success = remove_autostart()
                if not success:
                    messagebox.showwarning("Warning", "Settings saved but autostart removal failed.\n\nCheck permissions and try again.")

            messagebox.showinfo("Success", "✓ Settings saved successfully!\n\nRestart the app to apply changes.")
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numbers in all fields.\n\nDetails: {str(e)}")

    def send_test_email(self):
        """Send a test email to verify configuration with enhanced feedback"""
        # First save the current settings temporarily
        try:
            self.config.set('email_enabled', self.email_enabled.get())
            self.config.set('email_to', self.emailto.get())
            self.config.set('email_from', self.smtpusername.get())
            self.config.set('smtp_server', self.smtpserver.get())
            self.config.set('smtp_port', int(self.smtpport.get()))
            self.config.set('smtp_username', self.smtpusername.get())
            self.config.set('smtp_password', self.smtp_password.get())

            if not self.email_sender:
                messagebox.showerror("Error", "❌ Email sender not initialized!")
                return

            # Validate email fields
            if not self.emailto.get() or '@' not in self.emailto.get():
                messagebox.showerror("Error", "❌ Please enter a valid recipient email address")
                return

            if not self.smtpusername.get() or not self.smtp_password.get():
                messagebox.showerror("Error", "❌ Please enter SMTP username and password")
                return

            # Try to send test email
            result = messagebox.askokcancel("Send Test Email",
                                           f"Send a test email to:\n{self.emailto.get()}\n\nThis may take a few seconds.",
                                           icon='question')

            if not result:
                return

            # Create a simple progress indicator
            progress_window = tk.Toplevel(self)
            progress_window.title("Sending Email")
            progress_window.geometry("300x100")
            progress_window.configure(bg='#f5f5f7')
            progress_window.resizable(False, False)
            progress_window.transient(self)
            progress_window.grab_set()

            tk.Label(progress_window, text="Sending test email...",
                    font=('SF Pro Text', 12), bg='#f5f5f7',
                    fg='#1d1d1f').pack(pady=30)

            progress_window.update()

            try:
                success = self.email_sender.send_test_email()
                progress_window.destroy()

                if success:
                    messagebox.showinfo("Success", "✓ Test email sent successfully!\n\nCheck your inbox.")
                else:
                    messagebox.showerror("Error", "❌ Failed to send test email.\n\nPlease check your SMTP settings and try again.")
            except Exception as send_error:
                progress_window.destroy()
                messagebox.showerror("Error", f"❌ Failed to send email:\n\n{str(send_error)}")

        except ValueError:
            messagebox.showerror("Error", "❌ Please enter a valid port number")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error: {str(e)}")

    def change_password(self):
        new_pwd = simpledialog.askstring("New Password", "Enter new admin password:",
                                         show='*', parent=self)
        if new_pwd:
            confirm = simpledialog.askstring("Confirm Password", "Confirm new password:",
                                            show='*', parent=self)
            if new_pwd == confirm:
                self.config.set_password(new_pwd)
                messagebox.showinfo("Success", "Password changed successfully!")
            else:
                messagebox.showerror("Error", "Passwords don't match!")

    def reset_all(self):
        """Reset all data, screenshots, and dashboard"""
        if messagebox.askyesno("Confirm Reset",
                "This will delete:\n• All activity logs\n• All screenshots\n• Dashboard data\n\nThis cannot be undone! Continue?"):
            try:
                deleted_logs = 0
                deleted_screenshots = 0

                # Delete all log files
                for f in DATA_DIR.glob("d*.dat"):
                    f.unlink()
                    deleted_logs += 1
                for f in DATA_DIR.glob("*.dat"):
                    if f.name != "sys.dat":
                        f.unlink()
                        deleted_logs += 1

                # Delete all screenshots
                for f in SCREENSHOTS_DIR.glob("*.png"):
                    f.unlink()
                    deleted_screenshots += 1

                # Delete dashboard
                dashboard_file = BASE_DIR / "dashboard.html"
                if dashboard_file.exists():
                    dashboard_file.unlink()

                # Reset logger's current data
                if self.logger:
                    self.logger.today_log = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "work_seconds": 0,
                        "idle_seconds": 0,
                        "overtime_seconds": 0,
                        "suspicious_seconds": 0,
                        "screenshots": [],
                        "sessions": [],
                        "current_session_start": None,
                        "suspicious_events": [],
                        "keyboard_activity_count": 0,
                        "window_change_count": 0,
                        "idle_periods": [],
                        "current_idle_start": None
                    }
                    self.logger.save()

                messagebox.showinfo("Reset Complete",
                    f"Deleted:\n• {deleted_logs} log files\n• {deleted_screenshots} screenshots\n\nPlease restart the app.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset: {e}")


class WorkMonitorApp:
    """Main application class with anti-cheat detection"""

    def __init__(self):
        self.config = Config()
        self.logger = ActivityLogger()
        self.mouse_tracker = MouseTracker(self.config)  # Pass config for anti-cheat
        self.keyboard_tracker = KeyboardTracker(self.mouse_tracker.anticheat)
        self.screenshot_manager = ScreenshotManager(self.config)

        # Initialize email report sender
        self.email_sender = EmailReportSender(self.config, ActivityLogger)

        # Initialize dashboard server
        self.dashboard_server = DashboardServer(self.config, BASE_DIR)

        self.running = True
        self.is_working = False
        self.is_suspicious = False  # Anti-cheat flag
        self.last_screenshot_time = 0
        self.last_check_time = time.time()

        # Overlay widget process
        self.overlay_process = None
        self.overlay_script = BASE_DIR / "src" / "overlay_widget.py"

        # Create main window with Apple-inspired design
        self.root = tk.Tk()
        self.root.title("WorkMonitor")
        self.root.geometry("560x800")  # Larger for better spacing and all controls
        self.root.configure(bg='#f5f5f7')  # Apple-style light gray
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.root.resizable(True, True)  # Allow resizing for flexibility
        self.root.minsize(560, 800)  # Minimum size to show all controls

        # Set window icon
        icon_path = BASE_DIR / "icon.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception as e:
                print(f"Could not set window icon: {e}")

        self.setup_ui()
        self.start_monitoring()

        # Start email scheduler if enabled
        if self.config.get('email_enabled'):
            self.email_sender.start_scheduler()

        # Start dashboard server if enabled
        if self.config.get('dashboard_server_enabled'):
            self.dashboard_server.start()

        # Cleanup old screenshots on start
        removed = self.screenshot_manager.cleanup_old()
        if removed > 0:
            print(f"Cleaned up {removed} old screenshots")

    def setup_ui(self):
        """Setup the main UI with Apple 2026-inspired design"""
        # Main container with generous padding
        main_container = tk.Frame(self.root, bg='#f5f5f7')
        main_container.pack(fill='both', expand=True, padx=40, pady=40)

        # Title Section - Bold and prominent
        title_label = tk.Label(main_container, text="WorkMonitor",
                              font=('Segoe UI', 36, 'bold'),
                              bg='#f5f5f7', fg='#1d1d1f')
        title_label.pack(pady=(0, 8))

        subtitle_label = tk.Label(main_container, text="Intelligent Activity Tracking",
                                 font=('Segoe UI', 15),
                                 bg='#f5f5f7', fg='#86868b')
        subtitle_label.pack(pady=(0, 32))

        # Status Card - Clean white card with border
        status_card = tk.Frame(main_container, bg='#ffffff', relief='flat', bd=0)
        status_card.pack(fill='x', pady=(0, 18))
        status_card.configure(highlightbackground='#e5e5ea', highlightthickness=1)

        status_inner = tk.Frame(status_card, bg='#ffffff')
        status_inner.pack(padx=30, pady=24)

        self.status_label = tk.Label(status_inner, text="Initializing...",
                                     font=('Segoe UI', 17),
                                     bg='#ffffff', fg='#1d1d1f')
        self.status_label.pack()

        # Stats Card - White card with clean layout
        stats_card = tk.Frame(main_container, bg='#ffffff', relief='flat', bd=0)
        stats_card.pack(fill='x', pady=(0, 18))
        stats_card.configure(highlightbackground='#e5e5ea', highlightthickness=1)

        stats_inner = tk.Frame(stats_card, bg='#ffffff')
        stats_inner.pack(padx=30, pady=24, fill='x')

        # Work Time Row
        work_row = tk.Frame(stats_inner, bg='#ffffff')
        work_row.pack(fill='x', pady=8)
        tk.Label(work_row, text="Work Time", font=('Segoe UI', 15),
                bg='#ffffff', fg='#86868b').pack(side='left')
        self.work_label = tk.Label(work_row, text="0h 0m", font=('Segoe UI', 15, 'bold'),
                                   bg='#ffffff', fg='#34c759')
        self.work_label.pack(side='right')

        # Idle Time Row
        idle_row = tk.Frame(stats_inner, bg='#ffffff')
        idle_row.pack(fill='x', pady=8)
        tk.Label(idle_row, text="Idle Time", font=('Segoe UI', 15),
                bg='#ffffff', fg='#86868b').pack(side='left')
        self.idle_label = tk.Label(idle_row, text="0h 0m", font=('Segoe UI', 15, 'bold'),
                                  bg='#ffffff', fg='#ff9f0a')
        self.idle_label.pack(side='right')

        # Screenshots Row
        screenshot_row = tk.Frame(stats_inner, bg='#ffffff')
        screenshot_row.pack(fill='x', pady=8)
        tk.Label(screenshot_row, text="Screenshots", font=('Segoe UI', 15),
                bg='#ffffff', fg='#86868b').pack(side='left')
        self.screenshot_label = tk.Label(screenshot_row, text="0", font=('Segoe UI', 15, 'bold'),
                                        bg='#ffffff', fg='#0a84ff')
        self.screenshot_label.pack(side='right')

        # Anti-cheat Row
        anticheat_row = tk.Frame(stats_inner, bg='#ffffff')
        anticheat_row.pack(fill='x', pady=8)
        tk.Label(anticheat_row, text="Security Status", font=('Segoe UI', 15),
                bg='#ffffff', fg='#86868b').pack(side='left')
        self.anticheat_label = tk.Label(anticheat_row, text="Verified", font=('Segoe UI', 15, 'bold'),
                                        bg='#ffffff', fg='#34c759')
        self.anticheat_label.pack(side='right')

        # Network Row
        network_row = tk.Frame(stats_inner, bg='#ffffff')
        network_row.pack(fill='x', pady=8)
        tk.Label(network_row, text="Network Access", font=('Segoe UI', 15),
                bg='#ffffff', fg='#86868b').pack(side='left')
        self.network_label = tk.Label(network_row, text="Disabled", font=('Segoe UI', 15, 'bold'),
                                      bg='#ffffff', fg='#98989d')
        self.network_label.pack(side='right')

        # Timer Card - Large prominent display
        timer_card = tk.Frame(main_container, bg='#ffffff', relief='flat', bd=0)
        timer_card.pack(fill='x', pady=(0, 18))
        timer_card.configure(highlightbackground='#e5e5ea', highlightthickness=1)

        timer_inner = tk.Frame(timer_card, bg='#ffffff')
        timer_inner.pack(padx=30, pady=28)

        self.timer_label = tk.Label(timer_inner, text="00:00:00",
                                    font=('Consolas', 48, 'bold'),
                                    bg='#ffffff', fg='#34c759')
        self.timer_label.pack()

        timer_subtitle = tk.Label(timer_inner, text="Active Time Today",
                                 font=('Segoe UI', 15),
                                 bg='#ffffff', fg='#86868b')
        timer_subtitle.pack(pady=(8, 0))

        self.inactive_timer_label = tk.Label(timer_inner, text="Inactive: 0m 0s",
                                            font=('Segoe UI', 14),
                                            bg='#ffffff', fg='#98989d')
        self.inactive_timer_label.pack(pady=(12, 0))

        # Buttons Section - Modern button styling
        buttons_frame = tk.Frame(main_container, bg='#f5f5f7')
        buttons_frame.pack(fill='x', pady=(14, 0))

        # Primary Actions (Row 1)
        primary_row = tk.Frame(buttons_frame, bg='#f5f5f7')
        primary_row.pack(fill='x', pady=(0, 12))

        dashboard_btn = tk.Button(primary_row, text="Open Dashboard", command=self.open_dashboard,
                                 bg='#0a84ff', fg='white', font=('Segoe UI', 14, 'bold'),
                                 relief='flat', bd=0, padx=24, pady=16,
                                 cursor='hand2', activebackground='#0066cc',
                                 activeforeground='white')
        dashboard_btn.pack(side='left', expand=True, fill='x', padx=(0, 8))

        admin_btn = tk.Button(primary_row, text="Admin Panel", command=self.show_admin_panel,
                             bg='#5e5ce6', fg='white', font=('Segoe UI', 14, 'bold'),
                             relief='flat', bd=0, padx=24, pady=16,
                             cursor='hand2', activebackground='#4845c7',
                             activeforeground='white')
        admin_btn.pack(side='left', expand=True, fill='x', padx=(8, 0))

        # Secondary Actions (Row 2)
        secondary_row = tk.Frame(buttons_frame, bg='#f5f5f7')
        secondary_row.pack(fill='x')

        minimize_btn = tk.Button(secondary_row, text="Minimize to Tray", command=self.minimize_to_tray,
                                bg='#ffffff', fg='#1d1d1f', font=('Segoe UI', 14),
                                relief='flat', bd=0, padx=24, pady=16,
                                cursor='hand2', activebackground='#f0f0f5',
                                highlightthickness=1, highlightbackground='#d1d1d6',
                                activeforeground='#1d1d1f')
        minimize_btn.pack(side='left', expand=True, fill='x', padx=(0, 8))

        shutdown_btn = tk.Button(secondary_row, text="Shutdown Program", command=self.shutdown_program,
                                bg='#ff3b30', fg='white', font=('Segoe UI', 14, 'bold'),
                                relief='flat', bd=0, padx=24, pady=16,
                                cursor='hand2', activebackground='#e0321f',
                                activeforeground='white')
        shutdown_btn.pack(side='left', expand=True, fill='x', padx=(8, 0))

        # Fullscreen warning window (hidden by default)
        self.warning_window = None

    def is_work_hours(self):
        """Check if current time is within work hours"""
        now = datetime.now()
        work_start = now.replace(hour=self.config.get('work_start_hour'),
                                 minute=self.config.get('work_start_minute'),
                                 second=0, microsecond=0)
        work_end = now.replace(hour=self.config.get('work_end_hour'),
                               minute=self.config.get('work_end_minute'),
                               second=0, microsecond=0)
        return work_start <= now <= work_end

    def is_overtime(self):
        """Check if current time is overtime"""
        now = datetime.now()
        work_end = now.replace(hour=self.config.get('work_end_hour'),
                               minute=self.config.get('work_end_minute'),
                               second=0, microsecond=0)
        return now > work_end

    def start_monitoring(self):
        """Start the monitoring thread"""
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.update_ui()

    def show_warning_screen(self, idle_time):
        """Show fullscreen red warning for extended inactivity"""
        if self.warning_window is not None:
            # Update existing warning time
            if hasattr(self, 'warning_time_label') and self.warning_time_label:
                idle_mins = int(idle_time // 60)
                idle_secs = int(idle_time % 60)
                self.warning_time_label.config(text=f"Idle for {idle_mins}m {idle_secs}s")
            return

        self.warning_window = tk.Toplevel(self.root)
        self.warning_window.attributes('-fullscreen', True)
        self.warning_window.attributes('-topmost', True)
        self.warning_window.configure(bg='#cc0000')
        self.warning_window.overrideredirect(True)

        # Warning content
        frame = tk.Frame(self.warning_window, bg='#cc0000')
        frame.place(relx=0.5, rely=0.5, anchor='center')

        warning_label = tk.Label(frame, text="INACTIVE!", font=('Segoe UI', 72, 'bold'),
                                bg='#cc0000', fg='white')
        warning_label.pack(pady=20)

        idle_mins = int(idle_time // 60)
        idle_secs = int(idle_time % 60)
        self.warning_time_label = tk.Label(frame, text=f"Idle for {idle_mins}m {idle_secs}s",
                             font=('Segoe UI', 36), bg='#cc0000', fg='white')
        self.warning_time_label.pack(pady=10)

        hint_label = tk.Label(frame, text="Move mouse or press any key to dismiss",
                             font=('Segoe UI', 18), bg='#cc0000', fg='#ffcccc')
        hint_label.pack(pady=30)

        # Bind any input to dismiss
        self.warning_window.bind('<Motion>', self.hide_warning_screen)
        self.warning_window.bind('<Key>', self.hide_warning_screen)
        self.warning_window.bind('<Button>', self.hide_warning_screen)

    def hide_warning_screen(self, event=None):
        """Hide the fullscreen warning"""
        if self.warning_window is not None:
            self.warning_window.destroy()
            self.warning_window = None
            self.warning_time_label = None

    def monitor_loop(self):
        """Main monitoring loop with anti-cheat detection"""
        while self.running:
            try:
                current_time = time.time()
                elapsed = current_time - self.last_check_time
                self.last_check_time = current_time

                # Check mouse activity
                self.mouse_tracker.has_moved()
                mouse_idle = self.mouse_tracker.get_idle_seconds()

                # Check keyboard activity
                self.keyboard_tracker.check_activity()
                keyboard_idle = self.keyboard_tracker.get_idle_seconds()

                # Use the minimum of mouse/keyboard idle (any activity resets idle)
                idle_seconds = min(mouse_idle, keyboard_idle)

                # Get config values for idle thresholds
                idle_start_threshold = self.config.get('idle_start_seconds')
                warning_threshold = self.config.get('warning_screen_seconds')

                # Determine if user is working (any activity within idle start threshold)
                was_working = self.is_working
                self.is_working = idle_seconds < idle_start_threshold

                # Store current idle seconds for widget to read
                self.current_idle_seconds = idle_seconds if not self.is_working else 0

                # Track idle periods (when person left/returned)
                if not self.is_working and was_working:
                    # Person just went idle - mark as "left"
                    self.logger.start_idle_period()
                elif self.is_working and not was_working:
                    # Person just returned from idle - mark as "returned"
                    self.logger.end_idle_period()

                # Check for cheating/jiggling
                is_real = self.mouse_tracker.is_real_activity()
                self.is_suspicious = not is_real

                # Show fullscreen warning after warning_threshold during work hours only
                if idle_seconds >= warning_threshold and self.is_work_hours():
                    self.root.after(0, lambda: self.show_warning_screen(idle_seconds))
                else:
                    self.root.after(0, self.hide_warning_screen)

                # Update time tracking (ONLY during work hours - no before/after tracking)
                if self.is_work_hours():
                    if self.is_working and is_real:
                        # Real work activity
                        self.logger.add_work_time(elapsed)
                    elif self.is_working and not is_real:
                        # Suspicious activity (jiggler detected)
                        cheat_status = self.mouse_tracker.get_cheat_status()
                        self.logger.add_suspicious_time(elapsed, cheat_status.get('reason', ''))
                    else:
                        # Idle time (no activity for 5+ minutes)
                        self.logger.add_idle_time(elapsed)

                    # Update activity counts during work hours only
                    if self.mouse_tracker.anticheat:
                        self.logger.update_activity_counts(
                            self.keyboard_tracker.key_count,
                            self.mouse_tracker.anticheat.window_change_count
                        )

                # Take screenshots during work hours only
                screenshot_interval = self.config.get('screenshot_interval_minutes') * 60
                if self.is_working and self.is_work_hours():
                    if current_time - self.last_screenshot_time >= screenshot_interval:
                        filepath = self.screenshot_manager.capture()
                        if filepath:
                            self.logger.add_screenshot(filepath, is_suspicious=self.is_suspicious)
                            self.last_screenshot_time = current_time

                # Update dashboard
                summary = self.logger.get_summary()
                HTMLReportGenerator.save_dashboard(summary, self.config, self.logger)

            except Exception as e:
                print(f"Monitor error: {e}")

            time.sleep(1)

    def update_ui(self):
        """Update UI with current stats - Apple design style"""
        if not self.running:
            return

        try:
            summary = self.logger.get_summary()
            idle_secs = int(self.mouse_tracker.get_idle_seconds())

            # Update status with modern messaging
            if self.is_suspicious:
                status_text = "⚠️ Suspicious Activity Detected"
                self.status_label.configure(fg='#ff3b30')
            elif self.is_working:
                status_text = "✓ Active"
                self.status_label.configure(fg='#34c759')
            else:
                status_text = f"○ Idle"
                self.status_label.configure(fg='#ff9f0a')

            if not self.is_work_hours():
                status_text += " • Outside Work Hours"

            self.status_label.configure(text=status_text)

            # Update timer display
            total_work_secs = int(summary['work_hours'] * 3600)
            timer_h = total_work_secs // 3600
            timer_m = (total_work_secs % 3600) // 60
            timer_s = total_work_secs % 60
            self.timer_label.configure(text=f"{timer_h:02d}:{timer_m:02d}:{timer_s:02d}")

            # Update inactive timer
            if idle_secs >= 60:  # Show after 1 minute
                idle_mins = idle_secs // 60
                idle_s = idle_secs % 60
                self.inactive_timer_label.configure(text=f"Inactive: {idle_mins}m {idle_s}s")
                if idle_secs >= 300:  # 5 minutes - turn red
                    self.inactive_timer_label.configure(fg='#ff3b30')
                else:
                    self.inactive_timer_label.configure(fg='#ff9f0a')
            else:
                self.inactive_timer_label.configure(text="Inactive: 0m 0s", fg='#8e8e93')

            # Update stats with clean formatting
            work_h = int(summary['work_hours'])
            work_m = int((summary['work_hours'] - work_h) * 60)
            self.work_label.configure(text=f"{work_h}h {work_m}m")

            idle_h = int(summary['idle_hours'])
            idle_m = int((summary['idle_hours'] - idle_h) * 60)
            self.idle_label.configure(text=f"{idle_h}h {idle_m}m")

            self.screenshot_label.configure(text=f"{summary['screenshot_count']}")

            # Update anti-cheat status
            cheat_status = self.mouse_tracker.get_cheat_status()
            if cheat_status['is_cheating']:
                self.anticheat_label.configure(
                    text=f"Alert ({cheat_status['score']:.0f}%)",
                    fg='#ff3b30'
                )
            else:
                self.anticheat_label.configure(text="Verified", fg='#34c759')

            # Update network server status
            if self.dashboard_server.is_running():
                url = self.dashboard_server.get_access_url()
                self.network_label.configure(text=f"Active", fg='#34c759')
            else:
                self.network_label.configure(text="Disabled", fg='#8e8e93')

        except Exception as e:
            print(f"UI update error: {e}")

        self.root.after(1000, self.update_ui)

    def open_dashboard(self):
        """Open the HTML dashboard"""
        dashboard_path = BASE_DIR / "dashboard.html"
        if dashboard_path.exists():
            os.startfile(str(dashboard_path))
        else:
            messagebox.showinfo("Info", "Dashboard will be generated shortly...")

    def show_admin_panel(self):
        """Show admin panel with password"""
        password = simpledialog.askstring("Admin Login", "Enter admin password:",
                                         show='*', parent=self.root)
        if password and self.config.verify_password(password):
            # Store reference to prevent garbage collection
            self.admin_panel = AdminPanel(self.root, self.config, self.logger, self.email_sender, self.dashboard_server)
        elif password:
            messagebox.showerror("Error", "Invalid password!")

    def start_overlay_widget(self):
        """Start the overlay widget subprocess"""
        import subprocess
        if self.overlay_script.exists() and self.overlay_process is None:
            try:
                self.overlay_process = subprocess.Popen(
                    [sys.executable, str(self.overlay_script)],
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                print(f"Overlay widget started (PID: {self.overlay_process.pid})")
            except Exception as e:
                print(f"Failed to start overlay widget: {e}")

    def stop_overlay_widget(self):
        """Stop the overlay widget subprocess"""
        if self.overlay_process:
            try:
                self.overlay_process.terminate()
                self.overlay_process.wait(timeout=3)
                print("Overlay widget stopped")
            except Exception as e:
                print(f"Failed to stop overlay widget gracefully: {e}")
                try:
                    self.overlay_process.kill()
                except (OSError, ProcessLookupError) as kill_error:
                    logger.error(f"Failed to kill overlay process: {kill_error}")
            finally:
                self.overlay_process = None

    def hide_overlay_widget(self):
        """Hide the overlay widget"""
        self.stop_overlay_widget()

    def show_overlay_widget(self):
        """Show the overlay widget"""
        if self.overlay_process is None:
            self.start_overlay_widget()

    def toggle_overlay_widget(self):
        """Toggle overlay widget visibility"""
        if self.overlay_process is None:
            self.show_overlay_widget()
        else:
            self.hide_overlay_widget()

    def is_overlay_widget_visible(self):
        """Check if overlay widget is currently running"""
        if self.overlay_process is None:
            return False
        # Check if process is still alive
        if self.overlay_process.poll() is not None:
            # Process has terminated
            self.overlay_process = None
            return False
        return True

    def minimize_to_tray(self):
        """Minimize to system tray"""
        self.root.withdraw()

        # Load icon from file
        def get_icon_image():
            icon_path = BASE_DIR / "icon.ico"
            try:
                if icon_path.exists():
                    return Image.open(str(icon_path))
            except Exception as e:
                print(f"Could not load icon: {e}")

            # Fallback: create a simple icon
            img = Image.new('RGB', (64, 64), color='#3498db')
            draw = ImageDraw.Draw(img)
            draw.ellipse([10, 10, 54, 54], fill='#2ecc71')
            return img

        def on_show(icon, item):
            icon.stop()
            self.root.deiconify()

        def on_toggle_widget(icon, item):
            self.toggle_overlay_widget()

        def on_show_widget(icon, item):
            self.show_overlay_widget()

        def on_hide_widget(icon, item):
            self.hide_overlay_widget()

        def on_dashboard(icon, item):
            self.open_dashboard()

        def on_admin_panel(icon, item):
            self.show_admin_panel()

        def on_exit(icon, item):
            icon.stop()
            self.quit_app()

        # Create dynamic menu with widget visibility state
        def get_widget_menu_item():
            if self.is_overlay_widget_visible():
                return item('Hide Floating Widget', on_hide_widget)
            else:
                return item('Show Floating Widget', on_show_widget)

        menu = pystray.Menu(
            item('Show', on_show, default=True),
            pystray.Menu.SEPARATOR,
            get_widget_menu_item(),
            pystray.Menu.SEPARATOR,
            item('Open Dashboard', on_dashboard),
            item('Admin Panel', on_admin_panel),
            pystray.Menu.SEPARATOR,
            item('Exit', on_exit)
        )

        icon = pystray.Icon("WorkMonitor", get_icon_image(), "Work Monitor", menu)
        threading.Thread(target=icon.run, daemon=True).start()

    def shutdown_program(self):
        """Safely shutdown the program with confirmation"""
        result = messagebox.askyesno("Shutdown WorkMonitor",
                                     "Are you sure you want to shutdown WorkMonitor?\n\n" +
                                     "The application will stop tracking your activity.",
                                     icon='warning')
        if result:
            self.quit_app()

    def quit_app(self):
        """Quit the application"""
        self.running = False
        # Stop email scheduler
        if hasattr(self, 'email_sender'):
            self.email_sender.stop_scheduler()
        # Stop dashboard server
        if hasattr(self, 'dashboard_server'):
            self.dashboard_server.stop()

        # Clean up lock file
        lock_file = DATA_DIR / "app.lock"
        if lock_file.exists():
            try:
                lock_file.unlink()
            except OSError as e:
                logger.error(f"Failed to remove lock file: {e}")

        self.root.quit()
        self.root.destroy()

    def run(self):
        """Run the application"""
        self.root.mainloop()


def setup_autostart():
    """Setup Windows autostart"""
    import winreg
    import shutil

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_path = os.path.abspath(__file__)

    # For executable
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        # Find pythonw.exe in the same directory as python.exe
        pythonw_exe = sys.executable.replace('python.exe', 'pythonw.exe')
        if not os.path.exists(pythonw_exe):
            # Try to find pythonw in PATH
            pythonw_exe = shutil.which('pythonw')
            if not pythonw_exe:
                pythonw_exe = 'pythonw'  # Fallback to hoping it's in PATH

        # Use absolute paths for both pythonw and script
        app_path = f'"{pythonw_exe}" "{app_path}"'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)
        print(f"Autostart configured: {app_path}")
        return True
    except Exception as e:
        print(f"Autostart setup error: {e}")
        return False


def remove_autostart():
    """Remove Windows autostart entry"""
    import winreg

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"Autostart disabled for {APP_NAME}")
        return True
    except FileNotFoundError:
        # Entry doesn't exist, which is fine
        print(f"Autostart entry for {APP_NAME} not found (already disabled)")
        return True
    except Exception as e:
        print(f"Autostart removal error: {e}")
        return False


def check_autostart_enabled():
    """Check if autostart is currently enabled in Windows registry"""
    import winreg

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception as e:
        print(f"Error checking autostart status: {e}")
        return False


def set_windows_appid():
    """Set Windows AppUserModelID for proper taskbar display"""
    try:
        import ctypes
        myappid = f'com.enkhtamir.{APP_NAME}.1.0'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"Could not set Windows AppUserModelID: {e}")


def ensure_single_instance():
    """Ensure only one instance of the application is running. Prompt user if instance exists."""
    lock_file = DATA_DIR / "app.lock"
    current_pid = os.getpid()

    # Check if lock file exists
    if lock_file.exists():
        try:
            with open(lock_file, 'r') as f:
                old_pid = int(f.read().strip())

            # Check if the old process is still running
            if psutil.pid_exists(old_pid):
                try:
                    # Try to get the process
                    old_process = psutil.Process(old_pid)
                    # Check if it's actually our app (by name)
                    if 'python' in old_process.name().lower() or 'work_monitor' in old_process.name().lower():
                        # Show error dialog and exit without launching
                        import tkinter as tk
                        from tkinter import messagebox

                        root = tk.Tk()
                        root.withdraw()  # Hide the main window
                        messagebox.showerror(
                            "Application Already Running",
                            "The application is already running.\n\n"
                            "Please close the existing instance before starting a new one.\n\n"
                            f"Existing instance PID: {old_pid}"
                        )
                        root.destroy()
                        print(f"Cannot start - instance already running (PID: {old_pid})")
                        sys.exit(0)
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"Could not verify old process: {e}")
                    # Process doesn't exist or can't access - remove stale lock
                    lock_file.unlink(missing_ok=True)
                except Exception as e:
                    print(f"Error handling old instance: {e}")

            # Remove stale lock file if process doesn't exist
            else:
                lock_file.unlink(missing_ok=True)
        except Exception as e:
            print(f"Error reading lock file: {e}")
            lock_file.unlink(missing_ok=True)

    # Create new lock file with current PID
    try:
        with open(lock_file, 'w') as f:
            f.write(str(current_pid))
        print(f"Lock file created with PID: {current_pid}")
    except Exception as e:
        print(f"Could not create lock file: {e}")


def main():
    import subprocess

    # Ensure only one instance is running
    ensure_single_instance()

    # Set Windows app ID for proper taskbar/task manager display
    set_windows_appid()

    # Setup autostart based on config setting
    # Load config early to check autostart preference
    temp_config = Config()
    if temp_config.get('autostart_enabled'):
        # Ensure autostart is set up if enabled in config
        if not check_autostart_enabled():
            setup_autostart()
            print("Autostart configured. Application will run on Windows startup.")
    else:
        # Ensure autostart is removed if disabled in config
        if check_autostart_enabled():
            remove_autostart()
            print("Autostart disabled. Application will not run on Windows startup.")

    # Create app instance
    app = WorkMonitorApp()

    # Launch overlay widget as subprocess
    overlay_script = BASE_DIR / "src" / "overlay_widget.py"
    if overlay_script.exists():
        app.start_overlay_widget()

    try:
        app.run()
    finally:
        # Kill overlay widget when main app exits
        app.stop_overlay_widget()


if __name__ == "__main__":
    main()
