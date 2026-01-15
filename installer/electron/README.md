# Electron Desktop Wrapper for Task-Tracker

This directory contains the Electron wrapper that packages the Next.js dashboard as a native Windows desktop application.

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Electron Main Process (main.js)         │
│  - Manages application lifecycle                │
│  - Starts FastAPI backend (TaskTrackerAPI.exe)  │
│  - Optionally starts Monitor                    │
│  - Creates BrowserWindow                        │
└─────────────────────────────────────────────────┘
                      ↓
        ┌─────────────────────────────┐
        │  Chromium Renderer Process   │
        │  - Loads Next.js dashboard   │
        │  - Points to localhost:8000  │
        └─────────────────────────────┘
                      ↓
        ┌─────────────────────────────┐
        │    TaskTrackerAPI.exe        │
        │    (FastAPI on port 8000)    │
        └─────────────────────────────┘
```

## Development Setup

1. **Install dependencies:**
   ```bash
   cd installer/electron
   npm install
   ```

2. **Run in development mode:**
   ```bash
   # Terminal 1: Start Next.js dev server
   cd ../../dashboard
   npm run dev

   # Terminal 2: Start API server
   cd ../../api
   python main.py

   # Terminal 3: Start Electron
   cd ../../installer/electron
   npm start
   ```

## Production Build

The Electron app requires the PyInstaller executables to be built first.

1. **Build Python executables** (see `../pyinstaller/README.md`)
2. **Export Next.js as static files:**
   ```bash
   cd ../../dashboard
   npm run build
   npm run export  # This will need to be configured
   ```

3. **Copy exported files:**
   ```bash
   # Copy the exported Next.js build to electron/renderer
   cp -r ../../dashboard/out/* renderer/
   ```

4. **Build Electron app:**
   ```bash
   cd installer/electron
   npm run build
   ```

This will create the installer in `installer/electron/dist/`.

## Notes

- The main process (`main.js`) automatically detects if running in development or production
- In development, it connects to the Next.js dev server at `localhost:3000`
- In production, it serves static files from the `renderer/` directory
- The API server is always started automatically when the app launches
- The Work Monitor can be started from the system tray menu
