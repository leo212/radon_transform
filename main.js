const { app, BrowserWindow } = require('electron')
const path = require('path');
const url = require('url');
require("./public/js/config");

// Python Server
const PY_FOLDER = './';
const PY_MODULE = 'manage' ;

let pyProc = null;

const getScriptPath = () => {
  return path.join(__dirname, PY_FOLDER, PY_MODULE + '.py')
};

const createPyProc = () => {
  let script = getScriptPath();
  console.log(script);
  pyProc = require('child_process').spawn('python', [script, "runserver"],{ windowsHide : true });

  if (pyProc != null) {
    console.log('python server success started');
  } else {
    console.log('cannot start python server, is python installed?')
  }
};

const exitPyProc = () => {
  process.kill(-pyProc.pid);
  pyProc = null;
  pyPort = null;
};


app.on('ready', createPyProc);
app.on('will-quit', exitPyProc);

// Electron Window Management
let mainWindow = null;

const createWindow = () => {
  mainWindow = new BrowserWindow({width: 1280, height: 1080});
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'views/index.html'), 
    protocol: 'file:',
    slashes: true
  }));
  mainWindow.webContents.openDevTools();

  mainWindow.on('closed', () => {
    mainWindow = null;
  })
};

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
});