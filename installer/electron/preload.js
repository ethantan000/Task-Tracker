/**
 * Task-Tracker Desktop - Preload Script
 * Exposes secure APIs to the renderer process.
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process
// to use ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  // Get the API URL
  getApiUrl: () => ipcRenderer.invoke('get-api-url'),

  // Start the work monitor
  startMonitor: () => ipcRenderer.invoke('start-monitor'),

  // Get the data directory path
  getDataPath: () => ipcRenderer.invoke('get-data-path'),

  // Platform info
  platform: process.platform,
  isPackaged: process.env.NODE_ENV === 'production'
});

console.log('Preload script loaded');
