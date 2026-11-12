// Expose only the local app's close action and startup availability.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('openFlightDesktop', {
  quit: () => ipcRenderer.send('openflight:quit'),
  backendAvailable: !process.argv.includes('--openflight-backend-unavailable'),
});
