/**
 * Task-Tracker Desktop - Main Electron Process
 * Manages the application lifecycle, backend processes, and main window.
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Handle Squirrel startup events (Windows installer)
if (require('electron-squirrel-startup')) {
  app.quit();
}

// Global references
let mainWindow = null;
let apiProcess = null;
let monitorProcess = null;
let tray = null;

// Configuration
const API_PORT = 8000;
const API_URL = `http://localhost:${API_PORT}`;
const NEXT_SERVER_PORT = 3000;
const NEXT_URL = `http://localhost:${NEXT_SERVER_PORT}`;

// Paths
const isPackaged = app.isPackaged;
const rootPath = isPackaged
  ? path.join(process.resourcesPath)
  : path.join(__dirname, '..', '..');

const apiExePath = isPackaged
  ? path.join(process.resourcesPath, 'bin', 'TaskTrackerAPI.exe')
  : path.join(rootPath, 'api', 'main.py');

const monitorExePath = isPackaged
  ? path.join(process.resourcesPath, 'bin', 'TaskTrackerMonitor.exe')
  : path.join(rootPath, 'WorkMonitor', 'src', 'work_monitor.py');

const rendererPath = isPackaged
  ? path.join(__dirname, 'renderer', 'index.html')
  : NEXT_URL;

// Data directories
const dataDirPath = path.join(rootPath, 'WorkMonitor', '.cache');
const screenshotsDirPath = path.join(rootPath, 'WorkMonitor', '.tmp');

// Ensure data directories exist
function ensureDirectories() {
  [dataDirPath, screenshotsDirPath].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * Start the FastAPI backend server
 */
function startAPIServer() {
  return new Promise((resolve, reject) => {
    console.log('Starting API server...');

    if (isPackaged) {
      // Production: Run the compiled executable
      apiProcess = spawn(apiExePath, [], {
        cwd: path.dirname(apiExePath),
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });
    } else {
      // Development: Run Python script with uvicorn
      apiProcess = spawn('python', ['-m', 'uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', API_PORT.toString()], {
        cwd: rootPath,
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });
    }

    apiProcess.stdout.on('data', (data) => {
      console.log(`[API] ${data.toString()}`);
      if (data.toString().includes('Uvicorn running') || data.toString().includes('Application startup complete')) {
        resolve();
      }
    });

    apiProcess.stderr.on('data', (data) => {
      console.error(`[API Error] ${data.toString()}`);
    });

    apiProcess.on('close', (code) => {
      console.log(`API server exited with code ${code}`);
      if (code !== 0 && code !== null) {
        reject(new Error(`API server failed to start (exit code ${code})`));
      }
    });

    apiProcess.on('error', (err) => {
      console.error('Failed to start API server:', err);
      reject(err);
    });

    // Timeout fallback
    setTimeout(() => {
      if (apiProcess && !apiProcess.killed) {
        resolve(); // Assume it started successfully
      }
    }, 5000);
  });
}

/**
 * Start the Work Monitor application
 */
function startMonitor() {
  console.log('Starting Work Monitor...');

  if (isPackaged) {
    // Production: Run the compiled executable
    monitorProcess = spawn(monitorExePath, [], {
      cwd: path.dirname(monitorExePath),
      detached: true,
      stdio: 'ignore'
    });
    monitorProcess.unref(); // Allow it to run independently
  } else {
    // Development: Run Python script
    monitorProcess = spawn('python', [monitorExePath], {
      cwd: path.dirname(monitorExePath),
      detached: true,
      stdio: 'ignore'
    });
    monitorProcess.unref();
  }

  console.log('Work Monitor started');
}

/**
 * Create the main application window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(rootPath, 'WorkMonitor', 'icon.ico'),
    title: 'Task-Tracker Dashboard',
    backgroundColor: '#f5f5f7',
    show: false, // Don't show until ready
  });

  // Load the dashboard
  if (isPackaged) {
    mainWindow.loadFile(rendererPath);
  } else {
    mainWindow.loadURL(NEXT_URL);
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window close
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Development: Open DevTools
  if (!isPackaged) {
    mainWindow.webContents.openDevTools();
  }
}

/**
 * Create system tray icon
 */
function createTray() {
  const iconPath = path.join(rootPath, 'WorkMonitor', 'icon.ico');
  tray = new Tray(iconPath);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show Dashboard',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
        } else {
          createWindow();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Start Monitor',
      click: () => {
        if (!monitorProcess || monitorProcess.killed) {
          startMonitor();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('Task-Tracker');
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
    }
  });
}

/**
 * Cleanup processes on app exit
 */
function cleanup() {
  if (apiProcess) {
    console.log('Stopping API server...');
    apiProcess.kill();
    apiProcess = null;
  }

  // Note: We don't kill the monitor process as it should run independently
  // Users can stop it from the system tray or Task Manager if needed
}

/**
 * Main application initialization
 */
async function initialize() {
  try {
    console.log('Initializing Task-Tracker Desktop...');

    // Ensure data directories exist
    ensureDirectories();

    // Start the API server first
    await startAPIServer();
    console.log('API server started successfully');

    // Create the main window
    createWindow();

    // Create system tray
    createTray();

    // Optional: Auto-start the monitor
    // Uncomment the following line to automatically start the monitor:
    // startMonitor();

    console.log('Task-Tracker Desktop initialized successfully');
  } catch (error) {
    console.error('Failed to initialize application:', error);
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start Task-Tracker:\n\n${error.message}\n\nPlease check the logs and try again.`
    );
    app.quit();
  }
}

// App lifecycle events
app.whenReady().then(initialize);

app.on('window-all-closed', () => {
  // On macOS, apps typically stay open even with all windows closed
  // But this is a Windows app, so we keep the process running for the tray
  if (process.platform !== 'darwin') {
    // Keep running in background (tray remains active)
  }
});

app.on('activate', () => {
  // On macOS, re-create window when dock icon is clicked
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
  cleanup();
});

app.on('will-quit', cleanup);

// IPC handlers
ipcMain.handle('get-api-url', () => API_URL);
ipcMain.handle('start-monitor', () => {
  startMonitor();
  return { success: true };
});

ipcMain.handle('get-data-path', () => dataDirPath);
