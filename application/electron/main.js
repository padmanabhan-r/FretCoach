const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn, execSync } = require('child_process');
const fs = require('fs');
const http = require('http');

let mainWindow = null;
let pythonProcess = null;
let backendReady = false;
let isQuitting = false;

// Ensure single instance
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  console.log('Another instance is already running. Exiting.');
  app.quit();
} else {
  app.on('second-instance', () => {
    // Focus the main window if a second instance is attempted
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

// Kill any existing process on port 8000 at startup
function killExistingBackend() {
  try {
    if (process.platform === 'darwin' || process.platform === 'linux') {
      // Find and kill any process using port 8000
      try {
        const pid = execSync('lsof -t -i:8000 2>/dev/null || true', { encoding: 'utf-8' }).trim();
        if (pid) {
          console.log(`Found existing process on port 8000 (PID: ${pid}), killing...`);
          execSync(`kill -9 ${pid} 2>/dev/null || true`);
        }
      } catch (e) {
        // Ignore errors - port might not be in use
      }
    }
  } catch (error) {
    console.warn('Could not check for existing backend:', error.message);
  }
}

// Load environment variables from .env file
function loadEnvFile() {
  // Try multiple locations for .env file
  const envPaths = [
    path.join(__dirname, '../../backend/.env'),  // backend folder
    path.join(__dirname, '../../.env'),           // project root
    path.join(__dirname, '../.env'),              // application folder
  ];
  
  const env = { ...process.env };
  let envLoaded = false;
  
  for (const envPath of envPaths) {
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
      console.log(`✅ Loaded .env file from ${envPath}`);
      envLoaded = true;
      break;
    }
  }
  
  if (!envLoaded) {
    console.warn('⚠️  No .env file found. Smart bulb features will be disabled.');
    console.warn('   Create a .env file in backend/ or project root with your Tuya credentials.');
  }
  
  return env;
}

function createWindow() {
  const isDev = !app.isPackaged;

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#141414',
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      // Only disable webSecurity in development for localhost requests
      // In production, the packaged app can communicate with localhost backend safely
      webSecurity: !isDev,
      preload: path.join(__dirname, 'preload.js'),
    },
  });
  
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
  const backendDir = path.join(__dirname, '../../');
  const pythonPath = process.env.PYTHON_PATH || path.join(backendDir, '.venv/bin/python');

  // Load environment variables including smart bulb credentials
  const env = loadEnvFile();

  // Run as a module to support relative imports
  pythonProcess = spawn(pythonPath, ['-m', 'backend.api.server'], {
    cwd: backendDir,
    env,
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // Store the PID for cleanup
  if (pythonProcess.pid) {
    console.log(`Started FastAPI backend with PID: ${pythonProcess.pid}`);
  }

  pythonProcess.stdout?.on('data', (data) => {
    console.log(`FastAPI: ${data}`);
    // Safely send to renderer, handling EPIPE errors
    try {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('python-output', data.toString());
      }
    } catch (error) {
      // Ignore EPIPE errors when window is closing
      if (error.code !== 'EPIPE') {
        console.warn('Error sending to renderer:', error.message);
      }
    }
  });

  pythonProcess.stderr?.on('data', (data) => {
    console.error(`FastAPI Error: ${data}`);
    // Safely send to renderer, handling EPIPE errors
    try {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('python-error', data.toString());
      }
    } catch (error) {
      // Ignore EPIPE errors when window is closing
      if (error.code !== 'EPIPE') {
        console.warn('Error sending to renderer:', error.message);
      }
    }
  });

  pythonProcess.on('error', (error) => {
    console.error('Failed to start FastAPI process:', error);
  });

  pythonProcess.on('close', (code, signal) => {
    console.log(`FastAPI process exited with code ${code}, signal ${signal}`);
    pythonProcess = null;
    backendReady = false;
  });
}

