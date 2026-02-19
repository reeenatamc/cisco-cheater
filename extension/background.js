/**
 * background.js — Service worker de la extensión cisco-cheater.
 *
 * Gestiona:
 *  - Activación de clave / verificación
 *  - Comando de búsqueda rápida (shortcut)
 *  - Captura de pantalla
 */

const API_BASE = "http://localhost:8000";

// ─── Activación ─────────────────────────────────────────

async function activateKey(key) {
  const deviceId = await getOrCreateDeviceId();
  const res = await fetch(`${API_BASE}/activate/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, device_id: deviceId }),
  });
  return res.json();
}

async function verifyActivation() {
  const deviceId = await getOrCreateDeviceId();
  const res = await fetch(`${API_BASE}/verify_activation/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ device_id: deviceId }),
  });
  return res.json();
}

// ─── Device ID ──────────────────────────────────────────

function getOrCreateDeviceId() {
  return new Promise((resolve) => {
    chrome.storage.local.get("device_id", (result) => {
      if (result.device_id) {
        resolve(result.device_id);
      } else {
        const id = crypto.randomUUID();
        chrome.storage.local.set({ device_id: id }, () => resolve(id));
      }
    });
  });
}

// ─── Mensajes desde popup / content ─────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "activate") {
    activateKey(msg.key).then(sendResponse);
    return true; // async
  }

  if (msg.action === "verify") {
    verifyActivation().then(sendResponse);
    return true;
  }

  if (msg.action === "getDeviceId") {
    getOrCreateDeviceId().then((id) => sendResponse({ device_id: id }));
    return true;
  }
});

// ─── Shortcut (Ctrl+Shift+F) ───────────────────────────

chrome.commands?.onCommand?.addListener((command) => {
  if (command === "search-answer") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { action: "search" });
      }
    });
  }
  
  if (command === "capture-screen") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
          chrome.tabs.sendMessage(tabs[0].id, {
            action: "showCaptureOverlay",
            imageData: dataUrl,
          });
        });
      }
    });
  }
});

// ─── Instalación ────────────────────────────────────────

chrome.runtime.onInstalled.addListener(() => {
  console.log("[cisco-cheater] Extensión instalada.");
});
