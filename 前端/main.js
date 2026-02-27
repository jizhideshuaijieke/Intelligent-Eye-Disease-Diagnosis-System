const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const WinState = require('electron-win-state').default;

let loginWindow;
let mainWindow;

const createLoginWindow = () => {
  const { screen } = require('electron');
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    const loginWinWidth = 400;
    const loginWinHeight = 500;
    const x = Math.round((width - loginWinWidth) / 2);
    const y = Math.round((height - loginWinHeight) / 2);
    const winState = new WinState({
        defaultWidth: 400,
        defaultHeight: 500,
        center: true
    });
    loginWindow = new BrowserWindow({
        width: loginWinWidth,
        height: loginWinHeight,
        x,
        y,
        transparent: true,
        webPreferences: {
            preload: path.resolve(__dirname, './preload/index.js'),
            nodeIntegration: false,
            contextIsolation: true,
            transparency: true
        },
        show: false,
        frame: false
    });

    loginWindow.setMenu(null);
    loginWindow.loadURL('http://localhost:7000/login');
    winState.manage(loginWindow);

    loginWindow.on('ready-to-show', () => {
        loginWindow.show();
    });

    loginWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
        console.error(`Failed to load URL: ${validatedURL}, Error: ${errorDescription}`);
    });

    loginWindow.webContents.on('did-finish-load', () => {
        loginWindow.webContents.send('window-object', {
            type: 'window-object',
            windowId: loginWindow.id
        });
    });
};

const createMainWindow = () => {
  const winState = new WinState({
      defaultWidth: 1000,
      defaultHeight: 800
  });
  mainWindow = new BrowserWindow({
      ...winState.winOptions,
      transparent: true,
      webPreferences: {
          preload: path.resolve(__dirname, './preload/index.js'),
          transparent: true,
      },
      show: false,  // 初始不显示窗口
      frame: false
  });

  mainWindow.setMenu(null);
  mainWindow.loadURL('http://localhost:7000/analyses');
  mainWindow.maximize();
  winState.manage(mainWindow);

//   mainWindow.webContents.openDevTools({
//     mode: 'undocked',
//     additionalFeatures: {
//         'autofill': false
//     }
// });
  // 移除原 ready-to-show 事件中的显示逻辑
  // mainWindow.on('ready-to-show', () => {
  //     mainWindow.show();
  // });
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
      console.error(`Failed to load URL: ${validatedURL}, Error: ${errorDescription}`);
  });
  mainWindow.webContents.on('did-finish-load', () => {
      mainWindow.webContents.send('window-object', {
          type: 'window-object',
          windowId: mainWindow.id
      });
      mainWindow.show();  // 页面加载完成后显示窗口
  });
};

app.whenReady().then(() => {
    createLoginWindow();

    app.on('active', () => {
        if (BrowserWindow.getAllWindows().length === 0) createLoginWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

// 监听来自渲染进程的窗口操作请求
ipcMain.on('perform-window-action', (event, { windowId, action }) => {
    const win = BrowserWindow.fromId(windowId);
    if (win) {
        switch (action) {
            case 'close':
                win.close();
                break;
            case 'minimize':
                win.minimize();
                break;
            case 'maximize':
                if (win.isMaximized()) {
                    win.unmaximize();
                } else {
                    win.maximize();
                }
                break;
        }
    }
});

ipcMain.on('move-window', (event, { windowId, x, y, width, height }) => {
    const win = BrowserWindow.fromId(windowId);
    if (win) {
        let newBounds = {
            x: parseInt(x),
            y: parseInt(y),
            width: parseInt(width),
            height: parseInt(height)
        };
        win.setBounds(newBounds);
    }
});

ipcMain.on('login-success', () => {
    if (loginWindow) {
        loginWindow.close();
        createMainWindow();
        // 立即触发主窗口的登录成功事件
        if (mainWindow) {
          mainWindow.webContents.once('did-finish-load', () => {
            mainWindow.webContents.send('login-success');
          });
        }
    }
});    
