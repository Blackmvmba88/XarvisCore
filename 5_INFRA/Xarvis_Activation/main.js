const { app, BrowserWindow } = require('electron');
const express = require('express');
const path = require('path');
const http = require('http');

const appExpress = express();
const server = http.createServer(appExpress);

// Ruta estática para servir la interfaz web
appExpress.use(express.static(path.join(__dirname, 'public')));

appExpress.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Inicia el servidor Express
server.listen(3000, () => {
    console.log('Servidor web corriendo en http://localhost:3000');
});

// Configuración de Electron
function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
        },
    });

    win.loadURL('http://localhost:3000');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
