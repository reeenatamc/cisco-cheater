// Background script for Chrome extension
// Handles keyboard shortcuts and screen capture

chrome.commands.onCommand.addListener((command) => {
  if (command === "capture_screen") {
    captureAndSend();
  }
});

function captureAndSend() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
      chrome.tabs.captureVisibleTab(null, { format: "png" }, (imageDataUrl) => {
        if (chrome.runtime.lastError) {
          console.error("Error capturing tab:", chrome.runtime.lastError);
          return;
        }
        
        // Send image to content script
        chrome.tabs.sendMessage(tabs[0].id, {
          action: "screenCaptured",
          imageData: imageDataUrl
        });
      });
    }
  });
}

// Listen for direct capture requests from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "captureScreen") {
    chrome.tabs.captureVisibleTab(null, { format: "png" }, (imageDataUrl) => {
      if (chrome.runtime.lastError) {
        sendResponse({ error: chrome.runtime.lastError.message });
      } else {
        sendResponse({ imageData: imageDataUrl });
      }
    });
    return true; // Keep channel open for async response
  }
});
