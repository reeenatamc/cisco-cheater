const serverURL = "https://web-production-bd98a.up.railway.app";

// Flag to prevent multiple popups
let popupActivo = null;

// Flag for capture mode
let modoCaptura = false;
// const serverURL = "https://cisco-cheater.onrender.com";
// const serverURL = "http://104.248.177.44";


// Generate a unique device ID
function generateDeviceId() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['deviceId'], function (result) {
            let deviceId = result.deviceId;
            if (!deviceId) {
                deviceId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                    const r = Math.random() * 16 | 0;
                    const v = c === 'x' ? r : (r & 0x3 | 0x8);
                    return v.toString(16);
                });
                chrome.storage.local.set({ deviceId: deviceId });
            }
            resolve(deviceId);
        });
    });
}

// Check activation status
async function checkActivation() {
    const deviceId = await generateDeviceId();
    try {
        const response = await fetch(`${serverURL}/verify_activation/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ device_id: deviceId })
        });

        const text = await response.text();
        try {
            const data = JSON.parse(text);
            return data.is_activated;
        } catch (e) {
            console.error('Response is not JSON:', text.substring(0, 100));
            return false;
        }
    } catch (error) {
        console.error('Error checking activation:', error);
        return false;
    }
}

// Activate extension
async function activateExtension(key, geminiApiKey) {
    const deviceId = await generateDeviceId();
    try {
        const response = await fetch(`${serverURL}/activate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                key: key,
                device_id: deviceId
            })
        });

        const text = await response.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error('Response is not JSON:', text.substring(0, 200));
            return { success: false, message: 'Server error (invalid response)' };
        }

        if (response.ok) {
            chrome.storage.local.set({
                isActivated: true,
                geminiApiKey: geminiApiKey
            });
            return { success: true, message: data.message };
        } else {
            console.error('Server response:', data);
            return { success: false, message: data.error || 'Unknown server error' };
        }
    } catch (error) {
        console.error('Full error:', error);
        return { success: false, message: `Error connecting to server: ${error.message}` };
    }
}

// Start screen capture with area selector
function iniciarCapturaPantalla() {
    modoCaptura = true;

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'capturaOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: transparent;
        cursor: crosshair;
        z-index: 99999;
    `;

    // Create selection element
    const seleccion = document.createElement('div');
    seleccion.id = 'capturaSeleccion';
    seleccion.style.cssText = `
        position: fixed;
        border: 2px dashed #fff;
        background: rgba(255,255,255,0.1);
        display: none;
        z-index: 100000;
        pointer-events: none;
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(seleccion);

    let startX, startY, isDrawing = false;

    overlay.addEventListener('mousedown', (e) => {
        isDrawing = true;
        startX = e.clientX;
        startY = e.clientY;
        seleccion.style.left = startX + 'px';
        seleccion.style.top = startY + 'px';
        seleccion.style.width = '0';
        seleccion.style.height = '0';
        seleccion.style.display = 'block';
    });

    overlay.addEventListener('mousemove', (e) => {
        if (!isDrawing) return;

        const currentX = e.clientX;
        const currentY = e.clientY;

        const width = Math.abs(currentX - startX);
        const height = Math.abs(currentY - startY);
        const left = Math.min(startX, currentX);
        const top = Math.min(startY, currentY);

        seleccion.style.left = left + 'px';
        seleccion.style.top = top + 'px';
        seleccion.style.width = width + 'px';
        seleccion.style.height = height + 'px';
    });

    overlay.addEventListener('mouseup', async (e) => {
        if (!isDrawing) return;
        isDrawing = false;

        const rect = seleccion.getBoundingClientRect();

        // Clean up
        overlay.remove();
        seleccion.remove();
        modoCaptura = false;

        if (rect.width < 10 || rect.height < 10) {
            return; // Selection too small
        }

        // Show loading
        mostrarRespuesta('Capturing...', true);

        // Capture screen using background script
        console.log('Sending message to background...');

        chrome.runtime.sendMessage({ action: 'captureScreen' }, async (response) => {
            console.log('Response from background:', response);

            if (chrome.runtime.lastError) {
                console.error('Error runtime:', chrome.runtime.lastError);
                mostrarRespuesta('Error: ' + chrome.runtime.lastError.message, true);
                return;
            }

            if (response && response.error) {
                console.error('Background error:', response.error);
                mostrarRespuesta('Error: ' + response.error, true);
                return;
            }

            if (response && response.imageData) {
                try {
                    console.log('Processing image...');
                    // Crop image to selected area
                    const imagenRecortada = await recortarImagen(
                        response.imageData,
                        rect.left,
                        rect.top,
                        rect.width,
                        rect.height,
                        window.devicePixelRatio || 1
                    );

                    console.log('Sending to Gemini...');
                    // Send to Gemini
                    await enviarImagenAGemini(imagenRecortada);
                } catch (error) {
                    console.error('Error processing image:', error);
                    mostrarRespuesta('Error: ' + error.message, true);
                }
            } else {
                console.error('Invalid response:', response);
                mostrarRespuesta('No capture data', true);
            }
        });
    });

    // Cancel with ESC
    const cancelar = (e) => {
        if (e.key === 'Escape') {
            overlay.remove();
            seleccion.remove();
            modoCaptura = false;
            document.removeEventListener('keydown', cancelar);
        }
    };
    document.addEventListener('keydown', cancelar);
}

