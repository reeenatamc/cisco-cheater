// Content script for Cisco Cheater Chrome Extension
// Enhanced with aesthetic improvements for better UX

const serverURL = "https://cisco-cheater-production-2079.up.railway.app";

// ========== Device ID Generation ==========
function getDeviceId() {
  let deviceId = localStorage.getItem('cisco_device_id');
  if (!deviceId) {
    deviceId = 'dev_' + Math.random().toString(36).substr(2, 9) + Date.now();
    localStorage.setItem('cisco_device_id', deviceId);
  }
  return deviceId;
}

// ========== License Verification ==========
async function verifyActivation() {
  const deviceId = getDeviceId();
  try {
    const response = await fetch(`${serverURL}/verify_activation/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: deviceId })
    });
    const data = await response.json();
    return data.is_activated || false;
  } catch (error) {
    console.error('Error verifying activation:', error);
    return false;
  }
}

// ========== License Activation ==========
async function activateLicense(key) {
  const deviceId = getDeviceId();
  try {
    const response = await fetch(`${serverURL}/activate/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key: key, device_id: deviceId })
    });
    const data = await response.json();
    
    if (response.ok) {
      alert('✅ Licencia activada exitosamente!');
      return true;
    } else {
      alert('❌ Error: ' + (data.error || 'No se pudo activar'));
      return false;
    }
  } catch (error) {
    console.error('Error activating license:', error);
    alert('❌ Error de conexión al activar licencia');
    return false;
  }
}

// Prompt for license on first use
async function checkAndPromptActivation() {
  const isActivated = await verifyActivation();
  if (!isActivated) {
    const key = prompt('Por favor ingresa tu clave de activación:');
    if (key) {
      await activateLicense(key);
    }
  }
}

