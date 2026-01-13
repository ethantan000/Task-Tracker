"""
Work Monitor v2.0 - Complete Architectural Rebuild
Rebuilt from scratch with clean window lifecycle management and unbreakable layouts.

Key Improvements:
- ONE creation function per window type
- Hide/show instead of destroy/recreate (eliminates lifecycle errors)
- Unbreakable layouts (buttons always visible, proper scrolling)
- Admin panel works from all entry points (tray, button, etc.)
- Clean separation: business logic vs UI

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
from tkinter import ttk, messagebox, simpledialog, Canvas, Scrollbar, Frame
from datetime import datetime, timedelta
from pathlib import Path
import ctypes
from ctypes import wintypes
import math
import statistics
from collections import deque
import psutil
import subprocess
import webbrowser

# Import email and dashboard modules
try:
    from email_reports import EmailReportSender
    from dashboard_server import DashboardServer
except ImportError:
    EmailReportSender = None
    DashboardServer = None

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
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA_DIR = BASE_DIR / ".cache"
SCREENSHOTS_DIR = BASE_DIR / ".tmp"
CONFIG_FILE = DATA_DIR / "sys.dat"
LOG_FILE = DATA_DIR / "app.dat"
LOCK_FILE = DATA_DIR / "app.lock"

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
    "idle_start_seconds": 300,
    "warning_screen_seconds": 360,
    "admin_password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
    "screenshot_retention_days": 14,
    # Anti-cheat settings
    "anticheat_enabled": True,
    "min_movement_distance": 50,
    "jitter_detection_window": 30,
    "max_jitter_regularity": 0.85,
    "require_keyboard_activity": True,
    "keyboard_check_interval": 300,
    "require_window_changes": True,
    "window_change_interval": 600,
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


# ============================================================================
# BUSINESS LOGIC CLASSES (REUSED FROM ORIGINAL - THESE WORK WELL)
# ============================================================================

class AntiCheatDetector:
    """Detect mouse jigglers, fake activity, and cheating attempts"""

    def __init__(self, config):
        self.config = config
        self.movement_history = deque(maxlen=100)
        self.interval_history = deque(maxlen=50)
        self.distance_history = deque(maxlen=50)
        self.last_keyboard_time = time.time()
        self.keyboard_count = 0
        self.last_window_change = time.time()
        self.last_window_title = ""
        self.window_change_count = 0
        self.is_cheating = False
        self.cheat_reason = ""
        self.cheat_score = 0
        self.suspicious_events = deque(maxlen=50)

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
        if len(self.movement_history) >= 2:
            prev_time = self.movement_history[-2][0]
            interval = timestamp - prev_time
            self.interval_history.append(interval)

    def detect_jitter_pattern(self):
        """Detect if movements follow a jitter/oscillating pattern"""
        if len(self.movement_history) < 10:
            return False, 0, ""
        recent = list(self.movement_history)[-20:]
        distances = [m[3] for m in recent]
        avg_distance = statistics.mean(distances) if distances else 0

        if avg_distance < self.config.get('min_movement_distance'):
            if len(self.interval_history) >= 5:
                intervals = list(self.interval_history)[-10:]
                if len(intervals) >= 3:
                    try:
                        interval_std = statistics.stdev(intervals)
                        interval_mean = statistics.mean(intervals)
                        if interval_mean > 0:
                            cv = interval_std / interval_mean
                            regularity = 1 - min(cv, 1)
                            if regularity > self.config.get('max_jitter_regularity'):
                                return True, regularity * 100, f"Regular micro-movements detected (regularity: {regularity:.1%})"
                    except statistics.StatisticsError as e:
                        logger.error(f"Failed to calculate interval statistics: {e}")

            if len(recent) >= 6:
                x_positions = [m[1] for m in recent]
                y_positions = [m[2] for m in recent]
                x_changes = [x_positions[i+1] - x_positions[i] for i in range(len(x_positions)-1)]
                y_changes = [y_positions[i+1] - y_positions[i] for i in range(len(y_positions)-1)]
                x_reversals = sum(1 for i in range(len(x_changes)-1) if x_changes[i] * x_changes[i+1] < 0)
                y_reversals = sum(1 for i in range(len(y_changes)-1) if y_changes[i] * y_changes[i+1] < 0)
                total_reversals = x_reversals + y_reversals
                max_reversals = len(x_changes) - 1 + len(y_changes) - 1
                if max_reversals > 0:
                    reversal_rate = total_reversals / max_reversals
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
        is_jitter, jitter_score, jitter_reason = self.detect_jitter_pattern()
        if is_jitter:
            issues.append(jitter_reason)
            total_score += jitter_score * 0.5
        no_keyboard, kb_reason = self.detect_no_keyboard()
        if no_keyboard:
            issues.append(kb_reason)
            total_score += 30
        no_window, win_reason = self.detect_no_window_change()
        if no_window:
            issues.append(win_reason)
            total_score += 20
        self.cheat_score = min(100, total_score)
        self.is_cheating = self.cheat_score >= 50
        self.cheat_reason = "; ".join(issues) if issues else "None"
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
            keys_to_check = list(range(0x08, 0x5B)) + list(range(0x60, 0x88))
            for vk in keys_to_check:
                state = ctypes.windll.user32.GetAsyncKeyState(vk)
                was_pressed = self.last_key_state.get(vk, 0)
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
        self.real_activity = True

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
            if self.anticheat:
                self.anticheat.add_movement(self.last_position, current_pos, current_time)
                self.anticheat.check_active_window()
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
                if duration_seconds > 60:
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
            logger.error(f"Screenshot error: {e}")
            return None

    def cleanup_old(self):
        """Remove screenshots and logs older than retention period"""
        retention_days = self.config.get("screenshot_retention_days")
        cutoff = datetime.now() - timedelta(days=retention_days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")
        removed_screenshots = 0
        removed_logs = 0
        for file in SCREENSHOTS_DIR.glob("screenshot_*.png"):
            try:
                date_str = file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y%m%d")
                if file_date < cutoff:
                    file.unlink()
                    removed_screenshots += 1
            except (ValueError, IndexError, OSError) as e:
                logger.error(f"Failed to clean screenshot {file}: {e}")
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
        work_start_dt = datetime.now().replace(hour=config.get('work_start_hour'), minute=config.get('work_start_minute'))
        work_end_dt = datetime.now().replace(hour=config.get('work_end_hour'), minute=config.get('work_end_minute'))
        work_start = work_start_dt.strftime("%I:%M %p")
        work_end = work_end_dt.strftime("%I:%M %p")
        week_summary = ActivityLogger.get_week_summary()
        month_summary = ActivityLogger.get_month_summary()
        year_summary = ActivityLogger.get_year_summary()

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

        screenshots_html = ""
        if screenshots_today:
            for ss in screenshots_today[-20:]:
                ss_time = datetime.fromisoformat(ss['time']).strftime("%I:%M:%S %p")
                ss_path = ss.get('path', '')
                suspicious = ss.get('suspicious', False)
                border_style = 'border: 2px solid #e91e63;' if suspicious else 'border: 2px solid #333;'
                screenshots_html += f'''<a href="file:///{ss_path.replace(chr(92), '/')}" target="_blank" class="screenshot-thumb" style="{border_style}" title="{ss_time}">
                    <img src="file:///{ss_path.replace(chr(92), '/')}" alt="{ss_time}">
                    <span>{ss_time}</span>
                </a>\n'''

        idle_periods = summary.get('idle_periods', [])
        idle_periods_html = ""
        for period in idle_periods:
            idle_periods_html += f'''<tr>
                <td>{period['left']}</td>
                <td>{period['returned']}</td>
                <td>{period['duration']}</td>
            </tr>'''

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

        weekly_breakdown_html = generate_day_breakdown(week_summary.get('daily_data', []), 10)
        monthly_breakdown_html = generate_day_breakdown(month_summary.get('daily_data', []), 6)
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

        <div id="yearly" class="tab-content">
            <h2 style="text-align:center; margin-bottom:20px; color:#00d2ff;">This Year ({datetime.now().year})</h2>
            <div class="stats-grid">
                <div class="stat-card work"><div class="stat-label">Total Work</div><div class="stat-value">{year_summary['work_hours']:,.0f}h</div><div class="stat-sublabel">{year_summary['days_worked']} days worked</div></div>
                <div class="stat-card idle"><div class="stat-label">Total Idle</div><div class="stat-value">{year_summary['idle_hours']:,.0f}h</div></div>
                <div class="stat-card suspicious"><div class="stat-label">Suspicious</div><div class="stat-value">{year_summary['suspicious_hours']:,.0f}h</div></div>
                <div class="stat-card" style="border-left: 4px solid #2196F3;"><div class="stat-label">Real Work</div><div class="stat-value" style="color:#2196F3;">{year_summary['real_work_hours']:,.0f}h</div></div>
            </div>
        </div>

        <div class="footer">
            <p>Work Monitor v2.0 | Auto-refreshes every 30 seconds</p>
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


# ============================================================================
# NEW WINDOW MANAGER - CLEAN ARCHITECTURE
# ============================================================================

class WindowManager:
    """
    Centralized window lifecycle manager.

    Key Principles:
    - ONE creation function per window type (_create_*)
    - Hide/show using withdraw/deiconify (NOT destroy/recreate)
    - Single references per window
    - All entry points call the SAME show methods
    """

    def __init__(self, root, app):
        self.root = root
        self.app = app  # Reference to WorkMonitorApp

        # Single references per window type
        self.admin_panel = None
        self.warning_window = None
        self.widget_process = None
        self.tray_icon = None
        self.tray_thread = None

        # UI state
        self.is_in_tray = False

    # ========================================================================
    # MAIN WINDOW MANAGEMENT
    # ========================================================================

    def show_main_window(self):
        """Show main window from tray or hidden state"""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_in_tray = False

    def hide_main_window(self):
        """Hide main window to tray"""
        self.root.withdraw()
        self.is_in_tray = True

    def minimize_to_tray(self):
        """Minimize window to system tray"""
        self.hide_main_window()
        self.start_tray_icon()

    # ========================================================================
    # ADMIN PANEL MANAGEMENT (CRITICAL - WORKS FROM ALL ENTRY POINTS)
    # ========================================================================

    def show_admin_panel(self):
        """
        Show admin panel with password validation.
        Works from ALL entry points: button, tray menu, etc.
        """
        # Create independent dialog for password (no parent dependency)
        dialog = tk.Toplevel(self.root)
        dialog.withdraw()

        password = simpledialog.askstring(
            "Admin Access",
            "Enter admin password:",
            parent=dialog,
            show='*'
        )

        dialog.destroy()

        if password and self.app.config.verify_password(password):
            # Get or create admin panel
            panel = self.get_admin_panel()
            panel.deiconify()
            panel.lift()
            panel.focus_force()
        else:
            messagebox.showerror("Error", "Invalid password")

    def get_admin_panel(self):
        """Get or create admin panel - ONLY creation point"""
        if self.admin_panel is None or not self.admin_panel.winfo_exists():
            self.admin_panel = self._create_admin_panel()
        return self.admin_panel

    def hide_admin_panel(self):
        """Hide admin panel"""
        if self.admin_panel and self.admin_panel.winfo_exists():
            self.admin_panel.withdraw()

    def close_admin_panel(self):
        """Close admin panel (called on app exit)"""
        if self.admin_panel and self.admin_panel.winfo_exists():
            try:
                self.admin_panel.destroy()
            except tk.TclError as e:
                logger.error(f"Error destroying admin panel: {e}")
            finally:
                self.admin_panel = None

    def _create_admin_panel(self):
        """
        Create admin panel window with scrollable layout.
        This is the ONLY place where admin panel is created.
        """
        panel = tk.Toplevel(self.root)
        panel.title("Admin Panel")
        panel.geometry("700x900")
        panel.configure(bg='#f5f5f7')

        # Center on screen
        panel.update_idletasks()
        x = (panel.winfo_screenwidth() // 2) - (700 // 2)
        y = (panel.winfo_screenheight() // 2) - (900 // 2)
        panel.geometry(f"700x900+{x}+{y}")

        # Close button behavior: hide instead of destroy
        panel.protocol("WM_DELETE_WINDOW", self.hide_admin_panel)

        # Title bar (pinned top)
        title_frame = tk.Frame(panel, bg='#ffffff', height=60)
        title_frame.pack(side='top', fill='x')
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="Admin Panel",
            font=('Segoe UI', 18, 'bold'),
            bg='#ffffff',
            fg='#1d1d1f'
        ).pack(pady=15)

        # Scrollable content area (expands)
        canvas = Canvas(panel, bg='#f5f5f7', highlightthickness=0)
        scrollbar = Scrollbar(panel, orient='vertical', command=canvas.yview)
        content_frame = Frame(canvas, bg='#f5f5f7')

        canvas.pack(side='left', fill='both', expand=True, padx=20)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor='nw')

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfig(canvas_window, width=event.width)

        content_frame.bind('<Configure>', on_frame_configure)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        # === SETTINGS SECTIONS ===

        # Section 1: Work Hours
        section1 = self._create_section(content_frame, "Work Hours")
        tk.Label(section1, text="Start Time:", font=('Segoe UI', 11), bg='#ffffff').grid(row=0, column=0, sticky='w', padx=10, pady=5)

        start_frame = tk.Frame(section1, bg='#ffffff')
        start_frame.grid(row=0, column=1, sticky='w', padx=10, pady=5)

        start_hour = tk.Spinbox(start_frame, from_=0, to=23, width=5, font=('Segoe UI', 11))
        start_hour.pack(side='left')
        start_hour.delete(0, 'end')
        start_hour.insert(0, str(self.app.config.get('work_start_hour')))

        tk.Label(start_frame, text=":", bg='#ffffff', font=('Segoe UI', 11)).pack(side='left', padx=2)

        start_minute = tk.Spinbox(start_frame, from_=0, to=59, width=5, font=('Segoe UI', 11))
        start_minute.pack(side='left')
        start_minute.delete(0, 'end')
        start_minute.insert(0, str(self.app.config.get('work_start_minute')))

        tk.Label(section1, text="End Time:", font=('Segoe UI', 11), bg='#ffffff').grid(row=1, column=0, sticky='w', padx=10, pady=5)

        end_frame = tk.Frame(section1, bg='#ffffff')
        end_frame.grid(row=1, column=1, sticky='w', padx=10, pady=5)

        end_hour = tk.Spinbox(end_frame, from_=0, to=23, width=5, font=('Segoe UI', 11))
        end_hour.pack(side='left')
        end_hour.delete(0, 'end')
        end_hour.insert(0, str(self.app.config.get('work_end_hour')))

        tk.Label(end_frame, text=":", bg='#ffffff', font=('Segoe UI', 11)).pack(side='left', padx=2)

        end_minute = tk.Spinbox(end_frame, from_=0, to=59, width=5, font=('Segoe UI', 11))
        end_minute.pack(side='left')
        end_minute.delete(0, 'end')
        end_minute.insert(0, str(self.app.config.get('work_end_minute')))

        # Section 2: Monitoring Settings
        section2 = self._create_section(content_frame, "Monitoring Settings")

        tk.Label(section2, text="Screenshot interval (minutes):", font=('Segoe UI', 11), bg='#ffffff').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        screenshot_interval = tk.Spinbox(section2, from_=1, to=60, width=10, font=('Segoe UI', 11))
        screenshot_interval.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        screenshot_interval.delete(0, 'end')
        screenshot_interval.insert(0, str(self.app.config.get('screenshot_interval_minutes')))

        tk.Label(section2, text="Idle threshold (seconds):", font=('Segoe UI', 11), bg='#ffffff').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        idle_threshold = tk.Spinbox(section2, from_=60, to=3600, width=10, font=('Segoe UI', 11))
        idle_threshold.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        idle_threshold.delete(0, 'end')
        idle_threshold.insert(0, str(self.app.config.get('idle_start_seconds')))

        tk.Label(section2, text="Warning screen threshold (seconds):", font=('Segoe UI', 11), bg='#ffffff').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        warning_threshold = tk.Spinbox(section2, from_=60, to=3600, width=10, font=('Segoe UI', 11))
        warning_threshold.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        warning_threshold.delete(0, 'end')
        warning_threshold.insert(0, str(self.app.config.get('warning_screen_seconds')))

        # Section 3: Email Reports (placeholder - simplified)
        section3 = self._create_section(content_frame, "Email Reports")
        tk.Label(section3, text="Email features available in full version", font=('Segoe UI', 10, 'italic'), bg='#ffffff', fg='#666').pack(padx=10, pady=10)

        # Section 4: Network Access (placeholder - simplified)
        section4 = self._create_section(content_frame, "Network Access")
        tk.Label(section4, text="Dashboard server features available", font=('Segoe UI', 10, 'italic'), bg='#ffffff', fg='#666').pack(padx=10, pady=10)

        # Section 5: Startup Settings (placeholder - simplified)
        section5 = self._create_section(content_frame, "Startup Settings")
        autostart_var = tk.BooleanVar(value=self.app.config.get('autostart_enabled'))
        tk.Checkbutton(section5, text="Launch on Windows startup", variable=autostart_var, font=('Segoe UI', 11), bg='#ffffff').pack(padx=10, pady=10, anchor='w')

        # Action buttons (pinned bottom)
        button_frame = tk.Frame(panel, bg='#f5f5f7', height=80)
        button_frame.pack(side='bottom', fill='x', padx=20, pady=20)
        button_frame.pack_propagate(False)

        def save_settings():
            """Save all settings"""
            try:
                self.app.config.set('work_start_hour', int(start_hour.get()))
                self.app.config.set('work_start_minute', int(start_minute.get()))
                self.app.config.set('work_end_hour', int(end_hour.get()))
                self.app.config.set('work_end_minute', int(end_minute.get()))
                self.app.config.set('screenshot_interval_minutes', int(screenshot_interval.get()))
                self.app.config.set('idle_start_seconds', int(idle_threshold.get()))
                self.app.config.set('warning_screen_seconds', int(warning_threshold.get()))
                self.app.config.set('autostart_enabled', autostart_var.get())
                messagebox.showinfo("Success", "Settings saved successfully!")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        def change_password():
            """Change admin password"""
            old_pass = simpledialog.askstring("Change Password", "Enter current password:", show='*', parent=panel)
            if not old_pass or not self.app.config.verify_password(old_pass):
                messagebox.showerror("Error", "Invalid current password")
                return

            new_pass = simpledialog.askstring("Change Password", "Enter new password:", show='*', parent=panel)
            if not new_pass:
                return

            confirm_pass = simpledialog.askstring("Change Password", "Confirm new password:", show='*', parent=panel)
            if new_pass != confirm_pass:
                messagebox.showerror("Error", "Passwords don't match")
                return

            self.app.config.set_password(new_pass)
            messagebox.showinfo("Success", "Password changed successfully!")

        def reset_data():
            """Reset all data"""
            if messagebox.askyesno("Confirm Reset", "This will delete all tracked data. Continue?"):
                try:
                    for file in DATA_DIR.glob("d*.dat"):
                        file.unlink()
                    for file in SCREENSHOTS_DIR.glob("screenshot_*.png"):
                        file.unlink()
                    self.app.logger.today_log = self.app.logger.load_today()
                    messagebox.showinfo("Success", "All data has been reset!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to reset data: {e}")

        tk.Button(button_frame, text="Save Settings", command=save_settings,
                 bg='#34c759', fg='white', font=('Segoe UI', 12, 'bold'),
                 relief='flat', padx=20, pady=10, cursor='hand2').pack(side='left', padx=5)

        tk.Button(button_frame, text="Change Password", command=change_password,
                 bg='#007aff', fg='white', font=('Segoe UI', 12, 'bold'),
                 relief='flat', padx=20, pady=10, cursor='hand2').pack(side='left', padx=5)

        tk.Button(button_frame, text="Reset Data", command=reset_data,
                 bg='#ff3b30', fg='white', font=('Segoe UI', 12, 'bold'),
                 relief='flat', padx=20, pady=10, cursor='hand2').pack(side='left', padx=5)

        panel.withdraw()  # Hide by default
        return panel

    def _create_section(self, parent, title):
        """Helper to create a settings section"""
        section_frame = tk.Frame(parent, bg='#ffffff', relief='solid', borderwidth=1)
        section_frame.pack(fill='x', pady=10)

        tk.Label(section_frame, text=title, font=('Segoe UI', 13, 'bold'),
                bg='#ffffff', fg='#1d1d1f').pack(anchor='w', padx=15, pady=10)

        content = tk.Frame(section_frame, bg='#ffffff')
        content.pack(fill='both', padx=15, pady=(0, 15))

        return content

    # ========================================================================
    # WARNING SCREEN MANAGEMENT
    # ========================================================================

    def show_warning_screen(self):
        """Show fullscreen warning (idle too long)"""
        if self.warning_window and self.warning_window.winfo_exists():
            return  # Already showing

        self.warning_window = self._create_warning_screen()

    def dismiss_warning_screen(self):
        """Dismiss warning screen"""
        if self.warning_window and self.warning_window.winfo_exists():
            try:
                self.warning_window.destroy()
            except tk.TclError:
                pass
            finally:
                self.warning_window = None

    def _create_warning_screen(self):
        """Create fullscreen warning window"""
        warning = tk.Toplevel(self.root)
        warning.attributes('-fullscreen', True)
        warning.attributes('-topmost', True)
        warning.configure(bg='#cc0000')

        tk.Label(
            warning,
            text="⚠️ WARNING ⚠️\n\nYou have been idle for too long!\n\nPlease return to work.",
            font=('Segoe UI', 36, 'bold'),
            bg='#cc0000',
            fg='white'
        ).pack(expand=True)

        tk.Button(
            warning,
            text="I'm Back",
            command=self.dismiss_warning_screen,
            font=('Segoe UI', 18, 'bold'),
            bg='#ffffff',
            fg='#cc0000',
            padx=40,
            pady=15,
            cursor='hand2'
        ).pack(pady=30)

        # Dismiss on any click or key
        warning.bind('<Button-1>', lambda e: self.dismiss_warning_screen())
        warning.bind('<Key>', lambda e: self.dismiss_warning_screen())

        return warning

    # ========================================================================
    # FLOATING WIDGET MANAGEMENT
    # ========================================================================

    def start_floating_widget(self):
        """Start floating widget as subprocess"""
        if self.widget_process is None or self.widget_process.poll() is not None:
            try:
                self.widget_process = subprocess.Popen([
                    sys.executable,
                    str(BASE_DIR / "src" / "overlay_widget.py")
                ], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            except Exception as e:
                logger.error(f"Failed to start floating widget: {e}")

    def stop_floating_widget(self):
        """Stop floating widget subprocess"""
        if self.widget_process and self.widget_process.poll() is None:
            try:
                self.widget_process.terminate()
                self.widget_process.wait(timeout=2)
            except Exception as e:
                logger.error(f"Failed to stop floating widget: {e}")
                try:
                    self.widget_process.kill()
                except:
                    pass
            finally:
                self.widget_process = None

    def toggle_floating_widget(self):
        """Toggle floating widget on/off"""
        if self.widget_process and self.widget_process.poll() is None:
            self.stop_floating_widget()
        else:
            self.start_floating_widget()

    def is_widget_running(self):
        """Check if widget is currently running"""
        return self.widget_process is not None and self.widget_process.poll() is None

    # ========================================================================
    # SYSTEM TRAY MANAGEMENT
    # ========================================================================

    def start_tray_icon(self):
        """Start system tray icon in background thread"""
        if self.tray_icon:
            return  # Already running

        def create_icon_image():
            """Create tray icon image"""
            icon_path = BASE_DIR / "icon.ico"
            if icon_path.exists():
                try:
                    return Image.open(icon_path)
                except Exception as e:
                    logger.error(f"Failed to load icon: {e}")

            # Fallback: create simple icon
            img = Image.new('RGB', (64, 64), color='#0066cc')
            draw = ImageDraw.Draw(img)
            draw.ellipse([16, 16, 48, 48], fill='#00cc66')
            return img

        def on_show(icon, item):
            """Restore main window"""
            icon.stop()
            self.root.after(0, self.show_main_window)

        def on_admin_panel(icon, item):
            """Show admin panel from tray"""
            self.root.after(0, self.show_admin_panel)

        def on_dashboard(icon, item):
            """Open dashboard"""
            dashboard_path = BASE_DIR / "dashboard.html"
            if dashboard_path.exists():
                webbrowser.open(str(dashboard_path))

        def on_toggle_widget(icon, item):
            """Toggle floating widget"""
            self.root.after(0, self.toggle_floating_widget)

        def on_exit(icon, item):
            """Exit application"""
            icon.stop()
            self.root.after(0, self.app.quit_app)

        # Dynamic widget menu label
        def get_widget_label():
            return "Hide Floating Widget" if self.is_widget_running() else "Show Floating Widget"

        menu = pystray.Menu(
            item('Show', on_show),
            item(get_widget_label, on_toggle_widget),
            item('Open Dashboard', on_dashboard),
            item('Admin Panel', on_admin_panel),
            item('Exit', on_exit)
        )

        self.tray_icon = pystray.Icon(
            APP_NAME,
            create_icon_image(),
            APP_NAME,
            menu
        )

        # Run in daemon thread
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    def stop_tray_icon(self):
        """Stop system tray icon"""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    # ========================================================================
    # CLEANUP
    # ========================================================================

    def close_all_windows(self):
        """Close all windows on app exit"""
        self.stop_floating_widget()
        self.close_admin_panel()
        self.dismiss_warning_screen()
        self.stop_tray_icon()


# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class WorkMonitorApp:
    """
    Main application with clean architecture.

    This class handles:
    - Application initialization
    - Monitoring loop
    - Business logic coordination
    - UI updates
    """

    def __init__(self):
        # Single instance check
        if LOCK_FILE.exists():
            messagebox.showerror("Error", "WorkMonitor is already running!")
            sys.exit(1)
        LOCK_FILE.write_text(str(os.getpid()))

        # Initialize business logic
        self.config = Config()
        self.logger = ActivityLogger()
        self.screenshot_manager = ScreenshotManager(self.config)
        self.mouse_tracker = MouseTracker(self.config)
        self.keyboard_tracker = KeyboardTracker(self.mouse_tracker.anticheat)

        # Initialize UI
        self.root = tk.Tk()
        self.root.title(APP_NAME)

        # Set window icon
        try:
            icon_path = BASE_DIR / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            logger.error(f"Failed to set window icon: {e}")

        # Window size (adaptive to screen)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 560
        window_height = min(850, screen_height - 100)

        # Center on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(560, 800)  # Ensures all buttons visible

        # Close button behavior: minimize to tray
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Initialize window manager (handles all window lifecycle)
        self.window_manager = WindowManager(self.root, self)

        # Setup UI
        self.setup_ui()

        # Monitoring state
        self.running = True
        self.last_screenshot_time = 0
        self.was_idle = False
        self.warning_shown = False

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

        # Start email reports if enabled
        self.email_sender = None
        if EmailReportSender and self.config.get('email_enabled'):
            self.email_sender = EmailReportSender(self.config, self.logger)
            self.email_sender.start()

        # Start dashboard server if enabled
        self.dashboard_server = None
        if DashboardServer and self.config.get('dashboard_server_enabled'):
            self.dashboard_server = DashboardServer(self.config.get('dashboard_port'))
            self.dashboard_server.start()

        # Schedule UI updates
        self.update_ui()

    def setup_ui(self):
        """
        Setup main window UI with UNBREAKABLE LAYOUT.

        Layout Structure:
        - Header (pinned top, fixed height)
        - Content (scrollable, expands to fill space)
        - Buttons (pinned bottom, fixed height)

        This ensures buttons are ALWAYS visible at default window size.
        """
        # Theme colors
        BG_COLOR = '#f5f5f7'
        CARD_BG = '#ffffff'
        TEXT_DARK = '#1d1d1f'
        TEXT_LIGHT = '#86868b'

        self.root.configure(bg=BG_COLOR)

        # ====================================================================
        # HEADER (pinned top, fixed height)
        # ====================================================================
        header_frame = tk.Frame(self.root, bg=BG_COLOR)
        header_frame.pack(side='top', fill='x', padx=30, pady=(20, 0))

        tk.Label(
            header_frame,
            text="WorkMonitor",
            font=('Segoe UI', 36, 'bold'),
            bg=BG_COLOR,
            fg=TEXT_DARK
        ).pack()

        tk.Label(
            header_frame,
            text="Intelligent Activity Tracking",
            font=('Segoe UI', 15),
            bg=BG_COLOR,
            fg=TEXT_LIGHT
        ).pack()

        # ====================================================================
        # SCROLLABLE CONTENT AREA (expands to fill)
        # ====================================================================
        content_canvas = Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        scrollbar = Scrollbar(self.root, orient='vertical', command=content_canvas.yview)
        content_frame = Frame(content_canvas, bg=BG_COLOR)

        content_canvas.pack(side='left', fill='both', expand=True, padx=30)
        scrollbar.pack(side='right', fill='y')
        content_canvas.configure(yscrollcommand=scrollbar.set)

        content_window = content_canvas.create_window((0, 0), window=content_frame, anchor='nw')

        # Make canvas resize with window
        def on_frame_configure(event):
            content_canvas.configure(scrollregion=content_canvas.bbox('all'))

        def on_canvas_configure(event):
            content_canvas.itemconfig(content_window, width=event.width)

        content_frame.bind('<Configure>', on_frame_configure)
        content_canvas.bind('<Configure>', on_canvas_configure)

        # === STATUS CARD ===
        status_card = self._create_card(content_frame)

        self.status_indicator = tk.Label(
            status_card,
            text="● Active",
            font=('Segoe UI', 16, 'bold'),
            bg=CARD_BG,
            fg='#34c759'
        )
        self.status_indicator.pack(pady=10)

        self.work_hours_label = tk.Label(
            status_card,
            text="Outside Work Hours",
            font=('Segoe UI', 11),
            bg=CARD_BG,
            fg=TEXT_LIGHT
        )
        self.work_hours_label.pack()

        # === STATS CARD ===
        stats_card = self._create_card(content_frame)

        self.work_time_label = self._create_stat_row(stats_card, "Work Time", "0h 0m")
        self.idle_time_label = self._create_stat_row(stats_card, "Idle Time", "0h 0m")
        self.screenshots_label = self._create_stat_row(stats_card, "Screenshots", "0")
        self.security_label = self._create_stat_row(stats_card, "Security Status", "Verified")
        self.network_label = self._create_stat_row(stats_card, "Network Access", "Disabled")

        # === TIMER CARD ===
        timer_card = self._create_card(content_frame)

        self.timer_label = tk.Label(
            timer_card,
            text="00:00:00",
            font=('SF Mono', 48, 'bold'),
            bg=CARD_BG,
            fg=TEXT_DARK
        )
        self.timer_label.pack(pady=20)

        tk.Label(
            timer_card,
            text="Active Time Today",
            font=('Segoe UI', 13),
            bg=CARD_BG,
            fg=TEXT_LIGHT
        ).pack()

        self.inactive_label = tk.Label(
            timer_card,
            text="Inactive: 0m 0s",
            font=('Segoe UI', 11),
            bg=CARD_BG,
            fg=TEXT_LIGHT
        )
        self.inactive_label.pack(pady=(10, 0))

        # ====================================================================
        # BUTTON PANEL (pinned bottom, fixed height)
        # ====================================================================
        button_frame = tk.Frame(self.root, bg=BG_COLOR, height=120)
        button_frame.pack(side='bottom', fill='x', padx=30, pady=20)
        button_frame.pack_propagate(False)

        # Row 1: Primary actions
        row1 = tk.Frame(button_frame, bg=BG_COLOR)
        row1.pack(fill='x', pady=(0, 10))

        self._create_button(
            row1,
            "Open Dashboard",
            self.open_dashboard,
            bg='#007aff',
            side='left',
            expand=True
        )

        self._create_button(
            row1,
            "Admin Panel",
            self.window_manager.show_admin_panel,
            bg='#5856d6',
            side='left',
            expand=True
        )

        # Row 2: Secondary actions
        row2 = tk.Frame(button_frame, bg=BG_COLOR)
        row2.pack(fill='x')

        self._create_button(
            row2,
            "Minimize to Tray",
            self.window_manager.minimize_to_tray,
            bg=BG_COLOR,
            fg=TEXT_DARK,
            outline=True,
            side='left',
            expand=True
        )

        self._create_button(
            row2,
            "Shutdown Program",
            self.quit_app,
            bg='#ff3b30',
            side='left',
            expand=True
        )

    def _create_card(self, parent):
        """Create a white card container"""
        card = tk.Frame(parent, bg='#ffffff', relief='solid', borderwidth=1)
        card.pack(fill='x', pady=10)
        return card

    def _create_stat_row(self, parent, label, value):
        """Create a stat row (label | value)"""
        row = tk.Frame(parent, bg='#ffffff')
        row.pack(fill='x', padx=20, pady=8)

        tk.Label(
            row,
            text=label,
            font=('Segoe UI', 11),
            bg='#ffffff',
            fg='#1d1d1f',
            anchor='w'
        ).pack(side='left')

        value_label = tk.Label(
            row,
            text=value,
            font=('Segoe UI', 11, 'bold'),
            bg='#ffffff',
            fg='#1d1d1f',
            anchor='e'
        )
        value_label.pack(side='right')

        return value_label

    def _create_button(self, parent, text, command, bg, fg='white', outline=False, side='left', expand=False):
        """Create a styled button"""
        btn_config = {
            'text': text,
            'command': command,
            'font': ('Segoe UI', 12, 'bold'),
            'bg': bg,
            'fg': fg,
            'relief': 'solid' if outline else 'flat',
            'borderwidth': 2 if outline else 0,
            'padx': 20,
            'pady': 12,
            'cursor': 'hand2'
        }

        btn = tk.Button(parent, **btn_config)
        btn.pack(side=side, fill='x', expand=expand, padx=5)
        return btn

    # ========================================================================
    # MONITORING LOOP (runs in background thread)
    # ========================================================================

    def monitor_loop(self):
        """Background monitoring thread - checks activity every second"""
        while self.running:
            try:
                # Check mouse and keyboard activity
                self.mouse_tracker.has_moved()
                self.keyboard_tracker.check_activity()

                # Calculate idle time
                mouse_idle = self.mouse_tracker.get_idle_seconds()
                keyboard_idle = self.keyboard_tracker.get_idle_seconds()
                current_idle = min(mouse_idle, keyboard_idle)

                idle_threshold = self.config.get('idle_start_seconds')
                warning_threshold = self.config.get('warning_screen_seconds')

                is_working = current_idle < idle_threshold
                is_work_hours = self.is_work_hours()

                # Check for cheating
                is_cheating = False
                if self.config.get('anticheat_enabled'):
                    is_real = self.mouse_tracker.is_real_activity()
                    if not is_real:
                        is_cheating = True

                # Show warning screen if idle too long during work hours
                if is_work_hours and current_idle >= warning_threshold:
                    if not self.warning_shown:
                        self.root.after(0, self.window_manager.show_warning_screen)
                        self.warning_shown = True
                else:
                    if self.warning_shown:
                        self.root.after(0, self.window_manager.dismiss_warning_screen)
                        self.warning_shown = False

                # Track idle period transitions
                if is_working and self.was_idle:
                    # Person returned from idle
                    self.logger.end_idle_period()
                    self.was_idle = False
                elif not is_working and not self.was_idle:
                    # Person went idle
                    self.logger.start_idle_period()
                    self.was_idle = True

                # Log time (only during work hours)
                if is_work_hours:
                    if is_working:
                        self.logger.add_work_time(1)
                        if is_cheating:
                            self.logger.add_suspicious_time(1)
                    else:
                        self.logger.add_idle_time(1)

                    # Update activity counts
                    if self.mouse_tracker.anticheat:
                        kb_count = self.mouse_tracker.anticheat.keyboard_count
                        win_count = self.mouse_tracker.anticheat.window_change_count
                        self.logger.update_activity_counts(kb_count, win_count)

                # Capture screenshot at interval (only during work hours + working)
                screenshot_interval = self.config.get('screenshot_interval_minutes') * 60
                if is_work_hours and is_working:
                    if time.time() - self.last_screenshot_time >= screenshot_interval:
                        filepath = self.screenshot_manager.capture()
                        if filepath:
                            self.logger.add_screenshot(filepath, is_suspicious=is_cheating)
                            self.last_screenshot_time = time.time()

                # Generate dashboard HTML
                summary = self.logger.get_summary()
                HTMLReportGenerator.save_dashboard(summary, self.config, self.logger)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")

            time.sleep(1)

    def is_work_hours(self):
        """Check if current time is within work hours"""
        now = datetime.now()
        start_hour = self.config.get('work_start_hour')
        start_minute = self.config.get('work_start_minute')
        end_hour = self.config.get('work_end_hour')
        end_minute = self.config.get('work_end_minute')

        start_time = now.replace(hour=start_hour, minute=start_minute, second=0)
        end_time = now.replace(hour=end_hour, minute=end_minute, second=0)

        return start_time <= now <= end_time

    # ========================================================================
    # UI UPDATE (called periodically on main thread)
    # ========================================================================

    def update_ui(self):
        """Update UI with current data (must run on main thread)"""
        try:
            summary = self.logger.get_summary()

            # Update status indicator
            mouse_idle = self.mouse_tracker.get_idle_seconds()
            keyboard_idle = self.keyboard_tracker.get_idle_seconds()
            current_idle = min(mouse_idle, keyboard_idle)
            idle_threshold = self.config.get('idle_start_seconds')

            if current_idle < idle_threshold:
                self.status_indicator.configure(text="● Active", fg='#34c759')
            else:
                self.status_indicator.configure(text="○ Idle", fg='#ff9500')

            # Update work hours label
            if self.is_work_hours():
                self.work_hours_label.configure(text="During Work Hours")
            else:
                self.work_hours_label.configure(text="Outside Work Hours")

            # Update stats
            work_hours = int(summary['work_hours'])
            work_mins = int((summary['work_hours'] - work_hours) * 60)
            self.work_time_label.configure(text=f"{work_hours}h {work_mins}m")

            idle_hours = int(summary['idle_hours'])
            idle_mins = int((summary['idle_hours'] - idle_hours) * 60)
            self.idle_time_label.configure(text=f"{idle_hours}h {idle_mins}m")

            self.screenshots_label.configure(text=str(summary['screenshot_count']))

            # Security status (anti-cheat)
            cheat_status = self.mouse_tracker.get_cheat_status()
            if cheat_status['is_cheating']:
                self.security_label.configure(text="⚠️ Suspicious Activity", fg='#ff3b30')
            else:
                self.security_label.configure(text="✓ Verified", fg='#34c759')

            # Network status
            if self.config.get('dashboard_server_enabled'):
                self.network_label.configure(text="✓ Enabled", fg='#34c759')
            else:
                self.network_label.configure(text="Disabled", fg='#86868b')

            # Update timer
            total_seconds = int(summary['work_hours'] * 3600)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            self.timer_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")

            # Update inactive time
            idle_mins = int(current_idle // 60)
            idle_secs = int(current_idle % 60)
            self.inactive_label.configure(text=f"Inactive: {idle_mins}m {idle_secs}s")

        except Exception as e:
            logger.error(f"Error updating UI: {e}")

        # Schedule next update
        self.root.after(1000, self.update_ui)

    # ========================================================================
    # BUTTON ACTIONS
    # ========================================================================

    def open_dashboard(self):
        """Open dashboard in browser"""
        dashboard_path = BASE_DIR / "dashboard.html"
        if dashboard_path.exists():
            webbrowser.open(str(dashboard_path))
        else:
            messagebox.showinfo("Info", "Dashboard not yet generated. Please wait...")

    def on_window_close(self):
        """Handle window close button (minimize to tray)"""
        self.window_manager.minimize_to_tray()

    def quit_app(self):
        """Quit application completely"""
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit WorkMonitor?"):
            self.running = False

            # Stop all services
            if self.email_sender:
                self.email_sender.stop()
            if self.dashboard_server:
                self.dashboard_server.stop()

            # Close all windows
            self.window_manager.close_all_windows()

            # Remove lock file
            try:
                if LOCK_FILE.exists():
                    LOCK_FILE.unlink()
            except Exception as e:
                logger.error(f"Failed to remove lock file: {e}")

            # Destroy root window
            self.root.destroy()

    def run(self):
        """Run the application main loop"""
        self.root.mainloop()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app = WorkMonitorApp()
    app.run()