// Listener para atajos de teclado del background (cuando Chrome sí lo registra)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'iniciarCaptura') {
        if (popupActivo) { popupActivo.remove(); popupActivo = null; }
        if (!modoCaptura) { iniciarCapturaPantalla(); }
    }
});

// Listener directo en la página web (Garantía contra fallos de Chrome/Mac)
document.addEventListener('keydown', (e) => {
    // En Mac Option+. produce "≥", por eso usamos e.code === 'Period'
    if (e.altKey && e.code === 'Period') {
        e.preventDefault();
        if (popupActivo) { popupActivo.remove(); popupActivo = null; }
        if (!modoCaptura) { iniciarCapturaPantalla(); }
    }
});

// Crop image to selected area
async function recortarImagen(imageData, x, y, width, height, dpr) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = width * dpr;
            canvas.height = height * dpr;
            const ctx = canvas.getContext('2d');

            ctx.drawImage(
                img,
                x * dpr, y * dpr, width * dpr, height * dpr,
                0, 0, width * dpr, height * dpr
            );

            resolve(canvas.toDataURL('image/png'));
        };
        img.src = imageData;
    });
}

// Send image to Gemini for analysis
async function enviarImagenAGemini(imagenBase64) {
    const deviceId = await generateDeviceId();

    return new Promise((resolve) => {
        chrome.storage.local.get(['geminiApiKey'], async function (result) {
            const apiKey = result.geminiApiKey || "";

            try {
                const response = await fetch(`${serverURL}/consultar_gemini_imagen/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        imagen: imagenBase64,
                        api_key: apiKey,
                        device_id: deviceId
                    })
                });

                const text = await response.text();
                let data;
                try {
                    data = JSON.parse(text);
                } catch (e) {
                    mostrarRespuesta('Server error', true);
                    resolve();
                    return;
                }

                if (data.success) {
                    if (data.source === 'diccionario' && data.result) {
                        mostrarRespuesta({ results: [data.result] }, true);
                    } else {
                        mostrarRespuesta({ source: 'gemini', text: data.respuesta }, true);
                    }
                } else {
                    mostrarRespuesta(data.error || 'Error', true);
                }
                resolve();
            } catch (error) {
                mostrarRespuesta('Error: ' + error.message, true);
                resolve();
            }
        });
    });
}

// Query Gemini when question is not found in DB
async function consultarGemini(pregunta) {
    const deviceId = await generateDeviceId();

    return new Promise((resolve) => {
        chrome.storage.local.get(['geminiApiKey'], async function (result) {
            const apiKey = result.geminiApiKey;
            if (!apiKey) {
                resolve({ success: false, message: 'La llave de API fue omitida. Para que la Inteligencia Artificial te rescate, agrégala instalando la extensión nuevamente.' });
                return;
            }

            try {
                const response = await fetch(`${serverURL}/consultar_gemini/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        pregunta: pregunta,
                        api_key: apiKey,
                        device_id: deviceId
                    })
                });

                const text = await response.text();
                let data;
                try {
                    data = JSON.parse(text);
                } catch (e) {
                    console.error('Response is not JSON:', text.substring(0, 200));
                    resolve({ success: false, message: 'Server error' });
                    return;
                }

                if (data.success) {
                    resolve({ success: true, message: data.respuesta });
                } else {
                    resolve({ success: false, message: data.error || 'No response from Gemini' });
                }
            } catch (error) {
                console.error('Error querying Gemini:', error);
                resolve({ success: false, message: `Error: ${error.message}` });
            }
        });
    });
}

