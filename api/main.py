"""
FastAPI Backend for Task-Tracker Dashboard
Provides REST API endpoints and WebSocket for real-time activity monitoring.

Copyright (c) 2026
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from pathlib import Path
import json
import base64
import logging
from typing import Optional, Dict, List, Any
import asyncio
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths (same as monitoring app)
BASE_DIR = Path(__file__).parent.parent / "WorkMonitor"
DATA_DIR = BASE_DIR / ".cache"
SCREENSHOTS_DIR = BASE_DIR / ".tmp"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Data encoding helpers (same as work_monitor.py)
def encode_data(data: Dict) -> str:
    """Encode JSON data to base64"""
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()

def decode_data(encoded_str: str) -> Optional[Dict]:
    """Decode base64 data to JSON"""
    try:
        json_str = base64.b64decode(encoded_str.encode()).decode()
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Failed to decode data: {e}")
        return None

def get_log_filename(date_str: str) -> str:
    """Generate obfuscated log filename from date"""
    encoded = base64.b64encode(date_str.encode()).decode().replace('=', '').replace('/', '_')
    return f"d{encoded}.dat"

def date_from_log_filename(filename: str) -> Optional[str]:
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

# Data loading functions
def load_date(date_str: str) -> Optional[Dict]:
    """Load log for a specific date"""
    log_file = DATA_DIR / get_log_filename(date_str)
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                encoded = f.read()
                return decode_data(encoded)
        except (IOError, OSError) as e:
            logger.error(f"Failed to load log for date {date_str}: {e}")
    return None

def load_today() -> Dict:
    """Load today's activity log"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log = load_date(date_str)
    if log:
        return log

    # Return default structure if no data
    return {
        "date": date_str,
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

def get_date_range_summary(start_date: datetime, end_date: datetime) -> Dict:
    """Get summary for a date range"""
    total_work = 0
    total_idle = 0
    total_overtime = 0
    total_suspicious = 0
    total_screenshots = 0
    total_keyboard = 0
    total_window = 0
    daily_data = []

    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        log = load_date(date_str)
        if log:
            work_seconds = log.get("work_seconds", 0)
            idle_seconds = log.get("idle_seconds", 0)
            overtime_seconds = log.get("overtime_seconds", 0)
            suspicious_seconds = log.get("suspicious_seconds", 0)
            screenshots = len(log.get("screenshots", []))
            keyboard = log.get("keyboard_activity_count", 0)
            window = log.get("window_change_count", 0)

            total_work += work_seconds
            total_idle += idle_seconds
            total_overtime += overtime_seconds
            total_suspicious += suspicious_seconds
            total_screenshots += screenshots
            total_keyboard += keyboard
            total_window += window

            daily_data.append({
                "date": date_str,
                "work_seconds": work_seconds,
                "idle_seconds": idle_seconds,
                "overtime_seconds": overtime_seconds,
                "suspicious_seconds": suspicious_seconds,
                "real_work_seconds": work_seconds - suspicious_seconds,
                "screenshot_count": screenshots,
                "keyboard_activity_count": keyboard,
                "window_change_count": window,
            })

        current += timedelta(days=1)

    num_days = len(daily_data)
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_work_seconds": total_work,
        "total_idle_seconds": total_idle,
        "total_overtime_seconds": total_overtime,
        "total_suspicious_seconds": total_suspicious,
        "total_real_work_seconds": total_work - total_suspicious,
        "total_screenshot_count": total_screenshots,
        "total_keyboard_activity": total_keyboard,
        "total_window_changes": total_window,
        "average_work_per_day": total_work / num_days if num_days > 0 else 0,
        "average_idle_per_day": total_idle / num_days if num_days > 0 else 0,
        "daily_breakdown": daily_data,
    }

def get_week_summary() -> Dict:
    """Get summary for current week (Mon-Sun)"""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    return get_date_range_summary(start_of_week, today)

def get_month_summary() -> Dict:
    """Get summary for current month"""
    today = datetime.now()
    start_of_month = today.replace(day=1)
    return get_date_range_summary(start_of_month, today)

def get_year_summary() -> Dict:
    """Get summary for current year"""
    today = datetime.now()
    start_of_year = today.replace(month=1, day=1)
    return get_date_range_summary(start_of_year, today)

def load_config() -> Dict:
    """Load configuration from sys.dat"""
    config_file = DATA_DIR / "sys.dat"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                encoded = f.read()
                return decode_data(encoded) or {}
        except (IOError, OSError) as e:
            logger.error(f"Failed to load config: {e}")
    return {}