// ========== Search Question Function ==========
async function searchQuestion(questionText) {
  const deviceId = getDeviceId();
  try {
    const response = await fetch(`${serverURL}/buscar/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        pregunta: questionText,
        device_id: deviceId
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error searching question:', error);
    return { respuesta: '❌ Error de conexión', found: false };
  }
}

// ========== Format Answer with Aesthetic Improvements ==========
function formatAnswer(responseData) {
  const { respuesta, found } = responseData;
  
  if (!found) {
    return `<div style="color: #ff4444; font-weight: bold;">${respuesta}</div>`;
  }
  
  // Case 1: Tipo "unir" - Show pairs clearly
  if (typeof respuesta === 'object' && respuesta.tipo === 'unir') {
    let html = '<div style="line-height: 1.6;"><strong>Unir:</strong><br><br>';
    respuesta.pares.forEach(par => {
      html += `<div style="margin-bottom: 4px;"><strong>${par.izquierda}</strong> → ${par.derecha}</div>`;
    });
    html += '</div>';
    return html;
  }
  
  // Case 2: Array format (simple or multiple choice)
  if (Array.isArray(respuesta) && respuesta.length === 2) {
    const [indices, textos] = respuesta;
    
    // Single option
    if (typeof indices === 'number' || !indices.includes(',')) {
      return `<div><strong>Opción ${indices}:</strong> ${textos}</div>`;
    }
    
    // Multiple options
    const indicesArray = indices.split(',').map(s => s.trim());
    const textosArray = textos.split('.').map(s => s.trim()).filter(s => s);
    
    let html = '<div style="line-height: 1.6;">';
    indicesArray.forEach((idx, i) => {
      const texto = textosArray[i] || '';
      html += `<div style="margin-bottom: 3px;">• <strong>Opción ${idx}:</strong> ${texto}</div>`;
    });
    html += '</div>';
    return html;
  }
  
  // Fallback: just show as text
  return `<div>${respuesta}</div>`;
}

// ========== Popup Display ==========
let currentPopup = null;

function showPopup(x, y, content) {
  removePopup();
  
  const popup = document.createElement('div');
  popup.id = 'cisco-cheater-popup';
  popup.style.cssText = `
    position: fixed;
    left: ${x}px;
    top: ${y}px;
    background: ${isDarkMode() ? '#1a1a1a' : '#ffffff'};
    color: ${isDarkMode() ? '#e0e0e0' : '#333333'};
    border: 1px solid ${isDarkMode() ? '#444' : '#ccc'};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 10px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    z-index: 2147483647;
    max-width: 350px;
    opacity: 0.3;
    transition: opacity 0.2s ease;
    cursor: pointer;
  `;
  
  popup.innerHTML = content;
  document.body.appendChild(popup);
  currentPopup = popup;
  
  // Reveal on click
  popup.addEventListener('click', () => {
    popup.style.opacity = '1';
  });
  
  // Close on outside click
  setTimeout(() => {
    document.addEventListener('click', handleOutsideClick);
  }, 100);
}

function removePopup() {
  if (currentPopup) {
    currentPopup.remove();
    currentPopup = null;
  }
  document.removeEventListener('click', handleOutsideClick);
}

function handleOutsideClick(e) {
  if (currentPopup && !currentPopup.contains(e.target)) {
    removePopup();
  }
}

function isDarkMode() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

// ========== Text Selection Handler ==========
document.addEventListener('mouseup', async (e) => {
  const selectedText = window.getSelection().toString().trim();
  
  if (selectedText.length > 10) {
    const isActivated = await verifyActivation();
    if (!isActivated) {
      showPopup(e.pageX, e.pageY, 
        '<div style="color: #ff4444;">❌ Extensión no activada. Recarga la página.</div>');
      return;
    }
    
    // Show loading
    showPopup(e.pageX, e.pageY, '<div>🔍 Buscando...</div>');
    
    // Search question
    const result = await searchQuestion(selectedText);
    const formattedAnswer = formatAnswer(result);
    
    showPopup(e.pageX, e.pageY, formattedAnswer);
    
    // Add Gemini fallback button if not found
    if (!result.found) {
      addGeminiFallback(selectedText);
    }
  }
});

// ========== Gemini Integration (Fallback) ==========
function addGeminiFallback(questionText) {
  if (!currentPopup) return;
  
  const geminiBtn = document.createElement('div');
  geminiBtn.style.cssText = `
    margin-top: 8px;
    padding: 6px 10px;
    background: #4285f4;
    color: white;
    border-radius: 4px;
    cursor: pointer;
    text-align: center;
    font-size: 9px;
  `;
  geminiBtn.textContent = '👁️ Consultar con Gemini';
  geminiBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    askGemini(questionText);
  });
  
  const captureBtn = document.createElement('div');
  captureBtn.style.cssText = geminiBtn.style.cssText;
  captureBtn.textContent = '📸 Capturar área';
  captureBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    startAreaCapture();
  });
  
  currentPopup.appendChild(geminiBtn);
  currentPopup.appendChild(captureBtn);
}

function askGemini(questionText) {
  // TODO: Implement Gemini API integration
  console.log('Asking Gemini:', questionText);
  alert('Función Gemini en desarrollo');
}

// ========== Screen Capture with Area Selection ==========
function startAreaCapture() {
  chrome.runtime.sendMessage({ action: "captureScreen" }, (response) => {
    if (response.error) {
      console.error('Capture error:', response.error);
      return;
    }
    
    if (response.imageData) {
      showAreaSelector(response.imageData);
    }
  });
}

function showAreaSelector(imageDataUrl) {
  // Create overlay with captured image
  const overlay = document.createElement('div');
  overlay.id = 'cisco-area-selector';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 2147483646;
    cursor: crosshair;
  `;
  
  const img = document.createElement('img');
  img.src = imageDataUrl;
  img.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0.7;
  `;
  overlay.appendChild(img);
  
  const selector = document.createElement('div');
  selector.style.cssText = `
    position: absolute;
    border: 2px dashed #4285f4;
    background: rgba(66, 133, 244, 0.1);
    display: none;
  `;
  overlay.appendChild(selector);
  
  let startX, startY, isSelecting = false;
  
  overlay.addEventListener('mousedown', (e) => {
    startX = e.clientX;
    startY = e.clientY;
    isSelecting = true;
    selector.style.left = startX + 'px';
    selector.style.top = startY + 'px';
    selector.style.width = '0px';
    selector.style.height = '0px';
    selector.style.display = 'block';
  });
  
  overlay.addEventListener('mousemove', (e) => {
    if (!isSelecting) return;
    const width = e.clientX - startX;
    const height = e.clientY - startY;
    selector.style.width = Math.abs(width) + 'px';
    selector.style.height = Math.abs(height) + 'px';
    selector.style.left = (width < 0 ? e.clientX : startX) + 'px';
    selector.style.top = (height < 0 ? e.clientY : startY) + 'px';
  });
  
  overlay.addEventListener('mouseup', (e) => {
    if (!isSelecting) return;
    isSelecting = false;
    
    // Crop and process the selected area
    const rect = selector.getBoundingClientRect();
    overlay.remove();
    
    // TODO: Crop image and send to OCR/Gemini
    console.log('Selected area:', rect);
  });
  
  document.body.appendChild(overlay);
}

// ========== Remove text selection highlight ==========
const style = document.createElement('style');
style.textContent = `
  ::selection {
    background: transparent !important;
  }
  ::-moz-selection {
    background: transparent !important;
  }
`;
document.head.appendChild(style);

// ========== Initialize ==========
checkAndPromptActivation();