function stopPythonBackend() {
  if (!pythonProcess) {
    backendReady = false;
    return;
  }

  console.log('Stopping FastAPI backend...');
  const pid = pythonProcess.pid;

  // Remove all listeners to prevent EPIPE errors
  pythonProcess.stdout?.removeAllListeners();
  pythonProcess.stderr?.removeAllListeners();
  pythonProcess.removeAllListeners();

  try {
    // Try graceful shutdown first (SIGTERM)
    pythonProcess.kill('SIGTERM');

    // Force kill after a short timeout
    setTimeout(() => {
      try {
        if (pythonProcess) {
          pythonProcess.kill('SIGKILL');
        }
        // Also try to kill by PID directly as a fallback
        if (pid && process.platform !== 'win32') {
          try {
            execSync(`kill -9 ${pid} 2>/dev/null || true`);
          } catch (e) {
            // Process already dead
          }
        }
      } catch (error) {
        // Process already dead
      }
    }, 1000);
  } catch (error) {
    console.warn('Error stopping backend:', error.message);
  }

  pythonProcess = null;
  backendReady = false;
}

// Poll the backend until it responds
function waitForBackend(maxAttempts = 30, intervalMs = 500) {
  return new Promise((resolve, reject) => {
    let attempts = 0;

    const checkBackend = () => {
      attempts++;
      console.log(`Checking backend health (attempt ${attempts}/${maxAttempts})...`);

      const req = http.request({
        hostname: '127.0.0.1',
        port: 8000,
        path: '/',
        method: 'GET',
        timeout: 2000
      }, (res) => {
        if (res.statusCode === 200) {
          console.log('✅ Backend is ready!');
          backendReady = true;
          resolve(true);
        } else {
          retryOrFail();
        }
      });

      req.on('error', () => {
        retryOrFail();
      });

      req.on('timeout', () => {
        req.destroy();
        retryOrFail();
      });

      req.end();
    };

    const retryOrFail = () => {
      if (attempts < maxAttempts) {
        setTimeout(checkBackend, intervalMs);
      } else {
        console.error('❌ Backend failed to start after maximum attempts');
        reject(new Error('Backend failed to start'));
      }
    };

    checkBackend();
  });
}

// Handle app 'before-quit' event
app.on('before-quit', () => {
  isQuitting = true;
});

// Handle uncaught exceptions to prevent crashes
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  // Don't crash the app for EPIPE errors
  if (error.code === 'EPIPE') {
    console.log('Ignoring EPIPE error');
    return;
  }
});

app.whenReady().then(async () => {
  // Kill any existing backend on port 8000
  killExistingBackend();

  // Start the FastAPI backend
  startPythonBackend();

  // Wait for backend to be ready before creating window
  try {
    await waitForBackend();
    createWindow();

    // Notify renderer that backend is ready
    mainWindow?.webContents.on('did-finish-load', () => {
      try {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('backend-ready', true);
        }
      } catch (error) {
        // Ignore errors during startup
      }
    });
  } catch (error) {
    console.error('Failed to start backend:', error);
    // Create window anyway to show error to user
    createWindow();
    mainWindow?.webContents.on('did-finish-load', () => {
      try {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('backend-ready', false);
        }
      } catch (error) {
        // Ignore errors during startup
      }
    });
  }

  app.on('activate', async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      if (!backendReady) {
        killExistingBackend();
        startPythonBackend();
        try {
          await waitForBackend();
        } catch (error) {
          console.error('Failed to restart backend:', error);
        }
      }
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Stop the backend when all windows are closed
  stopPythonBackend();

  // On macOS, wait a bit for backend to fully stop before quitting
  if (process.platform === 'darwin') {
    setTimeout(() => {
      // Kill any remaining processes on port 8000
      killExistingBackend();
    }, 500);
  }

  // Quit on all platforms when windows close
  app.quit();
});

// Final cleanup on quit
app.on('will-quit', (event) => {
  // Ensure backend is stopped
  stopPythonBackend();
  killExistingBackend();
});

ipcMain.handle('start-backend', async () => {
  try {
    // If backend is already running, just return success
    if (backendReady && pythonProcess) {
      return { success: true, alreadyRunning: true };
    }
    startPythonBackend();
    await waitForBackend();
    return { success: true };
  } catch (error) {
    return { success: false, error: String(error) };
  }
});

ipcMain.handle('check-backend', async () => {
  return { ready: backendReady };
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
