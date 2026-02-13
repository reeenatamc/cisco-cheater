# Chrome Extension - Cisco Cheater

This directory contains the JavaScript files for the Cisco Cheater Chrome extension.

## Files

### background.js
Background service worker that handles:
- Keyboard shortcut commands (Alt+. for screen capture)
- Screen capture functionality via `chrome.tabs.captureVisibleTab`
- Message passing between background and content scripts

### content.js
Main content script that runs on web pages. Features include:

#### Core Functionality
- **Device ID Generation**: Creates a unique device identifier for license validation
- **License Management**: Activation and verification of user licenses
- **Question Search**: Automatically searches questions when text is selected
- **Response Formatting**: Displays answers with improved aesthetics

#### Enhanced UI/UX (Key Improvements)
1. **Matching/Drag Questions (tipo: 'unir')**:
   - Clear list format with bold left elements
   - Arrow separator (→) for better readability
   - All pairs visible at once without extra clicks
   - "Unir:" header for context

2. **Single Choice Questions (opcion_simple)**:
   - Format: `Opción N: texto` with bold number
   - Clean, single-line display

3. **Multiple Choice Questions (opcion_multiple)**:
   - Bullet-point list with each option on separate line
   - Bold option numbers for quick scanning

4. **Stealth Design**:
   - Initial opacity: 0.3 (nearly invisible)
   - Reveals to full opacity on click
   - Adapts to dark/light mode automatically
   - Small font (10px) to remain discreet
   - Closes on outside click

#### Additional Features
- **Gemini Integration**: Fallback AI assistant when question not found
- **Area Screenshot**: Select specific screen region for OCR/analysis
- **Transparent Selection**: Text selection doesn't show blue highlight

## Server Configuration

The extension connects to:
```javascript
const serverURL = "https://cisco-cheater-production-2079.up.railway.app";
```

## API Endpoints Used

- `POST /verify_activation/` - Verify device activation status
- `POST /activate/` - Activate license with key
- `POST /buscar/` - Search for questions

## Response Format

The backend now returns responses with a `found` field:

```javascript
// Found - Simple
{ 
  respuesta: [2, "Answer text"],
  found: true 
}

// Found - Multiple
{
  respuesta: ["1, 3", "Answer 1. Answer 3"],
  found: true
}

// Found - Matching
{
  respuesta: {
    tipo: 'unir',
    pregunta_numero: 5,
    pares: [
      { izquierda: 'Term', derecha: 'Definition' }
    ]
  },
  found: true
}

// Not Found
{
  respuesta: '❌ Pregunta no encontrada.',
  found: false
}
```
