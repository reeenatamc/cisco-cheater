// Background script para captura de pantalla
console.log('Background script cargado');

// Escuchar el comando de teclado (Alt+.)
chrome.commands.onCommand.addListener((command) => {
    console.log('Comando recibido:', command);
    
    if (command === 'capture_screen') {
        // Obtener la pestaña activa
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (chrome.runtime.lastError || !tabs || tabs.length === 0) {
                console.error('Error obteniendo tab:', chrome.runtime.lastError);
                return;
            }
            
            const tab = tabs[0];
            console.log('Capturando pestaña:', tab.id);
            
            // Capturar la pantalla
            chrome.tabs.captureVisibleTab(tab.windowId, { format: 'png' }, (imageData) => {
                if (chrome.runtime.lastError) {
                    console.error('Error capturando:', chrome.runtime.lastError);
                    return;
                }
                
                console.log('Captura exitosa, enviando al content script...');
                
                // Enviar la imagen al content script
                chrome.tabs.sendMessage(tab.id, {
                    action: 'showCaptureOverlay',
                    imageData: imageData
                });
            });
        });
    }
});

// También responder a mensajes directos (por si se necesita)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'captureScreen') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (!tabs || tabs.length === 0) {
                sendResponse({ error: 'No active tab' });
                return;
            }
            
            chrome.tabs.captureVisibleTab(tabs[0].windowId, { format: 'png' }, (imageData) => {
                if (chrome.runtime.lastError) {
                    sendResponse({ error: chrome.runtime.lastError.message });
                } else {
                    sendResponse({ imageData: imageData });
                }
            });
        });
        return true;
    }
});
