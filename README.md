# Task-Tracker v2.0 - Complete Redesign

**Mission-critical, production-ready activity monitoring system with Apple Vision Pro-level polish.**

## 🎯 Project Overview

A complete frontend and backend redesign of the Task-Tracker dashboard featuring:
- **Apple 2025 Aesthetic**: Heavy glassmorphism, ultra-fine borders, SF Pro typography
- **Real-time Updates**: WebSocket-based live data streaming
- **Production-Grade**: Industrial reliability with error handling and edge cases
- **Fully Responsive**: Flawless from 4K displays to mobile devices

## 📁 Project Structure

```
Task-Tracker/
├── api/                          # FastAPI Backend (NEW)
│   ├── main.py                  # REST API + WebSocket server
│   ├── requirements.txt         # Python dependencies
│   └── start.sh                 # Quick start script
│
├── dashboard/                    # Next.js Frontend (NEW)
│   ├── app/                     # App Router pages
│   ├── components/              # React components (Atomic Design)
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # Utilities and API client
│   ├── types/                   # TypeScript definitions
│   └── README.md                # Detailed dashboard docs
│
├── WorkMonitor/                  # Original Python App (UNCHANGED)
│   ├── src/
│   │   └── work_monitor.py      # Main monitoring application
│   └── dashboard.html           # Old dashboard (replaced)
│
└── README.md                     # This file
```

## ✨ Key Features

### Backend (FastAPI)
- RESTful API with 15+ endpoints
- WebSocket for real-time updates (5s polling)
- Reads existing `.cache/*.dat` files (no migration needed)
- Automatic data change detection and broadcasting
- Full CORS support for local development

### Frontend (Next.js + React)
- **Glassmorphic UI**: Apple-inspired design with backdrop blur
- **Spring Physics**: Framer Motion animations with snappy/smooth transitions
- **Real-time Dashboard**: Live updates via WebSocket
- **4 View Modes**: Daily, Weekly, Monthly, Yearly analytics
- **8+ Metrics**: Work time, idle time, suspicious activity, screenshots, etc.
- **Loading States**: Shimmer skeletons for all async operations
- **Error Boundaries**: Graceful error handling
- **Responsive Grid**: 4-column → 2-column → 1-column based on viewport

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** and npm
- **Python 3.10+**
- Task-Tracker monitoring app running (generates data in `.cache/`)

### Installation & Launch

#### Option 1: Run Everything (Recommended)

```bash
# 1. Install API dependencies
cd api
pip install -r requirements.txt

# 2. Install Dashboard dependencies
cd ../dashboard
npm install

# 3. Start API server (Terminal 1)
cd ../api
./start.sh
# API will run on http://localhost:8000

# 4. Start Dashboard (Terminal 2)
cd ../dashboard
npm run dev
# Dashboard will run on http://localhost:3000
```

#### Option 2: Individual Components

**API Only:**
```bash
cd api
pip install -r requirements.txt
python main.py
```

**Dashboard Only:**
```bash
cd dashboard
npm install
npm run dev
```

### Access Points

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **WebSocket**: ws://localhost:8000/ws/activity

