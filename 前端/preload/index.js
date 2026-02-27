const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    on: (channel, func) => {
        ipcRenderer.on(channel, (event, data) => func(data));
    },
    performWindowAction: (windowId, action) => {
        ipcRenderer.send('perform-window-action', { windowId, action });
    },
    moveWindow: (windowId, x, y, width, height) => {
      ipcRenderer.send('move-window', { windowId, x, y, width, height});
    },
    sendLoginSuccess: () => ipcRenderer.send('login-success'),
    onWindowObject: (callback) => ipcRenderer.on('window-object', callback)
});    