# FastAPI app
app = FastAPI(
    title="Task-Tracker API",
    description="Real-time activity monitoring API",
    version="2.0.0"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")

manager = ConnectionManager()

# Background task to watch for data changes and broadcast updates
last_data_check = None
async def watch_data_changes():
    """Watch for changes in today's activity data and broadcast to clients"""
    global last_data_check

    while True:
        try:
            today_file = DATA_DIR / get_log_filename(datetime.now().strftime("%Y-%m-%d"))
            if today_file.exists():
                mtime = today_file.stat().st_mtime
                if last_data_check is None or mtime > last_data_check:
                    last_data_check = mtime
                    # Data changed, broadcast update
                    if len(manager.active_connections) > 0:
                        await manager.broadcast({
                            "type": "activity_update",
                            "timestamp": datetime.now().isoformat()
                        })
        except Exception as e:
            logger.error(f"Error watching data changes: {e}")

        await asyncio.sleep(5)  # Check every 5 seconds

@app.on_event("startup")
async def startup_event():
    """Start background tasks on app startup"""
    asyncio.create_task(watch_data_changes())
    logger.info("FastAPI server started. Data watcher active.")

# API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Task-Tracker API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "activity": "/api/activity/*",
            "screenshots": "/api/screenshots/*",
            "stats": "/api/stats/*",
            "config": "/api/config",
            "websocket": "/ws/activity"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Activity Data Endpoints

@app.get("/api/activity/today")
async def get_today_activity():
    """Get today's activity data"""
    try:
        data = load_today()
        # Calculate real work time
        data["real_work_seconds"] = data["work_seconds"] - data["suspicious_seconds"]
        data["screenshot_count"] = len(data.get("screenshots", []))
        return data
    except Exception as e:
        logger.error(f"Error loading today's activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activity/date/{date}")
async def get_date_activity(date: str):
    """Get activity data for a specific date (YYYY-MM-DD)"""
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
        data = load_date(date)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for date {date}")

        # Calculate real work time
        data["real_work_seconds"] = data["work_seconds"] - data["suspicious_seconds"]
        data["screenshot_count"] = len(data.get("screenshots", []))
        return data
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error loading activity for {date}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activity/week")
async def get_week_activity():
    """Get current week's activity summary"""
    try:
        return get_week_summary()
    except Exception as e:
        logger.error(f"Error loading week summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activity/month")
async def get_month_activity():
    """Get current month's activity summary"""
    try:
        return get_month_summary()
    except Exception as e:
        logger.error(f"Error loading month summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activity/year")
async def get_year_activity():
    """Get current year's activity summary"""
    try:
        return get_year_summary()
    except Exception as e:
        logger.error(f"Error loading year summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activity/range")
async def get_range_activity(start: str, end: str):
    """Get activity summary for a custom date range"""
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")

        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

        return get_date_range_summary(start_date, end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error loading range summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Screenshot Endpoints

@app.get("/api/screenshots/today")
async def get_today_screenshots():
    """Get today's screenshots metadata"""
    try:
        data = load_today()
        screenshots = data.get("screenshots", [])

        # Add URL for each screenshot
        for screenshot in screenshots:
            filename = Path(screenshot["path"]).name
            screenshot["url"] = f"/api/screenshots/file/{filename}"

        return {"date": data["date"], "screenshots": screenshots}
    except Exception as e:
        logger.error(f"Error loading today's screenshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screenshots/{date}")
async def get_date_screenshots(date: str):
    """Get screenshots for a specific date"""
    try:
        datetime.strptime(date, "%Y-%m-%d")
        data = load_date(date)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for date {date}")

        screenshots = data.get("screenshots", [])

        # Add URL for each screenshot
        for screenshot in screenshots:
            filename = Path(screenshot["path"]).name
            screenshot["url"] = f"/api/screenshots/file/{filename}"

        return {"date": date, "screenshots": screenshots}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error loading screenshots for {date}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screenshots/file/{filename}")
async def get_screenshot_file(filename: str):
    """Serve a screenshot image file"""
    try:
        file_path = SCREENSHOTS_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Screenshot not found")

        return FileResponse(file_path, media_type="image/png")
    except Exception as e:
        logger.error(f"Error serving screenshot {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Idle Periods Endpoints

@app.get("/api/idle-periods/today")
async def get_today_idle_periods():
    """Get today's idle periods"""
    try:
        data = load_today()
        return {
            "date": data["date"],
            "idle_periods": data.get("idle_periods", [])
        }
    except Exception as e:
        logger.error(f"Error loading today's idle periods: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/idle-periods/{date}")
async def get_date_idle_periods(date: str):
    """Get idle periods for a specific date"""
    try:
        datetime.strptime(date, "%Y-%m-%d")
        data = load_date(date)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for date {date}")

        return {
            "date": date,
            "idle_periods": data.get("idle_periods", [])
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error loading idle periods for {date}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics Endpoints (Computed/Formatted)

@app.get("/api/stats/today")
async def get_today_stats():
    """Get formatted statistics for today"""
    try:
        data = load_today()

        work_seconds = data.get("work_seconds", 0)
        idle_seconds = data.get("idle_seconds", 0)
        suspicious_seconds = data.get("suspicious_seconds", 0)
        real_work_seconds = work_seconds - suspicious_seconds

        return {
            "date": data["date"],
            "stats": {
                "work_time": {
                    "seconds": work_seconds,
                    "formatted": format_time(work_seconds)
                },
                "idle_time": {
                    "seconds": idle_seconds,
                    "formatted": format_time(idle_seconds)
                },
                "suspicious_time": {
                    "seconds": suspicious_seconds,
                    "formatted": format_time(suspicious_seconds)
                },
                "real_work_time": {
                    "seconds": real_work_seconds,
                    "formatted": format_time(real_work_seconds)
                },
                "keyboard_activity": data.get("keyboard_activity_count", 0),
                "window_changes": data.get("window_change_count", 0),
                "screenshot_count": len(data.get("screenshots", [])),
                "idle_period_count": len(data.get("idle_periods", [])),
            }
        }
    except Exception as e:
        logger.error(f"Error computing today's stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/week")
async def get_week_stats():
    """Get formatted statistics for current week"""
    try:
        summary = get_week_summary()
        return format_summary_stats(summary, "week")
    except Exception as e:
        logger.error(f"Error computing week stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/month")
async def get_month_stats():
    """Get formatted statistics for current month"""
    try:
        summary = get_month_summary()
        return format_summary_stats(summary, "month")
    except Exception as e:
        logger.error(f"Error computing month stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/year")
async def get_year_stats():
    """Get formatted statistics for current year"""
    try:
        summary = get_year_summary()
        return format_summary_stats(summary, "year")
    except Exception as e:
        logger.error(f"Error computing year stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration Endpoints

@app.get("/api/config")
async def get_config():
    """Get application configuration"""
    try:
        config = load_config()
        return {
            "office_hours": {
                "start": config.get("office_start", "09:00"),
                "end": config.get("office_end", "17:00"),
            },
            "screenshot_interval": config.get("screenshot_interval", 180),
            "idle_timeout": config.get("idle_timeout", 300),
            "anti_cheat_enabled": config.get("anti_cheat_enabled", True),
        }
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket Endpoint

@app.websocket("/ws/activity")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time activity updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Utility functions

def format_time(seconds: int) -> str:
    """Format seconds into human-readable time string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"

def format_summary_stats(summary: Dict, period: str) -> Dict:
    """Format summary statistics with human-readable values"""
    return {
        "period": period,
        "start_date": summary["start_date"],
        "end_date": summary["end_date"],
        "totals": {
            "work_time": {
                "seconds": summary["total_work_seconds"],
                "formatted": format_time(summary["total_work_seconds"])
            },
            "idle_time": {
                "seconds": summary["total_idle_seconds"],
                "formatted": format_time(summary["total_idle_seconds"])
            },
            "suspicious_time": {
                "seconds": summary["total_suspicious_seconds"],
                "formatted": format_time(summary["total_suspicious_seconds"])
            },
            "real_work_time": {
                "seconds": summary["total_real_work_seconds"],
                "formatted": format_time(summary["total_real_work_seconds"])
            },
            "screenshot_count": summary["total_screenshot_count"],
            "keyboard_activity": summary["total_keyboard_activity"],
            "window_changes": summary["total_window_changes"],
        },
        "averages": {
            "work_per_day": {
                "seconds": int(summary["average_work_per_day"]),
                "formatted": format_time(int(summary["average_work_per_day"]))
            },
            "idle_per_day": {
                "seconds": int(summary["average_idle_per_day"]),
                "formatted": format_time(int(summary["average_idle_per_day"]))
            },
        },
        "daily_breakdown": summary["daily_breakdown"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