// Show activation dialog
function showActivationDialog() {
    const dialog = document.createElement('div');
    dialog.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      background: #f0f0f0;
      padding: 12px;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      z-index: 10000;
      color: #333;
      font-family: 'Segoe UI', Arial, sans-serif;
      border: 1px solid #ccc;
      max-width: 280px;
      font-size: 12px;
  `;

    dialog.innerHTML = `
      <div style="display: flex; align-items: center; margin-bottom: 8px;">
          <div style="width: 16px; height: 16px; background: #0078d7; margin-right: 8px; border-radius: 2px;"></div>
          <h3 style="margin: 0; font-size: 12px; font-weight: normal;">Initial setup</h3>
      </div>
      <label style="font-size: 11px; color: #555;">Activation key:</label>
      <input type="password" id="activationKey" placeholder="Enter key" 
             style="width: 100%; padding: 4px; margin: 4px 0 8px 0; border: 1px solid #ccc; 
                    font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; box-sizing: border-box;">
      <label style="font-size: 11px; color: #555;">Gemini API Key (optional):</label>
      <input type="password" id="geminiApiKey" placeholder="For web queries" 
             style="width: 100%; padding: 4px; margin: 4px 0; border: 1px solid #ccc; 
                    font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; box-sizing: border-box;">
      <p style="margin: 2px 0 8px 0; font-size: 10px; color: #888;">
          <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #0078d7;">Get free API key</a>
      </p>
      <div style="display: flex; justify-content: flex-end; margin-top: 8px;">
          <button id="activateBtn" style="padding: 4px 12px; background: #f0f0f0; 
                                         color: #333; border: 1px solid #ccc; border-radius: 2px; 
                                         cursor: pointer; font-family: 'Segoe UI', Arial, sans-serif; 
                                         font-size: 12px;">
              Accept
          </button>
      </div>
      <p id="activationMessage" style="margin: 8px 0 0 0; color: #666; font-size: 11px;"></p>
  `;

    document.body.appendChild(dialog);

    const activateBtn = dialog.querySelector('#activateBtn');
    const activationKey = dialog.querySelector('#activationKey');
    const geminiApiKeyInput = dialog.querySelector('#geminiApiKey');
    const messageEl = dialog.querySelector('#activationMessage');

    activateBtn.onclick = async () => {
        const result = await activateExtension(activationKey.value, geminiApiKeyInput.value);
        messageEl.textContent = result.message;
        messageEl.style.color = result.success ? '#2e7d32' : '#c62828';

        if (result.success) {
            setTimeout(() => {
                dialog.remove();
                location.reload();
            }, 1500);
        }
    };
}

// Helper to escape HTML in user content
function _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function mostrarRespuesta(respuesta, found = true, preguntaOriginal = null) {
    let box = document.createElement("div");

    // Detect if system is in dark mode
    const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (found && respuesta && typeof respuesta === 'object' && respuesta.results) {
        // ── NEW FORMAT: DB results with type/answers ──
        const result = respuesta.results[0];
        let html = '';

        // Helper to render answers for a given set
        function renderAnswers(answers, type) {
            let h = '';
            if (type === 'MATCH') {
                const borderColor = isDarkMode ? '#555' : '#ccc';
                h += `<table style="border-collapse:collapse;width:100%;font-size:7px;">`;
                answers.forEach(a => {
                    h += `<tr><td style="padding:1px 3px;border-bottom:1px solid ${borderColor};">${_escapeHtml(a.text)}</td><td style="padding:1px 2px;color:${isDarkMode ? '#aaa' : '#888'};">→</td><td style="padding:1px 3px;border-bottom:1px solid ${borderColor};">${_escapeHtml(a.match_pair || '')}</td></tr>`;
                });
                h += `</table>`;
            } else {
                const correct = answers.filter(a => a.is_correct);
                if (correct.length === 1) {
                    h += `<span style="display:inline-flex;align-items:center;margin-right:3px;"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="${isDarkMode ? '#8f8' : '#2a7a2a'}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg></span> ${_escapeHtml(correct[0].text)}`;
                } else {
                    correct.forEach(a => {
                        h += `<div style="margin:1px 0;"><span style="display:inline-flex;align-items:center;margin-right:3px;"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="${isDarkMode ? '#8f8' : '#2a7a2a'}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg></span> ${_escapeHtml(a.text)}</div>`;
                    });
                }
            }
            return h;
        }

        // Check if there are multiple variants
        if (result.variants && result.variants.length > 1) {
            const sepColor = isDarkMode ? '#555' : '#ccc';
            result.variants.forEach((v, i) => {
                if (i > 0) {
                    html += `<div style="border-top:1px dashed ${sepColor};margin:3px 0;padding-top:2px;font-size:6px;color:${isDarkMode ? '#888' : '#999'};">Caso ${v.variant}</div>`;
                }
                html += renderAnswers(v.answers, result.type);
            });
        } else {
            html += renderAnswers(result.answers, result.type);
        }

        box.innerHTML = html;
    } else if (found && Array.isArray(respuesta)) {
        // ── LEGACY FORMAT: [" ", "answer text"] ──
        box.innerHTML = `<strong>Option ${respuesta[0]}</strong>:<br>${respuesta[1]}`;
    } else if (found && respuesta && respuesta.source === 'gemini') {
        // ── GEMINI IA FORMAT FROM IMAGE CAPTURE ──
        box.innerHTML = `<div style="display:flex;align-items:center;gap:4px;margin-bottom:2px;font-size:9px;"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg><strong>IA</strong></div>${_escapeHtml(respuesta.text)}`;
    } else if (found && typeof respuesta === 'string') {
        box.innerText = respuesta;
    } else {
        // Not found - show query buttons
        const iconColor = isDarkMode ? '#aaa' : '#555';
        box.innerHTML = `
      <span style="display: inline-flex; align-items: center; margin-right: 6px;">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="${iconColor}" stroke-width="2.5" stroke-linecap="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </span>
      <button id="consultarGeminiBtn" style="
        padding: 3px 6px; 
        cursor: pointer; 
        background: ${isDarkMode ? 'rgba(50,50,50,0.8)' : 'rgba(220,220,220,0.8)'}; 
        border: 1px solid ${isDarkMode ? '#444' : '#bbb'}; 
        border-radius: 4px;
        color: inherit;
        margin-right: 4px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      ">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
          <circle cx="12" cy="12" r="3"></circle>
        </svg>
      </button>
      <button id="capturarPantallaBtn" style="
        padding: 3px 6px; 
        cursor: pointer; 
        background: ${isDarkMode ? 'rgba(50,50,50,0.8)' : 'rgba(220,220,220,0.8)'}; 
        border: 1px solid ${isDarkMode ? '#444' : '#bbb'}; 
        border-radius: 4px;
        color: inherit;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      ">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
      </button>
    `;
    }

    // Base styles
    box.style.position = "fixed";
    box.style.bottom = "16px";
    box.style.left = "16px";
    box.style.padding = "3px 6px";
    box.style.borderRadius = "4px";
    box.style.zIndex = "9999";
    box.style.fontFamily = "'Segoe UI', Arial, sans-serif";
    box.style.fontSize = "8px";
    box.style.maxWidth = "220px";
    box.style.backdropFilter = "blur(2px)";
    box.style.transition = "opacity 0.3s ease, background-color 0.3s ease, color 0.3s ease";
    box.style.opacity = "0.3"; // low initial opacity
    box.style.cursor = "pointer";

    if (isDarkMode) {
        box.style.backgroundColor = "rgba(30, 30, 30, 0.1)";
        box.style.color = "rgba(255, 255, 255, 0.3)";
    } else {
        box.style.backgroundColor = "rgba(240, 240, 240, 0.1)";
        box.style.color = "rgba(0, 0, 0, 0.3)";
    }

    // Remove previous popup if exists
    if (popupActivo) {
        popupActivo.remove();
    }

    document.body.appendChild(box);
    popupActivo = box;

    // Initial animation
    requestAnimationFrame(() => { box.style.opacity = "1"; });

    // If not found, add event listeners to buttons
    if (!found && preguntaOriginal) {
        // Text query button (eye icon)
        const geminiBtn = box.querySelector('#consultarGeminiBtn');
        if (geminiBtn) {
            geminiBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                geminiBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32"><animate attributeName="stroke-dashoffset" dur="1s" values="32;0" repeatCount="indefinite"/></circle></svg>';
                geminiBtn.disabled = true;

                const resultado = await consultarGemini(preguntaOriginal);

                if (resultado.success) {
                    box.innerHTML = `<div style="display:flex;align-items:center;gap:4px;margin-bottom:4px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg><strong>IA</strong></div>${resultado.message}`;
                    // Make result visible
                    box.style.backgroundColor = isDarkMode ? "rgba(33, 28, 28, 0.5)" : "rgba(240,240,240,0.5)";
                    box.style.color = isDarkMode ? "rgba(255,255,255,0.9)" : "rgba(0,0,0,0.9)";
                    box.style.maxWidth = "250px";
                } else {
                    geminiBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#e55" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
                }
            });
        }

        // Screen capture button (camera icon)
        const capturaBtn = box.querySelector('#capturarPantallaBtn');
        if (capturaBtn) {
            capturaBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                box.remove();
                popupActivo = null;
                iniciarCapturaPantalla();
            });
        }
    }

    // Handle clicks on the popup
    let activo = false;
    box.addEventListener("click", (e) => {
        // Don't toggle if a button was clicked
        if (e.target.id === 'consultarGeminiBtn' || e.target.id === 'capturarPantallaBtn') return;

        e.stopPropagation(); // Prevent click from propagating to body
        if (!activo) {
            // Make brighter
            box.style.backgroundColor = isDarkMode ? "rgba(30,30,30,0.3)" : "rgba(240,240,240,0.3)";
            box.style.color = isDarkMode ? "rgba(255,255,255,0.8)" : "rgba(0,0,0,0.8)";
        } else {
            // Return to original state
            box.style.backgroundColor = isDarkMode ? "rgba(30,30,30,0.1)" : "rgba(240,240,240,0.1)";
            box.style.color = isDarkMode ? "rgba(255,255,255,0.3)" : "rgba(0,0,0,0.3)";
        }
        activo = !activo;
    });

    // Click outside the popup
    const clickFuera = (e) => {
        if (!box.contains(e.target)) {
            box.remove();
            popupActivo = null;
            document.removeEventListener("click", clickFuera);
        }
    };
    document.addEventListener("click", clickFuera);
}


