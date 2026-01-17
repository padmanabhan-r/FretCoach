const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  startBackend: () => ipcRenderer.invoke('start-backend'),
  stopBackend: () => ipcRenderer.invoke('stop-backend'),
  checkBackend: () => ipcRenderer.invoke('check-backend'),
  getConfig: () => ipcRenderer.invoke('get-config'),
  onPythonOutput: (callback) => {
    ipcRenderer.on('python-output', (_event, data) => callback(data));
  },
  onPythonError: (callback) => {
    ipcRenderer.on('python-error', (_event, data) => callback(data));
  },
  onBackendReady: (callback) => {
    ipcRenderer.on('backend-ready', (_event, ready) => callback(ready));
  },
});
