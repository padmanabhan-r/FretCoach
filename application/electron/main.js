const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow = null;
let pythonProcess = null;

// Load environment variables from .env file
function loadEnvFile() {
  const envPath = path.join(__dirname, '../../.env');
  const env = { ...process.env };
  
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    envContent.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, ...valueParts] = trimmed.split('=');
        if (key && valueParts.length > 0) {
          env[key.trim()] = valueParts.join('=').trim();
        }
      }
    });
    console.log('✅ Loaded .env file with smart bulb configuration');
  } else {
    console.warn('⚠️  No .env file found. Smart bulb features will be disabled.');
    console.warn('   Create a .env file in the project root with your Tuya credentials.');
  }
  
  return env;
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#0f172a',
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // Always use dev server in development
  const isDev = !app.isPackaged;
  
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startPythonBackend() {
  const pythonScript = path.join(__dirname, '../../backend/api/server.py');
  const pythonPath = process.env.PYTHON_PATH || 'python3';
  
  // Load environment variables including smart bulb credentials
  const env = loadEnvFile();
  
  pythonProcess = spawn(pythonPath, [pythonScript], { env });

  pythonProcess.stdout?.on('data', (data) => {
    console.log(`FastAPI: ${data}`);
    mainWindow?.webContents.send('python-output', data.toString());
  });

  pythonProcess.stderr?.on('data', (data) => {
    console.error(`FastAPI Error: ${data}`);
    mainWindow?.webContents.send('python-error', data.toString());
  });

  pythonProcess.on('close', (code) => {
    console.log(`FastAPI process exited with code ${code}`);
  });
}

function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}

app.whenReady().then(() => {
  // Start the FastAPI backend first
  startPythonBackend();
  
  // Wait a bit for the backend to start, then create window
  setTimeout(() => {
    createWindow();
  }, 2000);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopPythonBackend();
  if (process.platform !== 'darwin') {
    // Backend already running, just return success
  }
});

ipcMain.handle('start-backend', async () => {
  try {
    startPythonBackend();
    return { success: true };
  } catch (error) {
    return { success: false, error: String(error) };
  }
});

ipcMain.handle('stop-backend', async () => {
  try {
    stopPythonBackend();
    return { success: true };
  } catch (error) {
    return { success: false, error: String(error) };
  }
});

ipcMain.handle('get-config', async () => {
  return {
    backendPath: path.join(__dirname, '../../backend'),
  };
});