// Initialization
async function initialize() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['isActivated'], async function (result) {
            const isActivated = result.isActivated === true;
            const deviceId = await generateDeviceId();

            // Add style to make selection transparent
            const style = document.createElement('style');
            style.textContent = `
              ::selection {
                  background: transparent;
                  color: inherit;
              }
              ::-moz-selection {
                  background: transparent;
                  color: inherit;
              }
          `;
            document.head.appendChild(style);

            if (!isActivated) {
                const isActuallyActivated = await checkActivation();
                if (!isActuallyActivated) {
                    showActivationDialog();
                    return;
                }
                chrome.storage.local.set({ isActivated: true });
            }

            // Original event listener code
            document.addEventListener("mouseup", async (e) => {
                // Ignore if in capture mode
                if (modoCaptura) {
                    return;
                }

                // Ignore if click was inside an active popup
                if (popupActivo && popupActivo.contains(e.target)) {
                    return;
                }

                const seleccion = window.getSelection().toString().trim();
                if (seleccion.length > 0) {
                    try {
                        await navigator.clipboard.writeText(seleccion);
                        const response = await fetch(`${serverURL}/buscar/`, {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "X-Requested-With": "XMLHttpRequest"
                            },
                            body: JSON.stringify({
                                pregunta: seleccion,
                                device_id: deviceId
                            })
                        });

                        if (response.status === 403) {
                            chrome.storage.local.remove('isActivated');
                            location.reload();
                            return;
                        }

                        const text = await response.text();
                        let data;
                        try {
                            data = JSON.parse(text);
                        } catch (e) {
                            console.error('Response is not JSON:', text.substring(0, 200));
                            mostrarRespuesta("Server error", true);
                            return;
                        }
                        mostrarRespuesta(data.results ? data : data.respuesta, data.found, seleccion);
                    } catch (err) {
                        console.error("Error:", err);
                        mostrarRespuesta("Error connecting to server.", true);
                    }
                }
            });
            resolve();
        });
    });
}

// Start the extension
initialize();