## 🔌 Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────┐
│           Original Python Monitoring App             │
│  (Unchanged - continues writing to .cache/*.dat)    │
└─────────────────────────────────────────────────────┘
                          ↓
                  File I/O (base64 encoded)
                          ↓
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)             │
│  - Reads .cache/*.dat files                         │
│  - Provides REST API endpoints                      │
│  - Broadcasts WebSocket updates every 5s            │
└─────────────────────────────────────────────────────┘
                          ↓
                   HTTP + WebSocket
                          ↓
┌─────────────────────────────────────────────────────┐
│         Next.js Dashboard (Port 3000)               │
│  - React Query for data caching                     │
│  - Real-time WebSocket updates                      │
│  - Glassmorphic UI components                       │
│  - Spring-based animations                          │
└─────────────────────────────────────────────────────┘
```

### No Data Migration Required

The new system reads directly from existing `.cache/*.dat` files:
- ✅ All historical data preserved
- ✅ No database setup needed
- ✅ Original monitoring app unchanged
- ✅ Drop-in replacement for old dashboard.html

## 📊 API Endpoints

### Activity Data
```
GET  /api/activity/today          # Today's activity log
GET  /api/activity/date/{date}    # Specific date (YYYY-MM-DD)
GET  /api/activity/week           # Current week summary
GET  /api/activity/month          # Current month summary
GET  /api/activity/year           # Current year summary
GET  /api/activity/range          # Custom date range (?start=...&end=...)
```

### Statistics (Formatted)
```
GET  /api/stats/today             # Today's formatted stats
GET  /api/stats/week              # Week stats with breakdown
GET  /api/stats/month             # Month stats
GET  /api/stats/year              # Year stats
```

### Screenshots & Idle Periods
```
GET  /api/screenshots/today       # Today's screenshots metadata
GET  /api/screenshots/{date}      # Date-specific screenshots
GET  /api/screenshots/file/{name} # Serve screenshot image
GET  /api/idle-periods/today      # Today's idle periods
GET  /api/idle-periods/{date}     # Date-specific idle periods
```

### Configuration & Health
```
GET  /api/config                  # Office hours, settings
GET  /api/health                  # Health check
WS   /ws/activity                 # WebSocket for real-time updates
```

## 🎨 Design System

### Colors (Apple 2025)
- **Background**: `#f5f5f7` (light gray)
- **Glass**: `rgba(255, 255, 255, 0.7)` with 20px blur
- **Success**: `#34c759` (green)
- **Warning**: `#ff9f0a` (orange)
- **Error**: `#ff3b30` (red)
- **Accent**: `#0a84ff` (blue)

### Typography (SF Pro)
- **Display**: 48px, 700 weight (headers)
- **Title 1**: 34px, 600 weight
- **Headline**: 17px, 600 weight
- **Body**: 17px, 400 weight
- **Footnote**: 13px, 400 weight

### Animations (Spring Physics)
```typescript
snappy:  { stiffness: 400, damping: 30 }  // Buttons, toggles
smooth:  { stiffness: 300, damping: 35 }  // Cards, modals
gentle:  { stiffness: 200, damping: 40 }  // Page transitions
bouncy:  { stiffness: 500, damping: 25 }  // Success states
```

## 📱 Responsive Design

| Breakpoint | Width    | Grid Columns | Use Case           |
|------------|----------|-------------|--------------------|
| 4K         | 2560px+  | 4 columns   | 4K displays        |
| 2XL        | 1536px+  | 4 columns   | Large desktop      |
| XL         | 1280px+  | 4 columns   | Desktop            |
| LG         | 1024px+  | 4 columns   | iPad landscape     |
| MD         | 768px+   | 2 columns   | iPad portrait      |
| SM         | 640px+   | 2 columns   | Small tablets      |
| Mobile     | 320px+   | 1 column    | iPhone SE          |

## 🧪 Development

### API Development
```bash
cd api
python main.py  # Hot reload enabled
```

### Dashboard Development
```bash
cd dashboard
npm run dev     # Hot reload enabled
```

### Production Build
```bash
cd dashboard
npm run build
npm run start
```

## 🔧 Configuration

### API Configuration
Edit `api/main.py` constants:
```python
BASE_DIR = Path(__file__).parent.parent / "WorkMonitor"
DATA_DIR = BASE_DIR / ".cache"
SCREENSHOTS_DIR = BASE_DIR / ".tmp"
```

### Dashboard Configuration
Edit `dashboard/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/activity
```

### Monitoring App Configuration
No changes required! The original app continues working as-is.

## ✅ Testing & Verification

### Backend Tests
```bash
# Check API health
curl http://localhost:8000/api/health

# Get today's activity
curl http://localhost:8000/api/activity/today

# Test WebSocket
npm install -g wscat
wscat -c ws://localhost:8000/ws/activity
```

### Frontend Tests
```bash
# Build verification
cd dashboard
npm run build

# Lint check
npm run lint
```

## 🚢 Deployment

### API Deployment
```bash
# Production mode with Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app
```

### Dashboard Deployment
```bash
cd dashboard
npm run build

# Deploy to Vercel, Netlify, or self-host with:
npm run start
```

## 🐛 Troubleshooting

### Issue: "Cannot connect to API"
**Solution:**
```bash
# 1. Check if API is running
curl http://localhost:8000/api/health

# 2. Check CORS settings in api/main.py
# 3. Verify .env.local in dashboard/
```

### Issue: "No data displayed"
**Solution:**
```bash
# 1. Verify monitoring app is running and generating data
ls -la WorkMonitor/.cache/

# 2. Check API can read files
curl http://localhost:8000/api/activity/today

# 3. Check browser console for errors
```

### Issue: "WebSocket not connecting"
**Solution:**
```bash
# 1. Check firewall/antivirus blocking WS connections
# 2. Verify WS URL in .env.local
# 3. Check API logs for WS connection attempts
```

## 📋 Component Inventory

### Atomic Components (9)
- Button (primary, secondary, ghost, danger)
- Badge (success, warning, error, neutral, accent)
- Skeleton (text, circular, rectangular, statCard, image)
- Typography (12 variants with SF Pro hierarchy)
- StatusDot (with pulse animation)

### Molecular Components (2)
- StatCard (with icon, trend, gradient)
- TabNavigation (with sliding indicator)

### Hooks (6)
- `useActivityData(period)` - Main data fetching
- `useTodayActivity()` - Today's data
- `useStats(period)` - Formatted statistics
- `useScreenshots(date)` - Screenshot management
- `useConfig()` - Configuration
- `useRealtime()` - WebSocket connection

## 📚 Documentation

- **Dashboard Docs**: `/dashboard/README.md` (comprehensive)
- **API Reference**: `http://localhost:8000/docs` (Swagger)

## 🎯 Vision Pro Checklist

- ✅ Glassmorphism with 0.5px borders
- ✅ Spring-based physics animations (Framer Motion)
- ✅ Apple SF Pro typography hierarchy
- ✅ Real-time WebSocket updates
- ✅ Responsive 4K to mobile
- ✅ Loading skeletons
- ✅ Error boundaries
- ✅ Empty states
- ✅ Accessible (ARIA labels, semantic HTML)
- ✅ Smooth tab transitions
- ✅ Hover micro-interactions
- ✅ Production-ready build
- ✅ Comprehensive documentation

## 📝 License

Copyright © 2026 - Task-Tracker v2.0

---

**Tech Stack:**
- **Backend**: FastAPI + Uvicorn + WebSockets
- **Frontend**: Next.js 14 + React 18 + TypeScript
- **Styling**: Tailwind CSS + Glassmorphism
- **Animations**: Framer Motion (spring physics)
- **Data**: React Query + Zustand
- **API**: REST + WebSocket

**Mission Accomplished:** Vision Pro-level polish ✨ + Industrial-grade reliability ⚙️
