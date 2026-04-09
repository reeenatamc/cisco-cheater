// Background script para captura de pantalla
console.log('Background script cargado');

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
            console.log('Enviando orden a la pestaña:', tab.id);
            
            // Enviar la orden al content script de que debe iniciar overlay
            chrome.tabs.sendMessage(tab.id, {
                action: 'iniciarCaptura'
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
