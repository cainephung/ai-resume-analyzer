const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let streamlitProcess;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true
    }
  });

  win.loadURL('http://localhost:8501');
}

app.whenReady().then(() => {
  // Path to run.py (1 level up from electron-app/)
  const scriptPath = path.join(__dirname, '..', 'dist', 'run');

  // Detect Python command: 'python3' on macOS, 'python' on Windows
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

  streamlitProcess = spawn(pythonCmd, [scriptPath], {
    shell: true,
    stdio: 'inherit'
  });

  // Wait a moment for Streamlit to boot before opening the window
  setTimeout(createWindow, 3000);

  app.on('before-quit', () => {
    if (streamlitProcess) {
      streamlitProcess.kill();
    }
  });
});
