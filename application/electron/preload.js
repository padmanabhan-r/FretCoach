const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  startBackend: () => ipcRenderer.invoke('start-backend'),
  stopBackend: () => ipcRenderer.invoke('stop-backend'),
  getConfig: () => ipcRenderer.invoke('get-config'),
  onPythonOutput: (callback) => {
    ipcRenderer.on('python-output', (_event, data) => callback(data));
  },
  onPythonError: (callback) => {
    ipcRenderer.on('python-error', (_event, data) => callback(data));
  },
});
